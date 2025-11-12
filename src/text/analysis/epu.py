"""
Economic Policy Uncertainty (EPU) Index Calculation Module

METHODOLOGY OVERVIEW
====================

This module implements the EPU index calculation methodology as follows:

1. RATIO CALCULATION (X_it):
   - For each newspaper i at time t, calculate the proportion of EPU news:
     X_it = (EPU news count in newspaper i at time t) / (All scraped news in newspaper i at time t)
   - Implemented in: calculate_ratios() method
   - Zero-division handling: Ratios with zero denominator result in NaN, which are handled downstream

2. STANDARDIZATION (Y_it):
   - Define T_1 as the standardization period (specified by 'cutoff' parameter)
   - Calculate standard deviation σ_i for each newspaper i over period T_1
   - Standardize X_it by dividing by σ_i: Y_it = X_it / σ_i
   - Implemented in: _calculate_z_score() method
   - Zero-division handling: If σ_i = 0 (no variation in data), Y_it is set to NaN instead of inf

3. MEAN AGGREGATION (Z_t):
   - Compute the mean of Y_it across all newspapers for each month:
     Z_t = mean(Y_it) at time t
   - Implemented in: _calculate_z_score() method (z_score_unweighted)
   - Zero-division handling: Uses skipna=True to ignore NaN values when computing mean

4. NORMALIZATION (EPU Index):
   - Calculate M = mean(Z_t) over the standardization period T_1
   - Normalize by multiplying Z_t by (100 / M) for all time periods
   - This ensures the EPU index has a mean of 100 over T_1
   - Implemented in: calculate_epu_score() method
   - Zero-division handling: If M = 0, scaling_factor becomes inf; protected by checking M != 0

WEIGHTED VARIANT:
   - Instead of simple mean, uses newspaper-specific weights (proportion of total news)
   - Z_t_weighted = sum(weight_i * Y_it) for each newspaper i
   - Implemented in: _calculate_z_score() method (z_score_weighted)

KEY FEATURES:
   - Handles multiple newspapers/sources simultaneously
   - Supports additional term categories for specialized EPU indices (e.g., inflation-specific)
   - Provides both weighted and unweighted EPU indices
   - Robust NaN handling throughout the pipeline

Last modified:
    2025-11-12

"""

import os
import re
from typing import List, Union
import pandas as pd
import numpy as np
from .utils import is_in_word_list, generate_continous_df, load_topics_words

# Load topic words from configuration file
_topics_data = load_topics_words()
ECON_LIST = _topics_data["economic"]
POLICY_LIST = _topics_data["policy"]
UNCERTAINTY_LIST = _topics_data["uncertainty"]


class EPU:
    """
    A class for analyzing Economic, Policy, and Uncertainty (EPU) news data.

    Attributes:
        filepath (Union[str, List[str]]): Path(s) to the news data file(s).
        cutoff (str): A cutoff date for calculating standard deviations.
        non_epu_urls (list): List of urls to be removed from identified epu news.
        econ_terms (list): List of terms related to the economy.
        policy_terms (list): List of terms related to policy.
        uncertainty_terms (list): List of terms related to uncertainty.
        additional_terms (Union[List, None]): Additional terms for further categorization.
        additional_name (Union[str, None]): Name for the additional category (e.g., 'inflation', 'jobs').
        raw_files (list): List to store raw data from files.
        stds (list): List to store standard deviations for EPU scores.
        news_cols (list): List to store news count columns.
        ratio_cols (list): List to store ratio columns.
        z_score_cols (list): List to store z-score columns.

    Example:
        e = EPU(filepaths, cutoff='2020-12-31')
        e.get_epu_category(subset_condition="date >= '2015-01-01' and date < '2024-01-01'")
        e.get_count_stats()
        e.calculate_epu_score()
    """

    def __init__(
        self,
        filepath: Union[str, List[str]],
        cutoff: str,
        non_epu_urls: list = None,
        econ_terms: list = ECON_LIST,
        policy_terms: list = POLICY_LIST,
        uncertainty_terms: list = UNCERTAINTY_LIST,
        additional_terms: Union[List, None] = None,
        additional_name: Union[str, None] = None,
    ):

        if isinstance(filepath, str):
            self.filepath = [filepath]
        elif isinstance(filepath, list):
            for fp in filepath:
                if not os.path.exists(fp):
                    raise FileNotFoundError(f"Cannot find {filepath}")

        self.filepath = filepath
        self.econ_terms = econ_terms
        self.policy_terms = policy_terms
        self.uncertainty_terms = uncertainty_terms
        self.additional_terms = additional_terms
        self.additional_name = additional_name
        self.raw_files = []
        self.cutoff = cutoff
        self.non_epu_urls = non_epu_urls if non_epu_urls is not None else []
        self.min_date = None
        self.max_date = None
        self.epu_stats = pd.DataFrame()
        self.stds = []
        self.news_cols = []
        self.ratio_cols = []
        self.z_score_cols = []

    @staticmethod
    def process_data(
        filepath: str, subset_condition: Union[str, None] = None
    ) -> pd.DataFrame:
        """
        Reads a CSV file and processes the data.

        Args:
            filename (str): The name of the CSV file.
            subset_condition (str): The conditions to pass on to df.query(), such as
                        "date >= 'YYYY-MM-DD'"

        Returns:
            pd.DataFrame: Processed DataFrame with the "Unnamed: 0" column dropped,
                        newline characters removed from the "news" column,
                        "date" column converted to datetime, and a new "ym" column added.
        """
        df = pd.read_csv(filepath, encoding="utf-8")
        df = df.drop_duplicates()
        df = df[~df.date.isna()].reset_index(drop=True)
        if subset_condition is not None:
            df = df.query(subset_condition).reset_index(drop=True)

        df["body"] = df["body"].replace("\n", "").str.lower()
        df["date"] = pd.to_datetime(df["date"], format="mixed")
        df["ym"] = [str(d.year) + "-" + str(d.month) for d in df.date]
        return df

    @staticmethod
    def get_count(data: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Computes the count of occurrences for a specific column in a DataFrame
        grouped by the year-month ('ym').

        Args:
            data (pd.DataFrame): The input DataFrame.
            column (str): The column for which the count is computed.

        Returns:
            pd.DataFrame: DataFrame with the count of occurrences for the specified column

        """
        try:
            count_df = (
                data.set_index("date")
                .groupby("ym")[[str(column)]]
                .count()
                .reset_index()
                .rename({str(column): str(column) + "_count"}, axis=1)
            )
            return count_df
        except KeyError as exc:
            print(f"Column '{column}': {exc}")

    def get_epu_category(self, subset_condition=None):
        """
        Reads the csv file that contains news and identifies the Economic/Policy/Uncertainty
        categories.

        Args:
            subset_condition (str): conditionals to pass to EPU().process_data()
        """
        for fp in self.filepath:
            country = fp.parent.parent.name
            newspaper = fp.parent.name.replace(country, "").strip("_")
            source = f"{country}_{newspaper}"
            raw = self.process_data(fp, subset_condition=subset_condition)
            for col, terms in zip(
                ["econ", "policy", "uncertain"],
                [self.econ_terms, self.policy_terms, self.uncertainty_terms],
            ):
                if terms is not None:
                    raw[col] = (
                        raw["body"]
                        .str.lower()
                        .apply(is_in_word_list, terms=terms)
                    )
                else:
                    raw[col] = True

            raw["epu"] = (raw.econ) & (raw.policy) & (raw.uncertain)

            # Check for additional terms categoty
            if self.additional_terms:
                raw["additional"] = (
                    raw["body"]
                    .str.lower()
                    .apply(is_in_word_list, terms=self.additional_terms)
                )
                raw["epu"] = (raw.epu) & (raw.additional)

            if (
                "url" in raw.columns
                and raw["url"].isin(self.non_epu_urls).sum() > 0
            ):
                raw.loc[raw.url.isin(self.non_epu_urls), "epu"] = False

            self.raw_files.append((source, raw.copy()))

    def calculate_news_and_epu_counts(
        self, file: pd.DataFrame
    ) -> pd.DataFrame:
        """
        The function

        """
        news_count = self.get_count(file, "body")
        epu_count = self.get_count(file[file["epu"]], "epu")
        return news_count.merge(epu_count, how="left", on="ym").fillna(0)

    def calculate_ratios(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        The function calculates the ratio of EPU news in relative to all news.
        """
        merged_df["ratio"] = merged_df["epu_count"] / merged_df["body_count"]
        return merged_df

    def merge_data_frames(
        self, epu_stats: pd.DataFrame, new_df: pd.DataFrame, source: str
    ) -> pd.DataFrame:
        """
        The function merged epu count dfs.
        """
        new_df.columns = [
            f"{source}_{col}" if col != "ym" else col for col in new_df.columns
        ]
        return (
            pd.merge(epu_stats, new_df, how="outer", on="ym")
            if not epu_stats.empty
            else new_df
        )

    def _calculate_total_news(self):

        self.news_cols = [
            col
            for col in self.epu_stats.columns
            if col.endswith("_body_count")
        ]
        self.epu_stats["news_total"] = self.epu_stats[self.news_cols].sum(
            axis=1
        )

    def get_count_stats(self):
        """
        Aggregates news and EPU counts, calculates ratios, and prepares data for
        EPU score calculation.
        """
        for source, file in self.raw_files:
            counts_df = self.calculate_news_and_epu_counts(file)
            ratios_df = self.calculate_ratios(counts_df)
            self.epu_stats = self.merge_data_frames(
                self.epu_stats, ratios_df, source
            )  # .fillna(0)

        # Check for date integrity
        self.epu_stats["date"] = pd.to_datetime(
            self.epu_stats["ym"], format="mixed"
        )
        self.min_date, self.max_date = (
            self.epu_stats.date.min(),
            self.epu_stats.date.max(),
        )
        self.epu_stats = generate_continous_df(
            self.epu_stats, self.min_date, self.max_date
        )

        self._calculate_total_news()
        self.ratio_cols = [
            col for col in self.epu_stats.columns if col.endswith("_ratio")
        ]
        for col in self.news_cols:
            new_col = col.replace("_body_count", "_weights")
            self.epu_stats[new_col] = self.epu_stats[col].div(
                self.epu_stats["news_total"]
            )

    def _calculate_z_score(self):
        """
        Calculates the z-scores for the EPU ratios to standardize them for
          comparison and analysis.
        """
        self.stds = []
        for ratio_col in self.ratio_cols:
            col = ratio_col.replace("_ratio", "")
            if self.cutoff is not None:
                std = self.epu_stats[self.epu_stats.date < self.cutoff][
                    ratio_col
                ].std()
            else:
                std = self.epu_stats[ratio_col].std()
            self.stds.append({col: std})
            # self.epu_stats[f"{col}_z_score"] = self.epu_stats[ratio_col].div(
            #     std).fillna(0).replace([np.inf, -np.inf], 0)
            if std == 0 or pd.isna(std):
                self.epu_stats[f"{col}_z_score"] = np.nan
            else:
                self.epu_stats[f"{col}_z_score"] = (
                    self.epu_stats[ratio_col] / std
                )

        self.z_score_cols = [
            col for col in self.epu_stats.columns if col.endswith("z_score")
        ]
        self.epu_stats["z_score_unweighted"] = self.epu_stats[
            self.z_score_cols
        ].mean(axis=1, skipna=True)
        self.epu_stats["z_score_weighted"] = 0
        for z_score_col in self.z_score_cols:
            weight_col = z_score_col.replace("z_score", "weights")
            self.epu_stats["z_score_weighted"] += (
                self.epu_stats[weight_col].multiply(
                    self.epu_stats[z_score_col]
                )
                if not pd.isna(self.epu_stats[z_score_col]).all()
                else 0
            )

    def calculate_epu_score(self):
        """
        Calculates the Economic Policy Uncertainty (EPU) scores based on z-scores and
            updates the DataFrame with these scores.
        """
        self._calculate_z_score()
        for name, col in zip(
            ["weighted", "unweighted"],
            ["z_score_weighted", "z_score_unweighted"],
        ):
            scaling_factor = 100 / (
                self.epu_stats[self.epu_stats.date < self.cutoff][col].mean()
            )
            self.epu_stats[f"epu_{name}"] = (
                scaling_factor * self.epu_stats[col]
            )

        # Add additional_name column if provided
        if self.additional_name:
            self.epu_stats[f"epu_{self.additional_name}"] = self.epu_stats[
                "epu_weighted"
            ]
