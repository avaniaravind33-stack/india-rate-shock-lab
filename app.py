"""
app.py — Streamlit dashboard for India Rate Shock Lab
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="India Rate Shock Lab",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0D1117; }
    [data-testid="stSidebar"]          { background: #161B22; }
    h1, h2, h3                         { color: #F0F6FC; }
    .metric-card {
        background: #161B22;
        border: 1px solid #21262D;
        border-radius: 8px;
        padding: 16px 20px;
    }
    .metric-label  { font-size: 12px; color: #8B949E; text-transform: uppercase; letter-spacing: 0.08em; }
    .metric-value  { font-size: 28px; font-weight: 700; color: #F0F6FC; margin: 4px 0; }
    .metric-sub    { font-size: 12px; color: #8B949E; }
    .hike-badge    { background: #7B1D1D; color: #FCA5A5; border-radius: 4px; padding: 2px 8px; font-size: 11px; }
    .cut-badge     { background: #14532D; color: #86EFAC; border-radius: 4px; padding: 2px 8px; font-size: 11px; }
</style>
""", unsafe_allow_html=True)


# ─── Data loading (cached) ──────────────────────────────────────────────────
@st.cache_data(show_spinner="Downloading price data …")
def load_data():
    from src.data_loader import download_prices, load_or_generate_mock, compute_returns
    try:
        prices = download_prices(force_refresh=False)
        if prices is None or prices.empty or len(prices) < 100:
            raise ValueError("Insufficient data from Yahoo Finance")
    except Exception as exc:
        st.warning(f"⚠️ Yahoo Finance unavailable ({exc}). Using synthetic data for demo.")
        prices = load_or_generate_mock()
    returns = compute_returns(prices)
    return prices, returns


@st.cache_data(show_spinner="Running event study …")
def run_event_study(_returns):
    from src.event_study import compute_abnormal_returns, compute_car, compute_rate_sensitivity
    from src.rbi_events import get_events_df
    events = get_events_df()
    result = compute_abnormal_returns(_returns, market_col="Nifty50")
    ar_df  = result["ar_df"]
    car_df = compute_car(ar_df)
    rate_df = compute_rate_sensitivity(_returns, events)
    return events, ar_df, car_df, rate_df, result["betas_df"]


prices, returns = load_data()
events, ar_df, car_df, rate_df, betas_df = run_event_study(returns)


# ─── Sidebar ───────────────────────────────────────────────────────────────────
from src.visualizations import (
    plot_rbi_timeline, plot_acar_heatmap, plot_car_fan,
    plot_rate_sensitivity, plot_rolling_beta, plot_sector_cumulative_returns,
)

st.sidebar.markdown("## 📉 India Rate Shock Lab")
st.sidebar.markdown("How Do RBI Rate Changes Propagate Through Indian Equities?")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "⏱ Policy Timeline", "📊 Event Study", "🎯 Rate Sensitivity", "📈 Rolling Beta", "📋 Data Tables"],
)

cycle_filter = st.sidebar.selectbox("Filter by rate cycle", ["All", "Hike", "Cut"])
sector_sel   = st.sidebar.selectbox(
    "Focus sector",
    [c for c in prices.columns if c != "Nifty50"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Methodology**")
st.sidebar.markdown("""
- Estimation window: 100 trading days
- Pre-event: −5 days
- Post-event: +20 days
- Expected return: OLS market model
- Inference: Newey-West HAC errors
""")
st.sidebar.markdown("---")
st.sidebar.markdown("*Data: Yahoo Finance / NSE · Built with Python & Streamlit*")


# ─── Overview Page ───────────────────────────────────────────────────────────
if page == "🏠 Overview":
    st.title("🇮🇳 India Rate Shock Lab")
    st.markdown("### How Do RBI Monetary Policy Changes Propagate Through Indian Equity Sectors?")
    st.markdown("---")

    n_hikes = len(events[events["cycle"] == "Hike"])
    n_cuts  = len(events[events["cycle"] == "Cut"])
    n_sectors = len([c for c in prices.columns if c != "Nifty50"])
    n_events_studied = car_df["event_date"].nunique() if not car_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Rate Change Events</div>
            <div class="metric-value">{len(events)}</div>
            <div class="metric-sub">2014 – 2025</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Rate Hikes</div>
            <div class="metric-value" style="color:#E63946">{n_hikes}</div>
            <div class="metric-sub">avg {events[events['cycle']=='Hike']['change_bps'].mean():.0f} bps</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Rate Cuts</div>
            <div class="metric-value" style="color:#2A9D8F">{n_cuts}</div>
            <div class="metric-sub">avg {abs(events[events['cycle']=='Cut']['change_bps'].mean()):.0f} bps</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Sectors Covered</div>
            <div class="metric-value">{n_sectors}</div>
            <div class="metric-sub">Bank · IT · Auto · FMCG · Pharma · Realty</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Sector Cumulative Performance (with RBI Events Marked)")
    fig = plot_sector_cumulative_returns(prices, events)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    ---
    #### Research Approach

    This project applies an **event-study methodology** to examine how RBI monetary-policy
    announcements transmit into Indian equity sector returns.

    **Key questions:**
    1. Do sectors respond differently to rate hikes vs. cuts?
    2. Is the market reaction immediate or does it persist over days?
    3. Which sectors exhibit the highest sensitivity to rate changes (β₂)?

    **Sectors under study:** Banking · IT · Automobiles · FMCG · Pharmaceuticals · Real Estate

    **Data sources:** NSE sector indices via Yahoo Finance, RBI policy announcements from RBI.org.in
    """)


# ─── Policy Timeline ─────────────────────────────────────────────────────────
elif page == "⏱ Policy Timeline":
    st.title("RBI Monetary Policy Timeline")
    fig = plot_rbi_timeline(events)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Policy Change Events")
    display_ev = events[["date","change_bps","rate_after","stance","cycle"]].copy()
    display_ev["date"] = display_ev["date"].dt.strftime("%Y-%m-%d")
    display_ev.columns = ["Date","Change (bps)","Repo Rate After (%)","Stance","Cycle"]

    def _color_cycle(val):
        if val == "Hike": return "background-color:#7B1D1D; color:#FCA5A5"
        if val == "Cut":  return "background-color:#14532D; color:#86EFAC"
        return ""

    st.dataframe(
        display_ev.style.applymap(_color_cycle, subset=["Cycle"]),
        use_container_width=True, hide_index=True,
    )


# ─── Event Study ─────────────────────────────────────────────────────────────
elif page == "📊 Event Study":
    st.title("Event Study — Abnormal Returns")

    st.markdown("#### Average CAR Heatmap")
    cycle_arg = None if cycle_filter == "All" else cycle_filter
    if not car_df.empty:
        fig = plot_acar_heatmap(car_df, cycle=cycle_arg)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Event study produced no results — check data availability.")

    st.markdown(f"#### {sector_sel} — Cumulative Abnormal Return Fan Chart")
    if not ar_df.empty:
        fig2 = plot_car_fan(ar_df, sector=sector_sel, cycle=cycle_arg)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    **Reading the chart:**
    - Day 0 = RBI announcement date.
    - Shaded band = ±1 standard deviation across events.
    - CAR > 0 above the dashed line means positive abnormal returns vs. market model prediction.
    """)


# ─── Rate Sensitivity ─────────────────────────────────────────────────────────
elif page == "🎯 Rate Sensitivity":
    st.title("Rate Sensitivity Scores (β₂)")
    st.markdown("""
    Estimated from the regression:

    **Sector Return = α + β₁ × Market Return + β₂ × Rate Change + ε**

    β₂ measures the sector's *direct* sensitivity to a 100 bps rate change,
    *after* controlling for the overall market move.
    Asterisks: * p<0.05, ** p<0.01 (Newey-West HAC standard errors).
    """)

    if not rate_df.empty:
        fig = plot_rate_sensitivity(rate_df)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Detailed Regression Results")
        styled = rate_df.reset_index()[[
            "sector","beta_rate","t_beta_rate","p_beta_rate","beta_market","r_squared","n_obs"
        ]].copy()
        styled.columns = ["Sector","β₂ (Rate Sens.)","t-stat","p-value","β₁ (Market)","R²","N"]
        styled["β₂ (Rate Sens.)"] = styled["β₂ (Rate Sens.)"].map("{:.4f}".format)
        styled["t-stat"]          = styled["t-stat"].map("{:.2f}".format)
        styled["p-value"]         = styled["p-value"].map("{:.3f}".format)
        styled["β₁ (Market)"]    = styled["β₁ (Market)"].map("{:.3f}".format)
        styled["R²"]              = styled["R²"].map("{:.3f}".format)
        st.dataframe(styled, use_container_width=True, hide_index=True)
    else:
        st.warning("Rate sensitivity model could not be estimated — check data.")


# ─── Rolling Beta ─────────────────────────────────────────────────────────────
elif page == "📈 Rolling Beta":
    st.title(f"Rolling Market Beta — {sector_sel}")
    st.markdown(f"""
    63-day (≈ 1 quarter) rolling OLS beta of **{sector_sel}** vs Nifty50.
    Beta > 1 → more volatile than the market; Beta < 1 → more defensive.
    """)
    fig = plot_rolling_beta(returns, sector=sector_sel)
    st.plotly_chart(fig, use_container_width=True)


# ─── Data Tables ──────────────────────────────────────────────────────────────
elif page == "📋 Data Tables":
    st.title("Raw Data Tables")

    tab1, tab2, tab3 = st.tabs(["Prices", "Returns", "CAR Summary"])
    with tab1:
        st.dataframe(prices.tail(100).round(2), use_container_width=True)
    with tab2:
        st.dataframe((returns.tail(100) * 100).round(4), use_container_width=True)
    with tab3:
        if not car_df.empty:
            show_car = car_df.copy()
            show_car["event_date"] = pd.to_datetime(show_car["event_date"]).dt.strftime("%Y-%m-%d")
            st.dataframe(show_car.round(4), use_container_width=True)
