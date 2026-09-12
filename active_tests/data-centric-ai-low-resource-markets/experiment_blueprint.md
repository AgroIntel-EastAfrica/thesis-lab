# Experiment: data-centric-ai-low-resource-markets

- **Owner:**
- **Started:**
- **Status:** active
- **Paper:** Paper — "Data-Centric AI for Agricultural Intelligence in
  Low-Resource Environments"
- **Source:** 15-paper publication roadmap revision (2026-09-12), adopted
  from an external reorganization proposal as a genuinely new thread not
  covered by the prior 12-paper structure.

## Objective

Every other forecasting/reasoning experiment in this lab asks "which
model/architecture performs best?" This one asks the orthogonal
question: for AgroIntel's real, already-known data problems — missing
FAOSTAT coverage for UG/SS/SO/CD (falls back to static
`BASE_PRICES_USD`, per memory `project_faostat_prices`), inconsistent
country/district identifiers across sources, and gaps `agribench-ea-benchmark`
will end up labeling — **does fixing the data move the needle more than a
bigger/better model would?** This is the "model-centric vs. data-centric"
tradeoff AgroIntel has never explicitly measured.

## Hypothesis

For the specific case of data-sparse countries (UG/SS/SO/CD — zero real
FAOSTAT PP rows per `project_faostat_prices`, corrected 2026-09-13 from
an earlier draft that had this swapped with the data-rich KE/TZ/RW/BI
group), a real improvement in the reliability of upstream data (e.g.
actually resolving vs. falling back to `BASE_PRICES_USD`) will reduce forecast
MAPE by more than swapping the NATIONAL-layer ensemble weights or model
family would — i.e. the ceiling on forecast quality for these countries
is currently set by data availability, not model choice, and no amount
of model tuning in `services/forecasting/price.py` will close that gap.

## Core Variables

- **Held constant:** the forecasting models themselves (XGBoost/Prophet/
  ensemble, as already implemented) — this experiment doesn't propose new
  architectures.
- **Varied:** (a) current real data pipeline (control — real FAOSTAT
  where available, static fallback where not), (b) a data-quality
  intervention (e.g. borrowing regional-average real prices instead of a
  fixed constant fallback, or flagging + excluding the lowest-confidence
  cells rather than silently substituting them).
- **Real data:** reuses `agribench-ea-benchmark`'s per-cell
  `data_quality`/`data_source` labeling once available, rather than
  inventing a separate labeling scheme.

## Success Metrics

- Decided before looking at results: if the data intervention improves
  MAPE for data-sparse countries by a larger margin than any single model
  change already tried in `shock-period-forecast-accuracy` or
  `transformer-forecasting-baseline`, that's real evidence for
  prioritizing data investment over model investment for this system —
  a genuinely actionable, non-obvious finding either way.
- Must report the real economic cost of the current static fallback
  (`BASE_PRICES_USD`) in the same units as the other forecasting
  experiments' MAE/RMSE/MAPE, so results are directly comparable.

## Results

*Not yet run — depends on `agribench-ea-benchmark`'s data-quality
labeling being available first.*
