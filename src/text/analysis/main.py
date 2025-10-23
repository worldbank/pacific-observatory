import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.text.analysis.epu import EPU
from src.text.analysis.sentiment import calculate_sentiment
from src.text.analysis.utils import generate_continous_df

DATA_ROOT = PROJECT_ROOT / "data" / "text"
# EXCLUDED_COUNTRIES = {"marshall_islands", "tonga"}
EXCLUDED_COUNTRIES = {}

country_dirs = [
    entry
    for entry in DATA_ROOT.iterdir()
    if entry.is_dir() and entry.name not in EXCLUDED_COUNTRIES
]

OUTPUT_DIR = PROJECT_ROOT / "testing_outputs" / "text"


def plot_epu(epu_stats, country_name, saved_folder):
    fig, ax = plt.subplots(figsize=(8, 6))
    epu_stats.plot(x="date", y="epu_weighted", color="blue", ax=ax)
    epu_stats.plot(
        x="date", y="epu_unweighted", color="lightgray", alpha=0.5, ax=ax
    )

    title = " ".join(n[0].upper() + n[1:] for n in country_name.split("_"))
    ax.set_title(f"{title}'s EPU Score")
    ax.set_xlabel("Date")

    fig.savefig(saved_folder / f"{country_name}_epu.png")


def get_epu(
    country, cutoff, subset_condition, plot=True, additional_terms=None
):
    country_name = country.name
    news_dirs = list(country.glob("*/news.jsonl"))
    e = EPU(news_dirs, cutoff=cutoff, additional_terms=additional_terms)
    e.get_epu_category(subset_condition=subset_condition)
    e.get_count_stats()
    e.calculate_epu_score()

    epu_stats = e.epu_stats
    saved_folder = OUTPUT_DIR / f"{country_name}/epu/"
    saved_folder.mkdir(parents=True, exist_ok=True)
    epu_stats.to_csv(
        saved_folder / f"{country_name}_epu.csv", encoding="utf-8"
    )

    if plot:
        plot_epu(epu_stats, country_name, saved_folder)

    return epu_stats


def plot_sentiment(sent_df, country_name, saved_folder):
    fig, ax = plt.subplots(figsize=(8, 6))
    sent_df.plot(x="date", y="score", color="blue", ax=ax)

    title = " ".join(n[0].upper() + n[1:] for n in country_name.split("_"))
    ax.set_title(f"{title}'s Sentiment Score")
    ax.set_xlabel("Date")

    fig.savefig(saved_folder / f"{country_name}_sentiment.png")


def get_sentiment(
    country, cutoff, subset_condition, plot=True, additional_terms=None
):
    country_name = country.name
    news_dirs = list(country.glob("*/news.jsonl"))
    e = EPU(news_dirs, cutoff=cutoff, additional_terms=additional_terms)
    e.get_epu_category(subset_condition=subset_condition)

    dfs = pd.DataFrame()
    for _, df in e.raw_files:
        df_select = df[["body", "date", "econ", "policy"]]
        dfs = pd.concat([dfs, df_select], axis=0).reset_index(drop=True)

    sent_df, sent_mean, sent_std = calculate_sentiment(dfs)

    min_date = str(sent_df.date.min().date())
    max_date = str(sent_df.date.max().date())

    sent_df = generate_continous_df(sent_df, min_date, max_date, freq="MS")
    sent_df["z_score"] = sent_df["score"].apply(
        lambda x: (x - sent_mean) / sent_std
    )

    saved_folder = OUTPUT_DIR / f"{country_name}/sentiment/"
    saved_folder.mkdir(parents=True, exist_ok=True)
    sent_df.to_csv(
        saved_folder / f"{country_name}_sentiment.csv", encoding="utf-8"
    )

    if plot:
        plot_sentiment(sent_df, country_name, saved_folder)


if __name__ == "__main__":
    cutoff = "2020-12-31"
    subset_condition = "date >= '2015-01-01' and date < '2024-01-01'"
    additional_terms = None
    for country in country_dirs:
        get_epu(
            country,
            cutoff,
            subset_condition,
            plot=True,
            additional_terms=additional_terms,
        )
        get_sentiment(
            country,
            cutoff,
            subset_condition,
            plot=True,
            additional_terms=additional_terms,
        )

