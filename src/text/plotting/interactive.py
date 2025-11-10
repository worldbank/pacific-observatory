"""Generate standalone HTML plots with dropdown menus"""
import os
import sys
import json
import pandas as pd
from pathlib import Path

# Countries to exclude from EPU and sentiment visualizations
EXCLUDE_COUNTRIES = [
    'american_samoa', 'guam', 'malaysia', 'marshall_islands', 'pacific', 'palau',
    'south_korea', 'singapore', 'thailand', 'timor_leste', 'tuvalu', 'vanuatu'
]

# Countries to exclude from prediction visualizations
EXCLUDE_PREDS = [
    'american_samoa', 'guam', 'malaysia', 'marshall_islands', 'mongolia',
    'singapore', 'south_korea', 'thailand', 'timor_leste', 'tuvalu'
]


def fmt_country(c):
    """Format country name from snake_case to Title Case (e.g., 'solomon_islands' -> 'Solomon Islands')"""
    return " ".join(w[0].upper() + w[1:] for w in c.split("_"))

def load_epu(country, data_dir):
    """Load EPU data and compute 3-month moving average"""
    f = data_dir / f"{country}/epu/{country}_epu.csv"
    if not f.exists():
        return None
    df = pd.read_csv(f)
    df["date"] = pd.to_datetime(df["date"], format="mixed")
    df["epu_weighted_ma3"] = df["epu_weighted"].rolling(window=3).mean()
    return df.sort_values("date")


def load_epu_topics(country, topics, data_dir):
    """Load topic-specific EPU data and compute 3-month moving average for each topic"""
    df = None
    for t in topics:
        f = data_dir / f"{country}/epu/{country}_epu_{t}.csv"
        if not f.exists():
            continue
        d = pd.read_csv(f)
        d["date"] = pd.to_datetime(d["date"], format="mixed")
        d[f"epu_{t}"] = d[f"epu_{t}"].rolling(window=3).mean()
        if df is None:
            df = d[["date", f"epu_{t}"]].copy()
        else:
            df = df.merge(d[["date", f"epu_{t}"]], on="date", how="outer")
    return df.sort_values("date") if df is not None else None


def load_sentiment(country, data_dir):
    """Load sentiment analysis data for a country"""
    f = data_dir / f"{country}/sentiment/{country}_sentiment.csv"
    if not f.exists():
        return None
    df = pd.read_csv(f)
    df["date"] = pd.to_datetime(df["date"], format="mixed")
    return df.sort_values("date")


def load_pred(country, data_dir):
    """Load inflation prediction data for a country"""
    f = data_dir / f"{country}/lasso_preds/predictions.csv"
    if not f.exists():
        return None
    df = pd.read_csv(f)
    df["date"] = pd.to_datetime(df["date"], format="mixed")
    return df.sort_values("date")

def df_to_json(df):
    """Convert DataFrame to JSON-serializable list of dictionaries"""
    data = []
    for _, row in df.iterrows():
        r = {}
        for col in df.columns:
            v = row[col]
            if pd.isna(v):
                r[col] = None
            elif isinstance(v, pd.Timestamp):
                r[col] = v.strftime("%Y-%m-%d")
            elif isinstance(v, (int, float)):
                r[col] = float(v) if not pd.isna(v) else None
            else:
                r[col] = str(v)
        data.append(r)
    return data

def gen_html(title, subtitle, chart_id, all_data, countries, script_content):
    """Generate standalone HTML page with Chart.js visualization and country dropdown"""
    # Build country options, filtering out excluded countries
    opts = "\n".join(
        f'<option value="{c}">{fmt_country(c)}</option>'
        for c in countries
        if (c in all_data) and (c not in EXCLUDE_COUNTRIES)
    )
    
    # CSS styling for responsive layout
    css_styles = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 15px;
            background: #fff;
        }
        .controls {
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        label {
            font-weight: 600;
            color: #333;
            font-size: 0.95em;
        }
        select {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.9em;
            cursor: pointer;
            background: #fff;
        }
        select:hover { border-color: #667eea; }
        select:focus { outline: 0; border-color: #667eea; }
        .chart-wrapper { position: relative; height: 350px; }
    """
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <style>{css_styles}</style>
</head>
<body>
    <div class="controls">
        <label for="country-select">Country:</label>
        <select id="country-select">{opts}</select>
    </div>
    <div class="chart-wrapper">
        <canvas id="chart"></canvas>
    </div>
    <script>
        const allData = {json.dumps(all_data)};
        let currentChart = null;
        {script_content}
    </script>
</body>
</html>"""

def gen_epu_html(countries, data_dir, out):
    """Generate EPU visualization with raw and 3-month moving average lines"""
    countries = sorted([c for c in countries if c not in EXCLUDE_COUNTRIES])
    all_data = {
        c: df_to_json(load_epu(c, data_dir))
        for c in countries
        if load_epu(c, data_dir) is not None
    }
    if not all_data:
        return
    
    # JavaScript code for EPU chart rendering
    script = """
        // Format date from YYYY-MM-DD to YYYY-MM
        function formatDate(d) {
            const date = new Date(d);
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        }

        // Render chart for selected country
        function renderChart(country) {
            const data = allData[country];
            if (!data || !data.length) return;

            // Extract date labels and EPU values
            const labels = data.map(r => formatDate(r.date));
            const epuWeighted = data.map(r => r.epu_weighted);
            const epuMA3 = data.map(r => r.epu_weighted_ma3);

            // Get canvas context and destroy previous chart if exists
            const ctx = document.getElementById('chart').getContext('2d');
            if (currentChart) currentChart.destroy();

            // Create new line chart with two datasets
            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'EPU Weighted',
                            data: epuWeighted,
                            borderColor: '#aacddd',
                            borderWidth: 1.5,
                            borderDash: [5, 5],  // Dotted line
                            fill: false,
                            tension: 0.1,
                            pointRadius: 0,
                            pointHoverRadius: 5
                        },
                        {
                            label: 'EPU Weighted MA(3)',
                            data: epuMA3,
                            borderColor: '#1d77b2',
                            borderWidth: 3,
                            fill: false,
                            tension: 0.1,
                            pointRadius: 0,
                            pointHoverRadius: 5
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { usePointStyle: true, padding: 15 }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            padding: 12
                        }
                    },
                    scales: {
                        x: { display: true, title: { display: true, text: 'Date' } },
                        y: { display: true, title: { display: true, text: 'EPU Index' } }
                    }
                }
            });
        }

        // Event listener: re-render chart when country selection changes
        document.getElementById('country-select').addEventListener('change', e => renderChart(e.target.value));

        // Initial chart render with first country
        renderChart(document.getElementById('country-select').value);
    """
    
    with open(out, 'w') as f:
        f.write(gen_html(
            "Economic Policy Uncertainty Index",
            "EPU Weighted and 3-Month Moving Average",
            "epu-chart",
            all_data,
            countries,
            script
        ))
    print(f"Created {out}")

def gen_epu_topics_html(countries, topics, data_dir, out):
    """Generate topic-specific EPU visualization with multiple datasets"""
    countries = sorted([c for c in countries if c not in EXCLUDE_COUNTRIES])
    all_data = {
        c: df_to_json(load_epu_topics(c, topics, data_dir))
        for c in countries
        if load_epu_topics(c, topics, data_dir) is not None
    }
    if not all_data:
        return
    
    # Define colors and labels for each topic
    colors = ['#00a37c', '#d95e10']
    labels = [" ".join(w.capitalize() for w in t.split("_")) for t in topics]
    
    # Convert to JSON for embedding in JavaScript
    topics_json = json.dumps(topics)
    colors_json = json.dumps(colors)
    labels_json = json.dumps(labels)
    
    # JavaScript code for topic-based EPU chart rendering
    script = f"""
        const topics = {topics_json};
        const colors = {colors_json};
        const labels = {labels_json};

        // Format date from YYYY-MM-DD to YYYY-MM
        function formatDate(d) {{
            const date = new Date(d);
            return `${{date.getFullYear()}}-${{String(date.getMonth() + 1).padStart(2, '0')}}`;
        }}

        // Render chart for selected country
        function renderChart(country) {{
            const data = allData[country];
            if (!data || !data.length) return;

            // Extract date labels
            const labels_chart = data.map(r => formatDate(r.date));
            
            // Build datasets dynamically for each topic
            const datasets = [];
            topics.forEach((topic, index) => {{
                datasets.push({{
                    label: `${{labels[index]}} EPU`,
                    data: data.map(r => r[`epu_${{topic}}`]),
                    borderColor: colors[index],
                    borderWidth: 3,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }});
            }});

            // Get canvas context and destroy previous chart if exists
            const ctx = document.getElementById('chart').getContext('2d');
            if (currentChart) currentChart.destroy();

            // Create new line chart with topic datasets
            currentChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels_chart,
                    datasets: datasets
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'top',
                            labels: {{ usePointStyle: true, padding: 15 }}
                        }},
                        tooltip: {{
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            padding: 12
                        }}
                    }},
                    scales: {{
                        x: {{ display: true, title: {{ display: true, text: 'Date' }} }},
                        y: {{ display: true, title: {{ display: true, text: 'EPU Index' }} }}
                    }}
                }}
            }});
        }}

        // Event listener: re-render chart when country selection changes
        document.getElementById('country-select').addEventListener('change', e => renderChart(e.target.value));

        // Initial chart render with first country
        renderChart(document.getElementById('country-select').value);
    """
    
    with open(out, 'w') as f:
        f.write(gen_html(
            "Economic Policy Uncertainty by Topic",
            "Topic-based EPU Analysis",
            "epu-topics-chart",
            all_data,
            countries,
            script
        ))
    print(f"Created {out}")

def gen_sentiment_html(countries, data_dir, out):
    """Generate sentiment analysis visualization"""
    countries = sorted([c for c in countries if c not in EXCLUDE_COUNTRIES])
    all_data = {
        c: df_to_json(load_sentiment(c, data_dir))
        for c in countries
        if load_sentiment(c, data_dir) is not None
    }
    if not all_data:
        return
    
    # JavaScript code for sentiment chart rendering
    script = """
        // Format date from YYYY-MM-DD to YYYY-MM
        function formatDate(d) {
            const date = new Date(d);
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        }

        // Render chart for selected country
        function renderChart(country) {
            const data = allData[country];
            if (!data || !data.length) return;

            // Extract date labels and sentiment scores
            const labels = data.map(r => formatDate(r.date));
            const sentimentScores = data.map(r => r.score);

            // Get canvas context and destroy previous chart if exists
            const ctx = document.getElementById('chart').getContext('2d');
            if (currentChart) currentChart.destroy();

            // Create new line chart with filled area
            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Sentiment Score',
                            data: sentimentScores,
                            borderColor: '#2aa8f7',
                            backgroundColor: 'rgba(42, 168, 247, 0.1)',
                            borderWidth: 3,
                            fill: true,  // Fill area under line
                            tension: 0.1,
                            pointRadius: 0,
                            pointHoverRadius: 5
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { usePointStyle: true, padding: 15 }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            padding: 12
                        }
                    },
                    scales: {
                        x: { display: true, title: { display: true, text: 'Date' } },
                        y: { display: true, title: { display: true, text: 'Sentiment Score' } }
                    }
                }
            });
        }

        // Event listener: re-render chart when country selection changes
        document.getElementById('country-select').addEventListener('change', e => renderChart(e.target.value));

        // Initial chart render with first country
        renderChart(document.getElementById('country-select').value);
    """
    
    with open(out, 'w') as f:
        f.write(gen_html(
            "Sentiment Analysis",
            "News Sentiment Score Over Time",
            "sentiment-chart",
            all_data,
            countries,
            script
        ))
    print(f"Created {out}")

def gen_news_html(countries, data_dir, out):
    """Generate news article count visualization"""
    countries = sorted([c for c in countries if c not in EXCLUDE_COUNTRIES])
    all_data = {
        c: df_to_json(load_epu(c, data_dir))
        for c in countries
        if load_epu(c, data_dir) is not None
    }
    if not all_data:
        return
    
    # JavaScript code for news count chart rendering
    script = """
        // Format date from YYYY-MM-DD to YYYY-MM
        function formatDate(d) {
            const date = new Date(d);
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        }

        // Render chart for selected country
        function renderChart(country) {
            const data = allData[country];
            if (!data || !data.length) return;

            // Extract date labels and article counts
            const labels = data.map(r => formatDate(r.date));
            const newsCounts = data.map(r => r.news_total);

            // Get canvas context and destroy previous chart if exists
            const ctx = document.getElementById('chart').getContext('2d');
            if (currentChart) currentChart.destroy();

            // Create new line chart with filled area
            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'News Count',
                            data: newsCounts,
                            borderColor: '#2aa8f7',
                            backgroundColor: 'rgba(42, 168, 247, 0.1)',
                            borderWidth: 3,
                            fill: true,  // Fill area under line
                            tension: 0.1,
                            pointRadius: 0,
                            pointHoverRadius: 5
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { usePointStyle: true, padding: 15 }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            padding: 12
                        }
                    },
                    scales: {
                        x: { display: true, title: { display: true, text: 'Date' } },
                        y: { display: true, title: { display: true, text: 'Article Count' } }
                    }
                }
            });
        }

        // Event listener: re-render chart when country selection changes
        document.getElementById('country-select').addEventListener('change', e => renderChart(e.target.value));

        // Initial chart render with first country
        renderChart(document.getElementById('country-select').value);
    """
    
    with open(out, 'w') as f:
        f.write(gen_html(
            "News Article Count",
            "Number of Articles Scraped Per Month",
            "news-chart",
            all_data,
            countries,
            script
        ))
    print(f"Created {out}")

def gen_pred_html(countries, data_dir, out):
    """Generate inflation prediction vs actual visualization"""
    countries = sorted([c for c in countries if c not in EXCLUDE_PREDS])
    all_data = {
        c: df_to_json(load_pred(c, data_dir))
        for c in countries
        if load_pred(c, data_dir) is not None
    }
    if not all_data:
        return
    
    # JavaScript code for inflation prediction chart rendering
    script = """
        // Format date from YYYY-MM-DD to YYYY-MM
        function formatDate(d) {
            const date = new Date(d);
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        }

        // Render chart for selected country
        function renderChart(country) {
            const data = allData[country];
            if (!data || !data.length) return;

            // Extract date labels and inflation values
            const labels = data.map(r => formatDate(r.date));
            const predictedInflation = data.map(r => r.predicted_inflation);
            const actualInflation = data.map(r => r.actual_inflation);

            // Get canvas context and destroy previous chart if exists
            const ctx = document.getElementById('chart').getContext('2d');
            if (currentChart) currentChart.destroy();

            // Create new line chart comparing predicted vs actual inflation
            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Predicted Inflation',
                            data: predictedInflation,
                            borderColor: '#ff9a00',  // Orange
                            borderWidth: 3,
                            fill: false,
                            tension: 0.1,
                            pointRadius: 0,
                            pointHoverRadius: 5
                        },
                        {
                            label: 'Actual Inflation',
                            data: actualInflation,
                            borderColor: '#43a5e3',  // Blue
                            borderWidth: 3,
                            fill: false,
                            tension: 0.1,
                            pointRadius: 0,
                            pointHoverRadius: 5
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { usePointStyle: true, padding: 15 }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            padding: 12
                        }
                    },
                    scales: {
                        x: { display: true, title: { display: true, text: 'Date' } },
                        y: { display: true, title: { display: true, text: 'Inflation Rate' } }
                    }
                }
            });
        }

        // Event listener: re-render chart when country selection changes
        document.getElementById('country-select').addEventListener('change', e => renderChart(e.target.value));

        // Initial chart render with first country
        renderChart(document.getElementById('country-select').value);
    """
    
    with open(out, 'w') as f:
        f.write(gen_html(
            "Predicted Inflation",
            "Model Predictions vs Actual Inflation",
            "pred-chart",
            all_data,
            countries,
            script
        ))
    print(f"Created {out}")

if __name__ == '__main__':
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    DATA_DIR = PROJECT_ROOT / "testing_outputs" / "text"
    OUTPUT_DIR = PROJECT_ROOT / "docs/images/interactive/text"
    
    countries = [d for d in os.listdir(DATA_DIR) if (DATA_DIR / d).is_dir()]
    
    gen_epu_html(countries, DATA_DIR, OUTPUT_DIR / "epu_pic.html")
    gen_epu_topics_html(countries, ["inflation", "job"], DATA_DIR, OUTPUT_DIR / "epu_topics_pic.html")
    gen_sentiment_html(countries, DATA_DIR, OUTPUT_DIR / "sentiment_pic.html")
    gen_news_html(countries, DATA_DIR, OUTPUT_DIR / "news_count_pic.html")
    gen_pred_html(countries, DATA_DIR, OUTPUT_DIR / "train_predictions_pic.html")
    print("All plots generated successfully!")
