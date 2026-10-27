# Getting data in

One CSV per instrument in this folder, named `<SYMBOL>_<timeframe>.csv`, with **UTC** timestamps:

```
timestamp,open,high,low,close,volume
2018-01-02 00:00:00,1.20061,1.20089,1.20055,1.20077,142
2018-01-02 00:05:00,1.20077,1.20081,1.20062,1.20066,98
```

`volume` is optional and nothing in this repository uses it. The four price columns are required.

No data is included in this repository; it is not ours to redistribute.

## The eighteen files

The symbol and timeframe for each come from `UNIVERSE` at the top of `src/data.py`, and the
filename is `f"{symbol}_{tf}.csv"`:

| class | files |
|---|---|
| indices, 1m | `NAS100_USD_1m.csv`, `SPX500_USD_1m.csv`, `US30_USD_1m.csv`, `US2000_USD_1m.csv`, `DE30_EUR_1m.csv` |
| index (Asia), 5m | `JP225_USD_5m.csv` |
| metal, 1m | `XAU_USD_1m.csv` |
| crypto, 1m | `BTC_USD_1m.csv`, `ETH_USD_1m.csv` |
| FX majors, 5m | `EUR_USD_5m.csv`, `GBP_USD_5m.csv`, `USD_JPY_5m.csv`, `USD_CAD_5m.csv`, `USD_CHF_5m.csv`, `USD_SEK_5m.csv` |
| FX crosses, 5m | `GBP_JPY_5m.csv`, `GBP_AUD_5m.csv`, `GBP_NZD_5m.csv` |

Edit `UNIVERSE` rather than renaming your files if a different timeframe is what you have. The
code does not care which timeframe a panel is built from — but see the warning below, because
the *feed* very much does.

The study used a retail broker's historical API, 2018-01-01 → 2026-05-21, one instrument at a
time. Any source with the same shape works.

## The thing that will break your reproduction

**Check whether your feed changes what a "day" contains, somewhere in the middle of your
sample.** This is the single most important instruction in this file, because it is what §0 of
the report is about and it is invisible unless you look for it.

Every one of the six index feeds used here switches from regular-trading-hours to near-24-hour in
late 2025 — Nasdaq goes from 390 bars a day to 1,380. Before that switch those feeds contain no
Asia or London data at all, so a session table pooled across the boundary silently compares 165
days against 2,163.

The diagnostic is three lines and it is the first thing `report.py` does:

```python
import pandas as pd, sys; sys.path.insert(0, "src")
from data import load_utc
d = load_utc("NAS100_USD")
print(d.resample("1D").size().groupby(d.resample("1D").size().index.year).median())
```

If the yearly medians are not flat — `report.py` flags anything above a 1.25 ratio as
`REGIME CHANGE` — you cannot pool sessions across the break, and neither could we.

## Two conventions worth knowing before you read any number

**The day runs 17:00 ET → 17:00 ET**, labelled by the end date. That is the convention used across
the rest of the programme this came from, so the numbers are comparable with work already done.
It is not special, and if you trade a different boundary you should measure that one — but pick
one and keep it.

**A second day definition, `day_srv`, assumes an EET/EEST broker clock** and has **not** been
pinned against a live terminal. It is built and flagged rather than silently trusted. Until you
check it against your own broker, read the `day_et` layer.

## Checking it loaded correctly

```bash
python -I src/data.py
```

That prints an inventory of what is present and then exercises the seal guard: nine instruments
held back for out-of-sample work must *raise* rather than load, and the script says so.

Then build one instrument and look at it before building eighteen:

```bash
python -I src/build_panels.py EUR_USD
```

The log line gives bars, days, the health gate the instrument earned, and its coverage
percentage. Coverage well under 95% on a 24-hour feed usually means missing history rather than a
bad gate — but on an RTH feed it may mean the gate is wrong for that instrument, which is the
second defect in the report's §0. The gate is relative to each instrument's own median bar count
for exactly that reason.

A validation worth repeating, because it is the one that caught an error in the spec: the two
partition identities (`share_path` and `share_ext` summing exactly over the exclusive blocks)
hold to 1e-9 on 100% of days. Session **ranges** do not sum to the day's range and cannot —
they came out at 2.03× on EUR_USD. If your `share_ext` does not telescope to high − low, the
blocks are not tiling your day.
