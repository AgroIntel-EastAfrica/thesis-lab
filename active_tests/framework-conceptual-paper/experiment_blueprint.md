# Experiment: framework-conceptual-paper

- **Owner:**
- **Started:**
- **Status:** active
- **Paper:** Paper 1 — "Agentic Intelligence for Data-Sparse Decision
  Making: A Framework for Multimodal Forecasting, Evidence-Grounded
  Reasoning, and Uncertainty-Aware Learning" (framework/position paper)
- **Source:** Concept paper "Agentic Agricultural Intelligence..."
  (Masaba, Makerere University), synthesized with the 12-paper
  publication roadmap this experiment set is organized around.

## Important: this is a synthesis paper, not a standalone empirical experiment

Unlike every other blueprint in this lab, Paper 1 doesn't run on its own
data — it formalizes the loop the *other* experiments each investigate
one arrow of: **Observe → Forecast → Retrieve → Reason → Quantify →
Act/Defer → Learn**. It's realistically written last (or drafted early
and revised as the empirical papers land), once at least a few of the
other experiments have real results to generalize from. This file exists
so the thread has a home in the lab now, not to imply it's independently
runnable today.

## Objective

Define agentic agricultural intelligence formally: separate **evidence**
(what was actually observed — e.g. a real climate event node in
`core/knowledge_graph/`), **prediction** (a model's output, e.g.
`ForecastPoint`), and **recommendation** (an action derived from a
prediction, e.g. `Recommendation`) as distinct objects with distinct
failure modes — a distinction AgroIntel's real architecture already
enforces in code (this session's own audits repeatedly found bugs from
these getting conflated, e.g. fabricated evidence presented as real).
Propose evaluation dimensions across all three, and catalogue real
failure modes observed while building the system.

## Hypothesis

N/A in the usual sense — this is a conceptual contribution. The
closest thing to a testable claim: the Observe→Forecast→Retrieve→
Reason→Quantify→Act/Defer→Learn framing will map cleanly onto
AgroIntel's real, already-built architecture (temporal knowledge graph =
Observe, `services/forecasting/price.py` = Forecast, `services/rag/` =
Retrieve, `core/knowledge_graph` causal traversal = Reason, the
calibration/confidence work = Quantify, `_apply_evidence_gate` =
Act/Defer, `ContinuousLearning` = Learn) without requiring the framework
to be stretched or the real system to be misdescribed to fit it.

## Core Variables

- **Held constant:** N/A (literature synthesis + architecture
  description, not a controlled experiment).
- **Varied:** N/A.
- **Real grounding required:** every claim in this paper about what the
  framework enables should cite a real, working piece of AgroIntel (file
  path + brief description), not a hypothetical capability — matching
  this whole lab's own evidence-based discipline.

## Success Metrics

- The framework should make a real, falsifiable prediction about what
  *should* happen when evidence/prediction/recommendation are properly
  separated (e.g. "systems that conflate prediction and recommendation
  will be more prone to presenting low-confidence forecasts as
  confident advice") — testable against real bugs already found and
  fixed this session (e.g. the fabricated-sources bug in
  `/hierarchical-query`, the missing abstention gate before this
  session's `_apply_evidence_gate`).
- Catalogue failure modes with a real example from this codebase's own
  history for each one, not a hypothetical.

## Results

*Not started — depends on enough of the other 16 experiments in this lab
having real results to generalize from.*
