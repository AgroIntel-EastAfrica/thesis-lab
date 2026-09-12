# Publication Roadmap

Maps this lab's 17 experiments to a 12-paper structure for the PhD, organized
around the theme **"Agentic Intelligence Under Uncertainty."** Adopted
2026-09-12 from an external 12-paper roadmap proposal, cross-checked against
this lab's existing 12 experiments (from the original concept paper's 6
objectives) before adding the 5 genuinely new threads.

Dates, target venues, and defense milestones are intentionally left blank —
those depend on the advisor, committee, and institution and are not something
that can be generated here. Fill them in as they're decided.

## Papers → Experiments

| # | Paper | Type | Experiment(s) | Target venue | Target date | Status |
|---|-------|------|----------------|---------------|--------------|--------|
| 1 | Agentic Intelligence for Data-Sparse Decision Making (framework) | Position/framework | [`framework-conceptual-paper`](active_tests/framework-conceptual-paper/experiment_blueprint.md) | | | Not started — written last |
| 2 | Multimodal price forecasting | Empirical | [`multimodal-price-representation`](active_tests/multimodal-price-representation/experiment_blueprint.md) | | | Active |
| 3 | Dynamic/temporal knowledge graph | Empirical | [`graph-propagated-forecasting`](active_tests/graph-propagated-forecasting/experiment_blueprint.md), [`graph-neural-network-embeddings`](active_tests/graph-neural-network-embeddings/experiment_blueprint.md) | | | Active |
| 4 | Shock/distribution-shift forecasting | Empirical | [`shock-period-forecast-accuracy`](active_tests/shock-period-forecast-accuracy/experiment_blueprint.md), [`transformer-forecasting-baseline`](active_tests/transformer-forecasting-baseline/experiment_blueprint.md) | | | Active |
| 5 | Probabilistic calibration | Empirical | [`forecast-confidence-calibration`](active_tests/forecast-confidence-calibration/experiment_blueprint.md), [`competing-scenario-analysis`](active_tests/competing-scenario-analysis/experiment_blueprint.md) | | | Active |
| 6 | Evidence retrieval / attribution | Empirical | [`evidence-attribution-quality`](active_tests/evidence-attribution-quality/experiment_blueprint.md) | | | Active |
| 7 | Evidence acquisition policy (NEW) | Empirical | [`evidence-acquisition-policy`](active_tests/evidence-acquisition-policy/experiment_blueprint.md) | | | Not started |
| 8 | Reasoning over conflicting evidence (NEW) | Empirical | [`contradictory-evidence-reasoning`](active_tests/contradictory-evidence-reasoning/experiment_blueprint.md) | | | Not started |
| 9 | Continual learning | Empirical | [`continual-learning-drift-audit`](active_tests/continual-learning-drift-audit/experiment_blueprint.md) | | | Active |
| 10 | Human-AI decision support | Empirical | [`human-ai-collaboration-study-design`](active_tests/human-ai-collaboration-study-design/experiment_blueprint.md), [`regional-equity-audit`](active_tests/regional-equity-audit/experiment_blueprint.md), [`robustness-under-missing-data`](active_tests/robustness-under-missing-data/experiment_blueprint.md) | | | Active |
| 11 | AgriBench-EA benchmark (NEW) | Dataset/resource | [`agribench-ea-benchmark`](active_tests/agribench-ea-benchmark/experiment_blueprint.md) | | | Not started — blocked on licensing review |
| 12 | Evaluation framework (NEW) | Synthesis/methodology | [`agentic-evaluation-framework`](active_tests/agentic-evaluation-framework/experiment_blueprint.md) | | | Not started — depends on Papers 2-10 results |

## Sequencing notes

- **Papers 2, 5, 6, 9, 10** draw on experiments already active in this lab
  with real code grounding — these are the most immediately publishable.
- **Papers 7 and 8** are new empirical threads grounded in real, currently
  hand-coded/fixed logic (`_apply_evidence_gate`, `WikiRetriever`'s fixed
  cascade, and the RAG layer's lack of conflict detection) — both are
  well-defined and could start any time.
- **Paper 11** (the benchmark) is a resource-release effort, not a modeling
  paper — it's on its own track (licensing/hosting) and doesn't block or get
  blocked by the others.
- **Paper 1** (framework) and **Paper 12** (evaluation) are both synthesis
  papers written once enough of Papers 2-10 have real results — they're
  listed first/last by number but realistically drafted last, or drafted
  early as a skeleton and revised as results land.

## Priority

Per the adopted roadmap's own priority marks, in order of near-term focus:

1. Paper 5 (calibration) — `forecast-confidence-calibration` already has
   real code (`_MIN_CONFIDENCE_TO_RECOMMEND` gate, ensemble calibration).
2. Paper 6 (evidence retrieval/attribution) — `evidence-attribution-quality`
   already has real grounding (`citation_check.py`, `check_grounding`).
3. Paper 9 (continual learning) — `continual-learning-drift-audit` already
   has the real feedback-loop bridge shipped this session.
4. Paper 7 (evidence acquisition policy) — new, but cleanly scoped against
   real existing fixed-policy code.
5. Paper 2/3/4 (forecasting/graph) — active, ongoing.
6. Paper 8, then Paper 10, then Paper 1/11/12 as their dependencies land.

## GitHub tracking

Each experiment above has a matching GitHub Issue (titled `[Thesis Lab]
<name>`) on the [AgroIntel Thesis Lab project board](https://github.com/users/jericho555/projects/1).
Each paper above corresponds to a GitHub Milestone of the same name — every
issue is assigned to its paper's milestone.
