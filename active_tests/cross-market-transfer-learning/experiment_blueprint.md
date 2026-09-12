# Experiment: cross-market-transfer-learning

- **Owner:**
- **Started:**
- **Status:** active
- **Paper:** Paper — "Cross-Market Transfer Learning for Agricultural
  Forecasting in Data-Sparse Economies"
- **Source:** 15-paper publication roadmap revision (2026-09-12), adopted
  from an external reorganization proposal as a genuinely new thread not
  covered by the prior 12-paper structure.

## Objective

`services/forecasting/price.py`'s three layers (LOCAL/XGBoost,
SUB_NATIONAL/Prophet, NATIONAL/ensemble) are each trained fresh, per
`(country_code, commodity)` call, from that country's own history alone
(confirmed by reading `get_price_forecast`'s real call path — every
model fit happens inside a single country/commodity's `PipelineContext`,
with no shared or pretrained parameters across countries). For a
data-sparse country (e.g. SS, with far fewer real historical price
points than UG or KE), this means the model has less real data to learn
from and nothing borrowed from richer neighbors. This experiment tests
whether transferring structure learned from data-rich EAC markets
(UG/KE/TZ/RW) improves forecasts for data-sparse ones (SS/SO/CD/BI).

## Hypothesis

A model pretrained on pooled, data-rich EAC market history and
fine-tuned (or used as a prior) for a specific data-sparse country will
achieve lower MAPE for that country than the current from-scratch,
single-country training — particularly for commodities traded across
multiple EAC countries, where price dynamics are plausibly correlated
(e.g. regional trade flows, shared growing seasons).

## Core Variables

- **Held constant:** the evaluation commodities and forecast horizons
  used elsewhere in this lab (`shock-period-forecast-accuracy`'s real
  MAE/RMSE/MAPE protocol), so results are comparable.
- **Varied:** training regime — (a) current per-country from-scratch
  training (control), (b) pooled-then-fine-tuned or transfer-learned
  variant, source countries = the data-rich set (UG/KE/TZ/RW per
  `regional-equity-audit`'s own real data-availability split).
- **Real data:** real historical prices already available to
  `services/forecasting/price.py` for all countries — no synthetic data.

## Success Metrics

- Decided before looking at results: transfer learning must improve
  MAPE for at least 2 of the 4 data-sparse countries (SS/SO/CD/BI) by a
  real, measurable margin over the from-scratch baseline to justify the
  added training complexity.
- If it doesn't help (e.g. EAC markets turn out to be less correlated
  than assumed, or a data-sparse country's dynamics are genuinely
  distinct), that's a legitimate, reportable result — directly relevant
  to `data-centric-ai-low-resource-markets`'s data-vs-model question.

## Results

*Not yet run.*
