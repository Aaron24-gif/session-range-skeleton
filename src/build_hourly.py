"""Hourly panel: instrument x day x hour-from-day-start.

Independent of build_panels.py so adding it costs no rebuild of the daily/session
layers. Gives the full intraday shape, and makes the 3/6/9 question a query instead
of a bespoke study.

Run:  python -I src/build_hourly.py [SYMBOL ...]   |   --all
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data as CL
from build_panels import prepare, OUT


def hourly_panel(f: pd.DataFrame, symbol: str, daykey: str) -> pd.DataFrame:
    d = f.copy()
    # hour index 1..24 measured from the day's own start, so it is comparable
    # across both day definitions and across DST.
    start = d.groupby(daykey)["ts"].transform("first")
    d["hr"] = (((d["ts"] - start).dt.total_seconds() // 3600) + 1).astype(int)
    d = d[(d["hr"] >= 1) & (d["hr"] <= 24)]

    g = d.groupby([daykey, "hr"])
    H = pd.DataFrame({
        "open": g["open"].first(), "high": g["high"].max(),
        "low": g["low"].min(), "close": g["close"].last(),
        "path_pts": g["absdiff"].sum(), "nbars": g.size(),
    }).reset_index().rename(columns={daykey: "day"})

    H["range_pts"] = H["high"] - H["low"]
    pip = CL.PIP.get(symbol)
    H["range_pips"] = H["range_pts"] / pip if pip else np.nan

    H = H.sort_values(["day", "hr"])
    gb = H.groupby("day")
    # strictly causal running extremes: what the day had built BEFORE this hour
    prior_hi = gb["high"].cummax().shift(1)
    prior_lo = gb["low"].cummin().shift(1)
    firstmask = H["hr"] == H.groupby("day")["hr"].transform("min")
    prior_hi = prior_hi.mask(firstmask)
    prior_lo = prior_lo.mask(firstmask)

    ext_up = (H["high"] - prior_hi).clip(lower=0).fillna(0.0)
    ext_dn = (prior_lo - H["low"]).clip(lower=0).fillna(0.0)
    H["ext_pts"] = np.where(firstmask, H["high"] - H["low"], ext_up + ext_dn)

    day_ext = H.groupby("day")["ext_pts"].transform("sum")
    day_path = H.groupby("day")["path_pts"].transform("sum")
    H["share_ext"] = np.where(day_ext > 0, H["ext_pts"] / day_ext, np.nan)
    H["share_path"] = np.where(day_path > 0, H["path_pts"] / day_path, np.nan)

    H["sets_day_high"] = False
    H["sets_day_low"] = False
    dh = H.groupby("day")["high"].transform("max")
    dl = H.groupby("day")["low"].transform("min")
    H["sets_day_high"] = np.isclose(H["high"], dh)
    H["sets_day_low"] = np.isclose(H["low"], dl)

    H["symbol"] = symbol
    H["cls"] = CL.CLASS[symbol]
    H["daykey"] = daykey
    return H


def build(symbol: str) -> dict:
    t0 = time.time()
    f = prepare(symbol)
    parts = [hourly_panel(f, symbol, dk) for dk in ("day_et", "day_srv")]
    H = pd.concat(parts, ignore_index=True)
    H.to_parquet(OUT / f"hourly_{symbol}.parquet", index=False)
    return {"symbol": symbol, "rows": len(H), "secs": round(time.time() - t0, 1)}


if __name__ == "__main__":
    args = sys.argv[1:]
    syms = list(CL.UNIVERSE) if (not args or args[0] == "--all") else args
    for s in syms:
        try:
            st = build(s)
            print(f"{s:12s} rows={st['rows']:>8,}  {st['secs']}s", flush=True)
        except Exception as e:
            print(f"{s:12s} FAILED: {type(e).__name__}: {e}", flush=True)
