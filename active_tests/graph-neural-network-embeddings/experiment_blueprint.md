# Experiment: graph-neural-network-embeddings

- **Owner:**
- **Started:**
- **Status:** active
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Section 2 names "dynamic graph neural networks"
  (Zheng et al. 2025) as the methodological basis for learning from
  evolving graph structure, distinct from the temporal knowledge graph
  (Wang et al. 2026) AgroIntel already implements. Objective 2.

## Objective

`graph-propagated-forecasting` (a sibling experiment) tests a simple,
hand-coded rule: "is there an active climate event connected to this
node." This experiment tests the paper's more ambitious version of the
same objective — instead of a hand-written rule, *learn* a vector
embedding for each commodity/country node from the graph's real
structure (`core/knowledge_graph/graph.py`'s real edges: `HAS_NEIGHBOR`,
`PRODUCES`, `CONNECTS`, `AFFECTED_BY`, `REDUCES_PRODUCTION_OF`) and use
that embedding as a forecasting feature. The real question: does letting
the model discover relational patterns beat hand-coding the one pattern
we already thought to check for?

## Hypothesis

A learned graph embedding (e.g. via a simple GNN or even a
non-parametric method like node2vec over the real graph) will capture
useful structure beyond the single hand-coded "active climate event"
signal — specifically, cross-commodity substitution effects (e.g. maize
and cassava prices moving together during a shared regional shock) that
no one has hand-coded a rule for. If the embedding adds no measurable
value beyond the simpler rule-based feature from
`graph-propagated-forecasting`, that's a legitimate result: it would
mean the graph's real edge structure isn't yet rich enough to reward a
learned approach, and the simpler rule-based version is the right level
of investment for now.

## Core Variables

- **Held constant:** same forecaster, same commodity/country test set,
  same evaluation metrics as `graph-propagated-forecasting` — this
  experiment should reuse that experiment's baseline and rule-based
  result as its own control/comparison point, not re-derive it.
- **Varied:** no graph feature (control) vs. the rule-based feature from
  `graph-propagated-forecasting` vs. a learned graph embedding.
- **Real data:** `core.knowledge_graph.AgroIntelKnowledgeGraph`'s real,
  live graph structure — the same one production reads from, snapshotted
  read-only for this experiment (never write experimental embeddings
  back into the production graph).

## Success Metrics

- A learned embedding must beat *both* the no-graph baseline and the
  simpler rule-based feature to justify its real complexity cost
  (training a GNN, keeping embeddings fresh as the graph changes) over
  the rule-based approach already built.
- If it only ties the rule-based approach, the honest conclusion is
  "not worth building yet" — record that explicitly rather than treating
  a tie as inconclusive.

## Results

*Not yet run — depends on `graph-propagated-forecasting` running first
to have a real rule-based result to compare against.*
