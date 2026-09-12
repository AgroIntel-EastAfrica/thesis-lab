# Experiment: shock-period-forecast-accuracy

- **Owner:**
- **Started:**
- **Status:** active
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Methodology section: "Evaluation will include
  MAE, RMSE, MAPE, weighted interval scores, calibration error and
  directional accuracy, **with particular attention to performance
  during market shocks rather than only average historical
  performance**." RQ2.

## Objective

This is an evaluation *protocol*, not a new model — it applies to
whichever forecaster is currently live in production
(`services/forecasting/price.py`) and can be re-run against any of the
other experiments in this sandbox once they produce a candidate model.
Every accuracy number this session has referenced so far
(`_compute_error_metrics`'s MAPE, the calibration coverage check) is an
*average* over whatever forecasts happened to resolve — nothing
specifically isolates performance during a real historical shock (a
drought, a border closure, a price spike from a real news event) versus
an ordinary week. The paper explicitly calls this out as a distinct,
necessary lens.

## Hypothesis

The production forecaster's real MAPE during real historical shock
windows (identifiable after the fact from real GDELT/news signals,
`services/alerts/live_generator.py`'s climate alerts, or large
day-over-day price moves in `market_prices`) will be measurably worse
than its average MAPE — i.e. the model is quietly less reliable exactly
when reliability matters most, and today's single aggregate metric
hides that.

## Core Variables

- **Held constant:** the forecaster and metric formulas — reuse
  `apps/workers/forecasting.py::_compute_error_metrics` unchanged so
  results are directly comparable to the production Prometheus gauges.
- **Varied:** the evaluation *window* — split real evaluated forecasts
  (once `forecast_evaluations` has accumulated real rows — see
  `forecast-confidence-calibration`'s known blocker) into "shock" vs.
  "normal" periods using an objective, pre-registered definition (e.g. a
  real climate alert was active, or day-over-day price move exceeded a
  fixed threshold) decided before looking at the accuracy numbers, not
  after.

## Success Metrics

- Report MAPE, RMSE, and directional accuracy separately for shock vs.
  normal windows — the finding is real and worth acting on if the gap
  is large (e.g. >50% relative MAPE degradation during shocks), not
  necessarily if it's small.
- This experiment's real value is in the *methodology* — once built, it
  should be re-runnable against every other forecasting experiment in
  this sandbox (the multimodal, graph, and transformer variants), not
  just the current production baseline.

## Results

*Not yet run — same real-data blocker as `forecast-confidence-calibration`:
needs `forecast_evaluations` rows with resolved `actual_price` values,
plus enough real shock events in that window to be statistically
meaningful.*
