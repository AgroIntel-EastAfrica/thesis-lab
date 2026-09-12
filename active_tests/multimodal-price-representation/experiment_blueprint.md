# Experiment: multimodal-price-representation

- **Owner:**
- **Started:**
- **Status:** active
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Objective 1 / RQ1

## Objective

The paper's Objective 1 asks for a representation that *jointly* models
market signals, trade, climate, and news for a commodity, rather than
treating each source as a separate feature bolted onto a price series.
AgroIntel already has all of these sources live (price history via
`services/market/price_model.py`, Comtrade trade data, NASA POWER
climate via `services/satellite/climate_data.py`, GDELT news signals),
but the production forecaster
(`services/forecasting/price.py::LocalPriceForecaster`/
`SubNationalPriceForecaster`) only ever feeds price history plus a
handful of hand-picked lag/seasonal features into XGBoost/Prophet — the
other modalities never enter the model itself. This experiment asks
whether a real joint representation beats that baseline, and if so, by
how much and for which commodities.

## Hypothesis

A shared embedding built from price history + trade volume + a climate
stress index (rainfall/soil-moisture anomaly) + a news-sentiment signal
will produce a lower forecast MAPE than the current price-only baseline,
particularly for commodities/countries where climate or trade shocks are
the dominant real driver of price moves (e.g. maize in a drought year) —
and *not* meaningfully better for commodities where price is already
well-explained by its own history (e.g. a stable staple in a normal
season). If the improvement doesn't hold even for the shock cases, that's
a real, useful negative result about whether this specific set of
modalities is worth the added complexity.

## Core Variables

- **Held constant:** commodity/country pairs and date ranges used for
  train/test splits; evaluation metric (MAPE, matching
  `apps/workers/forecasting.py::_compute_error_metrics`'s real formula so
  results are comparable to production numbers).
- **Varied:** the input representation — (a) price-only baseline
  (reproduce the current production model's real inputs as the control),
  (b) price + trade, (c) price + trade + climate, (d) all four modalities.
- **Real data, no production writes:** pull from the same real sources
  the app uses (`get_price_history`, Comtrade client, NASA POWER client,
  GDELT client) into a local cache/parquet file for this experiment only
  — never write results back to `forecast_evaluations` or any production
  table.

## Success Metrics

- Decided before looking at results: the full multimodal representation
  (d) must beat the price-only baseline (a) by at least 10% relative MAPE
  reduction, averaged over at least 3 commodity/country pairs with a
  known real climate or trade shock in the test window, to be worth
  productionizing.
- Report the ablation (b) and (c) results regardless of whether (d)
  "wins" — Objective 1's own methodology section explicitly asks which
  sources contribute meaningful predictive value under what conditions,
  not just whether the kitchen-sink model wins.

## Results

*Not yet run.*
