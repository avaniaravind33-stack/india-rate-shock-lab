# 🇮🇳 India Rate Shock Lab

**How Do RBI Monetary Policy Changes Propagate Through Indian Equity Sectors?**

A quantitative research project examining how the Reserve Bank of India's repo rate changes transmit across six NSE equity sector indices, using event-study methodology and rate-sensitivity regression.

---

## Research Question

When the RBI hikes or cuts rates, which sectors react most — and is the reaction immediate or persistent?

## What This Project Does

- **Event Study Framework** — Computes abnormal and cumulative abnormal returns (CARs) for 6 NSE sector indices across 23 RBI rate-change events (2014–2025)
- **Rate Sensitivity Scoring (β₂)** — OLS regression isolating the direct sector return attributable to rate changes after controlling for broad market moves
- **Interactive Dashboard** — Streamlit app with heatmaps, fan charts, rolling beta, and a full data explorer
- **Research Note** — 7-section structured analysis following academic event-study conventions

## Sectors Studied

| Sector | NSE Index | Ticker |
|--------|-----------|--------|
| Banking | Nifty Bank | `^NSEBANK` |
| IT | Nifty IT | `^CNXIT` |
| Automobiles | Nifty Auto | `^CNXAUTO` |
| FMCG | Nifty FMCG | `^CNXFMCG` |
| Pharmaceuticals | Nifty Pharma | `^CNXPHARMA` |
| Real Estate | Nifty Realty | `^CNXREALTY` |

## Methodology

```
Estimation window: T−125 to T−6  (≈ 100 trading days)
Event window:       T−5   to T+20 (25 trading days)

Expected return:    r_i = α + β·r_market  (OLS market model)
Abnormal return:    AR = actual − expected
CAR(a,b):           Σ AR from day a to day b

Rate sensitivity:   r_sector = α + β₁·r_mkt + β₂·ΔRate + ε
                    β₂ estimated with Newey-West HAC errors
```

## Project Structure

```
india-rate-shock-lab/
├── app.py                          # Streamlit dashboard
├── requirements.txt
├── src/
│   ├── rbi_events.py               # RBI policy event calendar (2014–2025)
│   ├── data_loader.py              # Yahoo Finance download + mock fallback
│   ├── event_study.py              # AR / CAR / rate sensitivity engine
│   └── visualizations.py          # Plotly charts
├── notebooks/
│   └── india_rate_shock_analysis.ipynb   # Full research notebook
├── research_note/
│   └── india_rate_shock_research_note.md # 7-section research note
├── data/                           # Cached price data (gitignored)
└── output/                         # Charts + Excel export
```

## Quickstart

```bash
git clone https://github.com/avaniaravind33-stack/india-rate-shock-lab.git
cd india-rate-shock-lab
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py

# Or open the research notebook
jupyter notebook notebooks/india_rate_shock_analysis.ipynb
```

## Key Results

- **Real Estate** and **Banking** exhibit the highest negative rate sensitivity (β₂)
- **IT** is effectively insulated from domestic rate cycles (USD revenues, INR depreciation hedge)
- Rate reactions **persist beyond announcement day** — especially in Realty and Banking
- Hike events generate larger negative reactions than equivalent-sized cut events produce positive ones

## Technologies

Python · pandas · NumPy · statsmodels · Plotly · Streamlit · yfinance · openpyxl

---

*Built as a quantitative research portfolio project. Data sourced from Yahoo Finance and RBI press releases.*
