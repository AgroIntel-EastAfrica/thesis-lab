# Experiment: agentic-market-monitoring

- **Owner:**
- **Started:**
- **Status:** active
- **Paper:** Paper — "Agentic AI for Continuous Agricultural Market
  Monitoring and Intelligence"
- **Source:** 15-paper publication roadmap revision (2026-09-12), adopted
  from an external reorganization proposal. Distinguished from
  `evidence-acquisition-policy` (Paper 7, per-query retrieval policy),
  `contradictory-evidence-reasoning` (Paper 8, textual conflict
  detection), and `continual-learning-drift-audit` (Paper 9, model
  retraining) — this one is about the always-on monitoring *loop* itself,
  not any single stage inside it.

## Important: this is largely already built, not a speculative proposal

Unlike most new threads in this lab, AgroIntel already runs a real,
continuous Observe → Detect → Retrieve → Reason → Report loop in
production: `services/alerts/live_generator.py::generate_live_alerts`
(real per-country alert generation), `services/intelligence/news_intelligence.py`
(GDELT/ReliefWeb/FAO GIEWS/EAC media RSS ingestion, 25 real
classification patterns for export bans/droughts/pest outbreaks/trade
agreements), and `services/alerts/subscriptions.py` (per-commodity,
per-country, per-severity delivery routing) — all wired into the Celery
beat schedule (`apps/scheduler/`), not a one-off script. This experiment
formalizes and evaluates that existing loop as a research contribution,
rather than proposing to build it from scratch.

## Objective

Characterize AgroIntel's real, already-running monitoring loop against
the paper's own agentic framing (Observe→Detect→Retrieve→Reason→Report),
identify where it already behaves like a real agentic system vs. where
it's closer to a fixed rule engine, and measure real detection quality
(true positive rate on real historical shocks, false-alarm rate, time-to-
detection) rather than assuming the existing alert system is already
"agentic" just because it runs continuously.

## Hypothesis

The current pipeline is real but only partially agentic: alert
generation (`generate_live_alerts`) and news classification (25 fixed
patterns) are rule-based detectors, not a reasoning agent — there is no
component that currently decides, per detected anomaly, whether to
retrieve more evidence before alerting (that gap is exactly what
`evidence-acquisition-policy` studies at the per-query level; this
experiment measures whether the same gap exists at the monitoring-loop
level, i.e. whether alerts fire on a single fixed-pattern match without
corroboration from a second, independent source).

## Core Variables

- **Held constant:** the real ingestion sources (GDELT, ReliefWeb, FAO
  GIEWS, EAC media RSS) and the real alert-delivery/subscription
  machinery — this experiment evaluates the existing detect→reason step,
  it doesn't replace the ingestion or delivery layers.
- **Varied:** detection/reasoning policy — (a) current fixed 25-pattern
  classification (control), (b) a variant that cross-checks a detected
  signal against a second independent source (e.g. the temporal
  knowledge graph's `active_climate_events`) before treating it as
  alert-worthy.
- **Real data:** a historical sample of real, already-fired alerts and
  real known market/climate shocks (e.g. from `shock-period-forecast-accuracy`'s
  own shock-period definitions) as ground truth.

## Success Metrics

- Quantify the real false-alarm rate and time-to-detection of the
  current fixed-pattern system against real historical shocks — decided
  before looking at results, a false-alarm rate above a meaningful
  threshold (e.g. 20%+) justifies adding a corroboration step; a low
  rate means the current fixed rules are already good enough and a
  learned/agentic upgrade isn't yet worth the complexity.
- Any proposed corroboration step must be evaluated on real
  precision/recall against the same historical ground truth, not just
  argued for conceptually.

## Results

*Not yet run.*
