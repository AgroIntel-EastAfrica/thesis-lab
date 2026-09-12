# Experiment: evidence-acquisition-policy

- **Owner:**
- **Started:**
- **Status:** active
- **Paper:** Paper 7 — "When Should an AI Agent Retrieve More Evidence?
  Learning Evidence Acquisition Policies Under Uncertainty"
- **Source:** 12-paper publication roadmap (external proposal, adopted
  into this lab), extending concept-paper Objective 3/4.

## Objective

AgroIntel already has two real, but *hand-coded and fixed*, versions of
an evidence-acquisition policy — this experiment's novelty is asking
whether a *learned* policy beats them:

1. `_apply_evidence_gate` (`services/intelligence/recommendations.py`) —
   a fixed-threshold binary policy: confidence/supporting_signals below
   a constant floor → downgrade to `WATCH`; otherwise → answer. Never
   "retrieve more" as a third option.
2. `WikiRetriever.get_context()` (`services/rag/wiki_retriever.py`) — a
   fixed *cascade*: exact match → Supabase search → semantic search →
   `HybridRetriever` fallback. Always tries every tier in the same fixed
   order regardless of how confident the first tier's result was.

Neither is a real decision *policy* in the paper's sense — both are
static rules, not something that learns when retrieval is worth its
cost from real outcome data.

## Hypothesis

A policy that dynamically chooses among {answer now, retrieve more,
retrieve from a different source, abstain} based on real, current
uncertainty signals (the same `confidence`/`supporting_signals` fields
`_apply_evidence_gate` already reads) will retrieve additional evidence
*less* often than `WikiRetriever`'s current fixed cascade (which always
tries every tier) while achieving the same or better final
`evidence_sufficient` rate — i.e. it saves real retrieval cost
(Supabase/semantic-search round trips) without sacrificing quality,
by learning which cases don't need every tier.

## Core Variables

- **Held constant:** the real retrieval tiers themselves (exact match,
  Supabase search, semantic search, hybrid fallback) — this experiment
  changes the *policy* for when to invoke each, not the tiers.
- **Varied:** policy — (a) the current fixed cascade (control), (b) a
  simple learned/heuristic policy using real confidence signals to skip
  tiers unlikely to help.
- **Real data:** real (commodity, country) query patterns and real tier
  hit/miss rates logged from `WikiRetriever`'s actual production calls —
  observational data, no changes to the live retrieval behavior while
  collecting it.

## Success Metrics

- Decided before looking at results: the learned policy must reduce the
  average number of retrieval tiers invoked per query by a real,
  measurable margin (e.g. 20%+) without reducing the real
  `evidence_sufficient` rate (from `evidence-attribution-quality`'s own
  measurement) by more than a small, pre-agreed tolerance.
- If it can't beat the fixed cascade on cost without a quality
  regression, that's a legitimate result: the fixed cascade is already a
  reasonable, cheap-to-reason-about policy, and a learned one isn't
  worth the added complexity yet.

## Results

*Not yet run.*
