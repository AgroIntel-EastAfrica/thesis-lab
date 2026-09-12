# Experiment: competing-scenario-analysis

- **Owner:**
- **Started:**
- **Status:** active
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Objective 4 / RQ4: "the system will estimate
  uncertainty, **evaluate competing scenarios** and determine when
  evidence is insufficient to justify a recommendation." The
  insufficient-evidence half of this objective is already shipped
  (`_apply_evidence_gate`, `services/intelligence/recommendations.py`);
  this experiment is the "competing scenarios" half, which nothing in
  production or the rest of this lab currently addresses.

## Objective

`RecommendationEngine.get_recommendations()` already computes **both** a
real bull case and a real bear case for every commodity/country pair —
`idx["bull_priority"]` and `idx["bear_priority"]` are both populated from
real pulse signals (`services/intelligence/recommendations.py`, the
commodity-index build step). But the construction logic that follows is
an `if/elif` chain (`if idx["bull_priority"] >= _HIGH_PRIORITY: ... elif
idx["bear_priority"] >= _HIGH_PRIORITY: ...`) that picks exactly one
branch and discards the other's priority value entirely — a real,
already-computed "competing scenario" is silently dropped before it ever
reaches a user. This experiment tests whether surfacing both scenarios
explicitly is more decision-useful than the current single-recommendation
output.

## Hypothesis

For a real, non-trivial fraction of production recommendations, the
"losing" scenario's priority is close enough to the winning one (e.g.
within 15 points, both non-trivial) that presenting a single confident
action (`SELL_NOW`, `BUY_NOW`, etc.) understates real uncertainty — the
recommendation looks decisive when the underlying signal was actually a
close call between two real, computed, conflicting scenarios.

## Core Variables

- **Held constant:** the real pulse/arbitrage signal data
  `RecommendationEngine` already computes from — this experiment reads
  real production signal data, it doesn't generate new data.
- **Varied:** presentation only — (a) the current single-recommendation
  output (control, reproducing real production behavior), (b) a
  dual-scenario view exposing both `bull_priority` and `bear_priority`
  plus an explicit `scenario_spread = abs(bull_priority - bear_priority)`
  for every commodity/country pair, regardless of which one the current
  code would have picked.
- **No production changes**: this experiment reads and reports on real
  signal data; it does not modify `RecommendationEngine` or change what
  the live API returns.

## Success Metrics

- Decided before looking at results: if `scenario_spread <= 15` for at
  least 10% of real recommendation-eligible commodity/country pairs in a
  representative sample, that's a real, actionable rate of "close calls"
  currently presented as confident single recommendations — enough to
  justify a concrete production follow-on (e.g. an explicit
  `scenario_spread` field on `Recommendation`, or downgrading
  close-call recommendations toward `WATCH` the same way
  `_apply_evidence_gate` already downgrades low-confidence ones).
- If the real rate is much lower (most recommendations have one
  dominant, clearly-winning scenario), that's also a legitimate,
  useful result — it would mean the current single-recommendation
  design is already a reasonable simplification most of the time, and
  the added complexity of a dual-scenario UI wouldn't be worth it.

## Results

*Not yet run.*
