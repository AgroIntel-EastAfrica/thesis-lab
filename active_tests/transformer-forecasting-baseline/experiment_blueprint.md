# Experiment: transformer-forecasting-baseline

- **Owner:**
- **Started:**
- **Status:** active
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Section 2 ("Proposed Technical Framework")
  explicitly names Temporal Fusion Transformers (Lim et al. 2021) as "a
  strong baseline for heterogeneous multi-horizon forecasting" and
  PatchTST (Nie et al. 2023) as "a contemporary Transformer-based
  comparison"; Objective 2 / RQ2.

## Objective

This is a model-architecture question, distinct from
`multimodal-price-representation` (which is about *input features*, not
architecture). AgroIntel's real forecaster
(`services/forecasting/price.py`) uses XGBoost (LOCAL layer), Prophet
(SUB_NATIONAL layer), and a 60/40 weighted ensemble of the two
(NATIONAL layer) — never a Transformer-based sequence model. The paper
names two specific, well-established alternatives worth comparing
against directly.

## Hypothesis

A Temporal Fusion Transformer or PatchTST, trained on the same real
historical price series the production forecaster uses, will *not*
meaningfully outperform the current Prophet+XGBoost ensemble on
short-horizon (7-30 day) forecasts, given how little historical data
each EAC country/commodity pair actually has (`get_price_history`'s real
backfill windows are short) — Transformer architectures typically need
more training data than gradient-boosted trees or classical
decomposition models to earn their added complexity. This is a real,
falsifiable prediction, not an assumption that "newer must be better."

## Core Variables

- **Held constant:** the same commodity/country test set, the same
  historical window, and the same MAPE/RMSE/directional-accuracy metrics
  `apps/workers/forecasting.py::_compute_error_metrics` already computes
  in production.
- **Varied:** model architecture only — (a) reproduce the real
  production ensemble as the control, (b) a PatchTST model, (c) a
  Temporal Fusion Transformer.
- Training data volume should be logged explicitly for every
  commodity/country pair tested — the hypothesis is specifically about
  data-sparsity, so the experiment needs to know exactly how sparse each
  test case really is.

## Success Metrics

- Decided before looking at results: a Transformer variant must beat the
  production ensemble by at least 5% relative MAPE on at least half of
  the tested commodity/country pairs to justify the added inference cost
  and complexity of running a Transformer in production.
- Report results split by how much real history each pair had — if a
  Transformer only wins on the longest-history pairs, that's a strong,
  useful confirmation of the sparsity hypothesis rather than a simple
  "yes/no."

## Results

*Not yet run.*
