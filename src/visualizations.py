"""
visualizations.py — All charts for the India Rate Shock Lab.
Each function returns a plotly Figure ready for display or export.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ── Brand palette ────────────────────────────────────────────────────────────
SECTOR_COLORS = {
    "Bank":   "#E63946",
    "IT":     "#457B9D",
    "Auto":   "#F4A261",
    "FMCG":   "#2A9D8F",
    "Pharma": "#8338EC",
    "Realty": "#FB8500",
}
HIKE_COLOR = "#E63946"
CUT_COLOR  = "#2A9D8F"
BG         = "#0D1117"
GRID       = "#21262D"

_LAYOUT_BASE = dict(
    plot_bgcolor  = BG,
    paper_bgcolor = BG,
    font          = dict(color="#E6EDF3", family="Inter, sans-serif", size=12),
    margin        = dict(l=60, r=30, t=60, b=50),
    xaxis         = dict(gridcolor=GRID, zeroline=False),
    yaxis         = dict(gridcolor=GRID, zeroline=False),
)


def _apply_base(fig):
    fig.update_layout(**_LAYOUT_BASE)
    return fig


# ── 1. RBI Rate Timeline ──────────────────────────────────────────────────────
def plot_rbi_timeline(events_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    for _, ev in events_df.iterrows():
        color = HIKE_COLOR if ev["cycle"] == "Hike" else CUT_COLOR
        fig.add_shape(
            type="line",
            x0=ev["date"], x1=ev["date"],
            y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(color=color, width=1.2, dash="dot"),
        )

    # Repo rate step line
    rate_x = []
    rate_y = []
    for _, ev in events_df.iterrows():
        rate_x += [ev["date"], ev["date"]]
        rate_y += [ev.get("rate_before", ev["rate_after"] - ev["change_bps"]/100),
                   ev["rate_after"]]

    fig.add_trace(go.Scatter(
        x=rate_x, y=rate_y,
        mode="lines",
        line=dict(color="#F0F6FC", width=2.5),
        name="Repo Rate (%)",
    ))

    # Annotate large moves
    for _, ev in events_df[abs(events_df["change_bps"]) >= 40].iterrows():
        sign = "+" if ev["change_bps"] > 0 else ""
        fig.add_annotation(
            x=ev["date"], y=ev["rate_after"],
            text=f"{sign}{int(ev['change_bps'])}bp",
            showarrow=True, arrowhead=2,
            font=dict(size=10, color="#F0F6FC"),
            bgcolor=HIKE_COLOR if ev["cycle"] == "Hike" else CUT_COLOR,
            borderpad=3,
        )

    fig.update_layout(
        title=dict(text="RBI Repo Rate — Policy Change Events (2014–2025)", font=dict(size=18)),
        xaxis_title="Date",
        yaxis_title="Repo Rate (%)",
        showlegend=True,
        **_LAYOUT_BASE,
    )
    return fig


# ── 2. Average CAR by Sector & Horizon ───────────────────────────────────────
def plot_acar_heatmap(car_df: pd.DataFrame, cycle: str | None = None) -> go.Figure:
    """
    Heatmap of Average CAR (ACAR) across sectors and horizons.
    cycle: 'Hike', 'Cut', or None (all).
    """
    df = car_df if cycle is None else car_df[car_df["cycle"] == cycle]

    horizon_cols = [c for c in car_df.columns if c.startswith("CAR[")]
    sectors      = df["sector"].unique()

    matrix = []
    for sec in sectors:
        row = df[df["sector"] == sec][horizon_cols].mean()
        matrix.append(row.values * 100)   # convert to %

    z = np.array(matrix)
    text = [[f"{v:.2f}%" for v in row] for row in z]

    fig = go.Figure(go.Heatmap(
        z=z, x=horizon_cols, y=list(sectors),
        text=text, texttemplate="%{text}",
        colorscale=[
            [0.0, "#1B4332"], [0.35, "#2D6A4F"],
            [0.5, "#21262D"],
            [0.65, "#7B1D1D"], [1.0, "#E63946"],
        ],
        zmid=0,
        colorbar=dict(title="ACAR (%)", tickfont=dict(color="#E6EDF3")),
    ))
    title_str = f"Average CAR by Sector & Horizon" + (f" — {cycle} Cycle" if cycle else "")
    fig.update_layout(
        title=dict(text=title_str, font=dict(size=16)),
        **_LAYOUT_BASE,
    )
    return fig


# ── 3. CAR Event-Window Fan Chart ────────────────────────────────────────────
def plot_car_fan(ar_df: pd.DataFrame, sector: str, cycle: str | None = None) -> go.Figure:
    """
    Show the mean ± 1-σ band of cumulative abnormal returns for a single sector.
    """
    df = ar_df[ar_df["sector"] == sector].copy()
    if cycle:
        df = df[df["cycle"] == cycle]

    # For each event, compute cumulative sum of AR over rel_days
    cum_ar_by_event = []
    for ev_date, grp in df.groupby("event_date"):
        grp = grp.sort_values("rel_day")
        grp["cum_ar"] = grp["ar"].cumsum()
        grp["event_date"] = ev_date
        cum_ar_by_event.append(grp)

    if not cum_ar_by_event:
        return go.Figure().update_layout(title="No data", **_LAYOUT_BASE)

    panel = pd.concat(cum_ar_by_event)
    stats = panel.groupby("rel_day")["cum_ar"].agg(["mean","std","count"]).reset_index()
    stats.columns = ["rel_day","mean","std","n"]
    stats["se"]   = stats["std"] / np.sqrt(stats["n"])

    color = SECTOR_COLORS.get(sector, "#58A6FF")

    fig = go.Figure()
    # ±1σ band
    fig.add_trace(go.Scatter(
        x=pd.concat([stats["rel_day"], stats["rel_day"][::-1]]),
        y=pd.concat([stats["mean"] + stats["std"], (stats["mean"] - stats["std"])[::-1]]) * 100,
        fill="toself",
        fillcolor=color.replace(")", ",0.15)").replace("rgb","rgba") if "rgb" in color else color+"26",
        line=dict(width=0),
        name="±1σ band",
        showlegend=True,
    ))
    # Mean line
    fig.add_trace(go.Scatter(
        x=stats["rel_day"], y=stats["mean"] * 100,
        mode="lines+markers",
        line=dict(color=color, width=2.5),
        marker=dict(size=5),
        name=f"{sector} mean CAR",
    ))
    # Event-day vline
    fig.add_vline(x=0, line=dict(color="#F0F6FC", width=1.5, dash="dash"))
    fig.add_hline(y=0, line=dict(color=GRID, width=1))

    cycle_str = f" ({cycle} events)" if cycle else ""
    fig.update_layout(
        title=dict(text=f"{sector} — Cumulative Abnormal Returns{cycle_str}", font=dict(size=16)),
        xaxis_title="Trading Days Relative to RBI Announcement",
        yaxis_title="Cumulative AR (%)",
        **_LAYOUT_BASE,
    )
    return fig


# ── 4. Rate Sensitivity Scores (β₂ plot) ─────────────────────────────────────
def plot_rate_sensitivity(rate_sens_df: pd.DataFrame) -> go.Figure:
    df = rate_sens_df.reset_index().sort_values("beta_rate")
    colors = [HIKE_COLOR if v > 0 else CUT_COLOR for v in df["beta_rate"]]

    fig = go.Figure(go.Bar(
        x=df["sector"],
        y=df["beta_rate"] * 100,            # scale: % per 100 bps
        marker_color=colors,
        text=[f"{v*100:.2f}" for v in df["beta_rate"]],
        textposition="outside",
        name="Rate Sensitivity (β₂)",
    ))
    fig.update_layout(
        title=dict(text="Rate Sensitivity Score (β₂) by Sector", font=dict(size=16)),
        xaxis_title="Sector",
        yaxis_title="β₂ × 100  (% return per 100 bps rate change)",
        **_LAYOUT_BASE,
    )
    # significance stars
    for _, row in df.iterrows():
        star = "**" if row["p_beta_rate"] < 0.01 else ("*" if row["p_beta_rate"] < 0.05 else "")
        if star:
            fig.add_annotation(
                x=row["sector"], y=row["beta_rate"] * 100,
                text=star, showarrow=False,
                font=dict(size=14, color="#F0F6FC"),
                yanchor="bottom",
            )
    return fig


# ── 5. Rolling Beta ───────────────────────────────────────────────────────────
def plot_rolling_beta(returns: pd.DataFrame, sector: str,
                      window: int = 63) -> go.Figure:
    """Rolling 63-day (≈ 1 quarter) beta of sector vs Nifty50."""
    if "Nifty50" not in returns.columns or sector not in returns.columns:
        return go.Figure().update_layout(title="Missing data", **_LAYOUT_BASE)

    betas = []
    for i in range(window, len(returns)):
        y = returns[sector].iloc[i-window:i].values
        x = sm_ols_beta(returns["Nifty50"].iloc[i-window:i].values, y)
        betas.append({"date": returns.index[i], "beta": x})

    beta_df = pd.DataFrame(betas).set_index("date")

    fig = go.Figure(go.Scatter(
        x=beta_df.index, y=beta_df["beta"],
        mode="lines",
        line=dict(color=SECTOR_COLORS.get(sector, "#58A6FF"), width=2),
        name=f"{sector} rolling β",
    ))
    fig.add_hline(y=1, line=dict(color=GRID, width=1, dash="dot"))
    fig.update_layout(
        title=dict(text=f"{sector} — Rolling {window}-Day Market Beta", font=dict(size=16)),
        xaxis_title="Date",
        yaxis_title="Beta (vs Nifty50)",
        **_LAYOUT_BASE,
    )
    return fig


def sm_ols_beta(x: np.ndarray, y: np.ndarray) -> float:
    valid = np.isfinite(x) & np.isfinite(y)
    if valid.sum() < 10:
        return np.nan
    cov = np.cov(x[valid], y[valid])
    return cov[0, 1] / cov[0, 0]


# ── 6. Sector Cumulative Returns Timeline ─────────────────────────────────────
def plot_sector_cumulative_returns(prices: pd.DataFrame, events_df: pd.DataFrame) -> go.Figure:
    sectors = [c for c in prices.columns if c != "Nifty50"]
    rebased = (prices / prices.iloc[0] * 100)

    fig = go.Figure()
    for sec in sectors:
        fig.add_trace(go.Scatter(
            x=rebased.index, y=rebased[sec],
            mode="lines",
            line=dict(color=SECTOR_COLORS.get(sec, "#58A6FF"), width=1.8),
            name=sec,
        ))
    # Nifty50 benchmark
    fig.add_trace(go.Scatter(
        x=rebased.index, y=rebased["Nifty50"],
        mode="lines",
        line=dict(color="#F0F6FC", width=2.5, dash="dot"),
        name="Nifty50",
    ))
    # Add event markers
    for _, ev in events_df.iterrows():
        color = HIKE_COLOR if ev["cycle"] == "Hike" else CUT_COLOR
        fig.add_vline(
            x=ev["date"],
            line=dict(color=color, width=0.8, dash="dot"),
            opacity=0.5,
        )
    fig.update_layout(
        title=dict(text="Sector Cumulative Returns (Rebased = 100)", font=dict(size=16)),
        xaxis_title="Date",
        yaxis_title="Index (Base = 100 at Start)",
        **_LAYOUT_BASE,
    )
    return fig
