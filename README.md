# Session-range skeleton — a map of where price actually moves

A descriptive measurement layer over 18 instruments and eight years: for every instrument, every
day and every session, how much of the day's range was built there, how far price travelled to
build it, and where the day's high and low formed.

**It found two defects in our own data before it measured anything, and either one would have
produced a confident, wrong answer.** That is the part worth reading first.

No strategy is here. Nothing is selected. The point of a map is that it is free; the choosing is
not, and the choosing happens somewhere else with a pre-registration attached.

---

## §0 first: two defects, both found by diagnostics

### The index feeds change what a "day" means, mid-sample

All six index feeds switch from regular-trading-hours to near-24-hour in late 2025. Nasdaq goes
from **390 bars a day to 1,380** — a factor of 3.5.

Before that switch those feeds contain **no Asia and no London data at all**. A pooled session
table across the boundary would compare a **165-day** sample against a **2,163-day** one and
report it as one number, with no warning anywhere, because both subsets are individually clean.

| | days | median bars | max yearly median | ratio | days with Asia data |
|---|---:|---:|---:|---:|---:|
| NAS100 | 2,163 | 390 | 1,380 | 3.54 | **165** |
| SPX500 | 2,163 | 390 | 1,378 | 3.54 | **165** |
| US30 | 2,163 | 390 | 1,380 | 3.54 | **165** |
| US2000 | 2,163 | 390 | 1,379 | 3.54 | **165** |
| DE30 | 2,131 | 510 | 1,221 | 2.39 | **159** |
| JP225 | 2,167 | 60 | 276 | 4.60 | 2,167 |
| EUR_USD *(for contrast)* | 2,178 | 288 | 288 | 1.00 | 2,178 |

**The six indices are therefore excluded from every session table in this repository.** They
appear only in the daily-range section, split by regime and never pooled across it. Twelve of the
eighteen instruments survive for session analysis.

### The coverage filter threw away 92.4% of good data

The inherited data-health gate was a 150-bar floor, calibrated for 24-hour feeds. Japan's feed is
a 60-bar-a-day RTH Tokyo feed, and it is **complete**. The gate rejected **92.4% of JP225 days**
as low-coverage.

Made relative to each instrument's own median bar count, JP225 went from **7.6% to 100%** usable.

A filter calibrated on one instrument and applied to another is not a filter, it is a silent
sample selection. Both defects are in the code with the reasoning attached:
`src/build_panels.py`, the `gate` comment.

---

## What the map says

### Range is not additive, and the first version of this spec was wrong about it

An early draft claimed session ranges sum to the day's range. **They cannot.** Sub-period
high−low ranges overlap the day's own range, so they always sum to more — measured at **2.03×**
on EUR_USD. The correction is in `SPEC.md` §3, left in place rather than quietly fixed.

Two decompositions genuinely do partition the day, and both were validated to 1e-9 on 100% of
days:

- **`share_path`** — session path length ÷ day path length, where path = Σ|closeₜ − closeₜ₋₁|.
  *Where the distance is travelled.* What many small trades could capture.
- **`share_ext`** — contribution to the day's final range: the first block its own range, every
  later block only what it added beyond the running extremes. Telescopes exactly to high − low.
  *Where the day's range actually gets built.* What a breakout could capture.

`breakout_index = share_ext ÷ share_path`. Above 1, a session expands the range efficiently
relative to how far it travelled. Below 1, it churns inside range that already existed.

It is **NaN for Asia**, deliberately: the first block of the day gets its whole range counted as
extension by construction, which inflates the ratio and makes it incomparable. A structurally
meaningless number is worse than a missing one.

### Duration normalisation inverts the obvious answer

A ten-hour session beats a three-and-a-half-hour one on every absolute measure. That is duration,
not activity.

Gold:

| session | hours | share of range built | **per hour** |
|---|---:|---:|---:|
| Asia | 10.0 | **51.6%** | 5.2% |
| London–NY overlap | 3.5 | 24.1% | **6.9%** |
| London only | 5.0 | 16.0% | 3.2% |
| NY only | 5.5 | 8.2% | 1.5% |

Asia builds half the day's range and is the least active hour-for-hour of the three real
sessions. The same inversion holds on every currency pair in the set. Both columns are true; they
answer different questions, and only the second one tells you where to spend attention.

### The crypto control, which could have killed the whole premise

BTC and ETH trade 24/7 with no exchange session. If "London carries the movement" is genuine
microstructure, crypto must show a **measurably flatter** profile across the four blocks. If it
shows the same session structure as FX, the session premise is an artefact of how we cut the
clock and every table above is suspect.

`path_cv` is the coefficient of variation of travel-per-hour across the four blocks — 0 is
perfectly flat:

| class | n | path_cv | peak ÷ trough |
|---|---:|---:|---:|
| metal | 1 | 0.414 | 2.39 |
| fx majors | 6 | 0.376 | 2.37 |
| fx crosses | 3 | 0.248 | 1.73 |
| **crypto** | 2 | **0.185** | **1.48** |

Crypto is the flattest class, by a clear margin, in the direction the premise predicted. The
session layer survives a test that could have ended it. This control cost nothing and is in the
universe for exactly this reason.

### Conditioning on yesterday's range buys you almost nothing

The folk claim — *yesterday did so-and-so, so today has an 80–90% chance of being under X* — is
real and **mostly mechanical**: volatility clusters, and that has been known since the 1980s. So
the honest question is not whether the conditional table works. It is whether conditioning
**narrows the band** versus not conditioning at all.

Width of the 10–90 band of next-day range, conditional on the prior day's quintile versus
unconditional:

| | narrowing |
|---|---:|
| best (US30) | 9.5% |
| median of 18 | ~3.2% |
| gold | **−2.4%** (conditioning makes it *wider*) |
| EUR_USD | −1.0% |

A HAR baseline — yesterday, the 5-day mean and the 22-day mean of log range — is in
`results/tables/C_har_baseline.csv`. It reaches R² 0.68 on gold and 0.23 on cable. **That is the
bar any range model has to clear**, and reporting a prior-day effect without it is rediscovering
volatility clustering with a new name on it.

### The 3/6/9 hour claim, tested with its confound controlled

A popular claim says hours 3, 6 and 9 are special. From a 17:00 ET day start those are 19:00,
22:00 and 01:00 ET — all three inside the Asia block. Comparing them against all 24 hours would
just rediscover that Asia is quiet, so the comparison that decides it is **against the other Asia
hours only**.

**All twelve usable instruments come in below 1.00**, in a range of 0.50 to 0.81. The 3/6/9 hours
are consistently *quieter* than the Asia hours around them. The best of the three ranks 3rd to
12th out of 24 depending on the instrument; a genuine effect would put it near 1st.

The control is the test. Without it the result is uninterpretable in either direction.

---

## What is in here

```
SPEC.md                         the design, written before the build, with its own corrections
src/data.py                     the data seam — one CSV per instrument, and the seal guard
src/build_panels.py             daily and session panels; the two defects live in its comments
src/build_hourly.py             the hourly panel, which makes 3/6/9 a query and not a study
src/report.py                   reads the panels, writes the report and every table as CSV
results/SKELETON_REPORT.md      the full map — every instrument, every session
results/tables/*.csv            the same 13 tables, machine readable
results/build_record.txt        the build log for all 18 instruments
```

`report.py` writes each table as markdown **and** CSV from the same dataframe, so a number in the
report and its machine-readable twin cannot drift apart.

### Reproducing

```bash
pip install -r requirements.txt
python -I src/data.py            # inventory + the seal guard
python -I src/build_panels.py --all
python -I src/build_hourly.py --all
python -I src/report.py
```

Panels land in `panels/` (override with `SKELETON_PANELS`), one parquet per instrument so a long
run is resumable. The daily and session panels take roughly ten minutes for all eighteen
instruments; the hourly pass is a second one.

You need eighteen CSVs in `data/`. See `data/HOWTO.md`. **No data is included in this
repository; it is not ours to redistribute.** Data after **2026-05-21** is refused by the loader —
that period is sealed out-of-sample work for the programme this came from.

## Things to be suspicious of

- **This is descriptive, so none of it is significance-tested, and that is deliberate.** 12
  instruments × 7 session definitions is not 84 hypothesis tests, it is one map; no significance
  is claimed, so none has to be corrected. **The bar lands when you select from it.** Picking
  "GBP_JPY London has the best breakout profile" out of those 84 fingerprints *is* an 84-cell
  selection and pays √(2 ln 84) ≈ **2.98**. Build the map freely; pre-register what you do with
  it.
- **The session windows are conventions, not facts.** The ET boundaries in `SPEC.md` §3 are the
  standard ones. If you trade different boundaries, measure those.
- **`day_srv` has not been pinned.** The server-day layer assumes an EET/EEST broker clock. Until
  that is checked against a live terminal, trust the `day_et` numbers and treat `day_srv` as
  indicative. It is flagged in the output rather than quietly assumed.
- **JP225 and DE30 are CFDs on foreign exchanges** measured on the same ET grid as everything
  else, for comparability. "Asia session" means something different for JP225 than for EUR_USD,
  and that is a known limitation, not a fixed one.
- **Crypto's span is shorter** — 2021 onward, 1,852 days against ~2,170 for everything else. It
  is the control, and the control has a smaller sample than the things it controls.

---

MIT licensed. Published by ANS Capital Group as part of an open research record. The map is the
cheap part; publishing the two defects it found in our own data is the part that is actually
worth something.
