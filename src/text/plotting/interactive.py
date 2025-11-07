"""Generate standalone HTML plots with dropdown menus"""
import os, sys, json, pandas as pd
from pathlib import Path

EXCLUDE_COUNTRIES = ['american_samoa','guam','malaysia','marshall_islands','pacific','palau','south_korea','singapore','thailand',"timor_leste",'tuvalu','vanuatu']
EXCLUDE_PREDS = ['american_samoa','guam','malaysia','marshall_islands','mongolia','singapore','south_korea','thailand','timor_leste','tuvalu']

def fmt_country(c): return " ".join(w[0].upper() + w[1:] for w in c.split("_"))

def load_epu(country, data_dir):
    f = data_dir / f"{country}/epu/{country}_epu.csv"
    if not f.exists(): return None
    df = pd.read_csv(f)
    df["date"] = pd.to_datetime(df["date"], format="mixed")
    df["epu_weighted_ma3"] = df["epu_weighted"].rolling(window=3).mean()
    return df.sort_values("date")

def load_epu_topics(country, topics, data_dir):
    df = None
    for t in topics:
        f = data_dir / f"{country}/epu/{country}_epu_{t}.csv"
        if not f.exists(): continue
        d = pd.read_csv(f)
        d["date"] = pd.to_datetime(d["date"], format="mixed")
        d[f"epu_{t}"] = d[f"epu_{t}"].rolling(window=3).mean()
        df = d[["date", f"epu_{t}"]].copy() if df is None else df.merge(d[["date", f"epu_{t}"]], on="date", how="outer")
    return df.sort_values("date") if df is not None else None

def load_sentiment(country, data_dir):
    f = data_dir / f"{country}/sentiment/{country}_sentiment.csv"
    if not f.exists(): return None
    df = pd.read_csv(f)
    df["date"] = pd.to_datetime(df["date"], format="mixed")
    return df.sort_values("date")

def load_pred(country, data_dir):
    f = data_dir / f"{country}/lasso_preds/predictions.csv"
    if not f.exists(): return None
    df = pd.read_csv(f)
    df["date"] = pd.to_datetime(df["date"], format="mixed")
    return df.sort_values("date")

def df_to_json(df):
    data = []
    for _, row in df.iterrows():
        r = {}
        for col in df.columns:
            v = row[col]
            if pd.isna(v): r[col] = None
            elif isinstance(v, pd.Timestamp): r[col] = v.strftime("%Y-%m-%d")
            elif isinstance(v, (int, float)): r[col] = float(v) if not pd.isna(v) else None
            else: r[col] = str(v)
        data.append(r)
    return data

def gen_html(title, subtitle, chart_id, all_data, countries, script_content):
    opts = "\n".join(f'<option value="{c}">{fmt_country(c)}</option>' for c in countries if (c in all_data)&(c not in EXCLUDE_COUNTRIES))
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;padding:15px;background:#fff}}
.controls{{margin-bottom:15px;display:flex;align-items:center;gap:10px}}label{{font-weight:600;color:#333;font-size:0.95em}}select{{padding:8px 12px;border:1px solid #ddd;border-radius:4px;font-size:0.9em;cursor:pointer;background:#fff}}
select:hover{{border-color:#667eea}}select:focus{{outline:0;border-color:#667eea}}.chart-wrapper{{position:relative;height:350px}}</style></head>
<body><div class="controls"><label for="country-select">Country:</label><select id="country-select">{opts}</select></div>
<div class="chart-wrapper"><canvas id="chart"></canvas></div>
<script>const allData={json.dumps(all_data)};let currentChart=null;{script_content}</script></body></html>"""

def gen_epu_html(countries, data_dir, out):
    countries = sorted([c for c in countries if c not in EXCLUDE_COUNTRIES])
    all_data = {c: df_to_json(load_epu(c, data_dir)) for c in countries if (load_epu(c, data_dir) is not None)}
    if not all_data: return
    script = """function formatDate(d){const date=new Date(d);return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}`}
function renderChart(c){const d=allData[c];if(!d||!d.length)return;const l=d.map(r=>formatDate(r.date)),e=d.map(r=>r.epu_weighted),m=d.map(r=>r.epu_weighted_ma3);
const ctx=document.getElementById('chart').getContext('2d');if(currentChart)currentChart.destroy();currentChart=new Chart(ctx,{type:'line',data:{labels:l,datasets:[{label:'EPU Weighted',data:e,borderColor:'#aacddd',borderWidth:1.5,borderDash:[5,5],fill:false,tension:0.1,pointRadius:0,pointHoverRadius:5},
{label:'EPU Weighted MA(3)',data:m,borderColor:'#1d77b2',borderWidth:3,fill:false,tension:0.1,pointRadius:0,pointHoverRadius:5}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top',labels:{usePointStyle:true,padding:15}},tooltip:{mode:'index',intersect:false,backgroundColor:'rgba(0,0,0,0.8)',padding:12}},scales:{x:{display:true,title:{display:true,text:'Date'}},y:{display:true,title:{display:true,text:'EPU Index'}}}}})
}
document.getElementById('country-select').addEventListener('change',e=>renderChart(e.target.value));renderChart(document.getElementById('country-select').value);
document.getElementById('info').innerHTML='<p><strong>EPU Weighted:</strong> Dotted line showing raw Economic Policy Uncertainty Index</p><p><strong>EPU Weighted MA(3):</strong> Solid line showing 3-month moving average</p>'"""
    with open(out, 'w') as f: f.write(gen_html("Economic Policy Uncertainty Index", "EPU Weighted and 3-Month Moving Average", "epu-chart", all_data, countries, script))
    print(f"Created {out}")

def gen_epu_topics_html(countries, topics, data_dir, out):
    countries = sorted([c for c in countries if c not in EXCLUDE_COUNTRIES])
    all_data = {c: df_to_json(load_epu_topics(c, topics, data_dir)) for c in countries if (load_epu_topics(c, topics, data_dir) is not None)}
    if not all_data: return
    colors = ['#00a37c', '#d95e10']
    labels = [" ".join(w.capitalize() for w in t.split("_")) for t in topics]
    topics_json = json.dumps(topics)
    colors_json = json.dumps(colors)
    labels_json = json.dumps(labels)
    script = "const topics=" + topics_json + ";const colors=" + colors_json + ";const labels=" + labels_json + """;
function formatDate(d){const date=new Date(d);return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}`}
function renderChart(c){const d=allData[c];if(!d||!d.length)return;const l=d.map(r=>formatDate(r.date)),ds=[];
topics.forEach((t,i)=>{ds.push({label:`${labels[i]} EPU`,data:d.map(r=>r[`epu_${t}`]),borderColor:colors[i],borderWidth:3,fill:false,tension:0.1,pointRadius:0,pointHoverRadius:5})});
const ctx=document.getElementById('chart').getContext('2d');if(currentChart)currentChart.destroy();currentChart=new Chart(ctx,{type:'line',data:{labels:l,datasets:ds},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top',labels:{usePointStyle:true,padding:15}},tooltip:{mode:'index',intersect:false,backgroundColor:'rgba(0,0,0,0.8)',padding:12}},scales:{x:{display:true,title:{display:true,text:'Date'}},y:{display:true,title:{display:true,text:'EPU Index'}}}}})
}
document.getElementById('country-select').addEventListener('change',e=>renderChart(e.target.value));renderChart(document.getElementById('country-select').value);
document.getElementById('info').innerHTML='<p><strong>Topic-based EPU:</strong> Comparing Economic Policy Uncertainty across different topics</p>'"""
    with open(out, 'w') as f: f.write(gen_html("Economic Policy Uncertainty by Topic", "Topic-based EPU Analysis", "epu-topics-chart", all_data, countries, script))
    print(f"Created {out}")

def gen_sentiment_html(countries, data_dir, out):
    countries = sorted([c for c in countries if c not in EXCLUDE_COUNTRIES])
    all_data = {c: df_to_json(load_sentiment(c, data_dir)) for c in countries if (load_sentiment(c, data_dir) is not None)}
    if not all_data: return
    script = """function formatDate(d){const date=new Date(d);return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}`}
function renderChart(c){const d=allData[c];if(!d||!d.length)return;const l=d.map(r=>formatDate(r.date)),s=d.map(r=>r.score);
const ctx=document.getElementById('chart').getContext('2d');if(currentChart)currentChart.destroy();currentChart=new Chart(ctx,{type:'line',data:{labels:l,datasets:[{label:'Sentiment Score',data:s,borderColor:'#2aa8f7',backgroundColor:'rgba(42,168,247,0.1)',borderWidth:3,fill:true,tension:0.1,pointRadius:0,pointHoverRadius:5}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top',labels:{usePointStyle:true,padding:15}},tooltip:{mode:'index',intersect:false,backgroundColor:'rgba(0,0,0,0.8)',padding:12}},scales:{x:{display:true,title:{display:true,text:'Date'}},y:{display:true,title:{display:true,text:'Sentiment Score'}}}}})
}
document.getElementById('country-select').addEventListener('change',e=>renderChart(e.target.value));renderChart(document.getElementById('country-select').value);
document.getElementById('info').innerHTML='<p><strong>Sentiment Score:</strong> Analysis of news sentiment over time</p>'"""
    with open(out, 'w') as f: f.write(gen_html("Sentiment Analysis", "News Sentiment Score Over Time", "sentiment-chart", all_data, countries, script))
    print(f"Created {out}")

def gen_news_html(countries, data_dir, out):
    countries = sorted([c for c in countries if c not in EXCLUDE_COUNTRIES])
    all_data = {c: df_to_json(load_epu(c, data_dir)) for c in countries if (load_epu(c, data_dir) is not None)}
    if not all_data: return
    script = """function formatDate(d){const date=new Date(d);return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}`}
function renderChart(c){const d=allData[c];if(!d||!d.length)return;const l=d.map(r=>formatDate(r.date)),n=d.map(r=>r.news_total);
const ctx=document.getElementById('chart').getContext('2d');if(currentChart)currentChart.destroy();currentChart=new Chart(ctx,{type:'line',data:{labels:l,datasets:[{label:'News Count',data:n,borderColor:'#2aa8f7',backgroundColor:'rgba(42,168,247,0.1)',borderWidth:3,fill:true,tension:0.1,pointRadius:0,pointHoverRadius:5}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top',labels:{usePointStyle:true,padding:15}},tooltip:{mode:'index',intersect:false,backgroundColor:'rgba(0,0,0,0.8)',padding:12}},scales:{x:{display:true,title:{display:true,text:'Date'}},y:{display:true,title:{display:true,text:'Article Count'}}}}})
}
document.getElementById('country-select').addEventListener('change',e=>renderChart(e.target.value));renderChart(document.getElementById('country-select').value);
document.getElementById('info').innerHTML='<p><strong>News Article Count:</strong> Number of articles scraped per month</p>'"""
    with open(out, 'w') as f: f.write(gen_html("News Article Count", "Number of Articles Scraped Per Month", "news-chart", all_data, countries, script))
    print(f"Created {out}")

def gen_pred_html(countries, data_dir, out):
    countries = sorted([c for c in countries if c not in EXCLUDE_PREDS])
    all_data = {c: df_to_json(load_pred(c, data_dir)) for c in countries if (load_pred(c, data_dir) is not None)}
    if not all_data: return
    script = """function formatDate(d){const date=new Date(d);return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}`}
function renderChart(c){const d=allData[c];if(!d||!d.length)return;const l=d.map(r=>formatDate(r.date)),p=d.map(r=>r.predicted_inflation),a=d.map(r=>r.actual_inflation);
const ctx=document.getElementById('chart').getContext('2d');if(currentChart)currentChart.destroy();currentChart=new Chart(ctx,{type:'line',data:{labels:l,datasets:[{label:'Predicted Inflation',data:p,borderColor:'#ff9a00',borderWidth:3,fill:false,tension:0.1,pointRadius:0,pointHoverRadius:5},
{label:'Actual Inflation',data:a,borderColor:'#43a5e3',borderWidth:3,fill:false,tension:0.1,pointRadius:0,pointHoverRadius:5}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top',labels:{usePointStyle:true,padding:15}},tooltip:{mode:'index',intersect:false,backgroundColor:'rgba(0,0,0,0.8)',padding:12}},scales:{x:{display:true,title:{display:true,text:'Date'}},y:{display:true,title:{display:true,text:'Inflation Rate'}}}}})
}
document.getElementById('country-select').addEventListener('change',e=>renderChart(e.target.value));renderChart(document.getElementById('country-select').value);
document.getElementById('info').innerHTML='<p><strong>Predicted Inflation:</strong> Orange line showing model predictions</p><p><strong>Actual Inflation:</strong> Blue line showing actual inflation rates</p>'"""
    with open(out, 'w') as f: f.write(gen_html("Predicted Inflation", "Model Predictions vs Actual Inflation", "pred-chart", all_data, countries, script))
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
