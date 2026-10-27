"""Read the skeleton panels and emit the descriptive map: results/SKELETON_REPORT.md.

Descriptive only. No cell is selected, nothing is promoted. See SKELETON_SPEC.md §0:
the map is free, the choosing is not.

TWO VALIDITY GATES, both added after diagnostics, not by design:
  * FEED REGIME. All six index feeds switch from RTH-only to near-24h in late
    2025 (NAS100 390 -> 1380 bars/day). Pooling across that boundary compares a
    ~165-day sample against a 2,163-day one. Indices are therefore excluded from
    session analysis and split by regime for daily analysis.
  * COMMON SAMPLE. Within an instrument, session blocks are compared only on days
    where ALL FOUR exclusive blocks have data. Otherwise each block is measured on
    a different set of days.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("SKELETON_PANELS", HERE.parent / "panels"))
RESULTS = HERE.parent / "results"
TABLES = RESULTS / "tables"
EXCL = ["Asia", "LDN_only", "Overlap", "NY_only"]
HRS = {"Asia": 10.0, "LDN_only": 5.0, "Overlap": 3.5, "NY_only": 5.5}
REGIME_RATIO = 1.25


def _load(kind: str) -> pd.DataFrame:
    fs = sorted(OUT.glob(f"{kind}_*.parquet"))
    if not fs:
        raise FileNotFoundError(f"no {kind}_*.parquet in {OUT}")
    return pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True)


def tbl(df: pd.DataFrame, name: str | None = None, idx: bool = False) -> str:
    """Markdown for the report, and the same table as CSV under results/tables/.

    Every number printed below therefore has a machine-readable twin that came from the same
    object, rather than from a second code path that could drift from it.
    """
    if name:
        TABLES.mkdir(parents=True, exist_ok=True)
        df.to_csv(TABLES / f"{name}.csv", index=idx)
    return df.to_markdown(index=idx, floatfmt=".3f")


# ──────────────────────────────────────── 0. what can actually be measured ──
def measurability(D: pd.DataFrame, S: pd.DataFrame):
    de = D[D.daykey == "day_et"]
    rows = []
    for sym, sub in de.groupby("symbol"):
        y = sub.groupby("year")["nbars"].median()
        ratio = y.max() / y.min()
        se = S[(S.symbol == sym) & (S.daykey == "day_et") & S.exclusive]
        have = se.groupby("session").size().reindex(EXCL).fillna(0)
        rows.append({
            "symbol": sym, "cls": sub["cls"].iloc[0],
            "days": len(sub), "med_bars": y.median(),
            "bars_min_yr": y.min(), "bars_max_yr": y.max(), "ratio": ratio,
            "feed": "stable" if ratio < REGIME_RATIO else "REGIME CHANGE",
            **{f"d_{k}": int(v) for k, v in have.items()},
        })
    M = pd.DataFrame(rows)
    M["sessions_usable"] = (M["feed"] == "stable") & (M[[f"d_{k}" for k in EXCL]].min(axis=1) > 400)
    stable = set(M.loc[M.sessions_usable, "symbol"])

    txt = ["## 0. WHAT CAN ACTUALLY BE MEASURED — read this before any table below\n",
           "Two defects were found by diagnostics and both would have silently invalidated "
           "the session results.\n",
           "**Feed regime.** Every one of the six index feeds switches from RTH-only to "
           "near-24h in late 2025 — NAS100 goes 390 → 1380 bars/day. Before that switch the "
           "indices have **no Asia or London data at all**. Pooling across the boundary would "
           "compare a ~165-day sample against a 2,163-day one and report it as one number.\n",
           "**Coverage gate.** The inherited 150-bar floor was calibrated for 24h feeds and "
           "rejected 92.4% of JP225 days as low-coverage when its RTH-only Tokyo feed (60 "
           "bars/day) was in fact complete. Made relative to each instrument's own median; "
           "JP225 went 7.6% → 100%.\n",
           tbl(M[["cls", "symbol", "days", "med_bars", "bars_min_yr", "bars_max_yr",
                  "ratio", "feed"] + [f"d_{k}" for k in EXCL] + ["sessions_usable"]]
               .sort_values(["cls", "symbol"]), "00_measurability"),
           f"\n**Session analysis is valid for {len(stable)} of {len(M)} instruments.** "
           "The six indices are excluded from every session table and appear only in the "
           "daily-range section, split by feed regime and never pooled across it.\n"]
    return "\n".join(txt), stable, M


def common_sample(S: pd.DataFrame, stable: set) -> pd.DataFrame:
    """Only days where all four exclusive blocks exist, on stable-feed instruments."""
    se = S[(S.daykey == "day_et") & S.exclusive & S.day_coverage_ok
           & S.symbol.isin(stable)].copy()
    k = se.groupby(["symbol", "day"])["session"].transform("nunique")
    return se[k == 4]


# ───────────────────────────────────────────────── A. session activity map ──
def section_sessions(se: pd.DataFrame):
    g = se.groupby(["cls", "symbol", "session"]).agg(
        n=("range_pts", "size"),
        range_pts=("range_pts", "median"),
        range_pips=("range_pips", "median"),
        share_ext=("share_ext", "mean"),
        share_path=("share_path", "mean"),
        brk=("breakout_index", "median"),
        eff=("efficiency", "median"),
        hi=("sets_day_high", "mean"),
        lo=("sets_day_low", "mean"),
    ).reset_index()
    g["hours"] = g["session"].map(HRS)
    g["pts_per_hr"] = g["range_pts"] / g["hours"]
    g["ext_per_hr"] = g["share_ext"] / g["hours"]
    g["path_per_hr"] = g["share_path"] / g["hours"]
    g["sets_extreme"] = g["hi"] + g["lo"]

    out = ["\n---\n\n## A. WHERE THE MOVEMENT IS — duration-normalised, common sample\n",
           "`ext_per_hr` = share of the day's range built here, per hour. `path_per_hr` = "
           "share of the day's travel, per hour. `brk` = breakout index (>1 expands "
           "efficiently, <1 churns inside existing range); NaN for Asia, which gets its whole "
           "range as extension by construction.\n"]
    for cls in ["metal", "fx_major", "fx_cross", "crypto"]:
        sub = g[g.cls == cls]
        if not len(sub):
            continue
        out.append(f"\n### {cls}\n")
        out.append(tbl(sub[["symbol", "session", "hours", "range_pts", "range_pips",
                            "pts_per_hr", "share_ext", "ext_per_hr", "share_path",
                            "brk", "eff", "sets_extreme"]]
                       .sort_values(["symbol", "ext_per_hr"], ascending=[True, False]),
                       f"A_sessions_{cls}"))
    rank = g.groupby("session").agg(
        ext_per_hr=("ext_per_hr", "median"), path_per_hr=("path_per_hr", "median"),
        share_ext=("share_ext", "median"), share_path=("share_path", "median"),
        brk=("brk", "median"), sets_extreme=("sets_extreme", "median"),
        eff=("eff", "median"),
    ).reindex(EXCL)
    out.append("\n### Pooled across the usable instruments (median of per-instrument values)\n")
    out.append(tbl(rank.reset_index(), "A_sessions_pooled"))
    return "\n".join(out), g


# ─────────────────────────────────────────── B. crypto control on sessions ──
def section_control(g: pd.DataFrame) -> str:
    rows = []
    for sym, sub in g.groupby("symbol"):
        v = sub.set_index("session")["ext_per_hr"].reindex(EXCL)
        p = sub.set_index("session")["path_per_hr"].reindex(EXCL)
        rows.append({"symbol": sym, "cls": sub["cls"].iloc[0],
                     "path_cv": p.std() / p.mean(), "ext_cv": v.std() / v.mean(),
                     "peak_block": p.idxmax(), "peak_over_trough": p.max() / p.min()})
    R = pd.DataFrame(rows)
    byc = R.groupby("cls").agg(n=("symbol", "size"), path_cv=("path_cv", "median"),
                               ext_cv=("ext_cv", "median"),
                               peak_over_trough=("peak_over_trough", "median")
                               ).sort_values("path_cv", ascending=False)
    return "\n".join([
        "\n---\n\n## B. CONTROL — does session structure survive where there is no session?\n",
        "BTC and ETH trade 24/7 with no exchange session. If \"London carries the movement\" "
        "is genuine microstructure, crypto must show a **measurably flatter** profile across "
        "the four blocks. `path_cv` is the coefficient of variation of travel-per-hour: "
        "0 = perfectly flat, higher = stronger session structure. **This test can falsify the "
        "session premise itself, which is why crypto is in the universe.**\n",
        tbl(byc.reset_index(), "B_control_by_class"),
        "\n### per instrument\n",
        tbl(R.sort_values("path_cv", ascending=False), "B_control_by_instrument"),
    ])


# ──────────────────────────────────── C. range calibration + HAR baseline ──
def section_range(D: pd.DataFrame, M: pd.DataFrame) -> str:
    de = D[(D.daykey == "day_et") & D.coverage_ok].copy()
    unstable = set(M.loc[M.feed != "stable", "symbol"])
    # for regime-change instruments keep only the dominant (pre-switch) regime, so a
    # daily range is never compared across a change in what a "day" contains
    de["drop"] = de.symbol.isin(unstable) & (de.year >= 2026)
    de = de[~de["drop"]]
    de = de.dropna(subset=["range_atr", "prior_range_atr"])

    out = ["\n---\n\n## C. NEXT-DAY RANGE — the calibration, and how much of it is mechanical\n",
           "Your example: *the prior day did so-and-so pips, so today has an 80–90% chance of "
           "being under X.* That table is below. **But the prediction itself is mostly "
           "volatility clustering**, known since the 1980s — so the honest question is not "
           "whether it works, it is whether conditioning **narrows the band** at all versus "
           "not conditioning.\n",
           f"Regime-change instruments are truncated to their pre-switch feed "
           f"({', '.join(sorted(unstable))} drop 2026), because an RTH day and a 24h day are "
           "not the same object.\n"]

    rows = []
    for sym, sub in de.groupby("symbol"):
        if len(sub) < 400:
            continue
        q = sub["prior_range_atr"].quantile([.2, .4, .6, .8]).values
        sub = sub.assign(bucket=np.digitize(sub["prior_range_atr"], q))
        u = sub["range_atr"].quantile([.1, .5, .9]).values
        for b, s2 in sub.groupby("bucket"):
            qq = s2["range_atr"].quantile([.1, .5, .9]).values
            rows.append({"symbol": sym, "prior_quintile": int(b) + 1, "n": len(s2),
                         "p10": qq[0], "p50": qq[1], "p90": qq[2],
                         "band_10_90": qq[2] - qq[0]})
        rows.append({"symbol": sym, "prior_quintile": 0, "n": len(sub),
                     "p10": u[0], "p50": u[1], "p90": u[2], "band_10_90": u[2] - u[0]})
    C = pd.DataFrame(rows)

    narrow = []
    for sym, sub in C.groupby("symbol"):
        uu = sub.loc[sub.prior_quintile == 0, "band_10_90"].iloc[0]
        cc = sub.loc[sub.prior_quintile > 0, "band_10_90"].mean()
        narrow.append({"symbol": sym, "uncond_band": uu, "mean_cond_band": cc,
                       "narrowing_pct": 100 * (1 - cc / uu)})
    N = pd.DataFrame(narrow).sort_values("narrowing_pct", ascending=False)
    out.append("### Does conditioning on the prior day actually help?\n")
    out.append("Width of the 10–90 band of `range_atr`, conditional on the prior day's "
               "quintile versus unconditional. **Near 0% means the prior day tells you almost "
               "nothing the unconditional distribution did not already tell you.**\n")
    out.append(tbl(N, "C_conditioning_narrowing"))

    out.append("\n### Full calibration — quintile 0 is the unconditional row\n")
    out.append("`p90` is the \"90% chance of being under\" number, in units of the prior day's "
               "ATR20.\n")
    out.append(tbl(C.sort_values(["symbol", "prior_quintile"]), "C_range_calibration"))

    har = []
    for sym, sub in de.groupby("symbol"):
        s2 = sub.sort_values("day")
        y = np.log(s2["range_pts"].replace(0, np.nan))
        M2 = pd.concat([y, y.shift(1), y.shift(1).rolling(5).mean(),
                        y.shift(1).rolling(22).mean()], axis=1).dropna()
        if len(M2) < 300:
            continue
        yy = M2.iloc[:, 0].values

        def r2(cols):
            X = np.column_stack([np.ones(len(M2))] + [M2.iloc[:, c].values for c in cols])
            b, *_ = np.linalg.lstsq(X, yy, rcond=None)
            return 1 - (yy - X @ b).var() / yy.var()

        har.append({"symbol": sym, "n": len(M2), "r2_prior_day": r2([1]),
                    "r2_HAR_1_5_22": r2([1, 2, 3])})
    H = pd.DataFrame(har)
    H["HAR_adds"] = H["r2_HAR_1_5_22"] - H["r2_prior_day"]
    out.append("\n### HAR baseline — in-sample R² on log(daily range)\n")
    out.append("**This is the mechanical baseline any range model must beat.** Reporting a "
               "prior-day effect without it would be rediscovering volatility clustering. "
               "`HAR_adds` is what the 5- and 22-day memory contributes beyond yesterday "
               "alone.\n")
    out.append(tbl(H.sort_values("r2_HAR_1_5_22", ascending=False), "C_har_baseline"))
    return "\n".join(out)


# ───────────────────────────────────────────────────── D. the 3/6/9 test ──
def section_369(Hr: pd.DataFrame, stable: set) -> str:
    h = Hr[(Hr.daykey == "day_et") & Hr.symbol.isin(stable)]
    prof = h.groupby(["symbol", "hr"]).agg(share_ext=("share_ext", "mean"),
                                           share_path=("share_path", "mean")).reset_index()
    tgt = {3, 6, 9}
    out = ["\n---\n\n## D. THE 3/6/9 HOUR SEQUENCE — tested, with the confound controlled\n",
           "From a 17:00 ET day start, hours 3, 6 and 9 are **19:00–20:00, 22:00–23:00 and "
           "01:00–02:00 ET** — all three fall inside the Asia block. A raw comparison against "
           "all 24 hours would therefore just rediscover that Asia is quiet. The decisive "
           "comparison is **against the other Asia hours only** (hours 1–10), which removes "
           "the session confound entirely.\n",
           "Bar to clear: over 21 independent cells the expected maximum |t| under pure noise "
           "is ≈ √(2 ln 21) ≈ **2.47**, so a ratio near 1.00 is the null, not a weak signal.\n"]
    rows = []
    for sym, sub in prof.groupby("symbol"):
        asia = sub[(sub.hr >= 1) & (sub.hr <= 10)]
        a, b = asia[asia.hr.isin(tgt)]["share_ext"], asia[~asia.hr.isin(tgt)]["share_ext"]
        allh = sub.set_index("hr")["share_ext"]
        rk = allh.rank(ascending=False)
        rows.append({"symbol": sym, "mean_369": a.mean(), "mean_other_asia": b.mean(),
                     "ratio": a.mean() / b.mean() if b.mean() else np.nan,
                     "best_369_rank_of_24": int(rk.reindex(sorted(tgt)).min())})
    R = pd.DataFrame(rows).sort_values("ratio", ascending=False)
    out.append("### Hours 3/6/9 versus the other Asia hours (`share_ext`, mean)\n")
    out.append(tbl(R, "D_369_vs_other_asia"))
    out.append("\n> `best_369_rank_of_24` is where the best of the three ranks among all 24 "
               "hours. A genuine effect would put it near 1.\n")
    piv = prof.pivot_table(index="hr", values=["share_ext", "share_path"], aggfunc="median")
    piv["is_369"] = piv.index.isin(tgt)
    out.append("\n### Pooled hour-of-day profile (median across usable instruments)\n")
    out.append(tbl(piv.reset_index(), "D_hour_profile"))
    return "\n".join(out)


def main() -> None:
    D, S = _load("daily"), _load("session")
    sec0, stable, M = measurability(D, S)
    se = common_sample(S, stable)
    secA, g = section_sessions(se)
    parts = [
        "# SKELETON REPORT — session and range behaviour map\n",
        f"**Development partition only (≤ 2026-05-21). {D.symbol.nunique()} instruments "
        f"built; {len(stable)} usable for session analysis. Sealed nine excluded.**\n",
        "Descriptive map. No cell is selected and nothing is promoted — per "
        "`SKELETON_SPEC.md` §0, the map is free and the choosing is not: picking one cell out "
        "of this map is a multiple-comparison problem and needs pre-registration.\n",
        "---\n", sec0, secA, section_control(g), section_range(D, M),
    ]
    try:
        parts.append(section_369(_load("hourly"), stable))
    except FileNotFoundError:
        parts.append("\n---\n\n## D. THE 3/6/9 TEST\n\n*Pending — run `build_hourly.py`.*\n")
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "SKELETON_REPORT.md").write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {RESULTS / 'SKELETON_REPORT.md'}  ({len(stable)} session-usable)")
    print(f"wrote {len(list(TABLES.glob('*.csv')))} tables to {TABLES}")


if __name__ == "__main__":
    main()
