# Publication Roadmap

Maps this lab's 20 experiments to a 16-paper structure for the PhD, organized
around the theme **"Agentic Intelligence Under Uncertainty."** Originally
adopted 2026-09-12 from an external 12-paper roadmap proposal; revised the
same day after a second external reorganization proposal (a 15-paper
portfolio) was evaluated against it — merged rather than appended
(12 + 15 ≠ 27): 3 genuinely new threads were adopted, 1 existing experiment
was promoted from a shared paper into its own dedicated paper, and the rest
of the second proposal's items were judged to be relabelings of papers this
lab already had, and skipped.

Dates, target venues, and defense milestones are intentionally left blank —
those depend on the advisor, committee, and institution and are not something
that can be generated here. Fill them in as they're decided.

**Note on framing external proposals:** don't promise a fixed paper count in
an external-facing proposal (e.g. to a funder/committee) — frame the work as
research thrusts with papers emerging from them, not a commitment to N
publications. See "Research thrusts" below.

## Papers → Experiments

| # | Paper | Type | Experiment(s) | Target venue | Target date | Status |
|---|-------|------|----------------|---------------|--------------|--------|
| 1 | Agentic Intelligence for Data-Sparse Decision Making (framework) | Position/framework | [`framework-conceptual-paper`](active_tests/framework-conceptual-paper/experiment_blueprint.md) | | | Not started — written last |
| 2 | Multimodal price forecasting | Empirical | [`multimodal-price-representation`](active_tests/multimodal-price-representation/experiment_blueprint.md) | | | Active |
| 3 | Dynamic/temporal knowledge graph | Empirical | [`graph-propagated-forecasting`](active_tests/graph-propagated-forecasting/experiment_blueprint.md), [`graph-neural-network-embeddings`](active_tests/graph-neural-network-embeddings/experiment_blueprint.md) | | | Active |
| 4 | Shock/distribution-shift forecasting | Empirical | [`shock-period-forecast-accuracy`](active_tests/shock-period-forecast-accuracy/experiment_blueprint.md), [`transformer-forecasting-baseline`](active_tests/transformer-forecasting-baseline/experiment_blueprint.md) | | | Active |
| 5 | Probabilistic calibration | Empirical | [`forecast-confidence-calibration`](active_tests/forecast-confidence-calibration/experiment_blueprint.md), [`competing-scenario-analysis`](active_tests/competing-scenario-analysis/experiment_blueprint.md) | | | Active |
| 6 | Data-centric AI for low-resource markets (NEW) | Empirical | [`data-centric-ai-low-resource-markets`](active_tests/data-centric-ai-low-resource-markets/experiment_blueprint.md) | | | Not started — depends on Paper 15's data-quality labels |
| 7 | Cross-market transfer learning (NEW) | Empirical | [`cross-market-transfer-learning`](active_tests/cross-market-transfer-learning/experiment_blueprint.md) | | | Not started |
| 8 | Evidence retrieval / attribution | Empirical | [`evidence-attribution-quality`](active_tests/evidence-attribution-quality/experiment_blueprint.md) | | | Active |
| 9 | Evidence acquisition policy | Empirical | [`evidence-acquisition-policy`](active_tests/evidence-acquisition-policy/experiment_blueprint.md) | | | Not started |
| 10 | Reasoning over conflicting evidence | Empirical | [`contradictory-evidence-reasoning`](active_tests/contradictory-evidence-reasoning/experiment_blueprint.md) | | | Not started |
| 11 | Agentic market monitoring (NEW) | Empirical | [`agentic-market-monitoring`](active_tests/agentic-market-monitoring/experiment_blueprint.md) | | | Not started — evaluates already-shipped production monitoring loop |
| 12 | Continual learning | Empirical | [`continual-learning-drift-audit`](active_tests/continual-learning-drift-audit/experiment_blueprint.md) | | | Active |
| 13 | Human-AI decision support | Empirical | [`human-ai-collaboration-study-design`](active_tests/human-ai-collaboration-study-design/experiment_blueprint.md), [`robustness-under-missing-data`](active_tests/robustness-under-missing-data/experiment_blueprint.md) | | | Active |
| 14 | Trustworthy Agricultural Intelligence Under Data Sparsity: An Empirical Study of Evidence Availability, Uncertainty, and Reliability (redesigned 2026-09-17, see below) | Empirical | [`evidence-sparsity-reliability`](active_tests/evidence-sparsity-reliability/experiment_blueprint.md) (predecessor [`regional-equity-audit`](concluded/regional-equity-audit/experiment_blueprint.md), concluded) | | | Active — Phase 0 in progress: schema + real price-modality collection built and run live 2026-09-17 (KE/RW/SS/SO x coffee/maize/tea, 12 real observations); weather/trade/production/textual-event modalities not yet started |
| 15 | AgriBench-EA benchmark | Dataset/resource | [`agribench-ea-benchmark`](active_tests/agribench-ea-benchmark/experiment_blueprint.md) | | | Not started — blocked on licensing review |
| 16 | Evaluation framework | Synthesis/methodology | [`agentic-evaluation-framework`](active_tests/agentic-evaluation-framework/experiment_blueprint.md) | | | Not started — depends on Papers 2-14 results |

## What changed in the 2026-09-12 revision, and why

The second external proposal suggested a 15-paper structure. Comparing it
item-by-item against the 12 papers already above:

- **Adopted as genuinely new** (real gaps, not covered by the existing 12):
  Data-centric AI (Paper 6), cross-market transfer learning (Paper 7),
  agentic market monitoring (Paper 11). Each has a real code hook in
  AgroIntel (see each blueprint's "Objective" section) rather than being
  speculative.
- **Adopted as a re-bucketing, not new work:** `regional-equity-audit` was
  previously one of three experiments folded into Paper 13 (Human-AI
  decision support). It's promoted to its own paper (14) because the
  second proposal's framing of it ("Trustworthy AI Under Unequal Data
  Availability") is a stronger, more publishable framing than leaving it
  as a sub-topic — no new experiment was created for this, just a clearer
  home for one that already existed.
- **Judged as relabelings of papers already in the 12, and skipped:** deep
  learning price forecasting, RAG for market intelligence, knowledge
  graphs, human-AI collaboration, multimodal forecasting, climate-aware
  forecasting — all substantively the same as Papers 2, 3, 8, 9, 13 above.
- **Explicitly skipped:** food security early warning (real overlap with
  Paper 11's already-shipped monitoring code — folding both into one paper
  avoids the redundancy the source proposal's own diagram risked),
  efficient models and federated learning (no real code hook in AgroIntel
  today — would be speculative rather than grounded like everything else
  in this lab, and the source proposal itself flagged both as
  lower-priority/peripheral).
- **Kept, not replaced:** Paper 1 (framework) and Paper 16 (evaluation
  framework) — the second proposal's 15-paper list dropped both entirely,
  but nothing in it replaces the synthesis role either plays here.

## Paper 14 redesign, 2026-09-17 — and an open coordination question

Paper 14's original design (`regional-equity-audit`) audited AgroIntel
by comparing data-rich vs. data-sparse *countries* directly, and mixed
data-availability, production bugs, forecasting validity, calibration,
and recommendation behavior into one experiment — real findings came
out of it (3 production bugs, a genuine 21.1% coverage split), but the
country-vs-country framing made causal interpretation difficult, as its
own confound-chasing repeatedly demonstrated. Reset into a controlled
experiment with evidence availability/quality/provenance/semantic
consistency as explicit factors instead of country identity — full
design in
[`active_tests/evidence-sparsity-reliability/experiment_blueprint.md`](active_tests/evidence-sparsity-reliability/experiment_blueprint.md),
concluded predecessor at
[`concluded/regional-equity-audit/experiment_blueprint.md`](concluded/regional-equity-audit/experiment_blueprint.md).

**Open question this reset surfaces, not yet resolved**: the redesigned
Paper 14 substantially overlaps by construction with Papers 5
(probabilistic calibration), 6 (data-centric AI for low-resource
markets), 8 (evidence retrieval/attribution), 9 (evidence acquisition
policy), 10 (reasoning over conflicting evidence), and 13 (human-AI
decision support) — its four sub-experiments (E1–E4) are essentially
smaller, bounded pilots of exactly what those six papers each go deeper
on. Two readings are both consistent with the redesign as given: Paper
14 stays a small, explicitly-bounded pilot that later *feeds into* those
six as their own separate deeper treatments; or some of them get
formally absorbed into Paper 14 once its infrastructure exists and their
separate scope turns out to be redundant. This table has **not** been
changed to reflect either resolution — that's the project owner's call,
not an inference to make unilaterally. Revisit once Phase 0 of the new
Paper 14 experiment (the gold-standard dataset + provenance layer) is
built and the real infrastructure overlap becomes concrete rather than
theoretical.

## Research thrusts

For external-facing framing (e.g. a funding/committee proposal) — present
these three thrusts and let papers emerge from them, rather than promising
a fixed paper count:

- **Thrust 1 — Learning from heterogeneous, data-sparse information**
  (Papers 2-7): multimodal representation, dynamic market graphs,
  distribution-shift robustness, calibration, data-centric AI, cross-market
  transfer.
- **Thrust 2 — Agentic reasoning and evidence acquisition** (Papers 8-11):
  evidence retrieval/attribution, evidence acquisition policy, conflicting
  evidence, continuous market monitoring.
- **Thrust 3 — Reliable adaptation and decision support** (Papers 12-14):
  continual learning, human-AI decision support, trustworthy AI under
  unequal data availability.
- **Research infrastructure** (Paper 15, AgriBench-EA) cuts across all
  three thrusts as the shared benchmark. Papers 1 and 16 are synthesis
  bookends written once the thrusts have real results.

## Sequencing notes

- **Papers 2, 5, 8, 12, 13** draw on experiments already active in this lab
  with real code grounding — these are the most immediately publishable.
- **Papers 9 and 10** are empirical threads grounded in real, currently
  hand-coded/fixed logic (`_apply_evidence_gate`, `WikiRetriever`'s fixed
  cascade, and the RAG layer's lack of conflict detection).
- **Paper 11** evaluates a monitoring loop that's already substantially
  built in production (`services/alerts/live_generator.py`,
  `news_intelligence.py`) — high real-evidence availability, low new-build
  cost.
- **Paper 6** depends on Paper 15's data-quality labeling; **Paper 7**
  (transfer learning) can start independently.
- **Paper 15** (the benchmark) is a resource-release effort, not a modeling
  paper — on its own track (licensing/hosting), doesn't block the others.
- **Papers 1 and 16** are synthesis papers written once enough of the
  others have real results — listed first/last by number but realistically
  drafted last, or drafted early as a skeleton and revised as results land.

## Priority

In order of near-term focus:

1. Paper 5 (calibration) — `forecast-confidence-calibration` already has
   real code (`_MIN_CONFIDENCE_TO_RECOMMEND` gate, ensemble calibration).
2. Paper 8 (evidence retrieval/attribution) — `evidence-attribution-quality`
   already has real grounding (`citation_check.py`, `check_grounding`).
3. Paper 12 (continual learning) — `continual-learning-drift-audit` already
   has the real feedback-loop bridge shipped this session.
4. Paper 11 (agentic market monitoring) — highest real-evidence-to-new-work
   ratio; the production loop already exists, "just" needs evaluation.
5. Paper 9 (evidence acquisition policy) — new, but cleanly scoped against
   real existing fixed-policy code.
6. Papers 2/3/4 (forecasting/graph) — active, ongoing.
7. Papers 7, 14, then 10, then 1/6/15/16 as their dependencies land.

## GitHub tracking

Each experiment above has a matching GitHub Issue (titled `[Thesis Lab]
<name>`) on the [AgroIntel Thesis Lab project board](https://github.com/users/jericho555/projects/1).
Each paper above corresponds to a GitHub Milestone of the same name — every
issue is assigned to its paper's milestone.
