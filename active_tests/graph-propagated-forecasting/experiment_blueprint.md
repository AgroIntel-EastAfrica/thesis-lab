# Experiment: graph-propagated-forecasting

- **Owner:**
- **Started:**
- **Status:** active
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Objective 2 / RQ2

## Objective

The paper's Objective 2 asks for forecasting models that exploit
relationships between commodities and regions instead of treating every
time series independently. AgroIntel already has two pieces that were
never connected until this session: a real, live temporal knowledge
graph (`core/knowledge_graph/`, migration 047 — countries, corridors,
commodities, and now real climate events from
`services/alerts/live_generator.py`) and a real forecaster
(`services/forecasting/price.py`) that still forecasts every
(commodity, country) pair in isolation. This experiment asks whether
propagating a signal through the graph's real relationships (e.g. a
drought event's `AFFECTED_BY`/`REDUCES_PRODUCTION_OF` edges, or a shared
trade corridor between two countries) improves a forecast versus
ignoring those relationships entirely.

## Hypothesis

For a commodity/country pair currently under an active real climate
event in the knowledge graph (queryable today via
`GraphTraversal.active_climate_events`, already wired into
`GET /forecasting/price/{country}/{commodity}`'s `causal_evidence`
field), a forecast that incorporates a graph-derived feature — e.g. "is
there a currently-active climate event connected to this country and/or
commodity" as a real exogenous input, or a cross-country signal
propagated along `HAS_NEIGHBOR`/`CONNECTS` edges for the same commodity —
will outperform the current graph-blind baseline during the event window.
Outside of an active event, we expect little to no difference, since the
graph currently only carries real signal for climate events (the static
topology alone — countries, corridors — isn't itself predictive without
a real event attached to it).

## Core Variables

- **Held constant:** the underlying forecaster (XGBoost/Prophet per
  `services/forecasting/price.py`); evaluation metric (MAPE) and
  commodity/country test set.
- **Varied:** whether the model receives a graph-derived feature at all,
  and which relationship types it's allowed to use (climate-event edges
  only, vs. climate-event + neighbor/corridor propagation).
- **Real data:** use `core.knowledge_graph.AgroIntelKnowledgeGraph`'s real
  graph state and real historical climate-event records (once
  `knowledge_graph_node_history` has accumulated some — this experiment
  may need to wait for real event history to build up, or backfill a
  synthetic-but-labeled event set for the initial pass and note that
  clearly in Results rather than presenting synthetic events as real).

## Success Metrics

- The graph-aware model must show a measurable MAPE improvement
  specifically during real, verified active-event windows — a small or
  negative improvement outside event windows is expected and fine (it
  would falsify a claim that the graph feature helps unconditionally,
  which isn't the hypothesis).
- Document how many real event-window data points were actually
  available for evaluation — this experiment's biggest real risk is that
  production hasn't accumulated enough real climate-event history yet to
  test the hypothesis properly (see the `forecast-confidence-calibration`
  experiment's Results for a related, real "not enough data yet" finding
  if it lands first).

## Results

*Not yet run.*
