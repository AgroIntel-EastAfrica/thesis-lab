# Experiment: forecast-confidence-calibration

- **Owner:**
- **Started:**
- **Status:** active
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Objective 4 / RQ4, motivated directly by Guo et
  al. 2017 ("On Calibration of Modern Neural Networks"), which the paper
  itself cites for exactly this concern

## Objective

Objective 4 asks the system to know when its own confidence is
untrustworthy, not just to report a confidence number. This session
shipped two real, narrower pieces of that: forecast intervals are now
persisted (`forecast_evaluations.predicted_lower`/`predicted_upper`,
migration 046) so interval coverage becomes checkable, and
`RecommendationEngine`'s recommendations now get withheld below a
confidence/evidence floor (`_apply_evidence_gate`). Neither of those is
the same as *calibration* in Guo et al.'s sense: does the model's stated
confidence (or `ForecastPoint.confidence`, or `mean_confidence`) actually
match its empirical hit rate? This experiment evaluates that directly,
once real production data exists to evaluate it against.

## Hypothesis

The forecaster's stated confidence values are currently a hand-set
constant per layer (0.80 for the sub-national/Prophet layer, 0.70 for the
untrained fallback — see `services/forecasting/price.py`), not something
derived from the model's own historical accuracy. The hypothesis is that
these hand-set values are **not** well-calibrated — i.e. an 80%-confidence
interval will not actually contain the real outcome ~80% of the time —
because nothing in the current pipeline has ever measured this. This is
exactly the kind of claim Guo et al.'s work warns against taking on
faith.

## Core Variables

- **Held constant:** nothing changes in the production forecaster for
  this experiment — it's purely observational/evaluative.
- **Measured:** for every row in `forecast_evaluations` with both
  `actual_price` and `predicted_lower`/`predicted_upper` populated,
  whether `predicted_lower <= actual_price <= predicted_upper` — the same
  check `apps/workers/forecasting.py::_compute_coverage` already
  performs in production, but this experiment can slice it by
  commodity, country, and forecast horizon in ways the production metric
  (a single per-commodity Prometheus gauge) doesn't expose.

## Success Metrics

- Decided before looking at results: real coverage within ±10 percentage
  points of the stated 80% confidence (i.e. 70-90% actual coverage) counts
  as "reasonably calibrated"; anything outside that range is a real,
  actionable finding that the hand-set confidence values need to become
  data-derived rather than constants.
- **Known real blocker, confirmed via a live, read-only production query
  on 2026-09-11**: `forecast_evaluations` currently has 0 rows in
  production. This experiment cannot produce a real result until the
  scheduled forecasting workers actually run against production and
  accumulate rows — which is itself gated on the open "confirm cloud
  deployment status" item in `product/PRODUCTION_AUDIT.md`. Document that
  blocker honestly in Results rather than fabricating a calibration
  number from synthetic data and presenting it as real.

## Results

*Not yet run — blocked on real production data existing (see Success
Metrics). Revisit once `forecast_evaluations` has accumulated rows with
resolved `actual_price` values.*
