# Experiment: evidence-sparsity-reliability

- **Owner:**
- **Started:** 2026-09-17 (design phase; Phase 0 build not yet started)
- **Status:** active — Phase 0 in progress (schema + price-modality
  collection built and run live 2026-09-17; weather/trade/production/
  textual-event modalities not yet started)
- **Paper:** Paper 14 — redesigned title: **"Trustworthy Agricultural
  Intelligence Under Data Sparsity: An Empirical Study of Evidence
  Availability, Uncertainty, and Reliability"** (previously "Trustworthy
  Agricultural Intelligence Under Unequal Data Availability" —
  [`regional-equity-audit`](../../concluded/regional-equity-audit/experiment_blueprint.md),
  concluded 2026-09-17 and reset into this experiment; see that file's
  own Concluding Note for what carries forward and why).
- **Provenance of this design**: given verbatim by the project owner on
  2026-09-17 as the redesign direction for Paper 14, transcribed here in
  full rather than summarized, since it *is* the plan to follow, not a
  proposal to paraphrase. Section numbers below match the original.

## Why this reset happened

The concluded `regional-equity-audit` experiment was valuable — it
exposed three real production bugs and quantified a genuine data-
availability gap — but it mixed too many things together: data
availability, production-system bugs, forecasting validity,
recommendation behavior, and calibration, in an audit framed around
comparing countries to each other (Kenya vs. Uganda). That makes causal
interpretation difficult: too many confounders differ between any two
countries at once, which is exactly what that experiment's own MAPE-
reversal and price-basis-mismatch findings kept demonstrating in
practice (see its Concluding Note for the full accounting).

This experiment turns Paper 14 into a **controlled scientific
experiment**, with AgroIntel as the experimental platform rather than
the object being casually audited.

## Objective — the new central question

The original question was roughly:

> Does unequal data availability translate into unequal service quality?

Replaced with:

> **How does evidence availability and evidence quality affect the
> reliability of AI intelligence under data-sparse conditions?**

This gives three experimental factors — **Evidence availability →
Evidence quality → Distribution shift** — and four outcomes —
**Forecast accuracy → Uncertainty calibration → Evidence grounding →
Decision reliability**.

**The most important conceptual shift**: don't ask *"How accurate is
AgroIntel?"* — ask *"Under what evidence conditions can an AI system be
trusted?"* That is the real bridge between Paper 14 and the PhD's
broader framing of studying how AI can construct reliable intelligence
from heterogeneous, incomplete, continuously changing information,
rather than simply building an agricultural product.

## Hypothesis

**Main hypothesis (H1, umbrella)**: As evidence becomes less complete,
less reliable, or more heterogeneous, AI intelligence degrades unless
the system explicitly models evidence provenance, uncertainty, and
evidence sufficiency.

Broken into measurable sub-hypotheses:

| # | Hypothesis |
|---|---|
| H1 | **Evidence availability** — reducing real observed data affects forecasting performance and uncertainty. |
| H2 | **Evidence quality** — poor-quality or semantically mismatched evidence produces *greater* error than simply missing evidence. |
| H3 | **Calibration** — confidence becomes less reliable as evidence quality/availability deteriorates, unless uncertainty is explicitly calibrated. |
| H4 | **Evidence grounding** — an agent that retrieves and validates evidence produces fewer unsupported claims than one without evidence verification. |
| H5 | **Abstention** — an uncertainty-aware agent increasingly defers rather than producing unsupported recommendations when evidence is insufficient. |

## Core Variables

### The four controlled experiments inside Paper 14

Not one giant "run AgroIntel and see what happens" — four scoped
experiments:

```text
                    PAPER 14
                       |
        +--------------+--------------+
        v              v              v
       E1             E2             E3             E4
    Forecasting    Calibration     Evidence      Decision
    under data     under data      grounding      /abstention
    sparsity       sparsity        & conflict
```

### E1 — Forecasting under controlled data availability

Fixed set of commodities/countries/markets/time periods, then
constructed evidence tiers (not country identity) as the independent
variable:

| Tier | Evidence condition |
|---|---|
| T0 | Price only |
| T1 | Price + weather |
| T2 | Price + weather + trade |
| T3 | Price + weather + trade + production |
| T4 | Full multimodal evidence |

Question: does adding heterogeneous evidence improve forecasting? —
directly aligned with the PhD proposal's RQ1 (does jointly representing
market, trade, climate, satellite and textual information improve
forecasting).

**Rule**: never compare Kenya vs. Uganda and conclude one country's AI
is worse — too many confounders. Compare *the same forecasting problem*
under controlled evidence conditions instead.

### Deliberate, systematic data sparsity (not just naturally-sparse countries)

Take a dataset with reasonably good coverage and systematically remove
information:

```text
100% data -> 75% -> 50% -> 25% -> 10% -> 0%
```

Evaluate the same model at every level. Gives controlled experimental
variables: data availability -> forecast error; data availability ->
uncertainty; data availability -> calibration.

**Three missingness mechanisms to test, not just random removal**:

- **MCAR** — randomly remove observations.
- **MAR** — remove observations according to observable conditions
  (certain countries, commodities, years, geographic levels).
- **Structured scarcity** — realistic situations: no recent prices, no
  production statistics, missing weather, missing trade data, missing
  satellite observations, missing textual evidence.

This makes data sparsity an **experimental variable**, not simply an
unfortunate characteristic of the dataset.

### E2 — Uncertainty and calibration

The concluded experiment found stated confidence ~80% vs. observed
interval coverage ~38.5% — real evidence something is wrong, but this
experiment determines *what happens when uncertainty is properly
modeled*.

Compare:
- **Baseline A** — uncalibrated model confidence.
- **Baseline B** — post-hoc calibration.
- **Baseline C** — prediction intervals.
- **Baseline D** — conformal prediction or another distribution-free
  uncertainty approach.

Then progressively reduce evidence availability and record, per level
(100% / 75% / 50% / 25% / 10%): confidence, coverage, calibration
error.

Question: can uncertainty estimation tell the system when its evidence
has become insufficient? — directly connected to PhD RQ4 (when should
the agent generate a recommendation, retrieve more evidence, or refrain
from recommending).

### E3 — Evidence grounding

This is where Paper 14 becomes genuinely agentic rather than a pure
forecasting paper. Construct scenarios:

- **Scenario A** — sufficient, consistent evidence.
- **Scenario B** — insufficient evidence.
- **Scenario C** — conflicting evidence.
- **Scenario D** — outdated evidence.
- **Scenario E** — semantically incompatible evidence (e.g. Source A:
  Uganda coffee *producer* price = X; Source B: Uganda coffee *retail*
  price = Y — a naive system combines them; a trustworthy agent
  recognizes these are different price bases. This is precisely what
  the concluded experiment's real price-basis incident exposed).

**Give the agent explicit actions** instead of forcing it to always
answer:

```text
              Evidence state
                    |
       +------------+------------+
       v            v            v
   Sufficient    Uncertain     Conflicting
       |            |            |
       v            v            v
   Recommend     Retrieve      Investigate
                    |
                    v
                Still weak?
                    |
                    v
                 Abstain
```

Measurable: recommendation accuracy, unsupported-recommendation rate,
evidence retrieval success, contradiction detection, abstention
precision, unnecessary abstention, calibration. Close to the PhD
proposal's "adaptive evidence acquisition."

### E4 — Decision reliability (deliberately the smallest of the four)

Not a large field study. Controlled agricultural decision scenarios —
e.g. *"Coffee prices are predicted to increase 12% over the next three
months. Should a cooperative increase inventory?"* — presented via:

1. raw data
2. conventional dashboard
3. AI forecast
4. evidence-grounded agent
5. uncertainty-aware agent

Measure: decision accuracy, risk identification, confidence, response
time, appropriate reliance, inappropriate reliance, override behavior —
maps directly onto the PhD proposal's human-AI evaluation outcomes.

### The experimental matrix

**Experiment A — Data availability**

| Condition | Evidence |
|---|---|
| C0 | price only |
| C1 | price + weather |
| C2 | + trade |
| C3 | + production |
| C4 | + text/events |

**Experiment B — Data sparsity**

| Condition |
|---|
| 100% |
| 75% |
| 50% |
| 25% |
| 10% |

**Experiment C — Evidence corruption**

| Condition |
|---|
| clean |
| stale |
| conflicting |
| wrong geography |
| wrong price basis |
| missing source |

**Experiment D — Agent behavior**: answer / retrieve / investigate /
abstain.

### Gold-standard evaluation dataset (the single most important
methodological improvement)

Every observation carries metadata: `country, commodity, market,
geography, date, value, unit, price_basis, source, source_timestamp,
data_quality, observed/synthetic`. E.g.:

```text
Uganda / Coffee / National / 2025 / Producer price / USD/tonne /
FAOSTAT / Observed / Verified
```
vs.
```text
Uganda / Coffee / National / 2025 / Reference price / USD/tonne /
Synthetic baseline / Synthetic / Not suitable as ground truth
```

Then the experiment always knows exactly what constitutes a valid
target — this directly prevents the concluded experiment's original
MAPE-mixing problem (its own §2026-09-15 entry: forecasting a synthetic
random walk against itself is a fundamentally easier, less meaningful
task than forecasting a real market, and the two must never be blended
into one number).

**Three states, never collapsed into two**:

```text
OBSERVED
SYNTHETIC
UNKNOWN
```
possibly further:
```text
OBSERVED
  |- VERIFIED
  `- UNVERIFIED
SYNTHETIC
  |- BASELINE
  `- IMPUTED
UNKNOWN
```

Hard rule the evaluation pipeline must enforce: **synthetic values
cannot be treated as ground truth.** (This is the same rule migration
048's `source_mismatch` tracking already implements in production —
see the concluded experiment's Concluding Note.)

### Evidence Quality Vector

Separate **data quantity** from **data quality**. Quantity = how much
information exists. Quality is multi-dimensional:

- **Quality** — how trustworthy is it?
- **Relevance** — does it address the question?
- **Freshness** — how old is it?
- **Compatibility** — can it legitimately be combined with other evidence?
- **Provenance** — where did it come from?
- **Coverage** — which country/commodity/geography does it actually represent?

Evidence Quality Vector: **E = (A, Q, R, F, C, P, G)** where A =
availability, Q = quality, R = relevance, F = freshness, C =
compatibility, P = provenance, G = geographic coverage — a candidate
scientific construct for the paper.

This gives a stronger definition of data sparsity than "there isn't
much data":

> **The degree to which the evidence required for a decision is
> unavailable, unreliable, stale, incomplete, or incompatible.**

A system can have lots of data but still have poor evidence:

```text
1,000,000 observations
        |
wrong geography / wrong price basis / old timestamps / unknown provenance
        |
LOTS OF DATA -> LOW EVIDENTIAL VALUE
```

### Strict evaluation hierarchy (fixes the forecasting-target problem)

- **Primary evaluation** — only independently verified observed values.
- **Secondary evaluation** — partially observed values, clearly
  labelled.
- **Synthetic evaluation** — synthetic data only for robustness
  experiments, never for headline accuracy claims.

Results are reported as three separate numbers — *observed-ground-truth
performance*, *synthetic robustness performance*, *unknown-target
cases* — never blended into one giant MAPE.

### Data provenance audit trail

Every prediction carries something like:

```text
FORECAST
--------
Country: Uganda | Commodity: Coffee | Horizon: 30 days
Evidence:
  [x] Price: FAOSTAT
  [x] Weather: NASA
  [x] Trade: Comtrade
  [ ] Local market: unavailable
  [!] News: 3 days old
Evidence completeness: 72% | Evidence quality: 81%
Prediction: $X | Interval: [$A, $B] | Confidence: 64%
Decision: RECOMMEND WITH CAUTION
```

Lets the experiment test whether stated confidence actually corresponds
to empirical reliability — fits the PhD proposal's emphasis on
distinguishing observations, predictions and recommendations while
retaining provenance.

### Failure-mode taxonomy (F1–F5) — carried forward from the concluded
experiment's real bugs, not invented in the abstract

| # | Failure mode | Real instance already found (concluded experiment) |
|---|---|---|
| F1 | **Provenance failure** | Synthetic data represented as real — the Selina Wamucii fabricated-price incident. |
| F2 | **Training-evidence contamination** | Model trained using inappropriate synthetic evidence — the unvalidated `BASE_PRICES_USD` anchor. |
| F3 | **Geographic/semantic-level failure** | Local/sub-national evidence silently routed to national level — the `GeographyLevel.LOCAL`/`.SUB_NATIONAL` routing bug. |
| F4 | **Source reliability failure** | External data connector silently fails — the FAOSTAT `_login()` form-encoding bug, silently degrading to synthetic for an unknown period. |
| F5 | **Semantic incompatibility** | Different price bases treated as comparable — the RW/BI coffee/tea price-source-mismatch incident (881–1186% false MAPE). |

Research question this taxonomy enables: **which classes of evidence
failure are most damaging to AI reliability?** — a scientific question,
not a bug list.

**A dedicated experiment for silent failures**: introduce controlled
perturbations (correct source -> source failure -> missing source ->
stale source -> wrong geography -> wrong price basis -> conflicting
source) and measure whether the agent (1) detects the problem, (2)
quantifies the uncertainty, (3) retrieves alternative evidence, (4)
changes its recommendation, (5) abstains when necessary. Tests AI
*resilience*, not merely forecasting.

### System architecture this experiment implies

```text
                    REAL WORLD
                        |
        +---------------+----------------+
        |               |                |
      Market          Climate           Trade
        |               |                |
        +---------------+----------------+
                        v
                Evidence Layer
                        |
          +-------------+--------------+
          v             v              v
      Provenance      Quality       Semantics
          |             |              |
          +-------------+--------------+
                        v
               Multimodal Model
                        |
                        v
                  Forecast
                        |
                        v
               Uncertainty Model
                        |
                        v
               Evidence Retrieval
                        |
                        v
                Agentic Reasoning
                        |
          +-------------+--------------+
          v             v              v
      Recommend       Retrieve       Abstain
          |             |              |
          +-------------+--------------+
                        v
                  Evaluation
                        |
        +---------------+----------------+
        v               v                v
    Accuracy       Calibration       Grounding
        |               |                |
        +---------------+----------------+
                        v
                Decision Reliability
```

A miniature version of the PhD research programme.

### Relationship to the wider publication roadmap — real overlap, flagged
honestly rather than hidden

| PhD objective | Paper 14 component |
|---|---|
| O1: Multimodal forecasting | Controlled evidence availability + multimodal forecasting (E1) |
| O2: Evidence-grounded agentic reasoning | Retrieval, provenance, contradiction, evidence sufficiency (E3) |
| O3: Controlled continual learning / human-AI | Calibration, abstention, feedback, decision evaluation (E2, E4) |

Paper 14 becomes a **pilot study spanning all three** PhD thrusts,
rather than a separate side project — the first empirical demonstration
of why those capabilities need to be integrated.

**This substantially overlaps, by design, with several already-scoped
papers in `thesis-lab/PUBLICATION_ROADMAP.md`**: Paper 5 (probabilistic
calibration -> E2), Paper 6 (data-centric AI for low-resource markets ->
the Evidence Quality Vector / gold-standard dataset), Paper 8 (evidence
retrieval/attribution -> E3 grounding), Paper 9 (evidence acquisition
policy -> E3's retrieve/investigate/abstain policy), Paper 10
(reasoning over conflicting evidence -> E3's Scenario C/E), Paper 13
(human-AI decision support -> E4). **Not resolved here** — this is an
explicit open coordination question the roadmap needs updated to
reflect, not something silently decided by this session. Two honest
readings, both consistent with the redesign as given:
1. Paper 14 stays a small, bounded *pilot* (4 countries, 3 commodities,
   1 task — see Success Metrics/Scope below) that later feeds into
   Papers 5/6/8/9/10/13 as their own deeper, separate treatments (the
   redesign's own explicit "don't build everything yet" framing
   supports this reading).
2. Some of those papers get formally absorbed into Paper 14 rather than
   remaining separate, if their scope turns out to be redundant once
   Paper 14's infrastructure exists.

`thesis-lab/PUBLICATION_ROADMAP.md`'s Paper 14 row has been updated to
flag this as open; the individual paper rows (5/6/8/9/10/13) have
**not** been changed, since deciding to absorb or not absorb them is
the project owner's call, not an inference this session should make
unilaterally.

## Success Metrics — deliberately bounded scope for this first pass

Explicitly **not** attempted yet: the full final AgroIntel agent, every
crop, every EAC country, every data source, every forecasting
architecture, continual learning, sophisticated human studies, every
satellite modality — building all of that would make the experiment
impossible to interpret.

**Scope, finalized 2026-09-17** (was "candidates, pending selection" —
now locked in against a fresh live check, not just the concluded
experiment's older numbers):
- **4 countries** — **Kenya, Rwanda** (data-rich) and **South Sudan,
  Somalia** (data-sparse). Confirmed live via `get_daily_price()` for
  all 3 commodities below: KE and RW return `price_source: "faostat"`
  (real) for coffee/maize/tea without exception; SS and SO return
  `price_source: "baseline"` (synthetic) for all three, also without
  exception — a clean, fully-matched split, not a partial one.
  Deliberately chose SS/SO over the blueprint's earlier UG/SS
  placeholder: SS and SO are the two data-sparse countries this lab has
  *independently* confirmed zero real coverage on a second,
  structurally different data system (UN Comtrade trade flows, not just
  FAOSTAT prices — see the concluded experiment's Phase 1) — the
  strongest, most defensible "genuinely data-sparse" pair available,
  rather than Uganda, which has real secondary infrastructure (UBOS/URA
  crawlers, real weather, real user/pulse activity) that would muddy a
  clean data-availability contrast even though its FAOSTAT price
  coverage is also zero. Kenya (highest real FAOSTAT row count, 1,284)
  and Rwanda (824 rows, and already has real production infrastructure
  from this session's price-source-mismatch fix — migration 048's
  `predicted_price_source` tracking was live-verified specifically
  against RW coffee/tea) are the two data-rich picks.
- **3 commodities** — coffee, maize, tea (confirmed real FAOSTAT
  coverage for both KE and RW, live-verified alongside the country
  selection above — not assumed from the concluded experiment's older
  numbers).
- **1 primary forecasting task** — 30-day agricultural price forecasting.
- **4–5 evidence modalities** — price, weather, trade, production,
  textual events/news.
- Controlled experiments on evidence availability (Experiments A–D
  above) on top of that fixed scope.

**Metrics, by category** (replacing "just MAPE"):

| Category | Metrics |
|---|---|
| Forecasting | MAE, RMSE, MAPE/sMAPE where appropriate, directional accuracy |
| Uncertainty | prediction interval coverage, interval width, calibration error, weighted interval score |
| Evidence | evidence precision, evidence recall/coverage, attribution accuracy, contradiction detection, temporal consistency |
| Agent behavior | appropriate retrieval rate, unnecessary retrieval rate, appropriate abstention, unsafe recommendation rate |
| Decision | decision quality, risk identification, confidence, appropriate reliance |

Decided-before-looking-at-results criteria for each hypothesis (H1–H5)
still need to be pinned down numerically once Phase 0's gold-standard
dataset exists — flagged as the first concrete task of Phase 1, not
guessed at here.

### Planned phase sequence

| Phase | Content |
|---|---|
| 0 | Build the gold-standard dataset and provenance layer |
| 1 | Establish forecasting baselines |
| 2 | Controlled evidence sparsity |
| 3 | Uncertainty/calibration |
| 4 | Evidence conflict and semantic mismatch |
| 5 | Agentic retrieval and abstention |
| 6 | Integrated reliability analysis |

None of these phases have started yet — this file is the design
document Phase 0 will be built against, per the project owner's
explicit "document this, don't build yet" instruction on 2026-09-17.

## What Paper 14 could ultimately establish

Not the fairly intuitive "data scarcity hurts agricultural
forecasting," but:

> **Which dimensions of evidence scarcity actually cause reliability
> degradation, and can an agentic system compensate through retrieval,
> uncertainty estimation and abstention?**

A plausible (not yet measured) results shape, useful as a falsifiable
target rather than a foregone conclusion:

```text
Missing data          -> moderate degradation
Poor provenance        -> large degradation
Semantic mismatch      -> very large apparent error
Uncalibrated confidence -> overconfident decisions
Evidence retrieval     -> partial recovery
Abstention             -> reduced unsupported recommendations
```

These are scientifically interesting findings even if the actual
results don't match this shape — the experiment is designed to produce
a meaningful result whether the agent succeeds, partially compensates,
or fails under increasing evidence scarcity, not to only be publishable
if it confirms the hypothesis.

## Core Variables (summary — see Experiments A–D above for full detail)

- **Held constant**: the platform (AgroIntel), the 4-country/3-commodity/
  1-task/4–5-modality scope, the gold-standard dataset's provenance
  schema once built.
- **Varied (the actual experimental factors)**: evidence availability
  (Experiment A tiers, Experiment B sparsity levels), evidence quality/
  corruption type (Experiment C), and agent policy availability
  (Experiment D).
- **Real data, matching the thesis-lab sandbox rules**: Phase 0's
  gold-standard dataset must be built read-only against real production
  data (matching the concluded experiment's own precedent — FAOSTAT,
  RecommendationEngine, `forecast_evaluations`) or genuinely synthetic
  data explicitly labeled `SYNTHETIC`, never a silent blend of the two.

## Results

### Phase 0, first slice — 2026-09-17: schema + real price-modality collection

Built and ran the first real piece of Phase 0, scoped deliberately
narrow: the price modality only (weather/trade/production/textual-event
modalities are separate, not-yet-built collection scripts — price went
first because `get_daily_price()`'s real/synthetic distinction is
already fully audited and trustworthy from this session's own price-
source-mismatch investigation, giving Phase 0 a solid foundation rather
than guessing at provenance for an unaudited modality).

**Built**: `scripts/provenance.py` — the real schema (`DataState` enum:
`OBSERVED_VERIFIED` / `OBSERVED_UNVERIFIED` / `SYNTHETIC_BASELINE` /
`SYNTHETIC_IMPUTED` / `UNKNOWN`, with `is_valid_ground_truth` true only
for `OBSERVED_VERIFIED` — the one rule that matters most, enforced in
code rather than just documented); `EvidenceQualityVector` (the 7-
dimension `E = (A,Q,R,F,C,P,G)` construct, each dimension `float | None`
— left `None` rather than fabricated where this slice has no real basis
to compute it yet); `GoldStandardObservation`, the actual per-row
schema. `scripts/collect_gold_standard.py` — real, read-only collection
against `services/market/price_model.get_daily_price()` for the
finalized scope, writing a local JSON file under `data/` (never a
production table, per the thesis-lab sandbox rule).

**Run live, 2026-09-17**: 12 real observations (4 countries × 3
commodities) —

```
observed_verified:  6   (KE coffee/maize/tea, RW coffee/maize/tea — all price_source="faostat")
synthetic_baseline: 6   (SS coffee/maize/tea, SO coffee/maize/tea — all price_source="baseline")
```

A clean, fully-matched split with zero exceptions — confirms the
finalized 4-country scope (see Success Metrics/Scope above) is correctly
chosen: the rich/sparse contrast is real and total for this modality,
not partial. Sample row (KE coffee):

```json
{
  "country_code": "KE", "commodity": "coffee", "market": "national",
  "geography_level": "NATIONAL", "observation_date": "2026-09-17",
  "value": 4807.3, "unit": "USD/tonne",
  "price_basis": "producer_price_faostat_usd_tonne",
  "source": "faostat", "data_state": "observed_verified"
}
```

**Verified**: `ruff check` clean. Output inspected directly (not just
"it ran without error") — field values, `price_basis` strings, and
`data_state` classification all confirmed correct against the same live
`get_daily_price()` check used to finalize country/commodity selection
above.

**What Phase 0 still needs, honestly not yet done**: weather, trade,
production, and textual-event collection scripts (the other 4–5
evidence modalities); the `EvidenceQualityVector`'s 7 dimensions remain
entirely unpopulated (`None`) until a second modality exists to compute
`compatibility`/`geographic_coverage`/etc. against; no historical
time-series collection yet (today's snapshot only — Experiment A/B's
tiered/sparsity comparisons need a real multi-date sample, not one
day); the numeric success criteria for H1–H5 (flagged in Success
Metrics as needing to be pinned down once real data exists) are still
undecided.
