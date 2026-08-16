# 🌍 Cost of Living Explorer

An interactive dashboard comparing the cost of living across 95 countries, with live currency conversion and a rotatable 3D globe view.

## 🎯 Overview

This project analyzes and visualizes cost-of-living data for 95 countries, built as a hands-on data analysis and dashboard-building exercise. It combines a public institutional dataset with a live currency exchange API, letting users explore costs in their own local currency rather than just USD.

## 🧠 Features

- **Single Country view** - see a full cost breakdown (rent, groceries, utilities, transport) for any one country
- **Compare Countries** - select 2-5 countries and compare their costs and affordability categories side by side
- **Rankings** - filter by region and sort cheapest-to-most-expensive or vice versa
- **Interactive 3D Globe** - a rotatable, zoomable world map color-coded by monthly cost of living, with hover details
- **Budget Finder** - enter a monthly budget and instantly see which of the 95 countries you could afford to live in
- **Live currency conversion** - view every price in any of 160+ currencies (defaults to LKR), powered by a live exchange rate API updated hourly

## 📊 Key findings

- Monthly cost of living across the 95 countries is **right-skewed**: most countries cluster between $700-$2,000/month, with a small number of significantly pricier outliers (Switzerland, Israel, Iceland) stretching the range up to $4,000/month.
- The **mean ($1,774)** is notably higher than the **median ($1,550)**, confirming that a handful of expensive countries pull the average upward.
- Regional averages range more than **2.5x**, from Asia (\~$1,337/month) to Oceania (\~$2,388/month).
- Sri Lanka ranks among the **3 cheapest countries globally** (~$750/month), with rent and utilities affordability scores roughly 4-5x higher (cheaper) than countries like the UK or Australia.

## 🛠️ Tech stack

- Python, Pandas (data loading, cleaning, aggregation)
- Plotly Express (interactive bar charts and 3D choropleth globe)
- Streamlit (dashboard UI and deployment)
- Google Colab (data exploration and development)
- Live APIs: [WhereNext Cost of Living Index](https://getwherenext.com/data/cost-of-living-2026) (dataset) and [ExchangeRate-API](https://www.exchangerate-api.com/) (currency conversion)

## 📂 Dataset

Sourced from the **WhereNext Cost of Living Index 2026**, itself derived from the **World Bank International Comparison Program (ICP) 2021** Price Level Indices — public-domain data covering 176 economies. Licensed **CC BY 4.0** (free to share and adapt with attribution).

Each country's estimate is a single-person monthly cost (rent, groceries, utilities, transport), calibrated so the United States = ~$3,000/month.

**Note on limitations:** these are national averages, not city-specific figures — actual costs in a country's capital or major city may differ substantially from the national estimate. Two countries in the original dataset (Myanmar, Zimbabwe) use fallback estimates due to incomplete source data.

## 🚀 Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Live demo

**[View the live app →](https://cost-of-living-explorer.streamlit.app/)**

Deployed for free on Streamlit Community Cloud.

## 📓 Notebook

The full data exploration process - loading, cleaning, statistical summaries, and chart prototyping - is available in `notebook.ipynb`.

## 🔮 Future work

- Add city-level cost data (WhereNext also publishes data for 380 cities) for more granular comparisons
- Add historical trend data to show how cost of living has changed year over year
- Add a "salary equivalent" calculator - what salary in Country B matches your current lifestyle in Country A
- Cache exchange rates more robustly to reduce dependency on third-party API uptime
