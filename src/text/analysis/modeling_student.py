"""
================================================================================
KNOWLEDGE DISTILLATION: LAG-FREE STUDENT MODEL TRAINING
================================================================================

PURPOSE:
  This script implements knowledge distillation to train a lag-free LASSO model
  that mimics the predictions of the full (lagged) LASSO model. The student model
  learns to reproduce the teacher model's predictions using only features that
  don't require lagged CPI data.

WORKFLOW:
  1. Train the main LASSO model (teacher) with all features including lagged CPI
  2. Generate in-sample predictions from the teacher model
  3. Define a feature set excluding lagged CPI variables
  4. Train a second LASSO model (student) using non-lag features as X and
     teacher predictions as y
  5. Compare both models' alpha and R² scores
  6. Apply the student model to out-of-bag countries (which lack lag variables)
  7. Save both prediction DataFrames (teacher and student) for comparison

KEY FEATURES:
  - Teacher model: Full LASSO with all features (including lagged CPI)
  - Student model: Lag-free LASSO trained on teacher predictions
  - Automatic detection of lagged features (contains "lag" or "cpi_inflation_ma")
  - Separate predictions for in-bag and out-of-bag countries
  - Comparison metrics: alpha, R² scores, prediction differences

INPUT DATA:
  - Source: pic_epu_combined.dta (Stata file)
  - Variables: country, date, grosstonnage, CPI, EPU indices, sentiment scores

OUTPUT:
  - Teacher predictions: {country}/lasso_preds/teacher/predictions.csv
  - Student predictions: {country}/lasso_preds/student/predictions.csv
  - Comparison metrics and model performance statistics

DEPENDENCIES:
  pandas, numpy, scikit-learn
================================================================================
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LassoCV, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, r2_score
import warnings
warnings.filterwarnings('ignore')

import sys, os
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


CPI_DATA_ROOT = PROJECT_ROOT / "data" / "auxiliary_data"
EPU_DATA_ROOT = PROJECT_ROOT / "testing_outputs" / "text"
TOPICS = ["inflation", "job"]

# Countries with complete CPI lag data (used for training)
TRAIN_COUNTRIES = [c for c in os.listdir(EPU_DATA_ROOT) if c not in EXCLUDE_COUNTRIES]

EXCLUDE_COUNTRIES = [
    'american_samoa', # No Data
    "guam", # No Data
    "malaysia", # Not enough news yet
    'marshall_islands', # No Data
    "new_zealand", # Quarterly Data
    "pacific", # No Data
    "palau", # Quarterly Data
    "papua_new_guinea", # Quarterly Data
    "south_korea", # Not enough news yet
    "singapore", # Not enough news yet
    "thailand", # Not enough news yet
    "tuvalu", # No Data
    "vanuatu", # Quarterly Data
    ]

OOB_COUNTRIES = [
    "pacific",
    "new_zealand",
    "papua_new_guinea",
    "tuvalu",
    "vanuatu",
]

# Set random seed for reproducibility
np.random.seed(123)

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================
def prepare_epu_data(countries):
    from data import read_epu_files, read_epu_topics_files, read_sentiment_files, group_monthly
    epu = read_epu_files(EPU_DATA_ROOT, countries)
    epu_topics = read_epu_topics_files(EPU_DATA_ROOT, TOPICS, countries)
    sentiment = read_sentiment_files(EPU_DATA_ROOT, countries)

    df = epu.set_index(['date', 'country']).join(
        epu_topics.set_index(['date', 'country'])
        ).join(
            sentiment.set_index(['date', 'country'])
            ).reset_index()
    df = group_monthly(df)

    # Create period variable (months since Jan 2015)
    df['period'] = (df['date'].dt.year - 2015) * 12 + df['date'].dt.month - 1

    # Sort by country and date
    df = df.sort_values(['country', 'date']).reset_index(drop=True)
    return df

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

def prepare_cpi(countries_slugs):
    from cpi import get_cpi_data
    countries = pd.read_csv(CPI_DATA_ROOT / "countries.csv")
    countries = countries[countries["slug"].isin(countries_slugs)]
    countries_list = countries["iso3"].tolist()
    country_map = countries.set_index("iso3")["slug"].to_dict()
    cpi = get_cpi_data(countries_list).rename(columns={"value": "cpi"})
    cpi = cpi.rename(columns={"COUNTRY": "country"})
    cpi['country_id'] = pd.factorize(cpi['country'])[0] + 1
    # Calculate inflation rates
    col_prefix = 'cpi'
    inflation_col = f'{col_prefix}_inflation'
            
    # Lag CPI by 1 period within each country
    cpi[f'l1_{col_prefix}'] = cpi.groupby('country_id')[col_prefix].shift(1)
            
    # Calculate inflation rate
    cpi[inflation_col] = (cpi[col_prefix] - cpi[f'l1_{col_prefix}']) * 100 / cpi[f'l1_{col_prefix}']
    # Generate MA3 (3-period moving average) for smoothing
    ma3_vars = [col for col in cpi.columns if 'inflation' in col]
    for var in ma3_vars:
        if var in cpi.columns and not var.endswith('_ma3'):
            cpi[f'{var}_ma3'] = cpi.groupby('country_id')[var].transform(lambda x: x.rolling(window=3, center=True).mean())
    cpi['country'] = cpi['country'].map(country_map)
    cpi = cpi[["country", "country_id", 'date', 'cpi', 'l1_cpi', 'cpi_inflation', 'cpi_inflation_ma3']]
    return cpi

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def run_lasso_model(X, y, model_name="LASSO"):
    """
    Run LASSO regression with cross-validation
    Returns predictions aligned with original data (NaN for invalid rows)
    """
    # Remove rows with missing values
    valid_idx = ~(X.isna().any(axis=1) | y.isna())
    X_clean = X[valid_idx].copy()
    y_clean = y[valid_idx].copy()
    
    if len(X_clean) == 0:
        print(f"Warning: No valid data for {model_name}")
        return None, None, None, None, None
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clean)
    
    # Run LassoCV
    lasso = LassoCV(cv=5, random_state=123, max_iter=10000)
    lasso.fit(X_scaled, y_clean)
    
    # Get predictions on clean data
    y_pred_clean = lasso.predict(X_scaled)
    
    # Create full-length prediction array with NaN for invalid rows
    y_pred_full = np.full(len(X), np.nan)
    y_pred_full[valid_idx.values] = y_pred_clean
    
    # Get coefficients
    coef_df = pd.DataFrame({
        'Variable': X.columns,
        'Coefficient': lasso.coef_
    })
    
    return lasso, y_pred_full, coef_df, scaler, X.columns.tolist()

def calculate_metrics(y_true, y_pred, y_pred_binary=None):
    """
    Calculate regression and classification metrics
    Handles pandas Series and numpy arrays with NaN values
    """
    # Convert to numpy arrays
    y_true_arr = y_true.values if isinstance(y_true, pd.Series) else y_true
    y_pred_arr = y_pred if isinstance(y_pred, np.ndarray) else np.array(y_pred)
    
    # Remove NaN values for regression metrics
    valid_idx = ~(np.isnan(y_true_arr) | np.isnan(y_pred_arr))
    y_true_clean = y_true_arr[valid_idx]
    y_pred_clean = y_pred_arr[valid_idx]
    
    if len(y_true_clean) == 0:
        return {}
    
    # Regression metrics
    residuals = y_true_clean - y_pred_clean
    mse = np.mean(residuals ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(residuals))
    
    metrics = {
        'MSE': mse,
        'RMSE': rmse,
        'MAE': mae
    }
    
    # Classification metrics (if binary predictions provided)
    if y_pred_binary is not None:
        y_true_binary = (y_true_clean > 0).astype(int)
        y_pred_binary_arr = y_pred_binary if isinstance(y_pred_binary, np.ndarray) else np.array(y_pred_binary)
        y_pred_binary_clean = y_pred_binary_arr[valid_idx]
        y_pred_binary_clean = (y_pred_binary_clean > 0).astype(int)
        
        if len(y_true_binary) > 0:
            cm = confusion_matrix(y_true_binary, y_pred_binary_clean)
            tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
            
            metrics['TP'] = tp
            metrics['TN'] = tn
            metrics['FP'] = fp
            metrics['FN'] = fn
            metrics['Accuracy'] = accuracy_score(y_true_binary, y_pred_binary_clean)
            
            if (tp + fp) > 0:
                metrics['Precision'] = tp / (tp + fp)
            if (tp + fn) > 0:
                metrics['Recall'] = tp / (tp + fn)
            if ('Precision' in metrics and 'Recall' in metrics):
                p = metrics['Precision']
                r = metrics['Recall']
                if (p + r) > 0:
                    metrics['F1-Score'] = 2 * (p * r) / (p + r)
    
    return metrics

def is_lagged_feature(feature_name):
    """
    Detect if a feature is a lagged variable.
    Returns True if feature contains 'lag' or 'cpi_inflation_ma' (without lag suffix).
    """
    feature_lower = feature_name.lower()
    if 'lag' in feature_lower:
        return True
    # Check for cpi_inflation_ma3 (the target variable, not a lag)
    if 'cpi_inflation_ma' in feature_lower and 'lag' not in feature_lower:
        return False
    return False

def get_non_lag_features(all_features):
    """
    Filter out lagged features from the feature list.
    Returns list of non-lagged features.
    """
    non_lag_features = [f for f in all_features if not is_lagged_feature(f)]
    return non_lag_features


if __name__ == '__main__':
    print("\n" + "="*70)
    print("KNOWLEDGE DISTILLATION: LAG-FREE STUDENT MODEL TRAINING")
    print("="*70)

    # ============================================================================
    # STEP 1: PREPARE DATA FOR TRAINING COUNTRIES
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 1: PREPARE DATA FOR TRAINING COUNTRIES")
    print("="*70)

    # Load EPU data for all countries
    all_countries = TRAIN_COUNTRIES + OOB_COUNTRIES
    df_epu = prepare_epu_data(all_countries)
    
    # Load CPI data for training countries only
    cpi_train = prepare_cpi(TRAIN_COUNTRIES)
    
    # Merge EPU and CPI for training countries
    df_train = df_epu[df_epu['country'].isin(TRAIN_COUNTRIES)].copy()
    df_train = df_train.set_index(['country', 'date']).join(
        cpi_train.set_index(['country', 'date'])
    ).reset_index()
    df_train = df_train.sort_values(['country', 'date']).reset_index(drop=True)
    
    print(f"Training countries: {TRAIN_COUNTRIES}")
    print(f"Training data shape: {df_train.shape}")
    print(f"Training data date range: {df_train['date'].min()} to {df_train['date'].max()}")

    # ============================================================================
    # STEP 2: TRAIN TEACHER MODEL (FULL LASSO WITH LAGS)
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 2: TRAIN TEACHER MODEL (FULL LASSO WITH LAGS)")
    print("="*70)

    # Prepare features for training
    df_pooled_train = df_train.copy()
    
    # Get list of unique countries in training set
    countries_train = df_pooled_train['country'].unique()
    print(f"Training countries in dataset: {countries_train}")

    # Select base features for LASSO (MA3 versions)
    feature_cols_base = [col for col in df_train.columns if any(x in col for x in ['inflation_epu', 'epu', 'sentiment']) and col.endswith('_ma3')]
    feature_cols_base = [col for col in feature_cols_base if col in df_train.columns]

    print(f"Base features: {feature_cols_base}")

    # Add lagged inflation
    for lag in [1, 2]:
        df_pooled_train[f'cpi_inflation_ma3_lag{lag}'] = df_pooled_train.groupby('country_id')['cpi_inflation_ma3'].shift(lag)

    feature_cols_with_lags = [f'cpi_inflation_ma3_lag{i}' for i in [1, 2]] + feature_cols_base

    # Create country dummy variables
    for country in countries_train:
        df_pooled_train[f'country_{country}'] = (df_pooled_train['country'] == country).astype(int)

    country_dummies = [f'country_{country}' for country in countries_train[:-1]]  # Drop one for multicollinearity

    # Create interaction terms: base features * country dummies
    interaction_cols = []
    for feature in feature_cols_with_lags:
        for country in countries_train[:-1]:  # Use all but one country to avoid multicollinearity
            interaction_col = f'{feature}_x_{country}'
            df_pooled_train[interaction_col] = df_pooled_train[feature] * df_pooled_train[f'country_{country}']
            interaction_cols.append(interaction_col)

    # Combine all features: base features + country dummies + interactions
    all_features_teacher = feature_cols_with_lags + country_dummies + interaction_cols

    print(f"Total features for teacher model (including interactions): {len(all_features_teacher)}")

    # Train TEACHER LASSO model
    print("\nTraining TEACHER LASSO model with country interaction terms (MA3)...")
    X_teacher = df_pooled_train[all_features_teacher]
    y_target = df_pooled_train['cpi_inflation_ma3']

    teacher_model, pred_teacher, coef_teacher, scaler_teacher, feature_names_teacher = run_lasso_model(
        X_teacher, y_target, "Teacher LASSO with interactions"
    )

    if teacher_model is not None:
        metrics_teacher = calculate_metrics(y_target, pred_teacher, pred_teacher)
        print(f"Teacher RMSE: {metrics_teacher.get('RMSE', np.nan):.6f}")
        print(f"Teacher MAE: {metrics_teacher.get('MAE', np.nan):.6f}")
        print(f"Teacher Accuracy: {metrics_teacher.get('Accuracy', np.nan):.4f}")
        print(f"Teacher alpha: {teacher_model.alpha_:.6f}")
        
        # Calculate R² for teacher model
        valid_idx_teacher = ~(np.isnan(y_target.values) | np.isnan(pred_teacher))
        y_true_clean = y_target.values[valid_idx_teacher]
        y_pred_clean = pred_teacher[valid_idx_teacher]
        r2_teacher = r2_score(y_true_clean, y_pred_clean)
        print(f"Teacher R²: {r2_teacher:.6f}")

    # ============================================================================
    # STEP 3: IDENTIFY NON-LAG FEATURES FOR STUDENT MODEL
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 3: IDENTIFY NON-LAG FEATURES FOR STUDENT MODEL")
    print("="*70)

    # Get non-lag features (excluding lagged CPI variables)
    non_lag_features = get_non_lag_features(all_features_teacher)
    
    print(f"Total non-lag features: {len(non_lag_features)}")
    print(f"Lagged features excluded: {len(all_features_teacher) - len(non_lag_features)}")
    
    # Show which features were excluded
    lagged_features = [f for f in all_features_teacher if f not in non_lag_features]
    print(f"\nExcluded lagged features ({len(lagged_features)}):")
    for feat in sorted(lagged_features)[:10]:
        print(f"  - {feat}")
    if len(lagged_features) > 10:
        print(f"  ... and {len(lagged_features) - 10} more")

    # ============================================================================
    # STEP 4: TRAIN STUDENT MODEL (LAG-FREE LASSO)
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 4: TRAIN STUDENT MODEL (LAG-FREE LASSO)")
    print("="*70)

    print("\nTraining STUDENT LASSO model with non-lag features...")
    print("Student learns to mimic teacher predictions using only non-lag features...")
    
    # Prepare student feature matrix
    X_student = df_pooled_train[non_lag_features].copy()
    
    # Use teacher predictions as target for student
    y_student_target = pd.Series(pred_teacher, index=df_pooled_train.index)
    
    student_model, pred_student, coef_student, scaler_student, feature_names_student = run_lasso_model(
        X_student, y_student_target, "Student LASSO (lag-free)"
    )

    if student_model is not None:
        metrics_student = calculate_metrics(y_student_target, pred_student, pred_student)
        print(f"Student RMSE (vs teacher): {metrics_student.get('RMSE', np.nan):.6f}")
        print(f"Student MAE (vs teacher): {metrics_student.get('MAE', np.nan):.6f}")
        print(f"Student Accuracy (vs teacher): {metrics_student.get('Accuracy', np.nan):.4f}")
        print(f"Student alpha: {student_model.alpha_:.6f}")
        
        # Calculate R² for student model (how well it mimics teacher)
        valid_idx_student = ~(np.isnan(y_student_target.values) | np.isnan(pred_student))
        y_true_student = y_student_target.values[valid_idx_student]
        y_pred_student = pred_student[valid_idx_student]
        r2_student = r2_score(y_true_student, y_pred_student)
        print(f"Student R² (vs teacher): {r2_student:.6f}")

    # ============================================================================
    # STEP 5: COMPARISON OF TEACHER VS STUDENT
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 5: COMPARISON OF TEACHER VS STUDENT MODELS")
    print("="*70)

    print(f"\nModel Comparison:")
    print(f"  Teacher alpha: {teacher_model.alpha_:.6f}")
    print(f"  Student alpha: {student_model.alpha_:.6f}")
    print(f"  Teacher R² (vs actual): {r2_teacher:.6f}")
    print(f"  Student R² (vs teacher): {r2_student:.6f}")
    
    # Calculate prediction differences
    valid_idx_both = ~(np.isnan(pred_teacher) | np.isnan(pred_student))
    pred_diff = np.abs(pred_teacher[valid_idx_both] - pred_student[valid_idx_both])
    print(f"\nPrediction Differences (Teacher vs Student):")
    print(f"  Mean absolute difference: {pred_diff.mean():.6f}")
    print(f"  Std absolute difference: {pred_diff.std():.6f}")
    print(f"  Max absolute difference: {pred_diff.max():.6f}")

    # ============================================================================
    # STEP 6: SAVE TEACHER AND STUDENT PREDICTIONS FOR TRAINING COUNTRIES
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 6: SAVE PREDICTIONS FOR TRAINING COUNTRIES")
    print("="*70)

    for country in countries_train:
        country_mask = df_pooled_train['country'] == country
        df_country = df_pooled_train[country_mask].copy()
        
        if len(df_country) == 0:
            print(f"Skipping {country}: No data")
            continue
        
        # Get predictions for this country
        y_pred_teacher_country = pred_teacher[country_mask.values]
        y_pred_student_country = pred_student[country_mask.values]
        
        # Create teacher predictions dataframe
        teacher_df = pd.DataFrame({
            'date': df_country['date'].values,
            'actual_inflation': df_country['cpi_inflation_ma3'].values,
            'predicted_inflation': y_pred_teacher_country
        })
        
        # Create student predictions dataframe
        student_df = pd.DataFrame({
            'date': df_country['date'].values,
            'actual_inflation': df_country['cpi_inflation_ma3'].values,
            'predicted_inflation': y_pred_student_country
        })
        
        # Create output directories
        teacher_dir = PROJECT_ROOT / "testing_outputs" / "text" / country / "lasso_preds" / "teacher"
        student_dir = PROJECT_ROOT / "testing_outputs" / "text" / country / "lasso_preds" / "student"
        teacher_dir.mkdir(parents=True, exist_ok=True)
        student_dir.mkdir(parents=True, exist_ok=True)
        
        # Save predictions
        teacher_file = teacher_dir / "predictions.csv"
        student_file = student_dir / "predictions.csv"
        teacher_df.to_csv(teacher_file, index=False)
        student_df.to_csv(student_file, index=False)
        print(f"Saved predictions for {country}")
        print(f"  Teacher: {teacher_file}")
        print(f"  Student: {student_file}")

    # ============================================================================
    # STEP 7: APPLY STUDENT MODEL TO OUT-OF-BAG COUNTRIES
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 7: APPLY STUDENT MODEL TO OUT-OF-BAG COUNTRIES")
    print("="*70)

    # Load EPU data for out-of-bag countries
    df_oob = df_epu[df_epu['country'].isin(OOB_COUNTRIES)].copy()
    
    print(f"Out-of-bag countries: {OOB_COUNTRIES}")
    print(f"Out-of-bag data shape: {df_oob.shape}")

    # Prepare features for out-of-bag countries
    df_oob_features = df_oob.copy()
    
    # Add lagged inflation (will be NaN for out-of-bag countries)
    for lag in [1, 2]:
        df_oob_features[f'cpi_inflation_ma3_lag{lag}'] = df_oob_features.groupby('country')['cpi_inflation_ma3'].shift(lag)

    # Create country dummy variables for out-of-bag countries
    for country in OOB_COUNTRIES:
        df_oob_features[f'country_{country}'] = (df_oob_features['country'] == country).astype(int)

    oob_predictions_all = []

    for country in OOB_COUNTRIES:
        print(f"\n--- Processing {country} ---")
        
        df_country = df_oob_features[df_oob_features['country'] == country].copy()
        
        if len(df_country) == 0:
            print(f"No data for {country}")
            continue
        
        # Prepare feature matrix for this country using non-lag features only
        X_country = pd.DataFrame(index=df_country.index)
        
        # Add only non-lag features
        for feature in non_lag_features:
            if feature in df_country.columns:
                X_country[feature] = df_country[feature].values
            else:
                # Feature doesn't exist, fill with 0
                X_country[feature] = 0.0
        
        # Ensure column order matches student features
        X_country = X_country[non_lag_features]
        
        # Fill any NaN values with 0
        X_country = X_country.fillna(0.0)
        
        # Standardize features using student scaler
        X_country_scaled = scaler_student.transform(X_country)
        
        # Make predictions using student model
        y_pred_student_country = student_model.predict(X_country_scaled)
        
        # Create predictions dataframe
        predictions_df = pd.DataFrame({
            'date': df_country['date'].values,
            'actual_inflation': np.nan,  # No actual inflation for OOB countries
            'predicted_inflation': y_pred_student_country
        })
        
        # Create output directory
        output_dir = PROJECT_ROOT / "testing_outputs" / "text" / country / "lasso_preds" / "student_oob"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save predictions
        output_file = output_dir / "predictions.csv"
        predictions_df.to_csv(output_file, index=False)
        print(f"Saved student OOB predictions for {country} to {output_file}")
        print(f"  Records: {len(predictions_df)}")
        print(f"  Mean predicted inflation: {y_pred_student_country.mean():.6f}")
        print(f"  Std predicted inflation: {y_pred_student_country.std():.6f}")
        
        # Store for summary
        oob_predictions_all.append({
            'country': country,
            'n_records': len(predictions_df),
            'mean_pred': y_pred_student_country.mean(),
            'std_pred': y_pred_student_country.std(),
            'min_pred': y_pred_student_country.min(),
            'max_pred': y_pred_student_country.max(),
        })

    # ============================================================================
    # STEP 8: SUMMARY OF OUT-OF-BAG PREDICTIONS
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 8: OUT-OF-BAG PREDICTIONS SUMMARY")
    print("="*70)

    if oob_predictions_all:
        oob_summary_df = pd.DataFrame(oob_predictions_all)
        print("\nStudent model out-of-bag predictions summary:")
        print(oob_summary_df.to_string(index=False))
    else:
        print("No out-of-bag predictions generated")

    print("\n" + "="*70)
    print("COMPLETED: KNOWLEDGE DISTILLATION PIPELINE")
    print("="*70)
