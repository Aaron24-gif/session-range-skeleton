# THE SKELETON — market-state and session-range substrate

**Spec v1, 2026-10-16.** A measurement layer, not a strategy. Body parts attach later.

*Published copy. Edited only to remove references to work that is not in this repository and to
describe the published data seam rather than the private cache it was built against. The design,
the corrections and the self-criticism are as written.*

---

## 0. WHAT THIS IS, AND THE ONE GOVERNANCE POINT THAT MATTERS

The skeleton is a **persisted panel** at two granularities — instrument × day, and
instrument × day × session — from which any later hypothesis is a *query* rather than a new
computation. That is what makes it a skeleton: the cost is paid once.

**It is descriptive, and descriptive work carries no multiplicity bar.** Measuring session range
on 17 instruments across 7 session definitions is not 119 hypothesis tests; it is one map. No
significance is claimed, so none has to be corrected.

**The bar lands when we SELECT from the map.** Choosing "GBP_JPY London has the best breakout
profile" out of 119 fingerprints *is* a 119-cell selection and pays √(2 ln 119) ≈ **3.09**. So:

> **Build the map freely. Pre-register what we do with it.**

That resolves the "so many cells" worry. The cells are free; the choosing is not.

---

## 1. UNIVERSE — 18 instruments, 5 asset classes, local cache only

| class | instruments | tf | span |
|---|---|---|---|
| Indices | NAS100_USD, SPX500_USD, US30_USD, US2000_USD, DE30_EUR | 1m | 2018 → 8.6yr |
| Index (Asia) | JP225_USD | 5m | 2018 → 8.4yr |
| Metal | XAU_USD | 1m | 2018 → 8.6yr |
| FX majors | EUR_USD, GBP_USD, USD_JPY, USD_CAD, USD_CHF, USD_SEK | 5m | 2018 → 8.4–8.6yr |
| FX crosses | GBP_JPY, GBP_AUD, GBP_NZD | 5m | 2018 → 8.4yr |
| **Crypto — control** | BTC_USD, ETH_USD | 1m | 2021 → 5.1yr |

**Crypto is a built-in falsification check, not filler.** BTC and ETH trade 24/7 with no exchange
session. If "London carries the most movement" is genuine microstructure, crypto must show a
measurably *weaker* session signature. If crypto shows the same session structure as FX, the
session premise is an artefact of how we cut the clock, and the whole skeleton's session layer is
suspect. This test costs nothing and can invalidate the premise, which is why it is in.

**Excluded:** nine instruments held back for out-of-sample work (XAG, XPT, XPD, XCU, BCO,
WTICO, NATGAS, USD_MXN, USD_ZAR). `data.py` raises on all nine rather than loading them.

**Partition: DEVELOPMENT only, hard cut at 2026-05-21.** Several cached series run to Aug 2026;
they are truncated. Everything ≥ 2026-05-22 stays sealed.

**Network: structurally impossible.** The original loader read a local cache and never imported
the vendor client's fetch path, because that client silently downloads on any cache-key mismatch
and the connection here is metered. The published loader reads plain CSVs and has no client to
import at all. Both share the property that matters: a run cannot quietly become a download.

---

## 2. THE DAY — both boundaries, as agreed

| key | definition | role |
|---|---|---|
| `day_et` | **17:00 ET → 17:00 ET, labelled by end date** | **primary.** The convention used across the rest of the programme — `(index + 7h).normalize()` on an ET index — so every number here is comparable with roughly a hundred hypotheses already tested against it. Pick one day boundary and keep it; the comparability is worth more than the boundary being ideal |
| `day_srv` | broker server day, 00:00 server time | secondary. Matches the daily candle on your own MT5 charts, so the range numbers are verifiable against what you see when you trade |

**Server offset is a declared parameter, not a guess.** Default EET (UTC+2 winter / UTC+3 summer,
EU DST) — the standard MT-broker clock. **This must be pinned against your own live terminal
before the `day_srv` numbers are trusted**; it is flagged in the output, and the `day_et` layer is
unaffected either way.

**DST is handled from a timezone-aware index, never from an ET-naive one.** The naive index is
ambiguous in the autumn fall-back hour; re-deriving session membership from it would smear London
by an hour twice a year. `prepare()` in `build_panels.py` takes minute-of-day from the aware
index for exactly this reason.

---

## 3. SESSIONS — overlapping and exclusive, both computed

**Overlapping** (the real trading sessions; shares sum to > 100%):

| session | ET window |
|---|---|
| Asia | 18:00 → 03:00 |
| London | 03:00 → 11:30 |
| NewYork | 08:00 → 17:00 |

**Exclusive blocks** (tile the full 24h with no gap):

| block | ET window | hours |
|---|---|---|
| Asia | 17:00 → 03:00 | 10.0 |
| LDN_only | 03:00 → 08:00 | 5.0 |
| Overlap | 08:00 → 11:30 | 3.5 |
| NY_only | 11:30 → 17:00 | 5.5 |

Asia starts at 17:00 (Sydney open) rather than 18:00 so the blocks tile the day exactly, leaving
no orphan rollover hour.

> **CORRECTION, found in validation.** An earlier draft of this spec claimed exclusive session
> *ranges* sum to 100% of the day's range. **That is false and cannot be true.** Sub-period
> high−low ranges overlap the day's own range, so their sum always exceeds it — measured at
> **2.03×** on EUR_USD. Range is not additive over time. §4a replaces it with two decompositions
> that genuinely do partition.

---

## 4. UNITS — three, because "pips" alone is a trap

Comparing pips across XAU, NAS100 and EUR_USD is meaningless. Every range is reported three ways:

| unit | definition | what it is for |
|---|---|---|
| `_pts` | raw price units (high − low) | **cost comparison** — spreads and commissions are quoted in points |
| `_pips` | points ÷ pip size, FX only (0.0001; 0.01 for JPY crosses) | the number you read intuitively. For gold, indices and crypto, **points are the unit** and `_pips` is left null rather than faked |
| `_atr` | points ÷ prior-day ATR20 | **the only cross-instrument comparable unit.** Every ranking across instruments uses this |

`_atr` uses the **prior** day's ATR so the normaliser is causal and never contains the day being
measured.

---

## 4a. THREE WAYS TO ASK "WHERE DO THE PIPS LIVE" — and only two of them partition

Validated on EUR_USD: both partition identities hold **exactly (1e-9) on 100% of days**.

| measure | definition | partitions? | reads as |
|---|---|---|---|
| `range_vs_day` | session range ÷ day range | **no** — sums to ~2.03× | "this session spans X% of the day's range". Comparable across sessions, but never a share of a whole |
| `share_path` | session path length ÷ day path length, where path = Σ \|closeₜ − closeₜ₋₁\| | **yes, exactly** | **where the distance is travelled** — the churn, what many small trades could capture |
| `share_ext` | contribution to the day's final range: first block its own range, every later block only what it added beyond the running extremes | **yes, exactly** — telescopes to day_hi − day_lo | **where the day's range actually gets built** — what a breakout could capture |

**`breakout_index` = `share_ext` ÷ `share_path`.** Above 1: the session expands the range
efficiently relative to how far it travelled — a breakout signature. Below 1: it travels a lot
while adding little new range — churn inside existing range, a mean-reversion signature.

**Known bias, and it is blanked rather than reported.** The first block of the day contributes its
*entire* range as extension by construction, since nothing precedes it. That inflates its ratio
and makes it incomparable with later blocks, so `breakout_index` is **NaN for Asia**. A
structurally meaningless number is worse than a missing one.

### Duration normalisation is mandatory
A 10-hour session trivially outranks a 3.5-hour one on every absolute measure. That is duration,
not activity. Every ranking is therefore reported **per hour** (`range_per_hr`, `path_per_hr`,
`ext_per_hr`) alongside the raw figure. On EUR_USD this inverts the naive ordering: Asia has the
largest raw range share and the **lowest** activity per hour.

---
## 5. PANEL 1 — `daily_panel` (instrument × day × day-definition)

`open high low close nbars` · `range_pts range_pips range_atr range_pct` ·
`body_pts` · `efficiency = |close−open| / range` · `gap_pts = open − prior_close` ·
`prior_range_pts prior_range_atr` · `atr14 atr20` (prior-day, causal) ·
`hi_minute lo_minute` (minutes from day start) · `hi_first` (bool: high formed before low) ·
`dow month year` · `coverage_ok`

`coverage_ok` uses a health gate inherited from the rest of the programme — `max(150, 0.58 ×
median weekday bars)` — which is what stops a 390-bar RTH index feed being rejected by a
gold-calibrated threshold. **That inherited 150-bar floor turned out to be wrong too; see the
report's §0.**

## 6. PANEL 2 — `session_panel` (instrument × day × session)

`open high low close nbars` · `range_pts range_pips range_atr` ·
**`share_of_day`** = session range ÷ day range ← *where the pips live* ·
**`sets_day_high` `sets_day_low`** ← *where the extremes form — the most actionable column* ·
`efficiency` · `hi_frac lo_frac` (position of the extreme within the session, 0→1) ·
`extends_prior_hi extends_prior_lo` (broke the prior session's extreme) ·
`reverted_after_extend` (broke it, then closed back inside) ·
`open_to_hi open_to_lo` (MFE/MAE from the session open, in ATR) ·
`coverage_ok`

---

## 7. THE BEHAVIOURAL FINGERPRINT — the breakout-vs-reversion answer

Five numbers per instrument × session, derived from Panel 2. This is the thing that tells us *how*
a session covers its pips, rather than just how many.

| number | reads as |
|---|---|
| `P(sets day extreme)` | does the day's high or low get made here |
| `median efficiency` | 1.0 = travels in a line (trend); 0.2 = chops inside a range |
| `median hi_frac / lo_frac` | **early** extreme → spike-then-hold; **late** → trends into the close |
| `P(extends prior) / P(reverted \| extended)` | **breakout vs fakeout rate** |
| `open_to_hi / open_to_lo` | symmetry of excursion from the open |

**This is where an earlier result constrains what the fingerprint is allowed to claim.** A prior
study in the same programme measured conditional MFE/MAE at 1.00–1.12 across a large grid, so
excursions are near-symmetric and little accrues to a directional bet. The fingerprint therefore characterises *how the range is
built*, which is a scale question, and does not claim a direction.

---

## 8. THE CONDITIONAL RANGE LAYER — and the trap in it

Your example — *"previous day's range did so-and-so pips, so today's range has an 80–90% chance of
being under X"* — is real, and **mostly mechanical**. Range is strongly autocorrelated because
volatility clusters. That is the HAR/GARCH effect, known since the 1980s.

**So the headline prediction is not the finding, and reporting it as one would be rediscovering
volatility clustering.** Two things in it are genuinely worth having:

1. **The calibrated band.** `P(range < X | prior-range decile)` is *operationally* useful for
   target and stop placement even though its mechanism is known. Deliverable: a per-instrument
   quantile table, honestly labelled as calibration rather than edge.
2. **The residual after HAR.** Fit the HAR baseline — log RV(t), 5-day mean, 22-day mean — and ask
   what is left. Any *non-mechanical* information about tomorrow's range lives in that residual
   and nowhere else.

The discipline generalises: **beat the mechanical baseline, never rediscover it.** Most published
"edges" in range prediction are volatility clustering with a new name on it.

---

## 9. THE 3/6/9 SIDE TEST — run properly, prior low, and there is a confound

Stated plainly: there is no mechanism, and it is numerology until shown otherwise. It is also
cheap, so it gets a fair test rather than a dismissal.

- **Outcome:** range contribution and extreme-formation rate for each of hours 1…24 from the day
  start.
- **Null:** hours 3, 6 and 9 must beat the **maximum of the other 21 hours**, not a vague
  baseline. Expected max |t| over 21 cells ≈ √(2 ln 21) ≈ **2.47**.
- **The confound, which is probably the whole answer:** from an 18:00 ET start, hours 3/6/9 are
  **21:00, 00:00 and 03:00 ET** — Asia open, Tokyo midday, and London open. Any apparent effect is
  session structure wearing a numerology costume. The test is therefore **conditional on session
  membership**; if the effect vanishes once session is controlled, it was never about 3/6/9.

That control *is* the test. Without it the result is uninterpretable either way.

---

## 10. BUILD ORDER

1. `data.py` — local-only loader, network structurally unreachable.
2. Validate on 3 instruments (XAU 1m, EUR_USD 5m, NAS100 1m) — one 24h metal, one FX, one
   RTH-shaped index. Check bar counts, DST boundaries, and that session shares sum correctly.
3. Fan out to all 18, persisting per instrument so the run is resumable.
4. `SKELETON_REPORT.md` — the descriptive map: session ranking per instrument, fingerprints,
   calibration tables, the crypto control, and the 3/6/9 result.

**Stop there.** No entries, no strategies. The skeleton has to be able to generate hypotheses
before we spend any on it.

---

## 11. OPEN DESIGN ITEMS — where your input changes the build

1. **Server offset** must be pinned against your own live terminal before `day_srv` is trusted.
   Read-only check; `day_et` is unaffected.
2. **Session windows are conventions, not facts.** The ET windows in §3 are the standard ones, but
   if you trade different boundaries, those are the ones worth measuring.
3. **Weekend and Sunday-open handling.** The Sunday 18:00 ET reopen is a partial session with a
   gap. Default: tagged and kept, excluded from medians via `coverage_ok`, never silently dropped.
4. **JP225 and DE30 are index CFDs on foreign exchanges.** Their "local session" is not the ET
   grid. They are measured on the same ET grid for comparability, and separately on their own
   exchange hours — otherwise "Asia session" means something different for JP225 than for EUR_USD.
