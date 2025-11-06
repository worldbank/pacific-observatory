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

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "testing_outputs" / "text"
output_file(filename=OUTPUT_DIR / "epu_pic.html")


countries = os.listdir(PROJECT_ROOT / "testing_outputs" / "text")

tabs = []

for country in countries:
    epu_file = OUTPUT_DIR / f"{country}/epu/{country}_epu_job.csv"
    epu = pd.read_csv(epu_file)
    epu["date"] = pd.to_datetime(epu["date"], format="mixed")
    epu["epu_weighted_ma3"] = epu["epu_weighted"].rolling(window=3).mean()

    source = ColumnDataSource(epu)

    hover = HoverTool(tooltips=[('Date', '@date{%Y-%m}'),
                                ('EPU weighted', '@epu_weighted'),
                                ('EPU unweighted', '@epu_unweighted'),
                                ('EPU (MA 3)', '@epu_weighted_ma3')],
                      formatters={'@date': 'datetime'})

    p = figure(height=400,
               width=700,
               x_axis_type="datetime",
               tools=[hover, BoxZoomTool(), ResetTool()])

    p.line("date",
           "epu_weighted",
           source=source,
           name="epu_weighted",
           line_width=2,
           legend_label="EPU (weighted)")

    p.line("date",
           "epu_weighted_ma3",
           source=source,
           name="epu_unweighted",
           color='darkorange',
           line_width=1.5,
           legend_label="EPU (MA 3)")

    p.line("date",
           "epu_unweighted",
           source=source,
           name="epu_unweighted",
           line_dash='dotted',
           color='green',
           legend_label="EPU (unweighted)")

    p.legend.location = "top_left"
    p.legend.click_policy = "mute"

    # Add a vertical
    p.vspan(x=pd.to_datetime("2021-01-01"),
            line_dash="dashed",
            line_color="green",
            name="cutoff")

    # epu_dt = (epu.set_index("date").groupby(
    #     [pd.Grouper(freq="Y")])[["epu_weighted",
    #                              "epu_unweighted"]].mean().reset_index())

    # dt_source = ColumnDataSource(epu_dt)

    columns = [
        TableColumn(field="date", title="Date", formatter=DateFormatter()),
        TableColumn(field="epu_weighted", title="EPU Weighted (Avg.)"),
        TableColumn(field="epu_unweighted", title="EPU Unweighted (Avg.)"),
    ]
    dt = DataTable(source=dt_source, columns=columns, width=700, height=300)
    # combined = column(p, dt)

    # Uppercase the first letter of the country name
    title = " ".join(w[0].upper() + w[1:] for w in country.split("_"))
    tab = TabPanel(child=p, title=title)
    tabs.append(tab)

show(Tabs(tabs=tabs))