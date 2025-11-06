import os
import sys

import pandas as pd
from bokeh.layouts import Row, column, gridplot
from bokeh.models import (Title, Legend, ColumnDataSource, Select, HoverTool,
                          BoxZoomTool, ResetTool, DataTable, DateFormatter,
                          TableColumn)
from bokeh.models.layouts import TabPanel, Tabs
from bokeh.plotting import figure, output_file, show, output_notebook
from pathlib import Path


def plot_epu(countries, output_path):
    output_file(filename=output_path)
    tabs = []
    countries = sorted(countries)
    for country in countries:
        epu_file = OUTPUT_DIR / f"{country}/epu/{country}_epu.csv"
        epu = pd.read_csv(epu_file)
        epu["date"] = pd.to_datetime(epu["date"], format="mixed")
        epu["epu_weighted_ma3"] = epu["epu_weighted"].rolling(window=3).mean()

        source = ColumnDataSource(epu)

        hover = HoverTool(tooltips=[('Date', '@date{%Y-%m}'),
                                    ('EPU Weighted', '@epu_weighted'),
                                    # ('EPU unweighted', '@epu_unweighted'),
                                    ('EPU Weighted Moving Average (MA 3)', '@epu_weighted_ma3')],
                        formatters={'@date': 'datetime'})

        p = figure(height=400,
                width=700,
                x_axis_type="datetime",
                tools=[hover, BoxZoomTool(), ResetTool()])

        p.line("date",
            "epu_weighted",
            source=source,
            name="epu_weighted",
            color='blue',
            line_width=1.5,
            line_dash='dotted',
            legend_label="EPU Weighted")

        p.line("date",
            "epu_weighted_ma3",
            source=source,
            name="epu_weighted_ma3",
            color='blue',
            line_width=2,
            legend_label="EPU Weighted Moving Average (MA 3)")

        p.legend.location = "top_left"
        p.legend.click_policy = "mute"

        # Uppercase the first letter of the country name
        title = " ".join(w[0].upper() + w[1:] for w in country.split("_"))
        tab = TabPanel(child=p, title=title)
        tabs.append(tab)

    show(Tabs(tabs=tabs))

def plot_epu_topics(countries, topics, output_path):
    output_file(filename=output_path)
    tabs = []
    
    # Color mapping for topics
    colors = ['green', 'orange']
    countries = sorted(countries)
    
    for country in countries:
        epu_data = None
        
        # Load data for each topic
        for topic in topics:
            epu_file = OUTPUT_DIR / f"{country}/epu/{country}_epu_{topic}.csv"
            epu = pd.read_csv(epu_file)
            epu["date"] = pd.to_datetime(epu["date"], format="mixed")
            epu[f"epu_{topic}"] = epu[f"epu_{topic}"].rolling(window=3).mean()
            
            if epu_data is None:
                epu_data = epu[["date", f"epu_{topic}"]].copy()
            else:
                epu_data = epu_data.merge(epu[["date", f"epu_{topic}"]], on="date", how="outer")
        
        epu_data = epu_data.sort_values("date").reset_index(drop=True)
        source = ColumnDataSource(epu_data)
        
        # Build tooltip list dynamically
        tooltips = [('Date', '@date{%Y-%m}')]
        for topic in topics:
            display_name = " ".join(w.capitalize() for w in topic.split("_"))
            tooltips.append((f'{display_name} EPU', f'@epu_{topic}'))
        
        hover = HoverTool(tooltips=tooltips, formatters={'@date': 'datetime'})
        
        p = figure(height=400,
                width=700,
                x_axis_type="datetime",
                tools=[hover, BoxZoomTool(), ResetTool()])
        
        # Plot each topic as a line
        for idx, topic in enumerate(topics):
            display_name = " ".join(w.capitalize() for w in topic.split("_"))
            p.line("date",
                f"epu_{topic}",
                source=source,
                name=f"epu_{topic}",
                color=colors[idx],
                line_width=2,
                legend_label=f"{display_name} EPU")
        
        p.legend.location = "top_left"
        p.legend.click_policy = "mute"
        
        # Uppercase the first letter of the country name
        title = " ".join(w[0].upper() + w[1:] for w in country.split("_"))
        tab = TabPanel(child=p, title=title)
        tabs.append(tab)
    
    show(Tabs(tabs=tabs))

if __name__ == '__main__':
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    OUTPUT_DIR = PROJECT_ROOT / "testing_outputs" / "text"


    countries = os.listdir(PROJECT_ROOT / "testing_outputs" / "text")
    plot_epu(countries, OUTPUT_DIR / "epu_pic.html")
    plot_epu_topics(countries, ["inflation", "job"], OUTPUT_DIR / "epu_topics_pic.html")