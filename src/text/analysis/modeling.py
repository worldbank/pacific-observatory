"""
================================================================================
INFLATION PREDICTION WITH COUNTRY INTERACTION TERMS - LASSO REGRESSION
================================================================================

PURPOSE:
  This script extends the pooled inflation prediction analysis by incorporating
  country-specific interaction terms. It models how economic indicators (EPU,
  sentiment) have different effects across countries using LASSO regression.

SECTIONS:
  1. ALL COUNTRIES ANALYSIS WITH INTERACTION TERMS
     - Pooled LASSO model with base features + country dummies + interactions
     - Interaction terms capture country-specific effects of economic indicators
     - Uses 3-period moving averages (MA3) for smoothing
     - Outputs: RMSE, accuracy, and top feature coefficients

  2. COUNTRY-SPECIFIC PREDICTIONS AND ACCURACY
     - Evaluates pooled model performance for each country individually
     - Calculates country-level RMSE, MAE, and accuracy metrics
     - Compares predictive power across countries

  3. OVERALL MODEL PERFORMANCE
     - Aggregate metrics across all countries and observations
     - RMSE, MAE, accuracy, precision, recall, and F1-score

  4. FEATURE IMPORTANCE FROM INTERACTIONS
     - Analyzes base feature coefficients
     - Shows country dummy effects
     - Displays top 20 interaction term coefficients

INPUT DATA:
  - Source: pic_epu_combined.dta (Stata file)
  - Variables: country, date, grosstonnage, CPI, EPU indices, sentiment scores

OUTPUT:
  - Console output with model coefficients and country-specific metrics
  - Feature importance rankings and interaction term analysis

KEY FUNCTIONS:
  - run_lasso_model(): Fits LASSO with CV, handles missing data
  - calculate_metrics(): Computes regression and classification metrics

DEPENDENCIES:
  pandas, numpy, scikit-learn
================================================================================
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LassoCV, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
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
    # Create country ID

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
        return None, None, None
    
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
    
    return lasso, y_pred_full, coef_df

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


if __name__ == '__main__':
    countries = [c for c in os.listdir(EPU_DATA_ROOT) if c not in EXCLUDE_COUNTRIES]
    df = prepare_epu_data(countries)
    cpi = prepare_cpi(countries)
    df = df.set_index(['country', 'date']).join(
        cpi.set_index(['country', 'date'])
    ).reset_index()
    df = df.sort_values(['country', 'date']).reset_index(drop=True)
    pd.set_option('display.max_columns', 99)
    print(df.tail(50))
    # raise Exception("Stop")
    # ============================================================================
    # SECTION 1: ALL COUNTRIES ANALYSIS WITH INTERACTION TERMS
    # ============================================================================
    print("\n" + "="*70)
    print("SECTION 1: ALL COUNTRIES ANALYSIS WITH INTERACTION TERMS")
    print("="*70)

    # Prepare data for pooled analysis
    df_pooled = df.copy()

    # Get list of unique countries
    countries = df_pooled['country'].unique()
    print(f"Countries in dataset: {countries}")

    # Select base features for LASSO (MA3 versions)
    feature_cols_base = [col for col in df.columns if any(x in col for x in ['inflation_epu', 'epu', 'sentiment']) and col.endswith('_ma3')]
    feature_cols_base = [col for col in feature_cols_base if col in df.columns]

    print(f"Base features: {feature_cols_base}")

    # Add lagged inflation
    for lag in [1, 2]:
        df_pooled[f'cpi_inflation_ma3_lag{lag}'] = df_pooled.groupby('country_id')['cpi_inflation_ma3'].shift(lag)

    feature_cols_with_lags = [f'cpi_inflation_ma3_lag{i}' for i in [1, 2]] + feature_cols_base

    # Create country dummy variables
    for country in countries:
        df_pooled[f'country_{country}'] = (df_pooled['country'] == country).astype(int)

    country_dummies = [f'country_{country}' for country in countries[:-1]]  # Drop one for multicollinearity

    # Create interaction terms: base features * country dummies
    interaction_cols = []
    for feature in feature_cols_with_lags:
        for country in countries[:-1]:  # Use all but one country to avoid multicollinearity
            interaction_col = f'{feature}_x_{country}'
            df_pooled[interaction_col] = df_pooled[feature] * df_pooled[f'country_{country}']
            interaction_cols.append(interaction_col)

    # Combine all features: base features + country dummies + interactions
    all_features = feature_cols_with_lags + country_dummies + interaction_cols

    print(f"Total features (including interactions): {len(all_features)}")

    # Model with interaction terms
    print("\nModel: LASSO with country interaction terms (MA3)")
    X_interactions = df_pooled[all_features]
    y = df_pooled['cpi_inflation_ma3']

    lasso_interactions, pred_interactions, coef_interactions = run_lasso_model(X_interactions, y, "LASSO with interactions")

    if lasso_interactions is not None:
        metrics_interactions = calculate_metrics(y, pred_interactions, pred_interactions)
        print(f"RMSE (with interactions): {metrics_interactions.get('RMSE', np.nan):.6f}")
        print(f"Accuracy: {metrics_interactions.get('Accuracy', np.nan):.4f}")
        print(f"MAE: {metrics_interactions.get('MAE', np.nan):.6f}")
        
        # Print top coefficients
        coef_sorted = coef_interactions.sort_values('Coefficient', key=abs, ascending=False)
        print("\nTop 15 features by absolute coefficient:")
        print(coef_sorted.head(15).to_string(index=False))

    # ============================================================================
    # SECTION 2: COUNTRY-SPECIFIC PREDICTIONS AND ACCURACY
    # ============================================================================
    print("\n" + "="*70)
    print("SECTION 2: COUNTRY-SPECIFIC PREDICTIONS AND ACCURACY")
    print("="*70)

    # Store predictions for each country
    country_results = []

    for country in countries:
        print(f"\n--- Processing {country} ---")
        
        df_country = df_pooled[df_pooled['country'] == country].copy()
        
        if len(df_country) == 0:
            print(f"No data for {country}")
            continue
        
        # Get predictions for this country from the pooled model
        country_mask = df_pooled['country'] == country
        y_true_country = df_pooled[country_mask]['cpi_inflation_ma3'].values
        y_pred_country = pred_interactions[country_mask.values]
        
        # Calculate metrics for this country
        metrics_country = calculate_metrics(y_true_country, y_pred_country, y_pred_country)
        
        print(f"  Samples: {len(df_country)}")
        print(f"  RMSE: {metrics_country.get('RMSE', np.nan):.6f}")
        print(f"  MAE: {metrics_country.get('MAE', np.nan):.6f}")
        print(f"  Accuracy: {metrics_country.get('Accuracy', np.nan):.4f}")
        
        # Store results
        result_row = {
            'Country': country,
            'N_Samples': len(df_country),
            'MSE': metrics_country.get('MSE', np.nan),
            'RMSE': metrics_country.get('RMSE', np.nan),
            'MAE': metrics_country.get('MAE', np.nan),
            'Accuracy': metrics_country.get('Accuracy', np.nan),
            'Precision': metrics_country.get('Precision', np.nan),
            'Recall': metrics_country.get('Recall', np.nan),
            'F1-Score': metrics_country.get('F1-Score', np.nan),
        }
        country_results.append(result_row)

    # Create summary dataframe
    country_results_df = pd.DataFrame(country_results)
    print("\n" + "="*70)
    print("COUNTRY-SPECIFIC ACCURACY SUMMARY")
    print("="*70)
    print(country_results_df.to_string(index=False))

    # ============================================================================
    # SECTION 3: OVERALL MODEL PERFORMANCE
    # ============================================================================
    print("\n" + "="*70)
    print("SECTION 3: OVERALL MODEL PERFORMANCE")
    print("="*70)

    overall_metrics = calculate_metrics(y, pred_interactions, pred_interactions)
    print(f"Overall RMSE: {overall_metrics.get('RMSE', np.nan):.6f}")
    print(f"Overall MAE: {overall_metrics.get('MAE', np.nan):.6f}")
    print(f"Overall Accuracy: {overall_metrics.get('Accuracy', np.nan):.4f}")
    print(f"Overall Precision: {overall_metrics.get('Precision', np.nan):.4f}")
    print(f"Overall Recall: {overall_metrics.get('Recall', np.nan):.4f}")
    print(f"Overall F1-Score: {overall_metrics.get('F1-Score', np.nan):.4f}")

    # ============================================================================
    # SECTION 4: FEATURE IMPORTANCE FROM INTERACTIONS
    # ============================================================================
    print("\n" + "="*70)
    print("SECTION 4: FEATURE IMPORTANCE")
    print("="*70)

    # Show coefficients for base features
    base_coefs = coef_interactions[coef_interactions['Variable'].isin(feature_cols_with_lags)].copy()
    base_coefs_sorted = base_coefs.sort_values('Coefficient', key=abs, ascending=False)
    print("\nBase feature coefficients:")
    print(base_coefs_sorted.to_string(index=False))

    # Show coefficients for country dummies
    country_coefs = coef_interactions[coef_interactions['Variable'].isin(country_dummies)].copy()
    country_coefs_sorted = country_coefs.sort_values('Coefficient', key=abs, ascending=False)
    print("\nCountry dummy coefficients:")
    print(country_coefs_sorted.to_string(index=False))

    # Show top interaction terms
    interaction_coefs = coef_interactions[coef_interactions['Variable'].isin(interaction_cols)].copy()
    interaction_coefs_sorted = interaction_coefs.sort_values('Coefficient', key=abs, ascending=False)
    print("\nTop 20 interaction term coefficients:")
    print(interaction_coefs_sorted.head(20).to_string(index=False))

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)
