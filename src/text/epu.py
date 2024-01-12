import os
import pandas as pd
import numpy as np
from .utils import (
    is_in_word_list, generate_continous_df
)
from typing import List, Union

ECON_LIST = [
    "economy", "economic", "economics", "business", "commerce", "finance",
    "industry"
]

POLICY_LIST = [
    "government", "governmental", "authorities", "minister", "ministry",
    "parliament", "parliamentary", "tax", "regulation", "legislation",
    "central bank", "imf", "world bank", "international monetary fund",
    "debt"
]

UNCERTAINTY_LIST = [
    "uncertain", "uncertainty", "uncertainties", "unknown", "unstable",
    "unsure", "undetermined", "risky", "risk", "not certain", "non-reliable",
    "fluctuations", "unpredictale"
]


class EPU:
    def __init__(self,
                 filepath: Union[str, List[str]],
                 cutoff: str,
                 econ_terms: list = ECON_LIST,
                 policy_terms: list = POLICY_LIST,
                 uncertainty_terms: list = UNCERTAINTY_LIST,
                 additional_terms: Union[List, None] = None):
        if isinstance(filepath, str):
            self.filepath = [filepath]

        # # TODO: check filepath's existence
        # elif not os.path.exists(filepath):
        #     raise FileNotFoundError(f"Cannot find {filepath}")
        self.filepath = filepath
        self.econ_terms = econ_terms
        self.policy_terms = policy_terms
        self.uncertainty_terms = uncertainty_terms
        self.additional_terms = additional_terms
        self.raw_files = []
        self.cutoff = cutoff
        self.stds = []

    @staticmethod
    def process_data(filepath: str, subset_condition: Union[str, None] = None) -> pd.DataFrame:
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
        df = pd.read_csv(filepath).drop("Unnamed: 0", axis=1)
        df = df[~df.date.isna()].reset_index(drop=True)
        if subset_condition is not None:
            df = df.query(subset_condition).reset_index(drop=True)

        df["news"] = df["news"].replace("\n", "")
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
            count_df = (data.set_index("date")
                            .groupby("ym")[[str(column)]]
                            .count()
                            .reset_index()
                            .rename({str(column): str(column) + "_count"}, axis=1))
            return count_df
        except KeyError:
            raise KeyError(f"Column '{column}' not found in the DataFrame.")

    def get_epu_category(self, subset_condition=None):
        """        
        Reads the csv file that contains news and identifies the Economic/Policy/Uncertainty
        categories. 

        Args: 
            subset_condition (str): conditionals to pass to EPU().process_data()
        """
        for fp in self.filepath:
            source = fp.split("/")[-1].replace("_news.csv", "")
            self.raw = self.process_data(fp, subset_condition=subset_condition)
            for col, terms in zip(["econ", "policy", "uncertain"], [self.econ_terms, self.policy_terms, self.uncertainty_terms]):
                self.raw[col] = self.raw["news"].str.lower().apply(
                    is_in_word_list, terms=terms)

            self.raw["epu"] = (self.raw.econ == True) & (
                self.raw.policy == True) & (self.raw.uncertain == True)

            # Check for additional terms categoty
            if self.additional_terms:
                self.raw["additional"] = self.raw["news"].str.lower().apply(
                    is_in_word_list, terms=self.additional_terms)
                self.raw["epu"] = (self.raw.epu == True) & (
                    self.raw.additional == True)
            self.raw_files.append((source, self.raw.copy()))

    def calculate_news_and_epu_counts(self, file: pd.DataFrame) -> pd.DataFrame:
        news_count = self.get_count(file, "news")
        epu_count = self.get_count(file[file["epu"]], "epu")
        return news_count.merge(epu_count, how="left", on="ym").fillna(0)

    def calculate_ratios(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        merged_df["ratio"] = merged_df["epu_count"] / merged_df["news_count"]
        return merged_df

    def merge_data_frames(self, epu_stats: pd.DataFrame,
                          new_df: pd.DataFrame,
                          source: str) -> pd.DataFrame:
        new_df.columns = [f"{source}_{col}" if col !=
                          "ym" else col for col in new_df.columns]
        return pd.merge(epu_stats, new_df, how="outer", on="ym") if not epu_stats.empty else new_df

    def _calculate_total_news(self):

        self.news_cols = [
            col for col in self.epu_stats.columns if col.endswith("_news_count")]
        self.epu_stats["news_total"] = self.epu_stats[self.news_cols].sum(
            axis=1)

    def get_count_stats(self) -> pd.DataFrame:
        self.epu_stats = pd.DataFrame()
        for (source, file) in self.raw_files:
            # news_count = self.get_count(file, "news")
            # epu_count = self.get_count(file[file["epu"] == True], "epu")
            # self.epu_stat = news_count.merge(
            #     epu_count, how="left", on="ym").fillna(0)
            # self.epu_stat["ratio"] = self.epu_stat["epu_count"] / \
            #     self.epu_stat["news_count"]
            # self.epu_stat.columns = [f"{source}_{col}" if col != "ym" else col
            #  for col in self.epu_stat.columns]
            # if self.epu_stats.empty:
            #     self.epu_stats = self.epu_stat
            # else:
            #     self.epu_stats = self.epu_stats.merge(
            #         self.epu_stat, how="outer", on="ym")
            counts_df = self.calculate_news_and_epu_counts(file)
            ratios_df = self.calculate_ratios(counts_df)
            self.epu_stats = self.merge_data_frames(
                self.epu_stats, ratios_df, source)

        # Check for date integrity
        self.epu_stats["date"] = pd.to_datetime(
            self.epu_stats["ym"], format="mixed")
        self.min_date, self.max_date = self.epu_stats.date.min(), self.epu_stats.date.max()
        self.epu_stats = generate_continous_df(
            self.epu_stats, self.min_date, self.max_date)

        self._calculate_total_news()
        self.ratio_cols = [
            col for col in self.epu_stats.columns if col.endswith("_ratio")]
        for col in self.news_cols:
            new_col = col.replace("_news_count", "_weights")
            self.epu_stats[new_col] = self.epu_stats[col].div(
                self.epu_stats["news_total"])

    def _calculate_z_score(self):
        self.stds = []
        for ratio_col in self.ratio_cols:
            col = ratio_col.replace("_ratio", "")
            if self.cutoff != None:
                std = self.epu_stats[self.epu_stats.date <
                                     self.cutoff][ratio_col].std()
            else:
                std = self.epu_stat[ratio_col].std()
            self.stds.append({col: std})
            self.epu_stats[f"{col}_z_score"] = self.epu_stats[ratio_col].div(std)

        self.z_score_cols = [col for col in self.epu_stats.columns if col.endswith("z_score")]
        self.epu_stats["z_score_unweighted"] = self.epu_stats[self.z_score_cols].mean(axis=1)
        self.epu_stats["z_score_weighted"] = 0
        for z_score_col in self.z_score_cols:
            weight_col = z_score_col.replace("z_score", "weights")
            self.epu_stats["z_score_weighted"] += self.epu_stats[weight_col].multiply(self.epu_stats[z_score_col])
    
    
    def calculate_epu_score(self):
        self._calculate_z_score()
        for name, col in zip(["weighted", "unweighted"], ["z_score_weighted", "z_score_unweighted"]):
            scaling_factor = 100/(self.epu_stats[self.epu_stats.date < self.cutoff][col].std())
            self.epu_stats[f"epu_{name}"] = scaling_factor * self.epu_stats[col]