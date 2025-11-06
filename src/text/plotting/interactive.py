import os
import sys

import pandas as pd
from bokeh.layouts import Row, column, gridplot
from bokeh.models import (Title, Legend, ColumnDataSource, Select, HoverTool,
                          BoxZoomTool, ResetTool, DataTable, DateFormatter,
                          TableColumn, CustomJS)
from bokeh.models.layouts import TabPanel, Tabs
from bokeh.plotting import figure, output_file, show, output_notebook
from pathlib import Path


def plot_epu(countries, output_path):
    output_file(filename=output_path)
    countries = sorted(countries)
    
    # Load all country data and create separate sources
    sources = {}
    for country in countries:
        epu_file = OUTPUT_DIR / f"{country}/epu/{country}_epu.csv"
        epu = pd.read_csv(epu_file)
        epu["date"] = pd.to_datetime(epu["date"], format="mixed")
        epu["epu_weighted_ma3"] = epu["epu_weighted"].rolling(window=3).mean()
        sources[country] = ColumnDataSource(epu)
    
    # Create initial plot with first country
    initial_source = sources[countries[0]]
    
    hover = HoverTool(tooltips=[('Date', '@date{%Y-%m}'),
                                ('EPU Weighted', '@epu_weighted'),
                                ('EPU Weighted Moving Average (MA 3)', '@epu_weighted_ma3')],
                    formatters={'@date': 'datetime'})

    p = figure(height=400,
            width=700,
            title = 'Economic Policy Uncertainty Index',
            x_axis_type="datetime",
            tools=[hover, BoxZoomTool(), ResetTool()])

    line1 = p.line("date",
        "epu_weighted",
        source=initial_source,
        name="epu_weighted",
        color='#aacddd',
        line_width=1.5,
        line_dash='dotted',
        legend_label="EPU Weighted")

    line2 = p.line("date",
        "epu_weighted_ma3",
        source=initial_source,
        name="epu_weighted_ma3",
        color='#1d77b2',
        line_width=3,
        legend_label="EPU Weighted Moving Average (MA 3)")

    p.legend.location = "top_left"
    p.legend.click_policy = "mute"
    
    # Create dropdown selector
    select = Select(title="Country:", value=countries[0], options=[(c, " ".join(w[0].upper() + w[1:] for w in c.split("_"))) for c in countries])
    
    # CustomJS callback to update source when dropdown changes
    callback = CustomJS(args=dict(sources=sources, line1=line1, line2=line2), code="""
        const selected_country = this.value;
        const new_source = sources[selected_country];
        line1.data_source.data = new_source.data;
        line2.data_source.data = new_source.data;
    """)
    select.js_on_change('value', callback)
    
    layout = column(select, p)
    show(layout)

def plot_epu_topics(countries, topics, output_path):
    output_file(filename=output_path)
    
    # Color mapping for topics
    colors = ['#00a37c', '#d95e10']
    countries = sorted(countries)
    
    # Load all country data and create separate sources
    sources = {}
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
        sources[country] = ColumnDataSource(epu_data)
    
    # Create initial plot with first country
    initial_source = sources[countries[0]]
    
    # Build tooltip list dynamically
    tooltips = [('Date', '@date{%Y-%m}')]
    for topic in topics:
        display_name = " ".join(w.capitalize() for w in topic.split("_"))
        tooltips.append((f'{display_name} EPU', f'@epu_{topic}'))
    
    hover = HoverTool(tooltips=tooltips, formatters={'@date': 'datetime'})
    
    p = figure(height=400,
            width=700,
            title='Economic Policy Uncertainty, Topic-based',
            x_axis_type="datetime",
            tools=[hover, BoxZoomTool(), ResetTool()])
    
    # Plot each topic as a line and store references
    lines = []
    for idx, topic in enumerate(topics):
        display_name = " ".join(w.capitalize() for w in topic.split("_"))
        line = p.line("date",
            f"epu_{topic}",
            source=initial_source,
            name=f"epu_{topic}",
            color=colors[idx],
            line_width=3,
            legend_label=f"{display_name} EPU")
        lines.append(line)
    
    p.legend.location = "top_left"
    p.legend.click_policy = "mute"
    
    # Create dropdown selector
    select = Select(title="Country:", value=countries[0], options=[(c, " ".join(w[0].upper() + w[1:] for w in c.split("_"))) for c in countries])
    
    # CustomJS callback to update source when dropdown changes
    callback = CustomJS(args=dict(sources=sources, lines=lines), code="""
        const selected_country = this.value;
        const new_source = sources[selected_country];
        for (let i = 0; i < lines.length; i++) {
            lines[i].data_source.data = new_source.data;
        }
    """)
    select.js_on_change('value', callback)
    
    layout = column(select, p)
    show(layout)

def plot_sentiment(countries, output_path):
    output_file(filename=output_path)
    countries = sorted(countries)
    
    # Load all country data and create separate sources
    sources = {}
    for country in countries:
        sentiment_file = OUTPUT_DIR / f"{country}/sentiment/{country}_sentiment.csv"
        sentiment = pd.read_csv(sentiment_file)
        sentiment["date"] = pd.to_datetime(sentiment["date"], format="mixed")
        sources[country] = ColumnDataSource(sentiment)
    
    # Create initial plot with first country
    initial_source = sources[countries[0]]
    
    hover = HoverTool(tooltips=[('Date', '@date{%Y-%m}'),
                                ('Sentiment Score', '@score')],
                    formatters={'@date': 'datetime'})

    p = figure(height=400,
            width=700,
            title='Sentiment Analysis',
            x_axis_type="datetime",
            tools=[hover, BoxZoomTool(), ResetTool()])

    line = p.line("date",
        "score",
        source=initial_source,
        name="score",
        color='#2aa8f7',
        line_width=3,
        legend_label="Sentiment Score")

    p.legend.location = "top_left"
    p.legend.click_policy = "mute"
    
    # Create dropdown selector
    select = Select(title="Country:", value=countries[0], options=[(c, " ".join(w[0].upper() + w[1:] for w in c.split("_"))) for c in countries])
    
    # CustomJS callback to update source when dropdown changes
    callback = CustomJS(args=dict(sources=sources, line=line), code="""
        const selected_country = this.value;
        const new_source = sources[selected_country];
        line.data_source.data = new_source.data;
    """)
    select.js_on_change('value', callback)
    
    layout = column(select, p)
    show(layout)
    
def plot_news_count(countries, output_path):
    output_file(filename=output_path)
    countries = sorted(countries)
    
    # Load all country data and create separate sources
    sources = {}
    for country in countries:
        epu_file = OUTPUT_DIR / f"{country}/epu/{country}_epu.csv"
        epu = pd.read_csv(epu_file)
        epu["date"] = pd.to_datetime(epu["date"], format="mixed")
        sources[country] = ColumnDataSource(epu)
    
    # Create initial plot with first country
    initial_source = sources[countries[0]]
    
    hover = HoverTool(tooltips=[('Date', '@date{%Y-%m}'),
                                ('News Count', '@news_total')],
                    formatters={'@date': 'datetime'})

    p = figure(height=400,
            width=700,
            title='News Article Count',
            x_axis_type="datetime",
            x_range=(pd.Timestamp("2015-01-01"), pd.Timestamp("2025-10-31")),
            tools=[hover, BoxZoomTool(), ResetTool()])

    line = p.line("date",
        "news_total",
        source=initial_source,
        name="news_total",
        color='#2aa8f7',
        line_width=3,
        legend_label="News Count")

    p.legend.location = "top_left"
    p.legend.click_policy = "mute"
    
    # Create dropdown selector
    select = Select(title="Country:", value=countries[0], options=[(c, " ".join(w[0].upper() + w[1:] for w in c.split("_"))) for c in countries])
    
    # CustomJS callback to update source when dropdown changes
    callback = CustomJS(args=dict(sources=sources, line=line), code="""
        const selected_country = this.value;
        const new_source = sources[selected_country];
        line.data_source.data = new_source.data;
    """)
    select.js_on_change('value', callback)
    
    layout = column(select, p)
    show(layout)

if __name__ == '__main__':
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    OUTPUT_DIR = PROJECT_ROOT / "testing_outputs" / "text"


    # Filter to only include directories (countries), excluding files like .html
    countries = [d for d in os.listdir(OUTPUT_DIR) if (OUTPUT_DIR / d).is_dir()]
    plot_epu(countries, OUTPUT_DIR / "epu_pic.html")
    plot_epu_topics(countries, ["inflation", "job"], OUTPUT_DIR / "epu_topics_pic.html")
    plot_sentiment(countries, OUTPUT_DIR / "sentiment_pic.html")
    plot_news_count(countries, OUTPUT_DIR / "news_count_pic.html")