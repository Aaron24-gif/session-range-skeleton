# SKELETON REPORT — session and range behaviour map

**Development partition only (≤ 2026-05-21). 18 instruments built; 12 usable for session analysis. Sealed nine excluded.**

Descriptive map. No cell is selected and nothing is promoted — per `SKELETON_SPEC.md` §0, the map is free and the choosing is not: picking one cell out of this map is a multiple-comparison problem and needs pre-registration.

---

## 0. WHAT CAN ACTUALLY BE MEASURED — read this before any table below

Two defects were found by diagnostics and both would have silently invalidated the session results.

**Feed regime.** Every one of the six index feeds switches from RTH-only to near-24h in late 2025 — NAS100 goes 390 → 1380 bars/day. Before that switch the indices have **no Asia or London data at all**. Pooling across the boundary would compare a ~165-day sample against a 2,163-day one and report it as one number.

**Coverage gate.** The inherited 150-bar floor was calibrated for 24h feeds and rejected 92.4% of JP225 days as low-coverage when its RTH-only Tokyo feed (60 bars/day) was in fact complete. Made relative to each instrument's own median; JP225 went 7.6% → 100%.

| cls      | symbol     |   days |   med_bars |   bars_min_yr |   bars_max_yr |   ratio | feed          |   d_Asia |   d_LDN_only |   d_Overlap |   d_NY_only | sessions_usable   |
|:---------|:-----------|-------:|-----------:|--------------:|--------------:|--------:|:--------------|---------:|-------------:|------------:|------------:|:------------------|
| crypto   | BTC_USD    |   1852 |   1440.000 |      1440.000 |      1440.000 |   1.000 | stable        |     1852 |         1851 |        1851 |        1851 | True              |
| crypto   | ETH_USD    |   1852 |   1440.000 |      1440.000 |      1440.000 |   1.000 | stable        |     1852 |         1851 |        1851 |        1851 | True              |
| fx_cross | GBP_AUD    |   2175 |    288.000 |       288.000 |       288.000 |   1.000 | stable        |     2175 |         2174 |        2174 |        2174 | True              |
| fx_cross | GBP_JPY    |   2179 |    288.000 |       288.000 |       288.000 |   1.000 | stable        |     2179 |         2174 |        2174 |        2174 | True              |
| fx_cross | GBP_NZD    |   2181 |    288.000 |       288.000 |       288.000 |   1.000 | stable        |     2179 |         2174 |        2174 |        2176 | True              |
| fx_major | EUR_USD    |   2178 |    288.000 |       287.000 |       288.000 |   1.003 | stable        |     2178 |         2175 |        2175 |        2176 | True              |
| fx_major | GBP_USD    |   2179 |    288.000 |       287.000 |       288.000 |   1.003 | stable        |     2179 |         2175 |        2175 |        2175 | True              |
| fx_major | USD_CAD    |   2188 |    288.000 |       286.000 |       288.000 |   1.007 | stable        |     2188 |         2175 |        2175 |        2175 | True              |
| fx_major | USD_CHF    |   2182 |    287.000 |       279.000 |       288.000 |   1.032 | stable        |     2182 |         2175 |        2175 |        2175 | True              |
| fx_major | USD_JPY    |   2187 |    288.000 |       287.000 |       288.000 |   1.003 | stable        |     2187 |         2175 |        2175 |        2175 | True              |
| fx_major | USD_SEK    |   2186 |    288.000 |       287.500 |       288.000 |   1.002 | stable        |     2186 |         2175 |        2175 |        2174 | True              |
| index    | DE30_EUR   |   2131 |    510.000 |       510.000 |      1221.000 |   2.394 | REGIME CHANGE |      159 |         2131 |        2131 |         293 | False             |
| index    | JP225_USD  |   2167 |     60.000 |        60.000 |       276.000 |   4.600 | REGIME CHANGE |     2167 |          163 |         165 |         164 | False             |
| index    | NAS100_USD |   2163 |    390.000 |       390.000 |      1380.000 |   3.538 | REGIME CHANGE |      165 |          164 |        2163 |        2161 | False             |
| index    | SPX500_USD |   2163 |    390.000 |       389.000 |      1378.000 |   3.542 | REGIME CHANGE |      165 |          164 |        2163 |        2161 | False             |
| index    | US2000_USD |   2163 |    390.000 |       390.000 |      1379.000 |   3.536 | REGIME CHANGE |      165 |          164 |        2163 |        2161 | False             |
| index    | US30_USD   |   2163 |    390.000 |       390.000 |      1380.000 |   3.538 | REGIME CHANGE |      165 |          164 |        2163 |        2161 | False             |
| metal    | XAU_USD    |   2174 |   1375.000 |      1307.000 |      1376.000 |   1.053 | stable        |     2174 |         2164 |        2164 |        2163 | True              |

**Session analysis is valid for 12 of 18 instruments.** The six indices are excluded from every session table and appear only in the daily-range section, split by feed regime and never pooled across it.


---

## A. WHERE THE MOVEMENT IS — duration-normalised, common sample

`ext_per_hr` = share of the day's range built here, per hour. `path_per_hr` = share of the day's travel, per hour. `brk` = breakout index (>1 expands efficiently, <1 churns inside existing range); NaN for Asia, which gets its whole range as extension by construction.


### metal

| symbol   | session   |   hours |   range_pts |   range_pips |   pts_per_hr |   share_ext |   ext_per_hr |   share_path |     brk |   eff |   sets_extreme |
|:---------|:----------|--------:|------------:|-------------:|-------------:|------------:|-------------:|-------------:|--------:|------:|---------------:|
| XAU_USD  | Overlap   |   3.500 |      14.730 |          nan |        4.209 |       0.241 |        0.069 |        0.263 |   0.821 | 0.436 |          0.572 |
| XAU_USD  | Asia      |  10.000 |      10.185 |          nan |        1.018 |       0.516 |        0.052 |        0.314 | nan     | 0.439 |          0.693 |
| XAU_USD  | LDN_only  |   5.000 |       9.465 |          nan |        1.893 |       0.160 |        0.032 |        0.214 |   0.599 | 0.426 |          0.275 |
| XAU_USD  | NY_only   |   5.500 |       8.525 |          nan |        1.550 |       0.082 |        0.015 |        0.209 |   0.000 | 0.408 |          0.467 |

### fx_major

| symbol   | session   |   hours |   range_pts |   range_pips |   pts_per_hr |   share_ext |   ext_per_hr |   share_path |     brk |   eff |   sets_extreme |
|:---------|:----------|--------:|------------:|-------------:|-------------:|------------:|-------------:|-------------:|--------:|------:|---------------:|
| EUR_USD  | Overlap   |   3.500 |       0.004 |       39.600 |        0.001 |       0.219 |        0.062 |        0.243 |   0.830 | 0.448 |          0.542 |
| EUR_USD  | LDN_only  |   5.000 |       0.003 |       34.800 |        0.001 |       0.250 |        0.050 |        0.260 |   0.912 | 0.465 |          0.406 |
| EUR_USD  | Asia      |  10.000 |       0.003 |       27.800 |        0.000 |       0.450 |        0.045 |        0.291 | nan     | 0.433 |          0.586 |
| EUR_USD  | NY_only   |   5.500 |       0.003 |       25.700 |        0.000 |       0.082 |        0.015 |        0.206 |   0.000 | 0.444 |          0.491 |
| GBP_USD  | Overlap   |   3.500 |       0.005 |       51.900 |        0.001 |       0.195 |        0.056 |        0.236 |   0.729 | 0.456 |          0.487 |
| GBP_USD  | LDN_only  |   5.000 |       0.005 |       50.300 |        0.001 |       0.276 |        0.055 |        0.273 |   0.967 | 0.446 |          0.440 |
| GBP_USD  | Asia      |  10.000 |       0.004 |       37.600 |        0.000 |       0.451 |        0.045 |        0.289 | nan     | 0.454 |          0.599 |
| GBP_USD  | NY_only   |   5.500 |       0.003 |       34.000 |        0.001 |       0.078 |        0.014 |        0.201 |   0.000 | 0.426 |          0.487 |
| USD_CAD  | Overlap   |   3.500 |       0.004 |       44.600 |        0.001 |       0.262 |        0.075 |        0.253 |   0.976 | 0.459 |          0.563 |
| USD_CAD  | Asia      |  10.000 |       0.003 |       29.950 |        0.000 |       0.453 |        0.045 |        0.293 | nan     | 0.442 |          0.556 |
| USD_CAD  | LDN_only  |   5.000 |       0.003 |       29.700 |        0.001 |       0.174 |        0.035 |        0.213 |   0.706 | 0.441 |          0.294 |
| USD_CAD  | NY_only   |   5.500 |       0.003 |       32.600 |        0.001 |       0.112 |        0.020 |        0.241 |   0.191 | 0.454 |          0.609 |
| USD_CHF  | Overlap   |   3.500 |       0.003 |       33.800 |        0.001 |       0.212 |        0.060 |        0.242 |   0.792 | 0.449 |          0.522 |
| USD_CHF  | LDN_only  |   5.000 |       0.003 |       30.000 |        0.001 |       0.251 |        0.050 |        0.260 |   0.908 | 0.462 |          0.406 |
| USD_CHF  | Asia      |  10.000 |       0.002 |       23.500 |        0.000 |       0.461 |        0.046 |        0.295 | nan     | 0.425 |          0.591 |
| USD_CHF  | NY_only   |   5.500 |       0.002 |       21.600 |        0.000 |       0.077 |        0.014 |        0.203 |   0.000 | 0.433 |          0.498 |
| USD_JPY  | Asia      |  10.000 |       0.451 |       45.100 |        0.045 |       0.604 |        0.060 |        0.382 | nan     | 0.438 |          0.830 |
| USD_JPY  | Overlap   |   3.500 |       0.429 |       42.900 |        0.123 |       0.181 |        0.052 |        0.215 |   0.689 | 0.456 |          0.453 |
| USD_JPY  | LDN_only  |   5.000 |       0.343 |       34.300 |        0.069 |       0.142 |        0.028 |        0.212 |   0.486 | 0.441 |          0.270 |
| USD_JPY  | NY_only   |   5.500 |       0.284 |       28.400 |        0.052 |       0.074 |        0.013 |        0.190 |   0.000 | 0.411 |          0.461 |
| USD_SEK  | Overlap   |   3.500 |       0.048 |      475.800 |        0.014 |       0.190 |        0.054 |        0.239 |   0.682 | 0.442 |          0.461 |
| USD_SEK  | LDN_only  |   5.000 |       0.048 |      478.350 |        0.010 |       0.268 |        0.054 |        0.276 |   0.925 | 0.460 |          0.448 |
| USD_SEK  | Asia      |  10.000 |       0.037 |      366.650 |        0.004 |       0.465 |        0.046 |        0.284 | nan     | 0.434 |          0.596 |
| USD_SEK  | NY_only   |   5.500 |       0.032 |      323.700 |        0.006 |       0.078 |        0.014 |        0.201 |   0.000 | 0.420 |          0.510 |

### fx_cross

| symbol   | session   |   hours |   range_pts |   range_pips |   pts_per_hr |   share_ext |   ext_per_hr |   share_path |     brk |   eff |   sets_extreme |
|:---------|:----------|--------:|------------:|-------------:|-------------:|------------:|-------------:|-------------:|--------:|------:|---------------:|
| GBP_AUD  | Asia      |  10.000 |       0.007 |       73.850 |        0.001 |       0.605 |        0.060 |        0.375 | nan     | 0.429 |          0.810 |
| GBP_AUD  | Overlap   |   3.500 |       0.007 |       66.200 |        0.002 |       0.141 |        0.040 |        0.200 |   0.524 | 0.445 |          0.412 |
| GBP_AUD  | LDN_only  |   5.000 |       0.007 |       67.300 |        0.001 |       0.198 |        0.040 |        0.245 |   0.701 | 0.465 |          0.363 |
| GBP_AUD  | NY_only   |   5.500 |       0.004 |       43.950 |        0.001 |       0.057 |        0.010 |        0.181 |   0.000 | 0.417 |          0.426 |
| GBP_JPY  | Asia      |  10.000 |       0.641 |       64.150 |        0.064 |       0.552 |        0.055 |        0.351 | nan     | 0.443 |          0.741 |
| GBP_JPY  | LDN_only  |   5.000 |       0.688 |       68.800 |        0.138 |       0.238 |        0.048 |        0.258 |   0.864 | 0.470 |          0.420 |
| GBP_JPY  | Overlap   |   3.500 |       0.650 |       65.050 |        0.186 |       0.147 |        0.042 |        0.205 |   0.490 | 0.454 |          0.419 |
| GBP_JPY  | NY_only   |   5.500 |       0.440 |       44.000 |        0.080 |       0.063 |        0.011 |        0.186 |   0.000 | 0.417 |          0.430 |
| GBP_NZD  | Asia      |  10.000 |       0.008 |       80.900 |        0.001 |       0.610 |        0.061 |        0.378 | nan     | 0.440 |          0.802 |
| GBP_NZD  | LDN_only  |   5.000 |       0.007 |       73.800 |        0.001 |       0.199 |        0.040 |        0.244 |   0.717 | 0.463 |          0.366 |
| GBP_NZD  | Overlap   |   3.500 |       0.007 |       70.500 |        0.002 |       0.132 |        0.038 |        0.195 |   0.480 | 0.445 |          0.407 |
| GBP_NZD  | NY_only   |   5.500 |       0.005 |       49.900 |        0.001 |       0.058 |        0.011 |        0.183 |   0.000 | 0.389 |          0.437 |

### crypto

| symbol   | session   |   hours |   range_pts |   range_pips |   pts_per_hr |   share_ext |   ext_per_hr |   share_path |     brk |   eff |   sets_extreme |
|:---------|:----------|--------:|------------:|-------------:|-------------:|------------:|-------------:|-------------:|--------:|------:|---------------:|
| BTC_USD  | Asia      |  10.000 |    1026.280 |          nan |      102.628 |       0.602 |        0.060 |        0.376 | nan     | 0.384 |          0.834 |
| BTC_USD  | Overlap   |   3.500 |     854.860 |          nan |      244.246 |       0.141 |        0.040 |        0.188 |   0.495 | 0.414 |          0.338 |
| BTC_USD  | NY_only   |   5.500 |     920.000 |          nan |      167.273 |       0.143 |        0.026 |        0.260 |   0.323 | 0.383 |          0.629 |
| BTC_USD  | LDN_only  |   5.000 |     668.530 |          nan |      133.706 |       0.113 |        0.023 |        0.176 |   0.341 | 0.408 |          0.205 |
| ETH_USD  | Asia      |  10.000 |      66.940 |          nan |        6.694 |       0.609 |        0.061 |        0.382 | nan     | 0.395 |          0.857 |
| ETH_USD  | Overlap   |   3.500 |      53.930 |          nan |       15.409 |       0.132 |        0.038 |        0.183 |   0.442 | 0.422 |          0.321 |
| ETH_USD  | NY_only   |   5.500 |      56.710 |          nan |       10.311 |       0.138 |        0.025 |        0.254 |   0.268 | 0.399 |          0.602 |
| ETH_USD  | LDN_only  |   5.000 |      43.750 |          nan |        8.750 |       0.120 |        0.024 |        0.181 |   0.340 | 0.402 |          0.224 |

### Pooled across the usable instruments (median of per-instrument values)

| session   |   ext_per_hr |   path_per_hr |   share_ext |   share_path |     brk |   sets_extreme |   eff |
|:----------|-------------:|--------------:|------------:|-------------:|--------:|---------------:|------:|
| Asia      |        0.053 |         0.033 |       0.534 |        0.333 | nan     |          0.717 | 0.436 |
| LDN_only  |        0.040 |         0.049 |       0.198 |        0.244 |   0.712 |          0.365 | 0.453 |
| Overlap   |        0.053 |         0.064 |       0.185 |        0.226 |   0.685 |          0.457 | 0.447 |
| NY_only   |        0.014 |         0.037 |       0.078 |        0.202 |   0.000 |          0.489 | 0.417 |

---

## B. CONTROL — does session structure survive where there is no session?

BTC and ETH trade 24/7 with no exchange session. If "London carries the movement" is genuine microstructure, crypto must show a **measurably flatter** profile across the four blocks. `path_cv` is the coefficient of variation of travel-per-hour: 0 = perfectly flat, higher = stronger session structure. **This test can falsify the session premise itself, which is why crypto is in the universe.**

| cls      |   n |   path_cv |   ext_cv |   peak_over_trough |
|:---------|----:|----------:|---------:|-------------------:|
| metal    |   1 |     0.414 |    0.560 |              2.389 |
| fx_major |   6 |     0.376 |    0.470 |              2.368 |
| fx_cross |   3 |     0.248 |    0.548 |              1.734 |
| crypto   |   2 |     0.185 |    0.461 |              1.484 |

### per instrument

| symbol   | cls      |   path_cv |   ext_cv | peak_block   |   peak_over_trough |
|:---------|:---------|----------:|---------:|:-------------|-------------------:|
| XAU_USD  | metal    |     0.414 |    0.560 | Overlap      |              2.389 |
| USD_CAD  | fx_major |     0.385 |    0.526 | Overlap      |              2.472 |
| USD_SEK  | fx_major |     0.382 |    0.450 | Overlap      |              2.398 |
| EUR_USD  | fx_major |     0.377 |    0.469 | Overlap      |              2.388 |
| USD_CHF  | fx_major |     0.375 |    0.471 | Overlap      |              2.348 |
| GBP_USD  | fx_major |     0.372 |    0.458 | Overlap      |              2.333 |
| GBP_JPY  | fx_cross |     0.275 |    0.491 | Overlap      |              1.738 |
| USD_JPY  | fx_major |     0.270 |    0.559 | Overlap      |              1.773 |
| GBP_AUD  | fx_cross |     0.248 |    0.548 | Overlap      |              1.734 |
| GBP_NZD  | fx_cross |     0.234 |    0.554 | Overlap      |              1.680 |
| BTC_USD  | crypto   |     0.197 |    0.458 | Overlap      |              1.522 |
| ETH_USD  | crypto   |     0.172 |    0.464 | Overlap      |              1.445 |

---

## C. NEXT-DAY RANGE — the calibration, and how much of it is mechanical

Your example: *the prior day did so-and-so pips, so today has an 80–90% chance of being under X.* That table is below. **But the prediction itself is mostly volatility clustering**, known since the 1980s — so the honest question is not whether it works, it is whether conditioning **narrows the band** at all versus not conditioning.

Regime-change instruments are truncated to their pre-switch feed (DE30_EUR, JP225_USD, NAS100_USD, SPX500_USD, US2000_USD, US30_USD drop 2026), because an RTH day and a 24h day are not the same object.

### Does conditioning on the prior day actually help?

Width of the 10–90 band of `range_atr`, conditional on the prior day's quintile versus unconditional. **Near 0% means the prior day tells you almost nothing the unconditional distribution did not already tell you.**

| symbol     |   uncond_band |   mean_cond_band |   narrowing_pct |
|:-----------|--------------:|-----------------:|----------------:|
| US30_USD   |         1.040 |            0.942 |           9.459 |
| SPX500_USD |         1.106 |            1.036 |           6.318 |
| US2000_USD |         0.943 |            0.885 |           6.195 |
| ETH_USD    |         1.305 |            1.234 |           5.452 |
| DE30_EUR   |         1.004 |            0.951 |           5.237 |
| NAS100_USD |         1.036 |            0.985 |           4.874 |
| JP225_USD  |         0.888 |            0.854 |           3.773 |
| USD_CHF    |         1.024 |            0.990 |           3.322 |
| USD_JPY    |         1.109 |            1.073 |           3.258 |
| GBP_AUD    |         0.968 |            0.937 |           3.165 |
| GBP_JPY    |         1.033 |            1.001 |           3.062 |
| BTC_USD    |         1.309 |            1.282 |           2.111 |
| USD_CAD    |         0.985 |            0.974 |           1.146 |
| GBP_USD    |         0.971 |            0.961 |           1.041 |
| USD_SEK    |         0.939 |            0.934 |           0.436 |
| GBP_NZD    |         0.907 |            0.916 |          -0.957 |
| EUR_USD    |         0.953 |            0.963 |          -1.022 |
| XAU_USD    |         1.054 |            1.079 |          -2.373 |

### Full calibration — quintile 0 is the unconditional row

`p90` is the "90% chance of being under" number, in units of the prior day's ATR20.

| symbol     |   prior_quintile |    n |   p10 |   p50 |   p90 |   band_10_90 |
|:-----------|-----------------:|-----:|------:|------:|------:|-------------:|
| BTC_USD    |                0 | 1829 | 0.424 | 0.890 | 1.733 |        1.309 |
| BTC_USD    |                1 |  366 | 0.340 | 0.734 | 1.423 |        1.084 |
| BTC_USD    |                2 |  366 | 0.425 | 0.834 | 1.587 |        1.163 |
| BTC_USD    |                3 |  365 | 0.429 | 0.881 | 1.598 |        1.169 |
| BTC_USD    |                4 |  366 | 0.437 | 0.915 | 1.829 |        1.392 |
| BTC_USD    |                5 |  366 | 0.613 | 1.085 | 2.213 |        1.601 |
| DE30_EUR   |                0 | 2011 | 0.474 | 0.814 | 1.478 |        1.004 |
| DE30_EUR   |                1 |  402 | 0.416 | 0.684 | 1.170 |        0.754 |
| DE30_EUR   |                2 |  402 | 0.423 | 0.751 | 1.249 |        0.826 |
| DE30_EUR   |                3 |  402 | 0.484 | 0.811 | 1.485 |        1.001 |
| DE30_EUR   |                4 |  402 | 0.496 | 0.856 | 1.489 |        0.992 |
| DE30_EUR   |                5 |  403 | 0.571 | 0.975 | 1.755 |        1.184 |
| ETH_USD    |                0 | 1829 | 0.449 | 0.896 | 1.754 |        1.305 |
| ETH_USD    |                1 |  366 | 0.372 | 0.732 | 1.448 |        1.076 |
| ETH_USD    |                2 |  366 | 0.412 | 0.822 | 1.500 |        1.088 |
| ETH_USD    |                3 |  365 | 0.476 | 0.923 | 1.705 |        1.229 |
| ETH_USD    |                4 |  366 | 0.503 | 0.906 | 1.821 |        1.318 |
| ETH_USD    |                5 |  366 | 0.635 | 1.126 | 2.091 |        1.456 |
| EUR_USD    |                0 | 2153 | 0.572 | 0.920 | 1.524 |        0.953 |
| EUR_USD    |                1 |  431 | 0.549 | 0.884 | 1.471 |        0.922 |
| EUR_USD    |                2 |  430 | 0.559 | 0.885 | 1.523 |        0.964 |
| EUR_USD    |                3 |  431 | 0.575 | 0.914 | 1.455 |        0.880 |
| EUR_USD    |                4 |  430 | 0.590 | 0.917 | 1.497 |        0.907 |
| EUR_USD    |                5 |  431 | 0.631 | 0.982 | 1.770 |        1.139 |
| GBP_AUD    |                0 | 2152 | 0.580 | 0.917 | 1.548 |        0.968 |
| GBP_AUD    |                1 |  431 | 0.513 | 0.818 | 1.361 |        0.847 |
| GBP_AUD    |                2 |  430 | 0.526 | 0.864 | 1.470 |        0.943 |
| GBP_AUD    |                3 |  430 | 0.601 | 0.908 | 1.515 |        0.914 |
| GBP_AUD    |                4 |  430 | 0.643 | 0.961 | 1.577 |        0.934 |
| GBP_AUD    |                5 |  431 | 0.675 | 1.056 | 1.722 |        1.047 |
| GBP_JPY    |                0 | 2152 | 0.546 | 0.904 | 1.578 |        1.033 |
| GBP_JPY    |                1 |  431 | 0.459 | 0.792 | 1.393 |        0.934 |
| GBP_JPY    |                2 |  430 | 0.520 | 0.852 | 1.438 |        0.919 |
| GBP_JPY    |                3 |  430 | 0.545 | 0.896 | 1.473 |        0.927 |
| GBP_JPY    |                4 |  430 | 0.583 | 0.927 | 1.569 |        0.987 |
| GBP_JPY    |                5 |  431 | 0.676 | 1.063 | 1.914 |        1.238 |
| GBP_NZD    |                0 | 2152 | 0.603 | 0.925 | 1.509 |        0.907 |
| GBP_NZD    |                1 |  431 | 0.531 | 0.857 | 1.460 |        0.929 |
| GBP_NZD    |                2 |  430 | 0.592 | 0.913 | 1.386 |        0.794 |
| GBP_NZD    |                3 |  430 | 0.593 | 0.887 | 1.482 |        0.889 |
| GBP_NZD    |                4 |  430 | 0.629 | 0.942 | 1.473 |        0.843 |
| GBP_NZD    |                5 |  431 | 0.638 | 1.010 | 1.761 |        1.123 |
| GBP_USD    |                0 | 2153 | 0.577 | 0.925 | 1.548 |        0.971 |
| GBP_USD    |                1 |  431 | 0.532 | 0.897 | 1.431 |        0.899 |
| GBP_USD    |                2 |  430 | 0.578 | 0.896 | 1.441 |        0.863 |
| GBP_USD    |                3 |  431 | 0.578 | 0.902 | 1.426 |        0.847 |
| GBP_USD    |                4 |  430 | 0.590 | 0.915 | 1.618 |        1.028 |
| GBP_USD    |                5 |  431 | 0.648 | 1.026 | 1.814 |        1.166 |
| JP225_USD  |                0 | 2045 | 0.397 | 0.699 | 1.284 |        0.888 |
| JP225_USD  |                1 |  409 | 0.319 | 0.605 | 1.107 |        0.788 |
| JP225_USD  |                2 |  409 | 0.396 | 0.658 | 1.124 |        0.728 |
| JP225_USD  |                3 |  409 | 0.421 | 0.686 | 1.112 |        0.690 |
| JP225_USD  |                4 |  409 | 0.420 | 0.729 | 1.326 |        0.906 |
| JP225_USD  |                5 |  409 | 0.483 | 0.861 | 1.642 |        1.159 |
| NAS100_USD |                0 | 1976 | 0.475 | 0.838 | 1.511 |        1.036 |
| NAS100_USD |                1 |  395 | 0.414 | 0.707 | 1.199 |        0.785 |
| NAS100_USD |                2 |  395 | 0.443 | 0.754 | 1.308 |        0.865 |
| NAS100_USD |                3 |  395 | 0.462 | 0.786 | 1.471 |        1.009 |
| NAS100_USD |                4 |  395 | 0.565 | 0.896 | 1.572 |        1.007 |
| NAS100_USD |                5 |  396 | 0.609 | 1.054 | 1.868 |        1.259 |
| SPX500_USD |                0 | 1976 | 0.445 | 0.807 | 1.551 |        1.106 |
| SPX500_USD |                1 |  395 | 0.367 | 0.633 | 1.101 |        0.734 |
| SPX500_USD |                2 |  395 | 0.400 | 0.726 | 1.267 |        0.867 |
| SPX500_USD |                3 |  395 | 0.486 | 0.759 | 1.437 |        0.951 |
| SPX500_USD |                4 |  395 | 0.536 | 0.857 | 1.707 |        1.172 |
| SPX500_USD |                5 |  396 | 0.614 | 1.148 | 2.072 |        1.458 |
| US2000_USD |                0 | 1975 | 0.519 | 0.852 | 1.463 |        0.943 |
| US2000_USD |                1 |  395 | 0.444 | 0.701 | 1.172 |        0.728 |
| US2000_USD |                2 |  395 | 0.505 | 0.806 | 1.293 |        0.788 |
| US2000_USD |                3 |  395 | 0.556 | 0.810 | 1.449 |        0.893 |
| US2000_USD |                4 |  395 | 0.555 | 0.878 | 1.448 |        0.893 |
| US2000_USD |                5 |  395 | 0.689 | 1.069 | 1.812 |        1.123 |
| US30_USD   |                0 | 1976 | 0.467 | 0.818 | 1.507 |        1.040 |
| US30_USD   |                1 |  395 | 0.394 | 0.650 | 1.134 |        0.740 |
| US30_USD   |                2 |  395 | 0.442 | 0.736 | 1.205 |        0.764 |
| US30_USD   |                3 |  395 | 0.482 | 0.840 | 1.388 |        0.907 |
| US30_USD   |                4 |  395 | 0.520 | 0.870 | 1.570 |        1.050 |
| US30_USD   |                5 |  396 | 0.628 | 1.079 | 1.875 |        1.247 |
| USD_CAD    |                0 | 2153 | 0.574 | 0.918 | 1.559 |        0.985 |
| USD_CAD    |                1 |  431 | 0.553 | 0.845 | 1.417 |        0.864 |
| USD_CAD    |                2 |  430 | 0.571 | 0.882 | 1.472 |        0.901 |
| USD_CAD    |                3 |  431 | 0.557 | 0.901 | 1.553 |        0.996 |
| USD_CAD    |                4 |  430 | 0.589 | 0.946 | 1.507 |        0.919 |
| USD_CAD    |                5 |  431 | 0.633 | 1.052 | 1.824 |        1.190 |
| USD_CHF    |                0 | 2153 | 0.567 | 0.915 | 1.591 |        1.024 |
| USD_CHF    |                1 |  431 | 0.530 | 0.834 | 1.381 |        0.851 |
| USD_CHF    |                2 |  430 | 0.562 | 0.873 | 1.511 |        0.950 |
| USD_CHF    |                3 |  431 | 0.538 | 0.925 | 1.555 |        1.017 |
| USD_CHF    |                4 |  430 | 0.608 | 0.904 | 1.561 |        0.952 |
| USD_CHF    |                5 |  431 | 0.637 | 1.034 | 1.818 |        1.181 |
| USD_JPY    |                0 | 2153 | 0.517 | 0.905 | 1.626 |        1.109 |
| USD_JPY    |                1 |  431 | 0.453 | 0.809 | 1.426 |        0.972 |
| USD_JPY    |                2 |  430 | 0.482 | 0.818 | 1.416 |        0.935 |
| USD_JPY    |                3 |  431 | 0.533 | 0.901 | 1.646 |        1.114 |
| USD_JPY    |                4 |  430 | 0.549 | 0.917 | 1.580 |        1.031 |
| USD_JPY    |                5 |  431 | 0.649 | 1.086 | 1.961 |        1.312 |
| USD_SEK    |                0 | 2153 | 0.589 | 0.934 | 1.528 |        0.939 |
| USD_SEK    |                1 |  431 | 0.542 | 0.875 | 1.348 |        0.806 |
| USD_SEK    |                2 |  430 | 0.569 | 0.924 | 1.590 |        1.021 |
| USD_SEK    |                3 |  431 | 0.595 | 0.934 | 1.501 |        0.906 |
| USD_SEK    |                4 |  430 | 0.597 | 0.956 | 1.511 |        0.914 |
| USD_SEK    |                5 |  431 | 0.646 | 1.019 | 1.671 |        1.025 |
| XAU_USD    |                0 | 2142 | 0.560 | 0.910 | 1.614 |        1.054 |
| XAU_USD    |                1 |  429 | 0.525 | 0.883 | 1.433 |        0.908 |
| XAU_USD    |                2 |  428 | 0.530 | 0.850 | 1.499 |        0.969 |
| XAU_USD    |                3 |  428 | 0.567 | 0.888 | 1.678 |        1.110 |
| XAU_USD    |                4 |  428 | 0.576 | 0.894 | 1.578 |        1.003 |
| XAU_USD    |                5 |  429 | 0.609 | 1.039 | 2.016 |        1.407 |

### HAR baseline — in-sample R² on log(daily range)

**This is the mechanical baseline any range model must beat.** Reporting a prior-day effect without it would be rediscovering volatility clustering. `HAR_adds` is what the 5- and 22-day memory contributes beyond yesterday alone.

| symbol     |    n |   r2_prior_day |   r2_HAR_1_5_22 |   HAR_adds |
|:-----------|-----:|---------------:|----------------:|-----------:|
| XAU_USD    | 2120 |          0.539 |           0.678 |      0.139 |
| NAS100_USD | 1954 |          0.505 |           0.613 |      0.109 |
| BTC_USD    | 1807 |          0.475 |           0.577 |      0.102 |
| SPX500_USD | 1954 |          0.471 |           0.550 |      0.079 |
| ETH_USD    | 1807 |          0.427 |           0.525 |      0.098 |
| USD_JPY    | 2131 |          0.377 |           0.495 |      0.118 |
| JP225_USD  | 2023 |          0.355 |           0.484 |      0.129 |
| US30_USD   | 1954 |          0.391 |           0.476 |      0.085 |
| US2000_USD | 1953 |          0.351 |           0.455 |      0.104 |
| DE30_EUR   | 1989 |          0.247 |           0.371 |      0.124 |
| USD_SEK    | 2131 |          0.212 |           0.358 |      0.145 |
| EUR_USD    | 2131 |          0.155 |           0.285 |      0.130 |
| USD_CAD    | 2131 |          0.161 |           0.276 |      0.115 |
| GBP_JPY    | 2130 |          0.193 |           0.274 |      0.081 |
| GBP_AUD    | 2130 |          0.153 |           0.234 |      0.081 |
| GBP_USD    | 2131 |          0.124 |           0.227 |      0.104 |
| USD_CHF    | 2131 |          0.124 |           0.209 |      0.085 |
| GBP_NZD    | 2130 |          0.114 |           0.202 |      0.088 |

---

## D. THE 3/6/9 HOUR SEQUENCE — tested, with the confound controlled

From a 17:00 ET day start, hours 3, 6 and 9 are **19:00–20:00, 22:00–23:00 and 01:00–02:00 ET** — all three fall inside the Asia block. A raw comparison against all 24 hours would therefore just rediscover that Asia is quiet. The decisive comparison is **against the other Asia hours only** (hours 1–10), which removes the session confound entirely.

Bar to clear: over 21 independent cells the expected maximum |t| under pure noise is ≈ √(2 ln 21) ≈ **2.47**, so a ratio near 1.00 is the null, not a weak signal.

### Hours 3/6/9 versus the other Asia hours (`share_ext`, mean)

| symbol   |   mean_369 |   mean_other_asia |   ratio |   best_369_rank_of_24 |
|:---------|-----------:|------------------:|--------:|----------------------:|
| XAU_USD  |      0.049 |             0.060 |   0.809 |                     3 |
| USD_JPY  |      0.048 |             0.066 |   0.729 |                     3 |
| EUR_USD  |      0.034 |             0.051 |   0.671 |                     9 |
| GBP_USD  |      0.034 |             0.052 |   0.660 |                    12 |
| GBP_JPY  |      0.041 |             0.063 |   0.656 |                     4 |
| GBP_AUD  |      0.043 |             0.069 |   0.618 |                     4 |
| USD_CAD  |      0.032 |             0.053 |   0.603 |                    10 |
| ETH_USD  |      0.040 |             0.070 |   0.578 |                     4 |
| BTC_USD  |      0.039 |             0.069 |   0.564 |                     4 |
| USD_SEK  |      0.031 |             0.055 |   0.555 |                    11 |
| GBP_NZD  |      0.038 |             0.072 |   0.523 |                     5 |
| USD_CHF  |      0.028 |             0.056 |   0.496 |                    10 |

> `best_369_rank_of_24` is where the best of the three ranks among all 24 hours. A genuine effect would put it near 1.


### Pooled hour-of-day profile (median across usable instruments)

|   hr |   share_ext |   share_path | is_369   |
|-----:|------------:|-------------:|:---------|
|    1 |       0.159 |        0.037 | False    |
|    2 |       0.050 |        0.029 | False    |
|    3 |       0.052 |        0.035 | True     |
|    4 |       0.064 |        0.042 | False    |
|    5 |       0.047 |        0.036 | False    |
|    6 |       0.027 |        0.030 | True     |
|    7 |       0.022 |        0.028 | False    |
|    8 |       0.021 |        0.029 | False    |
|    9 |       0.029 |        0.033 | True     |
|   10 |       0.047 |        0.048 | False    |
|   11 |       0.052 |        0.053 | False    |
|   12 |       0.048 |        0.051 | False    |
|   13 |       0.033 |        0.046 | False    |
|   14 |       0.033 |        0.046 | False    |
|   15 |       0.032 |        0.047 | False    |
|   16 |       0.066 |        0.064 | False    |
|   17 |       0.053 |        0.066 | False    |
|   18 |       0.047 |        0.064 | False    |
|   19 |       0.027 |        0.053 | False    |
|   20 |       0.017 |        0.043 | False    |
|   21 |       0.016 |        0.039 | False    |
|   22 |       0.016 |        0.036 | False    |
|   23 |       0.009 |        0.030 | False    |
|   24 |       0.005 |        0.024 | False    |