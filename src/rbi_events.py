"""
rbi_events.py  — Authoritative RBI monetary-policy event calendar
All dates are the MPC announcement / effective dates.
direction: +1 = hike, -1 = cut, 0 = hold (we only include change events)
"""

import pandas as pd

# -------------------------------------------------------------------
# RBI Repo Rate Change Events  (FY 2014 – FY 2025)
# Sources: RBI.org.in press releases
# -------------------------------------------------------------------
RBI_EVENTS = [
    # Date           Change(bps)  direction  Rate_after  Stance
    ("2014-01-28",   -25,         -1,         7.75,      "accommodative"),
    ("2014-06-03",   +25,         +1,         8.00,      "hawkish"),
    ("2015-01-15",   -25,         -1,         7.75,      "accommodative"),
    ("2015-03-04",   -25,         -1,         7.50,      "accommodative"),
    ("2015-09-29",   -50,         -1,         6.75,      "accommodative"),
    ("2016-04-05",   -25,         -1,         6.50,      "accommodative"),
    ("2018-06-06",   +25,         +1,         6.25,      "neutral"),
    ("2018-08-01",   +25,         +1,         6.50,      "neutral"),
    ("2019-02-07",   -25,         -1,         6.25,      "neutral"),
    ("2019-04-04",   -25,         -1,         6.00,      "accommodative"),
    ("2019-06-06",   -25,         -1,         5.75,      "accommodative"),
    ("2019-08-07",   -35,         -1,         5.40,      "accommodative"),
    ("2019-10-04",   -25,         -1,         5.15,      "accommodative"),
    ("2020-03-27",   -75,         -1,         4.40,      "accommodative"),  # COVID emergency
    ("2020-05-22",   -40,         -1,         4.00,      "accommodative"),  # COVID follow-up
    ("2022-05-04",   +40,         +1,         4.40,      "withdrawal"),     # inflation shock
    ("2022-06-08",   +50,         +1,         4.90,      "withdrawal"),
    ("2022-08-05",   +50,         +1,         5.40,      "withdrawal"),
    ("2022-09-30",   +50,         +1,         5.90,      "withdrawal"),
    ("2022-12-07",   +35,         +1,         6.25,      "withdrawal"),
    ("2023-02-08",   +25,         +1,         6.50,      "withdrawal"),
    ("2024-02-08",    0,           0,         6.50,      "neutral"),        # first hold after cycle
    ("2025-02-07",   -25,         -1,         6.25,      "accommodative"),  # FY26 easing start
    ("2025-04-09",   -25,         -1,         6.00,      "accommodative"),
]

def get_events_df() -> pd.DataFrame:
    df = pd.DataFrame(
        RBI_EVENTS,
        columns=["date", "change_bps", "direction", "rate_after", "stance"]
    )
    df["date"] = pd.to_datetime(df["date"])
    df["rate_before"] = df["rate_after"] - df["change_bps"] / 100
    df["cycle"] = df["direction"].map({+1: "Hike", -1: "Cut", 0: "Hold"})
    df = df[df["direction"] != 0].copy()   # keep only change events
    df = df.sort_values("date").reset_index(drop=True)
    return df

if __name__ == "__main__":
    print(get_events_df().to_string())
