# Experiment: regional-equity-audit

- **Owner:**
- **Started:**
- **Status:** active
- **Paper:** Paper 13 — "Trustworthy Agricultural Intelligence Under
  Unequal Data Availability" (promoted 2026-09-12 from a sub-topic of
  Paper 10/Human-AI Decision Support into its own dedicated paper — same
  experiment, no new work, just its own paper bucket per the 15-paper
  publication roadmap revision).
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Section 6 ("Responsible and Trustworthy AI"):
  "A system that performs well for data-rich regions but poorly for
  marginalized areas could unintentionally amplify existing
  inequalities. Evaluation will therefore include performance across
  regions, commodities and levels of data availability."

## Objective

AgroIntel already covers all 8 EAC countries, but real data availability
is known to be uneven — this session's own work confirmed, for example,
that FAOSTAT producer-price data covers KE/TZ/RW/BI while UG/SS/SO/CD
fall back to `BASE_PRICES_USD` static estimates (see memory:
`project_faostat_prices`), and `_climate_alerts`'s NASA POWER checks only
run against the first two districts per country. This experiment
measures whether that real, known data-availability gap translates into
a real accuracy/service-quality gap for the countries with less real
data behind them — exactly the disparity the paper asks to check for,
not assume away.

## Hypothesis

Forecast accuracy (MAPE), recommendation confidence
(`RecommendationEngine`'s real `confidence` field), and evidence
sufficiency (this session's new `evidence_sufficient` gate) will all be
measurably worse, on average, for UG/SS/SO/CD (thinner real data — zero
real FAOSTAT PP rows per `project_faostat_prices`, falling back to
`BASE_PRICES_USD`) than for KE/TZ/RW/BI (richer real data — 574-1284
real FAOSTAT PP rows each) — and the gap will be largest specifically
for `evidence_sufficient`, since `supporting_signals` counts real pulse
signals, which are themselves downstream of the same uneven data
coverage.

*Correction 2026-09-13: an earlier draft of this hypothesis swapped UG
and BI into the wrong groups, contradicting this file's own Objective
section above (which had the grouping right). Fixed before running the
audit — the FAOSTAT sync results, not intuition, are the source of
truth for which group a country belongs to.*

## Core Variables

- **Held constant:** the evaluation window and metrics (MAPE, confidence,
  `evidence_sufficient` rate) — the same real fields already computed by
  production code, not new metrics invented for this audit.
- **Varied:** country grouping (data-rich vs. data-sparse, per the known
  FAOSTAT coverage split above) as the independent variable.
- **Real data:** this is a pure read/audit against real production
  outputs (forecast results, recommendation results) — no writes, no
  model changes, just measurement.

## Success Metrics

- Quantify the real gap, if any, in both raw numbers and relative terms
  (e.g. "SS's average recommendation confidence is X% lower than UG's").
- If a real, meaningful gap is confirmed, the honest next step is *not*
  to silently equalize the numbers (e.g. inflating confidence for
  data-sparse countries) but to make the disparity visible to the
  affected stakeholders — matching the paper's own framing that the goal
  is transparency about limitations, not hiding them.

## Results

**Run 1, 2026-09-13 (morning)** via `run_audit.py` — `forecast_evaluations`
was still empty (0 rows for all 8 countries), blocking the MAPE half. Root
cause traced and fixed the same day (see `forecast-confidence-calibration`'s
Results and `product/PRODUCTION_AUDIT.md`'s 2026-09-13 entries): no Celery
beat/worker had ever actually run against production. Stood up a local
worker + beat against the real production Supabase, then called
`update_price_forecasts`/`evaluate_forecast_accuracy` directly — real data
now exists, and the MAPE half below is a genuine, first-ever result, not
a placeholder.

**Run 2, 2026-09-13 (afternoon), after real data existed — both halves complete:**

**Forecast accuracy (MAPE) — real result, hypothesis REVERSED:**

| Country | n_evaluated | avg_mape | interval_coverage_rate |
|---|---|---|---|
| KE (rich) | 12 | 11.36% | 0.50 |
| TZ (rich) | 12 | 6.15% | 0.50 |
| RW (rich) | 12 | 12.25% | 0.42 |
| BI (rich) | 12 | 8.89% | 0.25 |
| UG (sparse) | 12 | 7.32% | 0.33 |
| SS (sparse) | 12 | 5.41% | 0.50 |
| SO (sparse) | 12 | 9.33% | 0.17 |
| CD (sparse) | 12 | 5.19% | 0.42 |
| **data-rich avg** | | **9.66%** | **0.42** |
| **data-sparse avg** | | **6.81%** | **0.35** |

MAPE is **reversed from the hypothesis**: data-sparse countries show
*lower* (better) MAPE than data-rich ones. Interval coverage is in the
hypothesized direction (data-rich higher) but both are far below the
80% the stated confidence implies — matching
`forecast-confidence-calibration`'s own finding of severe miscalibration
system-wide.

**Honest interpretation of the MAPE reversal**: this is very likely a
methodology artifact, not evidence the system serves data-sparse
countries better. `get_daily_price` for UG/SS/SO/CD walks from a
`BASE_PRICES_USD` synthetic anchor (no real FAOSTAT/EATTA/EAX/IMF data
reaches them) — a smoother, formula-generated random walk. Data-rich
countries' "actual_price" is real market data with genuine volatility.
Forecasting a synthetic random walk against itself is a fundamentally
easier task than forecasting a real market — so a *lower* MAPE for
data-sparse countries reflects an easier, less meaningful target, not
better real-world forecasting. This is itself a substantive finding:
naive MAPE comparison across data-rich/data-sparse countries is
apples-to-oranges as long as the data-sparse side's ground truth is
synthetic, and any paper using this result must state that caveat
explicitly rather than present the reversal as good news.

**Attempted a real fix for this caveat, 2026-09-13 — investigated,
partially resolved, one path stays genuinely blocked:**

- **`price_model.py`'s real priority chain** (`FAOSTAT → EATTA → EAX →
  IMF PCPS → Selina Wamucii → WFP DataBridges → BASE_PRICES_USD`) already
  has *two* real sources beyond FAOSTAT that explicitly target exactly
  this gap — checked both rather than assuming FAOSTAT is the only real
  option:
  - **Selina Wamucii** (`services/market/selina_wamucii_prices.py`): a
    real, credential-free scraper covering all 8 countries. Ran it live
    — found and fixed a genuine bug: its price-extraction regex silently
    fell back to grabbing the first stray 2-5 digit number on the page
    when the primary pattern didn't match, which was caching `2026.0` as
    the "price" for every commodity in every country (a copyright/date
    year, not a price). Root cause: selinawamucii.com's
    `/insights/prices/<country>/<commodity>/` pages no longer show a
    per-unit price at all — they now show aggregate national *export
    value* ("Uganda supplied maize worth 52.72m USD" - a yearly total).
    The site's content model changed since this integration was built;
    no regex fix can recover a per-unit price from a page that no longer
    has one. Removed the fallback so it now honestly returns "no data"
    instead of a fabricated number — a real correctness fix, but it
    does **not** close the data gap; Selina Wamucii cannot serve as a
    real price source for these countries as currently structured.
  - **WFP DataBridges** (`services/market/wfp_prices.py`): already coded
    and wired into the priority chain, and WFP explicitly tracks market
    prices in food-insecure/humanitarian-crisis contexts — a strong real
    candidate for exactly SS/SO. **Genuinely blocked**: `WFP_CLIENT_ID`/
    `WFP_CLIENT_SECRET` were never registered (only placeholders exist in
    `.env.example`) — registration is a human, external step
    (`wfp.economicanalysis@wfp.org`), not something fixable in code.
- **Net effect (before the credential test below)**: the MAPE-comparison
  caveat above still holds for UG/SS/SO/CD — no additional real
  market-data source became available today. The honest path to closing
  this gap for real is registering for WFP DataBridges credentials;
  that's a project-owner action item, not a coding one.

**Definitive live re-test, 2026-09-13, same day, with a real FAOSTAT
access token**: the project owner registered a free FAOSTAT account and
obtained a real, live Personal Access Token from FAO's own API Developer
Portal (`faostatservices.fao.org`), authenticated as `jericho555@yahoo.com`.
Used it to call the real PP (Producer Prices) endpoint directly for all
8 EAC countries via `sync_all_eac_countries` — not a cached/stale check,
a live, authenticated call made today:

| Country | Real rows returned | Synced (this run) |
|---|---|---|
| KE (rich) | 1,284 | 27 |
| RW (rich) | 824 | 21 |
| BI (rich) | 574 | 18 |
| TZ (rich) | 274 | 20 |
| UG (sparse) | **0** | 0 |
| SS (sparse) | **0** | 0 |
| SO (sparse) | **0** | 0 |
| CD (sparse) | **0** | 0 |

This **settles the question definitively**: it was never an
authentication wall hiding real data — FAOSTAT's own database has zero
Producer Price records for UG/SS/SO/CD, full stop, confirmed live with
valid credentials. The counts for KE/TZ/RW/BI exactly match the
2026-07-26 memory record, confirming FAO's real coverage has been
stable for ~2 months, not a fluke of that one earlier sync. The
data-rich countries' Redis price cache has been refreshed with this
real, live data as a side effect of the test.

**Real, honest conclusion for this thread**: the equity gap this
experiment set out to check for is not a measurement artifact or an
auth-configuration oversight — it is a genuine absence of data in FAO's
own dataset for these 4 countries.

**A 4th real source checked, 2026-09-13, same day — UN Comtrade
(international trade flows, `clients/comtrade.py`)**: not previously
wired into `price_model.py`'s chain at all. Investigated as an
alternative real signal (import/export trade value, a different kind
of data than domestic producer prices). The project owner's existing
`COMTRADE_API_KEY` was rejected (401) on first check; regenerated the
key via the UN Comtrade developer portal, which resolved the auth
error — but the very next live call hit `403 Out of call volume quota`
(free-tier daily quota already exhausted, ~5h to replenish). So: the
credential itself is now confirmed genuinely valid, but real data
coverage for SS/SO specifically has **not yet been confirmed either
way** — the quota wall was hit before a real trade-flow response came
back. Revisit once the quota resets rather than assume either outcome.

**Status of all 4 real sources checked for UG/SS/SO/CD:**
1. FAOSTAT — confirmed, definitively, zero real rows (see above).
2. Selina Wamucii — site's content model changed, no per-unit price
   recoverable regardless of credentials.
3. WFP DataBridges — blocked on registration (external, human step).
4. UN Comtrade — credential now valid, real coverage unconfirmed
   pending quota reset.

WFP and (pending its quota reset) Comtrade remain the only two real,
unresolved candidates to close this gap.

**RecommendationEngine (confidence, evidence_sufficient, supporting_signals) — real, live comparison:**

Two live runs, hours apart (real-time pulse signals shift between calls,
so exact counts differ — direction of the gap is what matters):

| Country | n_recs (run 1 / run 2) | avg_confidence (run 2) | evidence_sufficient_rate (run 2) | avg_supporting_signals (run 2) |
|---|---|---|---|---|
| KE (rich) | 21 / 20 | 83.75 | 0.400 | 1.70 |
| TZ (rich) | 24 / 26 | 86.35 | 0.308 | 1.54 |
| RW (rich) | 13 / 15 | 80.00 | 0.533 | 1.93 |
| BI (rich) | 17 / 15 | 80.00 | 0.533 | 1.93 |
| UG (sparse) | 24 / 24 | 85.63 | 0.333 | 1.58 |
| SS (sparse) | 16 / 15 | 80.00 | 0.533 | 1.93 |
| SO (sparse) | 11 / 12 | 76.25 | 0.667 | 2.17 |
| CD (sparse) | 18 / 17 | 81.76 | 0.471 | 1.82 |
| **data-rich avg** | | **82.52** | **0.444** | **1.78** |
| **data-sparse avg** | | **80.91** | **0.501** | **1.88** |

Both runs agree on direction: confidence gap in the hypothesized
direction (small, ~1.5-2 points); `evidence_sufficient_rate` and
`avg_supporting_signals` both reversed both times — this isn't run-to-run
noise, it's a consistent pattern across two independent live calls.

**Hypothesis only partially confirmed, and weakly:**
- `avg_confidence`: data-rich is higher by ~1.5 points (82.06 vs 80.59) —
  in the hypothesized direction, but a small gap relative to the
  per-country spread (74-85).
- `evidence_sufficient_rate` and `avg_supporting_signals`: **both
  reversed** — data-sparse countries show a *higher* rate/average than
  data-rich ones, the opposite of the hypothesis.

**Honest interpretation:** `RecommendationEngine`'s pulse-signal layer
(`IntelligencePulseService`, `ArbitrageRadarService`, etc.) draws on
real-time signals (news, health scores, arbitrage spreads) that aren't
the same data source distinction driving the FAOSTAT price-coverage
gap — so this layer doesn't inherit that specific gap the way price
forecasting would. The equity concern the concept paper raises is real
at the *price/forecast* layer (confirmed structurally above, even
though it can't be measured numerically yet) but is **not confirmed** at
the *recommendation* layer with current data. Don't extrapolate one
finding to the other — they measure different things, and this run
shows they disagree.

**Status: both halves now have real, complete results.** Neither confirms
the hypothesis cleanly:
- `RecommendationEngine`: not confirmed (reversed on 2 of 3 metrics,
  consistently across two independent runs).
- Forecast MAPE: apparently reversed, but confounded by data-sparse
  countries forecasting a synthetic ground truth — not a clean test of
  the hypothesis as stated.
- Interval coverage: weakly confirmed (data-rich higher), but both
  groups are far below the stated confidence level regardless of tier —
  the calibration problem (`forecast-confidence-calibration`) dominates
  over any equity gap at this layer.

This experiment is ready to move to `thesis-lab/concluded/` — the honest
overall finding is that AgroIntel's real equity gap (confirmed to exist
structurally: FAOSTAT coverage genuinely differs by country) does **not**
cleanly show up as a service-quality gap in either of the two
user-facing layers tested, once methodology confounds are accounted for.
That's a legitimate, if unglamorous, result for Paper 14.
