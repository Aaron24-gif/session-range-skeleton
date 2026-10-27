"""Build the skeleton panels: instrument x day, and instrument x day x session.

Descriptive only. No signal, no entry, no selection. See SKELETON_SPEC.md.

Run:  python -I src/build_panels.py [SYMBOL ...]
      python -I src/build_panels.py --all

Panels are written to `panels/` (override with the SKELETON_PANELS environment variable), one
parquet per instrument so a long run is resumable.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# python -I strips the script dir from sys.path; restore it for the local import
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import data as CL

OUT = Path(os.environ.get("SKELETON_PANELS", HERE.parent / "panels"))
OUT.mkdir(parents=True, exist_ok=True)

# ET minute-of-day boundaries. 17:00=1020  03:00=180  08:00=480  11:30=690
# Exclusive blocks tile the full 24h with no gap, so share_of_day sums to 1.
EXCLUSIVE = {
    "Asia":     lambda m: (m >= 1020) | (m < 180),   # 17:00 -> 03:00 (Sydney+Tokyo)
    "LDN_only": lambda m: (m >= 180) & (m < 480),    # 03:00 -> 08:00
    "Overlap":  lambda m: (m >= 480) & (m < 690),    # 08:00 -> 11:30
    "NY_only":  lambda m: (m >= 690) & (m < 1020),   # 11:30 -> 17:00
}
# Real (overlapping) sessions. Shares sum to >100% by construction.
OVERLAPPING = {
    "Asia_s":   lambda m: (m >= 1020) | (m < 180),
    "London_s": lambda m: (m >= 180) & (m < 690),    # 03:00 -> 11:30
    "NewYork_s": lambda m: (m >= 480) & (m < 1020),  # 08:00 -> 17:00
}
SESSIONS = {**EXCLUSIVE, **OVERLAPPING}
# chronological order within the 17:00-anchored day, for "extends what came before"
EXCL_ORDER = ["Asia", "LDN_only", "Overlap", "NY_only"]

# nominal duration in hours. REQUIRED: without it a 10h session trivially
# outranks a 3.5h one on every absolute measure, which is duration, not activity.
SESSION_HOURS = {"Asia": 10.0, "LDN_only": 5.0, "Overlap": 3.5, "NY_only": 5.5,
                 "Asia_s": 10.0, "London_s": 8.5, "NewYork_s": 9.0}


def _wilder_atr(h, l, c, period=14):
    h, l, c = np.asarray(h, float), np.asarray(l, float), np.asarray(c, float)
    tr = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]),
                                              np.abs(l[1:] - c[:-1])))
    tr = np.concatenate([[h[0] - l[0]], tr])
    atr = np.full(len(tr), np.nan)
    if len(tr) < period:
        return atr
    atr[period - 1] = tr[:period].mean()
    for i in range(period, len(tr)):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr


def _sma_atr(h, l, c, n=20):
    h, l, c = np.asarray(h, float), np.asarray(l, float), np.asarray(c, float)
    pc = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return pd.Series(tr).rolling(n).mean().values


def prepare(symbol: str) -> pd.DataFrame:
    """Cached UTC bars -> ET-aware frame with both day keys and session labels."""
    df = CL.load_utc(symbol)
    et = df.tz_convert("America/New_York")

    # minute-of-day in ET, from the tz-AWARE index so DST is handled by the
    # tz database rather than by arithmetic on a naive index.
    mod = et.index.hour * 60 + et.index.minute

    out = pd.DataFrame({
        "open": df["open"].to_numpy(), "high": df["high"].to_numpy(),
        "low": df["low"].to_numpy(), "close": df["close"].to_numpy(),
    }, index=et.index)

    # primary day: 17:00 ET -> 17:00 ET, labelled by END date (house convention,
    # the convention used across the rest of the programme: (index + 7h).normalize()).
    out["day_et"] = (et.index + pd.Timedelta(hours=7)).normalize().tz_localize(None)

    # secondary day: broker server calendar day. EET/EEST = UTC+2/+3 with EU DST,
    # the standard MT-broker clock. MUST be pinned against the live terminal
    # before these numbers are trusted; day_et is unaffected either way.
    out["day_srv"] = df.index.tz_convert("Europe/Helsinki").normalize().tz_localize(None)

    # bar-to-bar travel, computed once; summed per group later. Vectorised
    # because a per-group .apply costs ~2200 python calls per session per daykey.
    out["absdiff"] = out["close"].diff().abs()
    out["ts"] = et.index
    out["mod"] = mod
    for name, fn in SESSIONS.items():
        out[name] = fn(mod)
    return out


def daily_panel(f: pd.DataFrame, symbol: str, daykey: str) -> pd.DataFrame:
    g = f.groupby(daykey)
    D = pd.DataFrame({
        "open": g["open"].first(), "high": g["high"].max(),
        "low": g["low"].min(), "close": g["close"].last(),
        "nbars": g.size(),
    })
    D.index.name = "day"

    # when the extremes formed, in minutes from the day's first bar
    hi_at = g["high"].idxmax()
    lo_at = g["low"].idxmin()
    first = g["ts"].first()
    D["hi_minute"] = (hi_at - first).dt.total_seconds().div(60).values
    D["lo_minute"] = (lo_at - first).dt.total_seconds().div(60).values
    D["hi_first"] = (D["hi_minute"] < D["lo_minute"])

    D["range_pts"] = D["high"] - D["low"]
    D["body_pts"] = (D["close"] - D["open"]).abs()
    D["efficiency"] = np.where(D["range_pts"] > 0, D["body_pts"] / D["range_pts"], np.nan)
    D["range_pct"] = D["range_pts"] / D["open"]

    pip = CL.PIP.get(symbol)
    D["range_pips"] = D["range_pts"] / pip if pip else np.nan

    D["atr14"] = _wilder_atr(D["high"].values, D["low"].values, D["close"].values, 14)
    D["atr20"] = _sma_atr(D["high"].values, D["low"].values, D["close"].values, 20)
    # causal normalisers: shift so a day is never divided by its own range
    D["atr14_prior"] = D["atr14"].shift(1)
    D["atr20_prior"] = D["atr20"].shift(1)
    D["range_atr"] = D["range_pts"] / D["atr20_prior"]

    D["prior_range_pts"] = D["range_pts"].shift(1)
    D["prior_range_atr"] = D["range_atr"].shift(1)
    D["gap_pts"] = D["open"] - D["close"].shift(1)

    # data-health gate, inherited from the rest of the programme: keeps a 390-bar RTH index
    # feed from being rejected by a gold-calibrated 800-bar threshold.
    wd = D[D.index.dayofweek < 5]["nbars"]
    med = float(np.median(wd.to_numpy())) if len(wd) >= 5 else np.nan
    # The 150-bar floor was calibrated for 24h feeds and binds only when median
    # < 259 bars/day. On JP225 (median 60, an RTH-only Tokyo feed) it rejected
    # 92.4% of days as "low coverage" when the feed was in fact complete. The
    # gate must be relative to the instrument's own typical day.
    gate = int(max(20, round(0.58 * med))) if med == med else 20
    D["coverage_ok"] = D["nbars"] >= gate

    D["symbol"] = symbol
    D["cls"] = CL.CLASS[symbol]
    D["daykey"] = daykey
    D["dow"] = D.index.dayofweek
    D["month"] = D.index.month
    D["year"] = D.index.year
    D.attrs["gate"] = gate
    D.attrs["median_bars"] = med
    return D.reset_index()


def session_panel(f: pd.DataFrame, D: pd.DataFrame, symbol: str,
                  daykey: str) -> pd.DataFrame:
    dref = D.set_index("day")
    pip = CL.PIP.get(symbol)
    rows = []

    for name in SESSIONS:
        sub = f[f[name]]
        if not len(sub):
            continue
        g = sub.groupby(daykey)
        S = pd.DataFrame({
            "open": g["open"].first(), "high": g["high"].max(),
            "low": g["low"].min(), "close": g["close"].last(),
            "nbars": g.size(),
        })
        S.index.name = "day"

        hi_at = g["high"].idxmax()
        lo_at = g["low"].idxmin()
        f0 = g["ts"].first()
        f1 = g["ts"].last()
        span = (f1 - f0).dt.total_seconds().replace(0, np.nan)
        S["hi_frac"] = ((hi_at - f0).dt.total_seconds() / span).values
        S["lo_frac"] = ((lo_at - f0).dt.total_seconds() / span).values

        S["range_pts"] = S["high"] - S["low"]
        S["range_pips"] = S["range_pts"] / pip if pip else np.nan
        S["efficiency"] = np.where(S["range_pts"] > 0,
                                   (S["close"] - S["open"]).abs() / S["range_pts"],
                                   np.nan)
        # path length = total distance travelled bar to bar. Unlike range this IS
        # additive over time, so share_path genuinely partitions the day.
        S["path_pts"] = g["absdiff"].sum()
        S["hours"] = SESSION_HOURS[name]
        S["range_per_hr"] = S["range_pts"] / S["hours"]
        S["path_per_hr"] = S["path_pts"] / S["hours"]

        j = S.join(dref[["high", "low", "range_pts", "atr20_prior", "coverage_ok"]],
                   rsuffix="_day", how="left")
        # NOT a partition: sub-period ranges overlap the day's range and their sum
        # always exceeds it. Read as "this session spans X% of the day's range".
        S["range_vs_day"] = np.where(j["range_pts_day"] > 0,
                                     j["range_pts"] / j["range_pts_day"], np.nan)
        S["sets_day_high"] = np.isclose(j["high"], j["high_day"])
        S["sets_day_low"] = np.isclose(j["low"], j["low_day"])
        S["range_atr"] = j["range_pts"] / j["atr20_prior"]
        S["open_to_hi"] = (j["high"] - j["open"]) / j["atr20_prior"]
        S["open_to_lo"] = (j["open"] - j["low"]) / j["atr20_prior"]
        S["day_coverage_ok"] = j["coverage_ok"].values
        S["day_range_pts"] = j["range_pts_day"].values

        S["session"] = name
        S["exclusive"] = name in EXCLUSIVE
        rows.append(S.reset_index())

    P = pd.concat(rows, ignore_index=True)

    # "did this block extend what the day had already built?" -- running max/min
    # over the EXCLUSIVE blocks only, in chronological order, strictly causal.
    ex = P[P["exclusive"]].copy()
    ex["ord"] = ex["session"].map({s: i for i, s in enumerate(EXCL_ORDER)})
    ex = ex.sort_values(["day", "ord"])
    gb = ex.groupby("day")
    prior_hi = gb["high"].cummax().shift(1)
    prior_lo = gb["low"].cummin().shift(1)
    # shift(1) leaks across the day boundary; blank the first block of each day
    firstmask = ex["ord"] == 0
    prior_hi = prior_hi.mask(firstmask)
    prior_lo = prior_lo.mask(firstmask)
    ex["prior_day_hi"] = prior_hi
    ex["prior_day_lo"] = prior_lo
    ex["extends_prior_hi"] = ex["high"] > ex["prior_day_hi"]
    ex["extends_prior_lo"] = ex["low"] < ex["prior_day_lo"]
    ex["reverted_after_hi"] = ex["extends_prior_hi"] & (ex["close"] < ex["prior_day_hi"])
    ex["reverted_after_lo"] = ex["extends_prior_lo"] & (ex["close"] > ex["prior_day_lo"])

    # RANGE-BUILD CONTRIBUTION -- the one decomposition that exactly partitions the
    # day's range. First block contributes its own range; every later block
    # contributes only what it added beyond the running extremes. The sum
    # telescopes to (day_hi - day_lo) identically.
    first = ex["ord"] == 0
    ext_up = (ex["high"] - ex["prior_day_hi"]).clip(lower=0).fillna(0.0)
    ext_dn = (ex["prior_day_lo"] - ex["low"]).clip(lower=0).fillna(0.0)
    ex["ext_pts"] = np.where(first, ex["high"] - ex["low"], ext_up + ext_dn)
    ex["share_ext"] = np.where(ex["day_range_pts"] > 0,
                               ex["ext_pts"] / ex["day_range_pts"], np.nan)
    # travel share: additive because path length is additive
    day_path = ex.groupby("day")["path_pts"].transform("sum")
    ex["share_path"] = np.where(day_path > 0, ex["path_pts"] / day_path, np.nan)
    # >1 means the session expanded the range efficiently relative to how far it
    # travelled: a breakout signature. <1 means churn inside existing range.
    ex["breakout_index"] = ex["share_ext"] / ex["share_path"]
    # The first block of the day contributes its WHOLE range as extension by
    # construction (nothing precedes it), which inflates its ratio and makes it
    # incomparable with later blocks. A structurally meaningless number is worse
    # than a missing one, so it is blanked rather than reported.
    ex.loc[first, "breakout_index"] = np.nan

    addcols = ["extends_prior_hi", "extends_prior_lo",
               "reverted_after_hi", "reverted_after_lo",
               "ext_pts", "share_ext", "share_path", "breakout_index"]
    P = P.merge(ex[["day", "session"] + addcols], on=["day", "session"], how="left")

    P["symbol"] = symbol
    P["cls"] = CL.CLASS[symbol]
    P["daykey"] = daykey
    return P


def build(symbol: str) -> dict:
    t0 = time.time()
    f = prepare(symbol)
    stats = {"symbol": symbol, "bars": len(f),
             "first": str(f.index[0].date()), "last": str(f.index[-1].date())}
    dparts, sparts = [], []
    for daykey in ("day_et", "day_srv"):
        D = daily_panel(f, symbol, daykey)
        S = session_panel(f, D, symbol, daykey)
        dparts.append(D)
        sparts.append(S)
        if daykey == "day_et":
            stats["days"] = len(D)
            stats["gate"] = D.attrs["gate"]
            stats["median_bars"] = D.attrs["median_bars"]
            stats["coverage_ok_pct"] = round(100 * D["coverage_ok"].mean(), 1)
    Dall = pd.concat(dparts, ignore_index=True)
    Sall = pd.concat(sparts, ignore_index=True)
    Dall.to_parquet(OUT / f"daily_{symbol}.parquet", index=False)
    Sall.to_parquet(OUT / f"session_{symbol}.parquet", index=False)
    stats["secs"] = round(time.time() - t0, 1)
    return stats


if __name__ == "__main__":
    args = sys.argv[1:]
    syms = list(CL.UNIVERSE) if (not args or args[0] == "--all") else args
    log = []
    for s in syms:
        try:
            st = build(s)
            log.append(st)
            print(f"{s:12s} bars={st['bars']:>9,} days={st['days']:>5,} "
                  f"gate={st['gate']:>4} cov={st['coverage_ok_pct']:>5}% "
                  f"{st['first']}..{st['last']}  {st['secs']}s", flush=True)
        except Exception as e:
            print(f"{s:12s} FAILED: {type(e).__name__}: {e}", flush=True)
    if log:
        pd.DataFrame(log).to_csv(OUT / "build_log.csv", index=False)
        print(f"\n{len(log)}/{len(syms)} built -> {OUT}")
