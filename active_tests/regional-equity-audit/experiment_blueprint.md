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

**Run 2026-09-13** via `thesis-lab/active_tests/regional-equity-audit/scripts/run_audit.py`
(real, read-only — no writes). Two parts, one blocked, one real:

**Forecast accuracy (MAPE) — blocked, not just "not yet run":**
`forecast_evaluations` has 0 rows for all 8 countries (confirmed
independently by `forecast-confidence-calibration`'s own audit, same
finding, same date). Worse than a timing gap: even once populated, a
fair MAPE comparison for UG/SS/SO/CD may not be *possible* with current
data sources — `get_daily_price` for these countries walks from a
`BASE_PRICES_USD` synthetic anchor (no real FAOSTAT/EATTA/EAX/IMF price
data reaches them), so "actual_price" for a data-sparse country isn't a
real market observation to forecast against — it's a formula-generated
value. That itself is a real, reportable finding about the depth of the
equity gap: it's severe enough that even *auditing* it accurately is
hard for the affected countries.

**RecommendationEngine (confidence, evidence_sufficient, supporting_signals) — real, live comparison:**

| Country | n_recs | avg_confidence | evidence_sufficient_rate | avg_supporting_signals |
|---|---|---|---|---|
| KE (rich) | 21 | 84.05 | 0.286 | 1.62 |
| TZ (rich) | 24 | 85.42 | 0.250 | 1.54 |
| RW (rich) | 13 | 77.31 | 0.462 | 2.00 |
| BI (rich) | 17 | 81.47 | 0.353 | 1.76 |
| UG (sparse) | 24 | 85.42 | 0.250 | 1.54 |
| SS (sparse) | 16 | 80.63 | 0.375 | 1.81 |
| SO (sparse) | 11 | 74.09 | 0.545 | 2.18 |
| CD (sparse) | 18 | 82.22 | 0.333 | 1.72 |
| **data-rich avg** | | **82.06** | **0.338** | **1.73** |
| **data-sparse avg** | | **80.59** | **0.376** | **1.81** |

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

**Next step**: this experiment can be considered concluded for its
`RecommendationEngine` half (real result: hypothesis not confirmed,
weakly reversed on 2 of 3 metrics). Its MAPE half stays open, blocked on
the same operational gap `forecast-confidence-calibration` is blocked
on.
