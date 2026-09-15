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
  on 2026-09-11, re-confirmed 2026-09-13**: `forecast_evaluations`
  currently has 0 rows in production (both checks: `total rows: 0`,
  `pending (actual_price null): 0` — the table isn't even accumulating
  *unevaluated* forecasts, meaning `update_price_forecasts` itself has
  never successfully written a row here, not just that
  `evaluate_forecast_accuracy` hasn't caught up yet). This experiment
  cannot produce a real result until the scheduled forecasting workers
  actually run against production and accumulate rows — which is itself
  gated on the open "confirm cloud deployment status" item in
  `product/PRODUCTION_AUDIT.md`. Document that blocker honestly in
  Results rather than fabricating a calibration number from synthetic
  data and presenting it as real.

## Results

**Blocker resolved 2026-09-13**: root-caused why the table was empty
(neither `deploy-production.yml` nor `deploy-staging.yml` actually
deploys anything — see `product/PRODUCTION_AUDIT.md`'s 2026-09-13 entry)
and fixed a real, independent bug in `railway.toml` found along the way
(worker missing 3 of 6 real queues). Stood up a local Celery worker +
beat against the real production Supabase to unblock this experiment
directly rather than wait on a full redeploy, then called
`update_price_forecasts` and `evaluate_forecast_accuracy` directly.

**First real calibration number, ever, for this system:**

```
evaluated: 96, calibration (interval coverage): 0.3854, mae: 99.53, rmse: 279.89, mape: 8.24
```

**Hypothesis CONFIRMED, strongly.** Real interval coverage is **38.5%**
against a stated ~80% confidence level — real outcomes fall inside the
claimed interval less than half as often as the stated confidence
implies. This is exactly the Guo-et-al.-style overconfidence the
hypothesis predicted: the hand-set 0.80/0.70 confidence constants in
`services/forecasting/price.py` are not calibrated to real accuracy,
and the gap is not small (38.5% vs. 80% is a ~2x miscalibration, not
a rounding-level discrepancy).

**Real bug found and fixed while producing this result**: the
`evaluate_forecast_accuracy` run also surfaced `Failed to record
performance: Object of type datetime is not JSON serializable` from
`ContinuousLearning.record_model_performance` (`services/recommendations/feedback.py`).
Pydantic's `.dict()` (v1-style alias, still present under Pydantic 2.x)
leaves `datetime` fields as native Python objects rather than ISO
strings, which the Supabase client's JSON encoding then rejects — a
systemic issue affecting all 4 `.dict()` call sites in that file
(feedback ingestion, 2 retraining-trigger paths, model performance).
Tests never caught this because they mock the Supabase call, so the
real serialization path never ran. Fixed by switching all 4 to
`.model_dump(mode="json")`, which correctly serializes datetimes.
Verified: existing test suite still passes; the direct call now
completes with no error.

**Caveat on sample size**: n=96, all from a single day's forecasts
(today's `target_date` only) — one data point per (country, commodity)
pair, not yet a real longitudinal sample. The 38.5% figure is a real,
first measurement, not yet a stable estimate; re-run after several
more days of `evaluate_forecast_accuracy` running (once real deployment
is confirmed, or via repeated manual triggers) before treating 38.5% as
the final number for publication — but the direction (badly
miscalibrated) is unlikely to reverse.

**Related real finding, 2026-09-15** (full detail in
`thesis-lab/active_tests/regional-equity-audit/experiment_blueprint.md`'s
"Post-fix verification + a bigger real finding" section): a second,
later evaluation batch surfaced a second, distinct source of
miscalibration beyond the hand-set confidence constants this experiment
targets — `BASE_PRICES_USD` (the synthetic training anchor
`PriceForecaster.fit()` uses) turns out to be badly wrong for coffee
and tea specifically in Rwanda and Burundi (off by ~10-13x from real
FAOSTAT levels) and Kenya (off by ~2x, opposite direction), never
having been cross-checked against real data. This means at least part
of this system's real miscalibration is a bad training anchor, not
just an uncalibrated confidence number — worth separating the two
causes before concluding a fix (e.g. data-derived confidence) would
close the whole gap on its own.
