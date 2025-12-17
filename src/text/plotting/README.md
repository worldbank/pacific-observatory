# Standalone HTML Plots

This folder contains standalone HTML plots generated from `interactive.py` data with dropdown menus.

## Files

- `generate_plots.py` - Python script to generate all 5 HTML files
- `epu_pic.html` - Economic Policy Uncertainty Index plot
- `epu_topics_pic.html` - EPU by Topic plot
- `sentiment_pic.html` - Sentiment Analysis plot
- `news_count_pic.html` - News Article Count plot
- `train_predictions_pic.html` - Inflation Predictions plot

## Usage

### Generate HTML Files

Run the generator script:
```bash
python interactive.py
```

This will create 5 standalone HTML files in the current directory.

### View Plots

Open any HTML file in a web browser. Each plot includes:
- Country dropdown selector
- Interactive Chart.js visualization
- Hover tooltips
- Responsive design

## Features

- **No dependencies** - Pure HTML/CSS/JavaScript
- **Standalone** - Each HTML file is self-contained
- **Interactive** - Country dropdown with instant chart updates
- **Responsive** - Works on desktop and mobile
- **Beautiful** - Modern gradient styling with smooth animations

## Data Requirements

The script expects data in this structure:
```
outputs/text/
├── {country}/
│   ├── epu/
│   │   ├── {country}_epu.csv
│   │   ├── {country}_epu_inflation.csv
│   │   └── {country}_epu_job.csv
│   ├── sentiment/
│   │   └── {country}_sentiment.csv
│   └── lasso_preds/
│       └── predictions.csv
```

## Plot Descriptions

### EPU Index
- Shows Economic Policy Uncertainty weighted index
- Includes 3-month moving average
- Dotted line: raw EPU Weighted
- Solid line: MA(3)

### EPU Topics
- Compares EPU across topics (Inflation, Jobs)
- Each topic as separate line
- 3-month moving average applied

### Sentiment Analysis
- News sentiment score over time
- Single line chart
- Filled area under curve

### News Count
- Number of articles scraped per month
- Tracks data availability
- Filled area under curve

### Inflation Predictions
- Model predictions vs actual inflation
- Orange line: predicted values
- Blue line: actual values
- Excludes countries with insufficient data
