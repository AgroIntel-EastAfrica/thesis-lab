# Experiment: continual-learning-drift-audit

- **Owner:**
- **Started:**
- **Status:** active
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Objective 5 / RQ5: "examine whether agentic
  systems can learn from real-world feedback **while avoiding
  uncontrolled model drift and reinforcing erroneous patterns**" (Parisi
  et al. 2019).

## Objective

Unlike the other experiments in this sandbox, the real mechanism this
one evaluates is already live in production: `ContinuousLearning`
(`services/recommendations/feedback.py`) records real model performance,
computes real drift scores (`compute_model_drift`), and
`recommendation_learning_bridge.py` now feeds real user decision
outcomes into it. Objective 5 isn't just "build a feedback loop" — it's
"determine whether that loop actually stays safe." This experiment is an
audit of the real, shipped mechanism, not a request to build a new one.

## Hypothesis

`compute_model_drift`'s window-based comparison (`window=7`, recent vs.
baseline mean) will correctly flag a real, injected synthetic drift
(e.g. a sustained shift in the `"recommendations"` win_rate metric) within
a small number of recording cycles, *and* will not fire false positives
on real, ordinary metric noise recorded before this session's feedback
loop went live. Both halves matter: a drift detector that never fires is
useless, and one that fires constantly gets ignored.

## Core Variables

- **Held constant:** the real `compute_model_drift`/
  `monitor_model_performance` implementations — this experiment tests
  the existing code as-is, not a modified version.
- **Varied:** the sequence of `model_performance` rows fed in — (a) a
  real, unmodified sample sequence to check for false positives, (b) a
  synthetic sequence with a deliberately injected step-change to check
  real sensitivity and how many cycles it takes to detect.
- **No production writes:** run against a local/test Supabase instance
  or a mocked `model_performance` table — never inject synthetic drift
  data into the real production `model_performance` table, which would
  corrupt the real signal the live `SevereModelDrift` alert depends on.

## Success Metrics

- Detects a real, meaningful injected drift (e.g. win_rate dropping from
  a stable ~70% to a sustained ~30%) within `window * 2` = 14 recorded
  cycles, matching the detector's own documented minimum-data
  requirement.
- Zero false positives against a real, unmodified historical sequence
  with normal variance.
- If either fails, that's a real, actionable finding about the `window`
  parameter or the drift-score formula (`services/recommendations/feedback.py::compute_model_drift`)
  needing to change — not a reason to distrust the whole mechanism
  without a concrete alternative in hand.

## Results

*Not yet run.*
