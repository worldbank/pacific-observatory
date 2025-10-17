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

DATA_ROOT = PROJECT_ROOT / "data" / "text"
EXCLUDED_COUNTRIES = {"marshall_islands", "tonga"}

country_dirs = [
    entry
    for entry in DATA_ROOT.iterdir()
    if entry.is_dir() and entry.name not in EXCLUDED_COUNTRIES
]

OUTPUT_DIR = PROJECT_ROOT / "testing_outputs" / "text"

def plot_epu(epu_stats, country_name, saved_folder):
    fig, ax = plt.subplots(figsize=(8, 6))
    epu_stats.plot(x="date", y="epu_weighted", color="blue", ax=ax)
    epu_stats.plot(x='date', y="epu_unweighted", color="lightgray", alpha=0.5, ax=ax)
    
    title = " ".join(n[0].upper() + n[1:] for n in country_name.split("_"))
    ax.set_title(f"{title}'s EPU Score")
    ax.set_xlabel("Date")
    
    fig.savefig(saved_folder / f"{country_name}_epu.png")

def get_epu(country, cutoff, subset_condition, plot=True, additional_terms=None):
    country_name = country.name
    news_dirs = list(country.glob("*/news.jsonl"))
    e = EPU(news_dirs, cutoff=cutoff, additional_terms=additional_terms)
    e.get_epu_category(subset_condition=subset_condition)
    e.get_count_stats()
    e.calculate_epu_score()
    
    epu_stats = e.epu_stats
    saved_folder = OUTPUT_DIR / f"{country_name}/epu/"
    saved_folder.mkdir(parents=True, exist_ok=True)
    epu_stats.to_csv(saved_folder / f"{country_name}_epu.csv", encoding="utf-8")
    
    if plot:
        plot_epu(epu_stats, country_name, saved_folder)
    
    return epu_stats

if __name__ == "__main__":
    cutoff = "2020-12-31"
    subset_condition = "date >= '2015-01-01'"
    additional_terms = None
    for country in country_dirs:
        get_epu(country, cutoff, subset_condition, plot=True, additional_terms=additional_terms)