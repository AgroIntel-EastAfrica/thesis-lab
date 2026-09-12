# Experiment: contradictory-evidence-reasoning

- **Owner:**
- **Started:**
- **Status:** active
- **Paper:** Paper 8 — "Reasoning Over Conflicting Evidence in
  Agricultural Intelligence Systems"
- **Source:** 12-paper publication roadmap, extending concept-paper
  Objective 3 (Asai et al. evidentiality).

## Objective

Distinct from `robustness-under-missing-data` (which predicts a
*numeric signal* disagreement gap — bullish pulse vs. bearish arbitrage
inside `RecommendationEngine`): this experiment is about *textual
source* conflicts inside the RAG/retrieval layer — e.g. one retrieved
chunk's metadata says production increased, another says it decreased.
AgroIntel's real retrieval code
(`services/rag/base.py::HybridSearcher`, `services/rag/wiki_retriever.py`)
currently has no mechanism to detect this at all — it ranks chunks by
similarity score only, with no source-reliability, recency, or
geographic-coverage weighting, and no explicit "these two retrieved
chunks disagree" signal.

## Hypothesis

A meaningful fraction of real multi-chunk retrievals for the same
(commodity, country) query contain genuinely conflicting claims (e.g.
different production-change directions from different sources/dates) —
and the current pipeline silently averages/concatenates them into one
summary with no indication a conflict existed, rather than surfacing the
disagreement or resolving it via source-reliability/recency weighting.

## Core Variables

- **Held constant:** the real retrieval tiers and chunk metadata
  (`source`, `date`, etc.) already attached by
  `services/embeddings/`/`services/rag/` — this experiment reads real
  metadata, it doesn't invent new fields.
- **Varied:** (a) current behavior — chunks concatenated with no
  conflict detection (control), (b) an explicit conflict-detection pass
  comparing claims across retrieved chunks for the same query, weighted
  by source recency/reliability metadata already present.

## Success Metrics

- Quantify the real rate of detected conflicts across a representative
  sample of real multi-chunk retrievals — decided before looking at
  results, a rate above a meaningful threshold (e.g. 5%+ of retrievals
  with 2+ chunks) justifies building a real conflict-detection pass into
  production; a near-zero rate means this isn't yet a practical problem
  worth solving, regardless of how theoretically interesting it is.
- Any real conflict found should be reportable in the same honest style
  `check_grounding` already uses for unverified claims (a labeled list,
  not a silently-adjusted confidence number) — consistent with this
  codebase's established "disclose, don't silently correct" pattern.

## Results

*Not yet run.*
