# Agentic Agricultural Intelligence: Learning to Forecast, Reason Over, and Act on Multimodal Market and Climate Signals in Data-Sparse Environments

**Jeremiah Masaba** — PhD Student, Computer Science, Makerere University

*This is the source concept paper this entire lab is built from. Every*
*experiment in [`active_tests/`](active_tests/) and [`concluded/`](concluded/),*
*and the 16-paper structure in [`PUBLICATION_ROADMAP.md`](PUBLICATION_ROADMAP.md),*
*traces back to a hypothesis, objective, or research question stated here.*
*Preserved verbatim (only figures/PDF layout dropped) so future work can*
*cite the actual proposal, not a paraphrase of it.*

## Abstract

Agricultural decisions depend on heterogeneous information including
prices, trade, weather, satellite observations, food-security reports,
news, and local data. In East Africa, these sources are fragmented,
incomplete, noisy, and difficult to integrate. Existing AI systems
commonly treat forecasting, retrieval, risk assessment, and decision
support as separate tasks. This research investigates how agentic AI
can construct reliable, continuously updated intelligence from
heterogeneous and evolving information under uncertainty. I propose a
framework integrating multi-modal representation learning,
probabilistic forecasting, dynamic knowledge representations, evidence
retrieval, uncertainty estimation, and controlled continual learning.
The agent will determine what evidence is relevant, retrieve
additional information when needed, reconcile conflicting signals,
quantify uncertainty, and recommend or defer action. East African
agriculture will serve as a real-world testbed for data sparsity,
non-stationary markets, climate variability, and distribution shift.
The work will test whether integrated intelligence improves
forecasting, calibration, evidence grounding, and decision quality
relative to isolated and reactive systems, while producing methods
applicable to other data-sparse decision environments.

**Potential Collaborators**: Makerere University, Department of
Computer Science; Uganda Bureau of Statistics (UBOS); Uganda Ministry
of Agriculture, Animal Industry and Fisheries (MAAIF).

## 1. Introduction

Agricultural decision-making is a continuous intelligence problem
rather than a single prediction task. A farmer, trader, cooperative,
exporter, or policymaker may need to determine whether a price
movement is temporary or structural, whether international demand
creates a local opportunity, or whether weather and market signals
indicate an emerging risk. Relevant evidence is distributed across
price and trade databases, production statistics, climate
observations, satellite imagery, food-security reports, news, policy
events, and local information. Recent reviews show progress in
agricultural machine learning while identifying persistent challenges
in heterogeneous data, geographical variation, generalization, and
smallholder deployment (Jabed and Azmi Murad, 2024).

Existing approaches usually optimize individual tasks such as
forecasting, classification, retrieval, or question answering. They
provide limited mechanisms for deciding what evidence should be
acquired next, reconciling conflicting sources, determining when
uncertainty warrants deferral, or using validated feedback to improve
subsequent decisions. Agricultural systems also contain evolving
relationships among commodities, markets, regions, trade flows, and
climate events, motivating temporal and dynamic representations (Wang
et al., 2026; Zheng et al., 2025).

The scientific gap is the absence of a principled framework for
continuous, evidence-grounded, uncertainty-aware intelligence over
heterogeneous and evolving data. The central question is: **How can an
AI system construct reliable intelligence from incomplete and changing
information, decide what evidence is needed, reason under uncertainty,
support decisions, and learn safely from validated feedback?**

### 1.1 Central Research Hypothesis

Integrating multi-modal forecasting, dynamic evidence retrieval,
uncertainty estimation, and controlled feedback learning within an
agentic architecture will produce more accurate, better calibrated,
and more reliable decision intelligence than isolated forecasting or
reactive information retrieval, particularly under data sparsity,
distribution shift, and shocks. The hypothesis will be tested against
statistical and machine-learning baselines, single-modality models,
non-agentic retrieval systems, and conventional dashboard support.

### 1.2 Research Objectives

- **O1: Multi-modal forecasting.** Develop representations and
  probabilistic models that jointly exploit market, trade, climate,
  satellite, and textual signals, including temporal and cross-market
  dependencies.
- **O2: Evidence-grounded agentic reasoning.** Develop agents that
  retrieve relevant evidence, compare conflicting information,
  represent temporal relationships, quantify uncertainty, and decide
  whether to recommend or defer.
- **O3: Controlled continual learning and human-AI support.**
  Investigate adaptation from validated feedback and evaluate whether
  evidence- and uncertainty-aware recommendations improve decisions
  without harmful drift or feedback loops.

## 2. Proposed Work

The framework follows: **Observe → Represent → Forecast → Retrieve →
Reason → Quantify Uncertainty → Recommend/Defer → Observe Outcome →
Learn.**

**Observation and forecasting.** Historical and streaming data will be
aligned across time and geography while preserving provenance and data
quality. A dynamic knowledge representation will model relationships
among commodities, markets, regions, weather events, production, and
trade. Temporal and graph models will be compared with strong
baselines including Temporal Fusion Transformers and PatchTST (Lim et
al., 2021; Nie et al., 2023). Probabilistic forecasts will quantify
uncertainty.

**Evidence-grounded reasoning.** An agent will monitor signals and
determine when additional evidence is required. Retrieval-augmented
generation combines learned models with external evidence (Lewis et
al., 2021). The research will evaluate relevance, temporal
consistency, provenance, contradiction handling, and whether retrieved
evidence actually supports generated conclusions.

**Uncertainty and decisions.** The system will distinguish observed
evidence, predictions, inferred explanations, and recommendations. It
will account for source reliability, data quality, predictive
uncertainty, and disagreement between evidence streams. When evidence
is insufficient or uncertainty exceeds a defined threshold, the agent
should abstain or retrieve more evidence rather than produce an
apparently confident recommendation. Calibration will be explicitly
evaluated (Guo et al., 2017).

**Controlled continual learning.** New data, expert assessment, user
decisions, and observed outcomes will inform evaluation and candidate
updates. Outcomes will not be treated as automatic causal evidence
that a recommendation succeeded. Updates will undergo drift detection,
temporal holdout evaluation, comparison with the incumbent model, and
human oversight before deployment, testing adaptation without
catastrophic forgetting or unjustified confidence (Parisi et al.,
2019).

## 3. Research Questions and Evaluation

- **RQ1**: Can multi-modal representations improve forecasting over
  single-source models?
- **RQ2**: Can temporal and relational representations improve
  forecasting during structural change and shocks?
- **RQ3**: Can retrieval and structured knowledge improve factual
  grounding and reliability?
- **RQ4**: When should an agent retrieve more evidence, recommend, or
  abstain?
- **RQ5**: Can controlled continual learning improve adaptation
  without harmful feedback loops, drift, or overconfidence?
- **RQ6**: Does proactive, evidence-grounded support improve decision
  quality over reactive systems?

Experiments will focus on a limited set of commodities, outcomes, and
geographic settings selected for scientific relevance and data
availability. Baselines will include statistical models, gradient
boosting, temporal neural networks, transformers, graph models, and
probabilistic methods. Metrics will include MAE, RMSE, MAPE, weighted
interval score, calibration error, and directional accuracy, with
dedicated evaluation during shocks and distribution shifts. Ablations
will identify the contribution of each modality.

Agentic evaluation will use controlled scenarios with missing data,
conflicting sources, temporal events, and simulated shocks. Metrics
will include factuality, evidence attribution, temporal consistency,
contradiction handling, uncertainty calibration, appropriate
abstention, and recommendation reliability. Human-AI studies will
assess decision quality, risk identification, confidence calibration,
response time, and appropriate reliance or override. **AgroIntel will
be the experimental research platform; the primary PhD contribution
will be the underlying models, algorithms, evaluation protocols, and
scientific understanding rather than the product.**

## 4. Expected Results, Impact and Trustworthiness

Expected contributions are: (1) multi-modal agricultural forecasting
methods; (2) evidence-grounded agentic reasoning; (3) uncertainty-aware
recommendation and abstention; (4) controlled continual-learning
methods; (5) evaluation protocols for agentic intelligence under
sparsity and shocks; (6) empirical evidence on human-AI decision
support; and (7) peer-reviewed publications and reproducible artifacts
where licensing permits.

The novelty is not applying an existing Transformer, knowledge graph,
RAG system, or LLM agent to agriculture. It is experimentally testing
whether their integration yields measurable gains in reliability and
decision quality under incomplete information, conflicting evidence,
and distribution shift. Agriculture is the testbed for a broader AI
problem: maintaining reliable intelligence when no single dataset
provides a complete and stable view of reality.

Trustworthiness is a core research requirement. Recommendations will
retain provenance and distinguish evidence from prediction and
recommendation. The system will support abstention, monitor
performance, and evaluate disparities across regions, commodities, and
data availability. Human oversight remains central.

## 5. Data, Software and Ethics Policy

Results will be disseminated through peer-reviewed publications,
conference presentations, reproducible protocols, and selected
open-source software where licensing permits. Data will be used under
provider licenses and access conditions; restricted data will not be
redistributed. Human-AI evaluation will follow informed consent and
institutional review requirements where applicable. The system is
intended to support rather than replace decision-makers.

The research aligns with Bloomberg's interests in agentic AI,
information retrieval, structured reasoning, time-series modeling, and
trustworthy AI (Bloomberg, 2026). It investigates how AI can integrate
heterogeneous, evolving information, retrieve relevant evidence,
reason under uncertainty, and support reliable decisions, using
data-sparse agriculture as a rigorous testbed for generalizable
intelligence methods.

**Bloomberg employee consultants**: None.

## References

- Bloomberg. *Unlocking the value of interconnected data.* Bloomberg
  Professional Services, 2026.
- Chuan Guo, Geoff Pleiss, Yu Sun, and Kilian Q. Weinberger. *On
  calibration of modern neural networks.* Proceedings of the 34th
  International Conference on Machine Learning, PMLR 70:1321–1330,
  Aug 2017.
- M. A. Jabed and M. A. Azmi Murad. *Crop yield prediction in
  agriculture: A comprehensive review of machine learning and deep
  learning approaches, with insights for future research and
  sustainability.* Heliyon, 10(24):e40836, November 2024.
- Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni,
  Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis,
  Wen-tau Yih, Tim Rocktäschel, Sebastian Riedel, and Douwe Kiela.
  *Retrieval-augmented generation for knowledge-intensive NLP tasks*,
  2021. [arXiv:2005.11401](https://arxiv.org/abs/2005.11401).
- Bryan Lim, Sercan Ö. Arik, Nicolas Loeff, and Tomas Pfister.
  *Temporal fusion transformers for interpretable multi-horizon time
  series forecasting.* International Journal of Forecasting,
  37(4):1748–1764, 2021.
- Yuqi Nie, Nam H. Nguyen, Phanwadee Sinthong, and Jayant Kalagnanam.
  *A time series is worth 64 words: Long-term forecasting with
  transformers*, 2023. [arXiv:2211.14730](https://arxiv.org/abs/2211.14730).
- German I. Parisi, Ronald Kemker, Jose L. Part, Christopher Kanan,
  and Stefan Wermter. *Continual lifelong learning with neural
  networks: A review.* Neural Networks, 113:54–71, 2019.
- Jiapu Wang, Boyue Wang, Meikang Qiu, Shirui Pan, Bo Xiong, Heng Liu,
  Linhao Luo, Tengfei Liu, Yongli Hu, Baocai Yin, and Wen Gao. *A
  survey on temporal knowledge graph completion: Taxonomy, progress,
  and prospects.* IEEE Transactions on Knowledge and Data
  Engineering, 2026.
- Y. Zheng, L. Yi, and Z. Wei. *A survey of dynamic graph neural
  networks.* Frontiers of Computer Science, 19:196323, 2025.

## How this lab maps to the proposal

| Proposal element | This lab |
|---|---|
| O1 (multi-modal forecasting) | Papers 2–7, Thrust 1 |
| O2 (evidence-grounded agentic reasoning) | Papers 8–11, Thrust 2 |
| O3 (continual learning + human-AI support) | Papers 12–14, Thrust 3 |
| RQ1–RQ2 (forecasting) | `evidence-sparsity-reliability` (Paper 14) Experiment E1 |
| RQ5 (calibration, part of RQ4/uncertainty) | `evidence-sparsity-reliability` Experiment E2 |
| RQ3 (retrieval/grounding), RQ4 (abstention) | `evidence-sparsity-reliability` Experiments E3/E4 (not yet run) |
| AgroIntel as "the experimental research platform" | [`agrointel`](https://github.com/AgroIntel-EastAfrica/agrointel), included here as a git submodule |
