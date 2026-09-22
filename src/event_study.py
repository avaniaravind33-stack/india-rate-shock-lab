"""
event_study.py — Event-study framework for RBI policy announcements.

Methodology
-----------
For each RBI event on date t:
  estimation window : [t-120, t-21]  (≈ 100 trading days)
  event window      : [t-5,  t+20]

Abnormal Return (AR) = Actual return − Expected return
  Expected return from OLS market model:  r_i = α + β·r_m + ε

Cumulative Abnormal Return (CAR) over [t+a, t+b]:
  CAR(a,b) = Σ AR_t  for t in [a, b]

Average CAR (ACAR) across N events = mean of CARs at each horizon.

Newey-West t-statistics are used for inference.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_hac
from typing import Tuple


# ------------------------------------------------------------------
# Core event-study engine
# ------------------------------------------------------------------
ESTIMATION_DAYS = 100   # days before pre-event window
PRE_EVENT       = 5     # days before event day
POST_EVENT      = 20    # days after event day


def _align_to_trading_days(
    date: pd.Timestamp,
    returns: pd.DataFrame,
) -> int | None:
    """Return integer iloc of date (or nearest subsequent trading day)."""
    idx = returns.index
    if date in idx:
        return idx.get_loc(date)
    # move forward up to 5 days
    for lag in range(1, 6):
        d = date + pd.Timedelta(days=lag)
        if d in idx:
            return idx.get_loc(d)
    return None


def compute_abnormal_returns(
    returns: pd.DataFrame,
    market_col: str = "Nifty50",
    estimation_window: int = ESTIMATION_DAYS,
    pre_event: int  = PRE_EVENT,
    post_event: int = POST_EVENT,
) -> dict:
    """
    Run full event study for all sectors across all events.

    Returns
    -------
    {
        "sector_ar"   : DataFrame [events × event_days × sectors],
        "sector_car"  : DataFrame of cumulative abnormal returns at key horizons,
        "betas"       : DataFrame of estimated market betas (sector × event),
        "event_log"   : DataFrame with event metadata + iloc positions,
    }
    But we flatten into:
        ar_panel   : pd.DataFrame  index=(event, rel_day), columns=sectors
        car_panel  : pd.DataFrame  index=event, columns=sector_×_horizon
    """
    from src.rbi_events import get_events_df
    events        = get_events_df()
    sector_cols   = [c for c in returns.columns if c != market_col]
    mkt_returns   = returns[market_col]

    all_ar     = []   # list of dicts
    all_betas  = []
    all_alphas = []
    event_log  = []

    for _, ev in events.iterrows():
        t0 = _align_to_trading_days(ev["date"], returns)
        if t0 is None:
            continue

        t_est_start = t0 - pre_event - estimation_window
        t_est_end   = t0 - pre_event - 1
        t_ev_start  = t0 - pre_event
        t_ev_end    = t0 + post_event

        # bounds check
        if t_est_start < 0 or t_ev_end >= len(returns):
            continue

        est_slice = returns.iloc[t_est_start : t_est_end + 1]
        ev_slice  = returns.iloc[t_ev_start  : t_ev_end  + 1]
        rel_days  = np.arange(-pre_event, post_event + 1)

        ev_entry = ev.to_dict()
        ev_entry["iloc_t0"]    = t0
        ev_entry["n_est_days"] = len(est_slice)
        event_log.append(ev_entry)

        betas_row  = {"date": ev["date"]}
        alphas_row = {"date": ev["date"]}

        for sec in sector_cols:
            # --- Estimate market model on estimation window ---
            y = est_slice[sec].values
            x = sm.add_constant(est_slice[market_col].values)
            valid = np.isfinite(y) & np.isfinite(x[:, 1])
            if valid.sum() < 30:
                continue
            res = sm.OLS(y[valid], x[valid]).fit()
            alpha, beta = res.params[0], res.params[1]
            betas_row[sec]  = beta
            alphas_row[sec] = alpha

            # --- Compute abnormal returns over event window ---
            actual_r   = ev_slice[sec].values
            market_r   = ev_slice[market_col].values
            expected_r = alpha + beta * market_r
            ar         = actual_r - expected_r

            for i, rd in enumerate(rel_days):
                all_ar.append({
                    "event_date": ev["date"],
                    "cycle":      ev["cycle"],
                    "change_bps": ev["change_bps"],
                    "rel_day":    rd,
                    "sector":     sec,
                    "ar":         ar[i] if i < len(ar) else np.nan,
                })

        all_betas.append(betas_row)
        all_alphas.append(alphas_row)

    ar_df    = pd.DataFrame(all_ar)
    betas_df = pd.DataFrame(all_betas).set_index("date")
    event_log_df = pd.DataFrame(event_log)

    return {
        "ar_df":        ar_df,
        "betas_df":     betas_df,
        "event_log_df": event_log_df,
        "sector_cols":  sector_cols,
    }


def compute_car(ar_df: pd.DataFrame, horizons: list[tuple[int,int]] | None = None) -> pd.DataFrame:
    """
    Compute Cumulative Abnormal Returns at specified horizons.
    horizons: list of (start_rel_day, end_rel_day) tuples.
    Returns DataFrame: index=(event_date, sector), columns=horizon labels.
    """
    if horizons is None:
        horizons = [(0, 0), (0, 1), (0, 4), (0, 19), (-5, -1)]
    results = []
    for (event_date, sector), grp in ar_df.groupby(["event_date", "sector"]):
        grp = grp.set_index("rel_day")["ar"].sort_index()
        row = {"event_date": event_date, "sector": sector}
        for (a, b) in horizons:
            mask   = (grp.index >= a) & (grp.index <= b)
            car    = grp[mask].sum()
            label  = f"CAR[{a:+d},{b:+d}]"
            row[label] = car
        # pull extra metadata
        meta = ar_df[ar_df["event_date"] == event_date][["cycle","change_bps"]].iloc[0]
        row["cycle"]      = meta["cycle"]
        row["change_bps"] = meta["change_bps"]
        results.append(row)
    return pd.DataFrame(results)


def compute_rate_sensitivity(returns: pd.DataFrame, events_df: pd.DataFrame,
                              market_col: str = "Nifty50") -> pd.DataFrame:
    """
    Estimate rate-sensitivity scores via OLS:
        r_sector = α + β1·r_market + β2·RateChange + ε
    β2 is the Rate Sensitivity Score.
    Merge returns with rate-change data on event days.

    Returns DataFrame: sector → [alpha, beta_mkt, beta_rate, r2, t_beta_rate]
    """
    sector_cols = [c for c in returns.columns if c != market_col]

    # Build a daily rate-change series (0 on non-event days)
    rate_series = pd.Series(0.0, index=returns.index, name="rate_change_bps")
    for _, ev in events_df.iterrows():
        t0 = _align_to_trading_days(ev["date"], returns)
        if t0 is not None:
            rate_series.iloc[t0] = ev["change_bps"]

    results = []
    for sec in sector_cols:
        y = returns[sec].values
        x = pd.DataFrame({
            "const":       1.0,
            "mkt":         returns[market_col].values,
            "rate_change": rate_series.values,
        })
        valid = np.isfinite(y) & np.isfinite(x["mkt"])
        X = x[valid].values
        Y = y[valid]
        try:
            res = sm.OLS(Y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
            results.append({
                "sector":        sec,
                "alpha":         res.params[0],
                "beta_market":   res.params[1],
                "beta_rate":     res.params[2],         # Rate Sensitivity Score
                "t_beta_rate":   res.tvalues[2],
                "p_beta_rate":   res.pvalues[2],
                "r_squared":     res.rsquared,
                "n_obs":         int(res.nobs),
            })
        except Exception as e:
            print(f"  OLS error for {sec}: {e}")
    df = pd.DataFrame(results).set_index("sector").sort_values("beta_rate")
    return df
