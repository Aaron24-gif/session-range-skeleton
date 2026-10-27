"""The data seam. One CSV per instrument in `data/`, UTC timestamps:

    timestamp,open,high,low,close,volume
    2018-01-02 00:00:00,1.20061,1.20089,1.20055,1.20077,142

No data is included in this repository; it is not ours to redistribute. `data/HOWTO.md` has the
shape, the sources this was built from, and the one thing that will otherwise break your
reproduction.

WHY THIS MODULE IS SHAPED LIKE THIS. The original loader read a local pickle cache and was written
specifically so that it **could not** download. Its vendor client returns a cached chunk if the
exact chunk file exists and otherwise hits the network, keyed on md5(symbol|start|end|timeframe) —
so a cache hit requires requesting the *same* chunk boundaries that were originally fetched, and
those vary per instrument. Any boundary mismatch would silently download a few hundred megabytes.
On a metered connection a loader that *might* fetch is not acceptable for an 18-instrument sweep.

This version reads plain CSVs instead, and keeps the two properties that mattered:

- **It cannot reach the network.** There is no client here to import.
- **It cannot reach the sealed period.** `DEV_MAX` truncates every series, and the instruments
  reserved for out-of-sample work raise rather than load.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"

# Instruments held back for out-of-sample work in the programme this came from. Loading one is a
# release decision, not a default, so it raises rather than warns.
SEALED = {"XAG_USD", "XPT_USD", "XPD_USD", "XCU_USD", "BCO_USD",
          "WTICO_USD", "NATGAS_USD", "USD_MXN", "USD_ZAR"}

# Hard development boundary. Several series run into Aug 2026; everything from 2026-05-22 is
# sealed and never loaded.
DEV_MAX = pd.Timestamp("2026-05-21 23:59:59", tz="UTC")

# pip size, FX only. Gold, indices and crypto are quoted in POINTS and get None — a faked pip
# number for those is worse than no number.
PIP = {
    "EUR_USD": 0.0001, "GBP_USD": 0.0001, "USD_CAD": 0.0001,
    "USD_CHF": 0.0001, "USD_SEK": 0.0001, "GBP_AUD": 0.0001,
    "GBP_NZD": 0.0001, "USD_JPY": 0.01, "GBP_JPY": 0.01,
}

# instrument -> the timeframe the panels are built from. 1m where it was held, else 5m.
UNIVERSE = {
    "NAS100_USD": "1m", "SPX500_USD": "1m", "US30_USD": "1m",
    "US2000_USD": "1m", "DE30_EUR": "1m", "XAU_USD": "1m",
    "BTC_USD": "1m", "ETH_USD": "1m",
    "JP225_USD": "5m",
    "EUR_USD": "5m", "GBP_USD": "5m", "USD_JPY": "5m", "USD_CAD": "5m",
    "USD_CHF": "5m", "USD_SEK": "5m", "GBP_JPY": "5m", "GBP_AUD": "5m",
    "GBP_NZD": "5m",
}

CLASS = {
    **{k: "index" for k in ("NAS100_USD", "SPX500_USD", "US30_USD",
                            "US2000_USD", "DE30_EUR", "JP225_USD")},
    "XAU_USD": "metal",
    **{k: "crypto" for k in ("BTC_USD", "ETH_USD")},
    **{k: "fx_major" for k in ("EUR_USD", "GBP_USD", "USD_JPY",
                               "USD_CAD", "USD_CHF", "USD_SEK")},
    **{k: "fx_cross" for k in ("GBP_JPY", "GBP_AUD", "GBP_NZD")},
}

COLS = ["open", "high", "low", "close", "volume"]


class SealViolation(RuntimeError):
    pass


def path_for(symbol: str, tf: str | None = None) -> Path:
    tf = tf or UNIVERSE[symbol]
    return DATA / f"{symbol}_{tf}.csv"


def load_utc(symbol: str, tf: str | None = None,
             end_max: pd.Timestamp = DEV_MAX) -> pd.DataFrame:
    """Full history for one instrument in UTC, truncated at the development boundary.

    Raises if nothing is there. It will NOT fall back to a download, because there is nothing
    here to download with.
    """
    if symbol in SEALED:
        raise SealViolation(
            f"{symbol} is held back for out-of-sample work; loading it needs a release decision"
        )
    tf = tf or UNIVERSE[symbol]
    p = path_for(symbol, tf)
    if not p.exists():
        raise FileNotFoundError(f"{p} not found - see data/HOWTO.md")

    d = pd.read_csv(p, parse_dates=["timestamp"]).set_index("timestamp")
    d = d[~d.index.duplicated(keep="first")].sort_index()
    if d.index.tz is None:
        d.index = d.index.tz_localize("UTC")
    else:
        d.index = d.index.tz_convert("UTC")
    d = d[d.index <= end_max]
    keep = [c for c in COLS if c in d.columns]
    if not {"open", "high", "low", "close"} <= set(keep):
        raise ValueError(f"{p}: need open/high/low/close columns, found {list(d.columns)}")
    assert d.index.max() <= DEV_MAX, "reached the sealed out-of-sample period"
    return d[keep]


def summary() -> pd.DataFrame:
    """Inventory of what can actually be built from what is in `data/`."""
    rows = []
    for sym, tf in UNIVERSE.items():
        p = path_for(sym, tf)
        rows.append({"symbol": sym, "cls": CLASS[sym], "tf": tf,
                     "file": p.name, "status": "ok" if p.exists() else "MISSING"})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(summary().to_string(index=False))
    print()
    for s in sorted(SEALED):
        try:
            load_utc(s)
            print(f"  FAIL: {s} was not refused")
        except SealViolation:
            pass
        except FileNotFoundError:
            print(f"  FAIL: {s} got as far as looking for a file")
    print(f"seal guard: all {len(SEALED)} refused")
