# Experiment: agentic-evaluation-framework

- **Owner:**
- **Started:**
- **Status:** active
- **Paper:** Paper 12 — "Evaluating Agentic Agricultural Intelligence:
  Accuracy, Evidence, Uncertainty, and Decision Reliability"
- **Source:** 12-paper publication roadmap.

## Important: this is a synthesis/methodology paper

Like `framework-conceptual-paper` (Paper 1), this doesn't run as an
independent experiment — it formalizes a shared evaluation methodology
across five dimensions, each of which already has (or will have) a real
measurement from another experiment in this lab. Its real contribution
is the *framework* — naming the dimensions, justifying why all five
matter together, and showing they can disagree (a system can score well
on Prediction while failing badly on Decision) — not new data collection
of its own.

## Objective

Assemble a formal, five-dimension evaluation framework, each dimension
backed by a real measurement already defined elsewhere in this lab or
in production:

- **Prediction:** MAE/RMSE/MAPE/directional accuracy — already computed
  by `apps/workers/forecasting.py::_compute_error_metrics` in
  production.
- **Evidence:** retrieval precision/coverage/attribution — from
  `evidence-attribution-quality` and `evidence-acquisition-policy`.
- **Reasoning:** contradiction detection/temporal consistency — from
  `contradictory-evidence-reasoning`.
- **Uncertainty:** calibration/abstention quality — from
  `forecast-confidence-calibration` and `competing-scenario-analysis`
  (calibration), and the real, shipped `_apply_evidence_gate`
  (abstention).
- **Decision:** decision quality/risk detection/appropriate reliance —
  from `human-ai-collaboration-study-design` and `regional-equity-audit`.

## Hypothesis

The five dimensions are not redundant with each other — a system (or a
specific AgroIntel component) can score well on one and poorly on
another. Concretely: `RecommendationEngine`'s Prediction-adjacent
metrics (confidence, supporting_signals) can look strong for a
commodity/country pair with a real regional-equity gap (per
`regional-equity-audit`'s own hypothesis) — i.e. good Prediction-layer
numbers can coexist with a real Decision-layer fairness problem the
Prediction metric alone would never surface.

## Core Variables

- **Held constant:** N/A — this is a synthesis of other experiments'
  real measurements, not a new data collection effort.
- **Varied:** N/A.

## Success Metrics

- The framework must be demonstrated against at least 2 real
  cases from this lab's own other experiments where the five dimensions
  genuinely disagree (not hypothetical examples) — proving the framework
  adds value beyond a single aggregate score.
- Every metric definition in the framework must cite the real code that
  already computes it (or the experiment that will), matching this
  lab's evidence-based discipline rather than proposing metrics nothing
  actually measures.

## Results

*Not started — depends on results from `evidence-attribution-quality`,
`contradictory-evidence-reasoning`, `forecast-confidence-calibration`,
`competing-scenario-analysis`, `human-ai-collaboration-study-design`,
and `regional-equity-audit` to have real cross-dimension comparisons to
draw from.*
