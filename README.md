# 🩺 NYS County Health Explorer

**Live Dashboard:** [🔗 nys-health-explorer.streamlit.app](https://nys-health-explorer.streamlit.app)

An interactive public health dashboard analyzing **25,000+ health indicators** across all **62 New York State counties**, built with real data from the NYS Department of Health.

![Dashboard Preview](https://img.shields.io/badge/Streamlit-Live-14b8a6?style=for-the-badge&logo=streamlit) ![Python](https://img.shields.io/badge/Python-3.10+-3b82f6?style=for-the-badge&logo=python) ![Data](https://img.shields.io/badge/Records-25,000+-f59e0b?style=for-the-badge)

---

## What This Dashboard Does

| Page | Feature |
|------|---------|
| **🏠 Overview** | Key metrics, health topic distribution, statewide map |
| **🗺️ County Map** | Select any topic + indicator → interactive map + county ranking |
| **📊 Rankings** | All 62 counties ranked by health burden (highest vs healthiest) |
| **🔍 County Dive** | Pick any county → full health profile vs state average |
| **🎯 Topic Spotlight** | Top counties per topic + cross-topic correlation heatmap |
| **🧠 ML Clusters** | K-Means + PCA clustering reveals urban vs rural health profiles |

## Key Findings

- **2 distinct health clusters:** Urban (15 counties) vs Rural (47 counties)
- **Bronx** has highest health burden at 1.34x state average
- **Hamilton, Tompkins, Putnam** ranked healthiest
- Strong correlations between obesity, diabetes, and cardiovascular indicators

## Data Source

Real-time data from the **NYS DOH Community Health Indicator Reports (CHIRS)** API:
- API: `health.data.ny.gov/resource/54ci-sdfi.json`
- 62 counties · 15 health topics · 300+ indicators · 25,000+ records

## Tech Stack

- **Python** · Pandas, NumPy, Requests
- **Streamlit** · Multi-page interactive dashboard
- **Plotly** · Maps, bar charts, heatmaps, scatter plots
- **scikit-learn** · K-Means, PCA, Silhouette Analysis

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Author

**Vikash Maheshwari** — M.Eng Computer Science & Engineering

---

*Built to demonstrate public health data analytics capabilities using the same data infrastructure (Socrata API, Streamlit) that powers the NYS DOH's own Community Health Explorer.*
