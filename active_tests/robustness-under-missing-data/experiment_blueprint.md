# Experiment: robustness-under-missing-data

- **Owner:**
- **Started:**
- **Status:** active
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Methodology, agentic component: "The system
  will be tested under missing data, conflicting sources, distribution
  shifts and simulated market shocks." RQ4.

## Objective

A chaos-engineering-style stress test of the real pipeline, distinct
from the other experiments here in that it doesn't test a new model — it
tests whether the *existing*, already-shipped degradation paths actually
degrade honestly rather than silently, when the paper's four named
failure conditions are deliberately induced. This session's work already
established a real precedent for this kind of testing (`product/PRODUCTION_AUDIT.md`'s
"more chaos testing" pass, referenced in this repo's history) — this
experiment extends that same discipline specifically to the concept
paper's four named conditions.

## Hypothesis

- **Missing data**: `RecommendationEngine.get_recommendations()` already
  returns `self._failure("No intelligence data available...")` when both
  pulse and arbitrage signals are empty — expect this to hold under a
  deliberately-empty-signal test.
- **Conflicting sources**: no code path currently exists that detects
  disagreement *between* independent signals (e.g. a bullish pulse
  signal and a bearish arbitrage signal for the same commodity) — expect
  the current system to silently pick whichever branch's construction
  gate fires first, with no explicit "these sources disagree" flag. This
  is a real, predicted gap, not just a test of existing behavior.
- **Distribution shift**: `compute_model_drift` (see
  `continual-learning-drift-audit`) is the one real mechanism that could
  catch this — expect it to require the full `window*2` cycles before
  flagging anything, meaning a sudden shift has a real, measurable blind
  spot before detection.
- **Simulated market shocks**: covered by `shock-period-forecast-accuracy`;
  cross-reference rather than duplicate.

## Core Variables

- **Held constant:** the real production code paths under test — this
  experiment injects synthetic *inputs*, not code changes.
- **Varied:** which of the four conditions is induced, and how severely
  (e.g. fully missing vs. partially missing data).

## Success Metrics

- For each condition, document whether the system (a) degrades honestly
  (returns a real failure/low-confidence result, matching this
  codebase's own established "no fabricated data" discipline) or (b)
  degrades silently (returns a confident-looking result built on
  incomplete or contradictory inputs with no indication of the problem).
- The "conflicting sources" gap predicted above, if confirmed, is a real,
  scoped follow-on: a genuine feature (an explicit disagreement check
  between pulse and arbitrage signals) the paper's own framework
  section explicitly calls for and that doesn't exist today.

## Results

*Not yet run.*
