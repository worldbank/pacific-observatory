"""
Comprehensive test script for EPU and main analysis modules.
Designed for quick debugging with minimal functions and maximum inline code.
"""
import sys
from pathlib import Path
import pandas as pd
pd.set_option('display.max_columns',999)
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.text.analysis.epu import EPU
from src.text.analysis.sentiment import calculate_sentiment
from src.text.analysis.utils import generate_continous_df


if __name__ == "__main__":
    COUNTRY = "japan"
    
    # ============================================================================
    # SETUP: Define paths and configuration
    # ============================================================================
    DATA_ROOT = PROJECT_ROOT / "data" / "text"
    OUTPUT_DIR = PROJECT_ROOT / "testing_outputs" / "text"
    
    country_path = DATA_ROOT / COUNTRY
    print(f"Country path: {country_path}")
    print(f"Country path exists: {country_path.exists()}")
    
    # Find all news.csv files for the country
    news_dirs = list(country_path.glob("*/news.csv"))
    print(f"Found {len(news_dirs)} news.csv files:")
    for nd in news_dirs:
        print(f"  - {nd}")
    
    if not news_dirs:
        raise FileNotFoundError(f"No news.csv files found in {country_path}")
    
    # ============================================================================
    # CONFIGURATION: EPU and analysis parameters
    # ============================================================================
    cutoff = "2020-12-31"
    subset_condition = "date >= '2015-01-01' and date < '2025-10-01'"
    
    # Job-related terms
    additional_terms_job = [
        "job", "labor", "jobs", "career", "vacancies", "vacancy",
        "employment", "salary", "unemployment", "full-time", "part-time",
        "contractual", "freelance", "remote work", "gig", "employed",
        "resume", "cv", "cover letter", "hiring", "recruitment",
        "unemployed", "underemployed", "self-employed", "jobless", "retired",
        "layoffs", "job application", "occupation", "soft skills", "hard skills",
        "labor force", "job market", "minimum wage", "disabled worker",
        "career advancement", "workplace culture", "retirement plans",
        "maternity leave", "paternity leave",
    ]
    additional_name_job = "job"
    
    # Inflation-related terms
    additional_terms_inflation = [
        "inflation", "cpi", "price", "expense", "budget", "income",
        "demand", "cost", "supply", "goods", "food", "tobacco", "rent",
        "salary", "utilities", "fuel", "clothing", "rice", "noodle",
        "flour", "sugar", "salt", "consumer",
    ]
    additional_name_inflation = "inflation"
    
    # ============================================================================
    # TEST 1: Basic EPU initialization and data loading
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 1: EPU Initialization and Data Loading")
    print("="*80)
    
    epu_basic = EPU(
        news_dirs,
        cutoff=cutoff,
    )
    print(f"EPU object created successfully")
    print(f"  - Filepaths: {len(epu_basic.filepath)} files")
    print(f"  - Cutoff: {epu_basic.cutoff}")
    print(f"  - Additional terms: {epu_basic.additional_terms}")
    print(f"  - Additional name: {epu_basic.additional_name}")
    
    # ============================================================================
    # TEST 2: EPU category identification (basic)
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 2: EPU Category Identification (Basic)")
    print("="*80)
    
    epu_basic.get_epu_category(subset_condition=subset_condition)
    print(f"EPU categories identified for {len(epu_basic.raw_files)} sources")
    
    for source, df in epu_basic.raw_files:
        print(f"\nSource: {source}")
        print(f"  - Total rows: {len(df)}")
        print(f"  - Columns: {list(df.columns)}")
        print(f"  - Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  - EPU articles: {df['epu'].sum()}")
        print(f"  - Econ articles: {df['econ'].sum()}")
        print(f"  - Policy articles: {df['policy'].sum()}")
        print(f"  - Uncertain articles: {df['uncertain'].sum()}")
        # print(f"  - Sample EPU row:\n{df[df['epu']].head(1).to_string()}")
    
    # ============================================================================
    # TEST 3: Count statistics calculation (basic)
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 3: Count Statistics Calculation (Basic)")
    print("="*80)
    
    epu_basic.get_count_stats()
    print(f"Count statistics calculated")
    print(f"  - EPU stats shape: {epu_basic.epu_stats.shape}")
    print(f"  - Columns: {list(epu_basic.epu_stats.columns)}")
    print(f"  - Date range: {epu_basic.epu_stats['date'].min()} to {epu_basic.epu_stats['date'].max()}")
    print(f"  - News columns: {epu_basic.news_cols}")
    print(f"  - Ratio columns: {epu_basic.ratio_cols}")
    print(f"\nLast 5 rows of EPU stats:")
    print(epu_basic.epu_stats.tail())
    
    # ============================================================================
    # TEST 4: EPU score calculation (basic)
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 4: EPU Score Calculation (Basic)")
    print("="*80)
    
    epu_basic.calculate_epu_score()
    print(f"EPU scores calculated")
    print(f"  - Z-score columns: {epu_basic.z_score_cols}")
    print(f"  - Stds: {epu_basic.stds}")
    print(f"  - EPU stats columns: {list(epu_basic.epu_stats.columns)}")
    print(f"\nEPU Score Statistics:")
    print(f"  - epu_weighted: mean={epu_basic.epu_stats['epu_weighted'].mean():.2f}, "
          f"std={epu_basic.epu_stats['epu_weighted'].std():.2f}, "
          f"min={epu_basic.epu_stats['epu_weighted'].min():.2f}, "
          f"max={epu_basic.epu_stats['epu_weighted'].max():.2f}")
    print(f"  - epu_unweighted: mean={epu_basic.epu_stats['epu_unweighted'].mean():.2f}, "
          f"std={epu_basic.epu_stats['epu_unweighted'].std():.2f}, "
          f"min={epu_basic.epu_stats['epu_unweighted'].min():.2f}, "
          f"max={epu_basic.epu_stats['epu_unweighted'].max():.2f}")
    print(f"\nLast 5 rows of EPU stats:")
    #print(epu_basic.epu_stats[['date', 'epu_weighted', 'epu_unweighted']].tail())
    print(epu_basic.epu_stats.tail(20))
    
    raise
    # ============================================================================
    # TEST 5: EPU with additional terms (job)
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 5: EPU with Additional Terms (Job)")
    print("="*80)
    
    epu_job = EPU(
        news_dirs,
        cutoff=cutoff,
        additional_terms=additional_terms_job,
        additional_name=additional_name_job,
    )
    epu_job.get_epu_category(subset_condition=subset_condition)
    epu_job.get_count_stats()
    epu_job.calculate_epu_score()
    
    print(f"EPU with job terms calculated")
    print(f"  - Additional name: {epu_job.additional_name}")
    print(f"  - EPU stats columns: {list(epu_job.epu_stats.columns)}")
    
    for source, df in epu_job.raw_files:
        print(f"\nSource: {source}")
        print(f"  - Total rows: {len(df)}")
        print(f"  - Job-related articles: {df['additional'].sum()}")
        print(f"  - EPU + Job articles: {(df['epu'] & df['additional']).sum()}")
    
    print(f"\nJob EPU Score Statistics:")
    print(f"  - epu_job: mean={epu_job.epu_stats['epu_job'].mean():.2f}, "
          f"std={epu_job.epu_stats['epu_job'].std():.2f}, "
          f"min={epu_job.epu_stats['epu_job'].min():.2f}, "
          f"max={epu_job.epu_stats['epu_job'].max():.2f}")
    print(f"\nLast 5 rows of job EPU stats:")
    print(epu_job.epu_stats[['date', 'epu_job', 'epu_weighted']].tail().to_string())
    
    # ============================================================================
    # TEST 6: EPU with additional terms (inflation)
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 6: EPU with Additional Terms (Inflation)")
    print("="*80)
    
    epu_inflation = EPU(
        news_dirs,
        cutoff=cutoff,
        additional_terms=additional_terms_inflation,
        additional_name=additional_name_inflation,
    )
    epu_inflation.get_epu_category(subset_condition=subset_condition)
    epu_inflation.get_count_stats()
    epu_inflation.calculate_epu_score()
    
    print(f"EPU with inflation terms calculated")
    print(f"  - Additional name: {epu_inflation.additional_name}")
    
    for source, df in epu_inflation.raw_files:
        print(f"\nSource: {source}")
        print(f"  - Total rows: {len(df)}")
        print(f"  - Inflation-related articles: {df['additional'].sum()}")
        print(f"  - EPU + Inflation articles: {(df['epu'] & df['additional']).sum()}")
    
    print(f"\nInflation EPU Score Statistics:")
    print(f"  - epu_inflation: mean={epu_inflation.epu_stats['epu_inflation'].mean():.2f}, "
          f"std={epu_inflation.epu_stats['epu_inflation'].std():.2f}, "
          f"min={epu_inflation.epu_stats['epu_inflation'].min():.2f}, "
          f"max={epu_inflation.epu_stats['epu_inflation'].max():.2f}")
    print(f"\nLast 5 rows of inflation EPU stats:")
    print(epu_inflation.epu_stats[['date', 'epu_inflation', 'epu_weighted']].tail().to_string())
    
    # ============================================================================
    # TEST 7: Sentiment calculation
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 7: Sentiment Calculation")
    print("="*80)
    
    epu_for_sentiment = EPU(
        news_dirs,
        cutoff=cutoff,
    )
    epu_for_sentiment.get_epu_category(subset_condition=subset_condition)
    
    dfs = pd.DataFrame()
    for _, df in epu_for_sentiment.raw_files:
        df_select = df[["body", "date", "econ", "policy"]]
        dfs = pd.concat([dfs, df_select], axis=0).reset_index(drop=True)
    
    print(f"Concatenated dataframe for sentiment: {dfs.shape}")
    print(f"  - Columns: {list(dfs.columns)}")
    print(f"  - Date range: {dfs['date'].min()} to {dfs['date'].max()}")
    
    sent_df, sent_mean, sent_std = calculate_sentiment(dfs)
    print(f"\nSentiment calculated")
    print(f"  - Sentiment dataframe shape: {sent_df.shape}")
    print(f"  - Sentiment mean: {sent_mean:.4f}")
    print(f"  - Sentiment std: {sent_std:.4f}")
    print(f"  - Sentiment score range: {sent_df['score'].min():.4f} to {sent_df['score'].max():.4f}")
    
    min_date = str(sent_df.date.min().date())
    max_date = str(sent_df.date.max().date())
    sent_df = generate_continous_df(sent_df, min_date, max_date, freq="MS")
    
    print(f"\nContinuous sentiment dataframe generated")
    print(f"  - Shape after continuous generation: {sent_df.shape}")
    print(f"  - Columns: {list(sent_df.columns)}")
    
    sent_df["z_score"] = sent_df["score"].apply(
        lambda x: (x - sent_mean) / sent_std
    )
    print(f"\nZ-scores calculated")
    print(f"  - Z-score range: {sent_df['z_score'].min():.4f} to {sent_df['z_score'].max():.4f}")
    print(f"\nFirst 5 rows of sentiment data:")
    print(sent_df.head().to_string())
    
    # ============================================================================
    # TEST 8: Output file generation
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 8: Output File Generation")
    print("="*80)
    
    # Save basic EPU
    saved_folder = OUTPUT_DIR / f"{COUNTRY}/epu/"
    saved_folder.mkdir(parents=True, exist_ok=True)
    
    filename_basic = f"{COUNTRY}_epu.csv"
    epu_basic.epu_stats.to_csv(saved_folder / filename_basic, encoding="utf-8", index=False)
    print(f"Saved basic EPU: {saved_folder / filename_basic}")
    
    # Save job EPU
    filename_job = f"{COUNTRY}_epu_{additional_name_job}.csv"
    epu_job.epu_stats.to_csv(saved_folder / filename_job, encoding="utf-8", index=False)
    print(f"Saved job EPU: {saved_folder / filename_job}")
    
    # Save inflation EPU
    filename_inflation = f"{COUNTRY}_epu_{additional_name_inflation}.csv"
    epu_inflation.epu_stats.to_csv(saved_folder / filename_inflation, encoding="utf-8", index=False)
    print(f"Saved inflation EPU: {saved_folder / filename_inflation}")
    
    # Save sentiment
    saved_folder_sentiment = OUTPUT_DIR / f"{COUNTRY}/sentiment/"
    saved_folder_sentiment.mkdir(parents=True, exist_ok=True)
    filename_sentiment = f"{COUNTRY}_sentiment.csv"
    sent_df.to_csv(saved_folder_sentiment / filename_sentiment, encoding="utf-8", index=False)
    print(f"Saved sentiment: {saved_folder_sentiment / filename_sentiment}")
    
    # ============================================================================
    # TEST 9: Data validation and comparison
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 9: Data Validation and Comparison")
    print("="*80)
    
    # Compare EPU scores across different configurations
    comparison_df = epu_basic.epu_stats[['date', 'epu_weighted', 'epu_unweighted']].copy()
    comparison_df.columns = ['date', 'epu_basic_weighted', 'epu_basic_unweighted']
    
    comparison_df = comparison_df.merge(
        epu_job.epu_stats[['date', 'epu_job']],
        on='date',
        how='left'
    )
    
    comparison_df = comparison_df.merge(
        epu_inflation.epu_stats[['date', 'epu_inflation']],
        on='date',
        how='left'
    )
    
    print(f"Comparison dataframe shape: {comparison_df.shape}")
    print(f"\nCorrelation between EPU scores:")
    print(comparison_df[['epu_basic_weighted', 'epu_job', 'epu_inflation']].corr().to_string())
    
    print(f"\nComparison statistics:")
    print(comparison_df[['epu_basic_weighted', 'epu_job', 'epu_inflation']].describe().to_string())
    
    print(f"\nLast 5 rows of comparison:")
    print(comparison_df.tail().to_string())
    
    # ============================================================================
    # TEST 10: Summary and debugging checkpoint
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 10: Summary and Debugging Checkpoint")
    print("="*80)
    
    print(f"\nAll tests completed successfully for country: {COUNTRY}")
    print(f"\nKey statistics:")
    print(f"  - Basic EPU articles: {epu_basic.epu_stats['epu_weighted'].notna().sum()}")
    print(f"  - Job EPU articles: {epu_job.epu_stats['epu_job'].notna().sum()}")
    print(f"  - Inflation EPU articles: {epu_inflation.epu_stats['epu_inflation'].notna().sum()}")
    print(f"  - Sentiment records: {len(sent_df)}")
    
    print(f"\nOutput files generated:")
    print(f"  - {saved_folder / filename_basic}")
    print(f"  - {saved_folder / filename_job}")
    print(f"  - {saved_folder / filename_inflation}")
    print(f"  - {saved_folder_sentiment / filename_sentiment}")
    
    print("\n" + "="*80)
    print("DEBUGGING CHECKPOINT: Insert 'raise' below to stop and inspect variables")
    print("="*80)
    # raise  # Uncomment to stop here and inspect variables
