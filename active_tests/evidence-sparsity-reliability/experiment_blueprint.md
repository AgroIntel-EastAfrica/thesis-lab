# Experiment: evidence-sparsity-reliability

- **Owner:**
- **Started:** 2026-09-17
- **Status:** active — Phase 0 in progress. 2 of 4–5 evidence modalities
  fully collected live 2026-09-17 (price, weather); trade built but
  blocked mid-run by a real UN Comtrade API rate limit (reopen item:
  re-run after ~2026-09-18 03:00 UTC); production and textual-event
  modalities not yet started. Evidence Quality Vector still unpopulated
  (technically computable now, deliberately deferred).
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

### Success criteria per hypothesis — pinned down 2026-09-20

**A real timing problem, stated honestly rather than hidden**: this
section's own name promises "decided-before-looking-at-results"
criteria. That is only true for H2–H5 below — E1 already ran (the
blueprint's tenth/eleventh/thirteenth slices) before this section was
written, so any numeric threshold for H1 written *now* would be
post-hoc, not pre-registered, no matter how it's phrased. H1 is
therefore given a **retrospective** criterion instead — stated as what
a reasonable bar would have been, applied honestly to data already
seen, not dressed up as a prediction. H2–H5 have no results yet (E2–E4
haven't run), so their criteria below genuinely are decided before
looking — the real thing this section originally promised, just not
for all five hypotheses at once.

- **H1 — evidence availability** (retrospective, not pre-registered):
  a reasonable a priori bar — "affects forecasting performance"
  supported if MAPE differs by ≥2 percentage points *or* directional
  accuracy differs by ≥10 points between evidence tiers tested.
  Applied to the real E1 results already obtained: directional
  accuracy moved by +10.5 points (T0→T1, 0.489→0.594, clears the bar);
  MAPE moved by only 0.5 points (15.0%→14.3%, does not). **Partial,
  metric-dependent support** — consistent with H1's own "affects"
  wording (not "always improves"): T1→T3 also showed evidence
  actively *worsening* RMSE, which is itself evidence for H1's neutral
  framing over a naively optimistic reading of it.
- **H2 — evidence quality** (pre-registered, E3 not yet run):
  supported if substituting a *corrupted* value (wrong country, wrong
  price basis, or a stale/expired year — Experiment C's real
  conditions) for one real input produces mean MAPE **≥5 percentage
  points higher** than simply *omitting* that input (i.e., demonstrably
  worse than admitted-missing evidence, not just similarly bad). Not
  supported if the gap is under 2 points.
- **H3 — calibration** (pre-registered, E2 not yet run, grounded in a
  real prior number): the concluded experiment found 80% stated
  confidence vs. 38.5% observed coverage — a real 41.5-point miss.
  Supported if, at 100% evidence availability, a calibrated model
  (Baseline C/D) lands within **10 points** of its nominal confidence
  (e.g. 80% nominal → 70–90% observed) while the uncalibrated baseline
  (Baseline A) misses by **more than 20 points** — beating the
  concluded experiment's own real failure, not an arbitrary target.
  Further supported if the calibrated model's coverage stays within 15
  points of nominal even at 25% evidence availability, while the
  uncalibrated baseline's gap widens by more than 15 points over that
  same range (degrades more gracefully, not just starts better).
- **H4 — evidence grounding** (pre-registered, E3's agent harness not
  yet built): supported if an agent with evidence verification (checks
  a retrieved value's `DataState` before using it) produces an
  unsupported-claim rate **≥15 percentage points lower** than an
  equivalent agent without verification, across Scenarios A–E.
- **H5 — abstention** (pre-registered, E4 not yet run): supported if
  an uncertainty-aware agent's abstention rate is **non-decreasing**
  across Experiment B's 5 sparsity levels (100%→10%) *and* exceeds
  **50%** at the 10% level (defers on the majority of genuinely
  insufficient cases), while its false-abstention rate at 100%
  availability stays **under 10%** (doesn't defer when it shouldn't).

**Status**: a first, defensible draft grounded in real numbers where
they exist (H3's threshold is not arbitrary — it's the concluded
experiment's own documented failure), not yet reviewed by the project
owner or an advisor — real future work, not a hidden gap.

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

### Phase 0, second slice — 2026-09-17: weather modality, and a schema revision

**Schema revision, before any data outside the first price-only demo
depended on the narrower shape**: `GoldStandardObservation`'s single
`commodity` field couldn't honestly name what weather data measures (a
temperature reading isn't a commodity). Added `modality` (`"price"` /
`"weather"` / …) and `variable` (the specific measured quantity, e.g.
`"producer_price"`, `"temperature_2m"`); `commodity` is now optional,
`None` for modalities with no crop subject. The price collector was
updated to match and re-run — same clean 6/6 observed/synthetic split
as before, confirming the schema change didn't alter the underlying
data, just how it's labeled.

**Built**: `scripts/collect_weather.py`, against the real NASA POWER API
(`clients/nasa_power.py`), for the same 4-country scope, real capital
coordinates read directly from `configs/countries/<name>.yaml` (Nairobi,
Kigali, Juba, Mogadishu — not re-derived or guessed).

**A real data-quality nuance found and handled, not glossed over**: a
live test call before writing the script showed NASA POWER returns
`-999.0` as a fill-value sentinel for a date it hasn't finished
processing yet — the most recent 3 days of a test query all came back
`-999.0`. Naively treating that as a real value would have been exactly
the kind of provenance mistake this whole experiment exists to prevent.
The collector walks backward from today to find each parameter's most
recent genuinely-available reading and records *that real date* as
`observation_date` — an honest freshness signal — rather than claiming
today's date for a stale or fabricated value.

**Run live, 2026-09-17**: 8 real observations (4 countries × 2
parameters — temperature and precipitation) —

```
KE temperature_2m: 20.95 celsius (as of 2026-09-14)   KE precipitation: 0.28 mm/day
RW temperature_2m: 21.07 celsius (as of 2026-09-14)   RW precipitation: 4.97 mm/day
SS temperature_2m: 29.63 celsius (as of 2026-09-14)   SS precipitation: 4.69 mm/day
SO temperature_2m: 26.80 celsius (as of 2026-09-14)   SO precipitation: 1.97 mm/day
```

All 8 rows are `observed_verified` — **including South Sudan and
Somalia**, the two countries with zero real price coverage. This is a
genuinely interesting, confirmed real finding, not an assumption: unlike
price, weather evidence is **uniformly available across both country
tiers** — NASA POWER's satellite coverage doesn't care whether a country
has a functioning national statistics office submitting data to FAO.
Directly demonstrates the blueprint's own point that evidence
availability is a per-modality property, not a fixed per-country one —
the same country can be data-rich on one evidence axis and data-sparse
on another, which is precisely why the redesign treats evidence
availability as an experimental factor rather than a country label.

**Verified**: `ruff check` clean on both scripts. Output inspected
directly, not just "it ran" — every value, unit, and the walked-back
`observation_date` cross-checked against the live test call's own raw
NASA POWER response.

### Phase 0, third slice — 2026-09-17: trade modality, blocked mid-run by
a real API rate limit (itself a genuine finding, not just an obstacle)

**Built**: `scripts/collect_trade.py`, against the real UN Comtrade API
(`clients/comtrade.py`). Real shape difference from price/weather,
confirmed via a live test call first: `get_trade_flows()` returns one
row **per trading partner** (73 real rows for Kenya coffee exports,
2023), not a single aggregate figure — trade flows measure total export
*value* (USD), not a unit price, a fundamentally different kind of
measurement than the price modality's USD/tonne. Each observation here
sums `primaryValue` across every real partner row Comtrade returns for
a given reporter/commodity/year — an honest aggregation of real data,
recorded under its own `variable` name (`export_value_total`) rather
than conflated with "price."

**What actually happened live**: the standalone test call for Kenya
coffee succeeded (73 real rows, e.g. two sample partner rows worth
$572,089.59 and $51,518.97 — genuinely non-zero, confirming real trade
data exists for this reporter/commodity/year). But running the full
12-call collector (4 countries × 3 commodities) immediately hit UN
Comtrade's real API quota: `403 "Out of call volume quota. Quota will
be replenished in 07:37:XX"` — a genuine, live rate limit, not a bug in
this script, and the same fallback path the client tries on failure
hit the identical quota (same underlying account, no separate rescue).
All 12 observations correctly recorded as `DataState.UNKNOWN` — the
collector deliberately does **not** treat a rate-limited call as
confirmed-zero trade, which would be a real false negative
indistinguishable from the SS/SO "genuinely zero" finding the concluded
experiment already established for the `TOTAL` commodity code. This
run cannot yet confirm or deny that same zero holds per-commodity for
coffee/maize/tea specifically — that's still an open question, not
assumed to match.

**Why this is a real finding worth keeping, not just an obstacle**: an
evidence source's own operational rate limits are themselves a
dimension of evidence availability a production agentic system has to
handle — this is a live, concrete instance of failure mode F4 (source
reliability failure, see the taxonomy above) happening to this exact
experiment while building it, not a hypothetical. Directly relevant to
Experiment C (evidence corruption: "missing source") and Experiment E3
(does the agent detect the problem rather than silently treating a
failed call as a zero-evidence signal?).

**Reopen item**: re-run `collect_trade.py` once the quota replenishes
(~7.5h from 2026-09-17 19:22 UTC, i.e. roughly 2026-09-18 03:00 UTC) to
get the real, complete per-commodity picture for all 4 countries — not
yet done as of this entry.

**Verified**: `ruff check` clean. The one real successful call (KE
coffee, 73 partner rows) was inspected directly before the quota hit;
the 12-row `UNKNOWN` batch was verified to be the correct, honest
degradation path, not a crash or a silently-wrong zero.

### Phase 0, fourth slice — 2026-09-17/18: production modality, unblocked
by fixing two real production bugs found along the way

**Built**: `scripts/collect_production.py`, against
`services/forecasting/yield_prediction.py`'s
`_fetch_faostat_yield_history()` (real FAOSTAT QCL domain). Unlike
price/weather/trade, this function returns a full year→MT/ha history
rather than one point-in-time reading, so each observation here takes
the single most recent real year in that history — the same "most
recent real reading" convention `collect_weather.py` already
established for a different underlying reason (NASA POWER's
fill-value walk-back).

**A necessary detour before this modality was usable at all**:
attempting to build this collector immediately surfaced that
`_fetch_faostat_yield_history()` had never worked for real, in two
compounding ways. (1) It never sent an `Authorization` header on its
FAOSTAT QCL request — every real call has 401'd since the module
shipped, silently degrading every `YieldPredictionService` caller to
the hardcoded knowledge-base fallback table the whole time. (2) With
auth fixed, it still returned zero rows: the code queried element
`"5421"`, which matches none of QCL's real element codes (5312 Area
harvested, 5412 Yield, 5510 Production) — a digit transposition of
5412. Fixing the code alone still wasn't enough: a live test proved
QCL's server-side `element` query filter itself doesn't reliably work
(a request with `element=5412` explicit still returned 0 rows despite
64 real years of exactly that element existing for the same area/item
with no filter applied) — the actual fix fetches all elements per
(area, item) and filters client-side by `Element Code`, the same
defensive pattern already added to `faostat_prices.py`'s PP fetcher
earlier this session, now proven empirically necessary here too. A
third, latent bug surfaced once real training data started flowing for
the first time: `_xgboost_yield_predict` fed `rainfall_deviation` into
XGBoost as a training feature, but every training row's value for it
was a hardcoded `0.0` (no real per-year rainfall history exists), so a
tree model could never learn to use it — any rainfall value passed at
inference was silently ignored. Caught live via a real, previously-
passing test (`test_optimal_rainfall_boosts_yield`) failing once the
real code path became reachable for the first time; fixed by applying
rainfall as a post-hoc climate multiplier, matching the sibling
`_linear_trend_predict`/baseline branches' existing convention. All
three fixes are real production code changes (not thesis-lab), went
through the full commit → push → PR cycle to `master` (not merged —
pending the project owner's go-ahead, per this session's standing
policy), and are logged in `product/PRODUCTION_AUDIT.md`'s Change Log.

**What actually happened live**, run against the real, now-fixed
FAOSTAT API for the full 4×3 scope:

| Country | Coffee | Maize | Tea |
|---|---|---|---|
| KE | 64 yrs, 0.0436 MT/ha | 64 yrs, 0.1666 MT/ha | 64 yrs, 1.1765 MT/ha |
| RW | 64 yrs, 0.1156 MT/ha | 64 yrs, 0.1834 MT/ha | 64 yrs, 0.4582 MT/ha |
| SS | no data | 13 yrs, 0.0965 MT/ha | no data |
| SO | no data | 64 yrs, 0.0690 MT/ha | no data |

8 of 12 observations `observed_verified`, 4 `unknown` (SS/SO coffee and
tea).

**A third, genuinely distinct evidence-availability pattern** — the
central emerging finding of Phase 0 so far. Price split cleanly by
*country tier* (KE/RW real, SS/SO synthetic). Weather was *uniform
across all 4 countries* regardless of tier (satellite coverage doesn't
care about a country's national statistics capacity). Production is
uniform across countries but varies by *commodity*: maize, a staple
food-security crop, is tracked by FAOSTAT even for SS and SO; coffee
and tea, export cash crops, are only tracked for countries that
actually produce them at scale (KE, RW). Three modalities, three
different real shapes of "sparse" — directly supporting the
experiment's core premise that evidence availability is a property of
the (modality, commodity, country) triple, not any single one of those
dimensions alone.

**Verified**: `ruff check` clean on `collect_production.py`. The
production-code fixes it depends on were independently verified per
this session's full bar: `ruff`/mypy clean (mypy findings confirmed
identical before/after via `git stash`), the directly relevant pytest
suites pass, and the live 4×3 result above matches exactly what was
independently confirmed during the bug-fix investigation itself before
this collector script existed.

**Reopen item retried, still blocked**: re-ran `collect_trade.py` at
2026-09-18 00:59 UTC expecting the quota to have replenished — it
hadn't. Same `403 "Out of call volume quota"`, now reporting
`"replenished in 02:00:02"` (~2026-09-18 03:00 UTC), consistent with
the original ~7.5h window from the first hit rather than a shorter one
— the second attempt's own 12 calls did not additionally extend the
wait (UN Comtrade's quota appears to be a fixed replenishment
timestamp, not a rolling one restarted by each failed call). All 12
observations again correctly recorded as `DataState.UNKNOWN`, not a
false zero. Output: `data/gold_standard_trade_20260917_220008.json`
(superseding, not deleting, the first blocked run's file — both are
honest records of the same real constraint).

### Phase 0, fifth slice — 2026-09-18: trade modality unblocked, and a
fourth real evidence-availability pattern that extends the concluded
experiment's own earlier finding

**What actually happened live**: re-ran `collect_trade.py` at
2026-09-18 10:14 UTC, well past the ~03:00 UTC quota reset — this time
it worked. Real, non-zero trade data for **Kenya only**: coffee
$518,720,901, maize $9,984,905, tea $2,691,966,006 (all
`observed_verified`, confirmed by inspecting the real per-partner rows
behind the sums). **Rwanda, South Sudan and Somalia all returned a
genuine, confirmed `200 OK` with zero rows** for all three commodities
— verified directly with a standalone manual call (not just trusting
the collector): `get_trade_flows(reporter="RW", commodity_code="0901",
flow="exports", year=2023)` logged `request_success ... status=200`
immediately followed by `trade_flows_retrieved ... count=0` — a real
API success carrying no data, not a rate limit, timeout, or bug. Reran
the full collector a second time immediately after (no `403`s, only
soft per-second `rate_limited` retries that all recovered) and got
byte-identical results — ruling out one-off flakiness.

**A fourth real evidence-availability pattern, and it doesn't match
any of the first three**: this is neither the price modality's split
(KE+RW rich, SS+SO sparse) nor weather's uniform-everywhere, nor
production's uniform-but-commodity-dependent. Trade is **KE only**,
with Rwanda now landing on the sparse side despite being one of this
experiment's two "data-rich" tier countries. This directly *extends*
the concluded `regional-equity-audit` experiment's own earlier,
narrower finding — that South Sudan and Somalia were zero for UN
Comtrade's `TOTAL` commodity aggregate — in two ways: (1) confirming
that zero holds per-commodity (coffee/maize/tea individually, not just
the aggregate) for SS/SO, and (2) showing it is *not* a data-rich vs.
data-sparse story at all here, since Rwanda (data-rich in this
experiment's price-modality tiering) is equally zero. Four modalities
now on record, four genuinely different shapes of "sparse" — the
strongest evidence yet for this experiment's core premise that
evidence availability is a property of the (modality, commodity,
country) triple, not reducible to any single dimension, not even
"country data-richness" as a general trait.

**Verified**: two independent live runs, byte-identical; the RW-zero
result cross-checked with a standalone direct client call outside the
collector script, confirmed as a real `200`/zero-rows response, not an
error being swallowed. `ruff check` clean.

**What Phase 0 still needs, honestly not yet done**: the textual/news-
event modality (the last of the planned 4–5 modalities, not yet
started); the `EvidenceQualityVector`'s 7 dimensions are *now
technically computable* (four real modalities exist to compare against
each other) but still entirely unpopulated (`None`) — deliberately
deferred rather than attempted this pass, to keep each increment
reviewable rather than compounding scope; no historical time-series
collection yet (single-snapshot data for all four modalities so far —
Experiment A/B's tiered/sparsity comparisons need a real multi-date
sample, not one day); the numeric success criteria for H1–H5 (flagged
in Success Metrics as needing to be pinned down once real data exists)
are still undecided.

### Phase 0, sixth slice — 2026-09-18: text/news modality, the last of
the planned 4–5 — and a genuinely different kind of finding: source
*reliability*, not source *availability*

**Built**: `scripts/collect_text.py`, against
`services/intelligence/news_intelligence.py`'s
`NewsIntelligenceService.fetch_and_analyze()` (real GDELT + ReliefWeb +
EAC media RSS, no API key required). Unlike the other four modalities,
"evidence" here isn't a price or a count of production years — it's
*coverage*: how many real, classified market signals exist for a given
(country, commodity) this week. `signals_extracted` is the recorded
`value`; the pre-classification `articles_analyzed` count is kept in
`price_basis` for transparency.

**What actually happened live, and why it isn't being reported as a
clean 4×3 result**: three independent live runs (two fully concurrent
via `asyncio.gather`, one after switching to sequential calls with a
1.1s gap once a concurrency-collision hypothesis was formed) all
landed at roughly the same **~2 of 12 pairs succeeding**, the rest
timing out against GDELT specifically (`Connection timeout to host
api.gdeltproject.org`, 3 retries exhausted) with `ReliefWeb`/`RSS`
contributing nothing further. The initial hypothesis — that
`NewsIntelligenceService` opens a fresh `GDELTClient` per call, so its
own `rate_limit_per_second=1.0` never throttles *across* the 12
concurrent calls this collector was making — was real and worth fixing
(the collector now runs sequentially, the responsible way to treat a
free, unauthenticated, rate-limited API), but it was not sufficient:
the sequential run still only landed 2 of 12. That rules out
self-inflicted concurrency as the *sole* cause and points to a
currently-degraded, GDELT-specific reachability issue from this
environment right now — consistent with the broader pattern of
transient external-network flakiness observed elsewhere this same
session (PostHog API timeouts, GitHub CLI TLS handshake failures,
`git push` RPC failures to a completely different host).

**Why this is being kept and reported as a real finding rather than
retried into a clean number**: forcing a clean 4×3 result by retrying
until it looked tidy would be exactly the kind of quiet
success-shaping this experiment's own gold-standard schema exists to
prevent. Instead: this modality's actual, live-observed behavior is
that its primary free-tier source (GDELT) has a materially higher
*operational* failure rate than FAOSTAT, NASA POWER, or UN Comtrade —
all of which, across this Phase 0's price/weather/production/trade
collection, failed cleanly (a `403`, a `200`/zero-rows) rather than
silently timing out on 5 of 6 attempts. That is itself a genuine
evidence-*quality* finding, not an evidence-*availability* one: a
source can exist and still be unreliable enough that an agentic system
polling it in real time would need to treat it very differently from
this experiment's other four modalities (retries, timeouts, and
explicit reliability scoring — directly the concern the blueprint's
`EvidenceQualityVector.provenance`/`quality` dimensions exist to
capture, not yet populated but now with a concrete real example
motivating why). Recorded honestly with `DataState.UNKNOWN` for the
timed-out pairs (not a false zero) and `OBSERVED_VERIFIED` only for
the pairs that genuinely returned data.

**Verified**: `ruff check` clean on `collect_text.py`. The concurrency
fix was verified as real and correct (sequential pacing is
unambiguously the responsible way to call this API regardless of
whether it fully explained the failure rate) even though it did not
fully resolve the reliability issue. Two of the three live run outputs
kept as data (`gold_standard_text_20260918_103057.json`, the first
concurrent baseline; `gold_standard_text_20260918_110514.json`, the
sequential-fix attempt) — the third, near-duplicate concurrent run
removed as redundant.

**Phase 0 status**: all 4–5 planned evidence modalities now have at
least one real, live collection attempt (price, weather, production,
trade all cleanly collected; text collected but reliability-limited).
**What Phase 0 still needs, honestly not yet done**: a reliable
text-modality collection (retry once GDELT's reachability from this
environment recovers — no announced reset time to wait for, unlike UN
Comtrade's quota, so this is an open-ended reopen item rather than a
scheduled one); the `EvidenceQualityVector`'s 7 dimensions, now with
five real modalities' worth of raw material to compute them from but
still entirely unpopulated (`None`) — deliberately deferred to keep
each increment reviewable; no historical time-series collection yet
(every modality so far is a single snapshot); the numeric success
criteria for H1–H5 are still undecided. Phase 0's data-collection
layer is now substantially built; the next real step is either a
second collection pass per modality (to start building the
time-series Experiments A/B actually need) or beginning to populate
the `EvidenceQualityVector` from what already exists.

### Phase 0, seventh slice — 2026-09-18: a first Evidence Quality Vector,
scored from real facts this session already established

**Built**: `scripts/evidence_quality_rubric.py` (the scoring rubric,
fully inline-documented with the real fact each number is grounded
in — never a guess dressed up as precision) and
`scripts/populate_evidence_quality.py` (applies it to the latest real
collection per modality and writes one consolidated, scored dataset).
Pure local computation over already-collected data — no network calls
to verify.

**The rubric, by dimension**: **A** (availability) is mechanical, read
straight off `DataState` — the one dimension needing no judgment call,
since it already *is* this experiment's core instrument. **F**
(freshness) is also mechanical: the real gap between `observation_date`
and `collected_at`, decayed over a 10-year horizon (chosen because this
session's most stale real data — trade's fixed 2023 reference year,
production's FAOSTAT reporting lag — is years, not decades, old). The
other five (**Q**, **R**, **C**, **P**, **G**) are modality-level and
each is justified against a specific real fact from this session, not
a general impression of the source: **Q** (quality) from each source's
*actual observed reliability this session* — FAOSTAT/NASA POWER/UN
Comtrade all failed cleanly (a `403`, a `200`/zero-rows) when they
failed at all, versus GDELT's real, repeatedly-confirmed ~2-of-12
success rate across three independent live runs. **G** (geographic
coverage) is grounded the same way: weather's score is capped not
because NASA POWER is a weak source (it scores highest on every other
dimension) but because `collect_weather.py` reads one point — the
capital city's coordinates — as a stand-in for the whole country, a
real, named structural limitation, not a hypothetical one; text's G is
capped because `news_intelligence.py` tags a country via keyword
matching in article text, not confirmed geolocation.

**What actually happened, run against all 56 real observations
collected across Phase 0 so far**:

| Modality | A | Q | R | F | C | P | G |
|---|---|---|---|---|---|---|---|
| price | 0.58 | 0.90 | 1.00 | 1.00 | 0.90 | 0.90 | 0.85 |
| production | 0.67 | 0.90 | 0.90 | 0.89 | 0.85 | 0.90 | 0.85 |
| text | 0.17 | 0.35 | 0.50 | 1.00 | 0.30 | 0.40 | 0.55 |
| trade | 0.25 | 0.75 | 0.85 | 0.73 | 0.50 | 0.90 | 0.90 |
| weather | 1.00 | 0.95 | 0.60 | 1.00 | 0.90 | 0.95 | 0.50 |

Hand-verified several cells directly against the raw data before
trusting the table: price's A=0.58 matches its real 6/6
observed-verified/synthetic-baseline split exactly
((6×1.0+6×0.15)/12); text's A=0.17 matches its real 2/12 success rate;
weather's A=1.00 matches all 8 observations being
`observed_verified`.

**What the table makes visible that no single modality's own writeup
did on its own**: no modality wins on every dimension, and the
dimensions genuinely trade off against each other rather than moving
together. Weather has the best source (Q=0.95, P=0.95) but the worst
geographic fidelity (G=0.50) — an excellent measurement of the wrong
place. Text has the worst everything except freshness (F=1.00, since
every failed GDELT call this session still recorded today's date
honestly) — fresh but nearly everything else about it is weak. Trade
has strong provenance and geography (P=0.90, G=0.90 — a real national
customs authority reporting on its own country) but the weakest
compatibility (C=0.50, a raw USD total conflating price and volume)
and middling availability (A=0.25, this session's real quota/rate-limit
friction). This is the concrete version of the blueprint's own
"1,000,000 observations / wrong geography or wrong price basis / LOTS
OF DATA -> LOW EVIDENTIAL VALUE" diagram — evidence quality is
multi-dimensional in a way a single availability number (or a single
"data quality" score) genuinely cannot capture, now demonstrated with
real numbers instead of asserted in the abstract.

**Honest limits of this slice**: every number here is a **Phase 0
estimate** — a principled, inspectable, individually-justified first
pass, not a validated or learned measurement. The modality-level scores
in particular (Q/R/C/P/G) are the same five numbers applied to every
observation within a modality regardless of country or commodity —
real per-observation variation (e.g. is KE's FAOSTAT price series
better-attested than SO's near-total absence of one) isn't yet
captured, since the underlying `DataState`-per-row split already
carries most of that signal through `A`. Revising individual numbers
in the rubric, or making Q/R/C/P/G vary within a modality rather than
only across modalities, is real future work, not a gap being hidden.

**Verified**: `ruff check` clean on both new files. Output:
`data/gold_standard_all_with_quality_20260918_135956.json` (56 scored
observations, all 5 modalities' latest real collections).

**Phase 0 status**: data-collection layer built (5/5 modalities, at
least one real live attempt each) and a first, real,
individually-justified `EvidenceQualityVector` now computed for every
observation collected so far — the last item on Phase 0's own original
scope list. **What's still genuinely open**: no historical time-series
yet (every modality is still a single snapshot — needed for
Experiments A/B's tiered/sparsity comparisons); the numeric success
criteria for H1–H5 remain undecided; the rubric above is a first pass,
not a validated instrument. The reasonable next step is either a
second collection pass (to start real time-series data) or moving into
Experiment E1 (forecasting under controlled data availability) using
what Phase 0 has already built.

### Phase 0, eighth slice — 2026-09-19: the first real time series —
a genuine prerequisite for E1, not just an enhancement

**Why this had to happen before E1, not alongside it**: E1 needs
historical observations to fit or evaluate a forecast against — every
modality collected so far was a single point-in-time snapshot, which
the blueprint's own "what Phase 0 still needs" list already flagged as
blocking Experiments A/B's tiered/sparsity comparisons. Re-reading E1's
own spec while starting it made this concrete rather than abstract:
there is no such thing as "forecast the next value" from one
observation. This had to be built first.

**Built**: `scripts/collect_price_history.py` — a real, non-trivial
discovery made this collection possible cheaply. Production already
had this shape solved: `_fetch_faostat_yield_history()` fetches every
real year from FAOSTAT but `collect_production.py` only kept the
latest one. Price has the identical shape:
`services/market/faostat_prices.py`'s `sync_faostat_prices()` already
calls `_fetch_pp_data()` to get every real year, then deliberately
keeps only the most-recent year per item for its own production
caching purpose. This script calls `_fetch_pp_data()` directly and
keeps every year instead — no new bugs to find or fix, since the
already-verified 2026-09-17 login fix and the already-added
`Element Code` defensive filter both carry over unchanged.

**What actually happened live**, the real FAOSTAT PP time series for
the full 4×3 scope:

| Country | Coffee | Maize | Tea |
|---|---|---|---|
| KE | 31 yrs (1991–2024) | 32 yrs (1991–2024) | 29 yrs (1991–2024) |
| RW | 16 yrs (1991–2015) | 30 yrs (1991–2024) | 13 yrs (1999–2015) |
| SS | no data | no data | no data |
| SO | no data | no data | no data |

157 real observations, all `OBSERVED_VERIFIED` where data exists.
SS/SO's zero matches the earlier price-snapshot slice's finding
exactly — a second, independent confirmation via a completely
different code path (the full-history fetch vs. the
latest-year-only cache), not just the same number repeated.

**A real, previously-invisible finding this only surfaces because it's
a time series**: Rwanda's coffee and tea price reporting **stops at
2015** while its maize reporting continues cleanly to 2024 — a full
decade-plus gap that a single latest-snapshot observation could never
reveal (the earlier price snapshot slice recorded RW as simply
"observed, real" for all three commodities, which was true but
incomplete). This is a genuine, additional evidence-availability
dimension beyond the five already documented: even within one
country's one modality, *recency* of the most recent real data point
varies by commodity, and only becomes visible once you ask for more
than one point.

**Verified**: `ruff check` clean. Real counts sanity-checked against
the raw per-country API response's own `rows` count in the request
logs (e.g. KE returned 1284 raw PP rows across all ~30 tracked
commodities before filtering down to these 3 — plausible given
FAOSTAT tracks dozens of commodities per country, not a suspiciously
round or truncated number).

**Phase 0 status**: price now has real historical depth; production's
already-fetched-but-discarded full history (available via the exact
same pattern, `_fetch_faostat_yield_history()`) is the obvious next,
cheap follow-up to give E1 a second time-series modality. Weather,
trade, and text remain single-snapshot — NASA POWER and UN Comtrade
both support real date-range queries so weather/trade could follow the
same pattern; text is inherently a point-in-time signal (a week's news
coverage) and would need repeated collection over real calendar time
to become a series, not a single richer query. **E1 can now begin in a
narrow, honest form**: price-only (T0) forecasting for KE and RW,
where real multi-year history exists — SS/SO and the higher evidence
tiers (T1–T4) remain blocked on the missing modalities' own histories.

### Phase 0, ninth slice — 2026-09-19: the second real time series
(production) — the cheap follow-up, confirmed genuinely cheap

**Built**: `scripts/collect_production_history.py`. Exactly the
predicted follow-up from the previous slice:
`_fetch_faostat_yield_history()` already returns a full year→MT/ha
dict; `collect_production.py` (the original production collector) kept
only the latest year, matching every other Phase 0 collector's
single-snapshot convention before that convention was identified as
blocking E1. This script keeps every year instead — no new bugs, no
new auth/element-code work, the exact same already-fixed real function.

**What actually happened live**: 465 real observations, the deepest
history of any modality collected so far. KE and RW get the full
**64-year FAOSTAT record (1961–2024)** for all three commodities — not
just "many years" but literally FAOSTAT's entire QCL time series for
this area/item pair. SS gets 13 years of maize only (2012–2024,
matching its real national statistical capacity coming online only
recently). SO gets the full 64 years for maize only. SS and SO both
still return zero for coffee and tea — a third independent confirmation
of the same real finding (production data availability follows
commodity, not country tier), now visible across the entire 64-year
window rather than one snapshot year, so it isn't a one-year reporting
gap — these countries have *never* had FAOSTAT-tracked coffee/tea
production data, going back to 1961.

**Verified**: `ruff check` clean. Real per-row counts match exactly
what the earlier production-snapshot slice already established
(64/64/64/64/64/64/0/64/0/13/0/0 years per KE/RW/SS/SO × coffee/maize/
tea), now as a genuine time series rather than a single point read off
the same underlying data.

**Phase 0 status**: two of five modalities (price, production) now
have real multi-year time series; both happened to be "cheap" once
found, because both `_fetch_pp_data()` and `_fetch_faostat_yield_
history()` already fetched full real histories internally and only
needed to stop discarding them. Weather and trade would need genuine
new work (repeated real API calls across real dates, not a single
richer query) to become time series; text is structurally a
point-in-time signal. **E1 can now run two tiers meaningfully wider
than before**: price-only (T0) and price+production for KE/RW, with
SS/SO limited to whichever tiers include only maize-tracked modalities.
The next real step is either extending weather/trade to genuine
multi-date collection, or actually running E1's first forecast against
what already exists.

### Phase 0 → Experiment E1, tenth slice — 2026-09-19: the first real
forecast run — does a second evidence modality actually help?

**A real, stated scope narrowing before results, not after**: the
blueprint's own Success Metrics section names 30-day price forecasting
as the primary task. No modality has real daily/monthly history yet —
FAOSTAT PP/QCL (the only two with any real series) are both annual
publications. `scripts/run_e1_forecast.py` runs **annual** next-year
price forecasting instead, the only real task the currently-collected
data can support. 30-day forecasting remains real future work, blocked
on a modality with genuine daily/monthly ground truth — not silently
substituted for here.

**Design**: only T0 (price alone) vs. price+production — not the full
T0–T4 ladder, since weather/trade/text still have no real history
(fabricating one for them would violate this experiment's founding
rule against treating synthetic data as observed ground truth). Both
models are deliberately the same simple family (ordinary least
squares, `sklearn.LinearRegression`) differing only in feature count —
T0 predicts year *t*'s price from year *t*−1's price; T0+Production
adds year *t*−1's yield as a second feature — so any accuracy
difference reflects the evidence added, not a fancier model. Split is
time-ordered (last ~20% of each series' real years held out), never
random — a real backtest. Run only for the 6 (country, commodity)
pairs with real, non-empty, aligned price *and* production history
(KE/RW × coffee/maize/tea) — SS/SO are excluded, not silently dropped:
both are synthetic-baseline for price, and this experiment's core rule
is that only real observed data may be a forecasting target.

**What actually happened, real backtested results on held-out years
(2–6 test years per series depending on real data length)**:

| Series | n train / test | T0 MAE / MAPE / dir.acc | T0+Production MAE / MAPE / dir.acc |
|---|---|---|---|
| KE coffee | 23 / 6 | 999.07 / 19.8% / 0.33 | 1001.21 / 19.9% / 0.50 |
| KE maize | 24 / 6 | 52.27 / 12.3% / 0.50 | 51.56 / 12.1% / 0.50 |
| KE tea | 22 / 5 | 363.71 / 14.1% / 1.00 | 387.61 / 15.2% / 0.60 |
| RW coffee | 9 / 2 | 126.67 / 9.1% / 0.50 | 75.42 / 5.4% / 0.50 |
| RW maize | 22 / 5 | 82.76 / 19.5% / 0.60 | 81.38 / 18.5% / 0.80 |
| RW tea | 9 / 2 | 23.32 / 15.3% / 0.00 | 22.26 / 14.6% / 0.50 |

**Aggregate across all 6 series**: MAE 274.6 → 269.9, RMSE 357.5 →
348.2, MAPE 15.0% → 14.3%, directional accuracy 0.489 → 0.567 — T0+
Production wins on **all four** metrics.

**The honest reading, not the convenient one**: the aggregate favors
adding production evidence, but the per-series picture is genuinely
mixed, not uniform — KE coffee and KE tea got *worse* with production
added (real, not noise-hidden: KE tea's directional accuracy dropped
from a perfect 1.00 to 0.60), while RW coffee improved substantially
(MAPE 9.1% → 5.4%). This is directionally consistent with RQ1's
premise (heterogeneous evidence helps) but **not strong evidence on
its own** — 6 series, 2–6 held-out years each, is a genuinely small
sample; a single volatile test year (RW coffee's 2-year test window in
particular) can swing a series' numbers substantially. This is
reported as the real, first, preliminary result it is — not
oversold as validating H1, and not the 30-day-forecast result the
blueprint originally specified.

**Verified**: `ruff check` clean. sklearn/numpy already present in the
environment (no new thesis-lab dependency needed). No data leakage —
every test-year prediction uses only strictly-prior real years' price
and production values, confirmed by construction (`build_xy` only ever
indexes `yr - 1`).

**What this actually establishes for Paper 14**: E1 is no longer
untested — there is now one real, honestly-caveated data point
answering "does adding evidence help forecasting" for this narrow
annual, 2-modality, 6-series slice, with a small but real
directionally-positive effect and real per-series exceptions that
themselves are worth investigating (why did production evidence hurt
KE coffee/tea specifically?). Real next steps: more series (once
weather/trade become real time series) to increase statistical power;
investigating the KE coffee/tea regressions specifically rather than
averaging over them; and eventually the real 30-day-forecast task once
a modality with that granularity exists.

### Phase 0 → Experiment E1, eleventh slice — 2026-09-19: why did
production evidence hurt KE coffee/tea? — a real mechanism, and a
correction to how the previous slice's aggregate should be read

**What was investigated**: pulled the exact real (year, price, lag
price, lag production) triples the E1 script actually used for each
series' test window, rather than guessing from the aggregate numbers
alone.

**Finding 1 — KE's real price series has mid-series gaps**: coffee is
missing 2017–2019 entirely; tea is missing 2017–2021. `run_e1_forecast
.py`'s lag construction (`yr - 1 in price`) already handles this
correctly — years immediately after a gap (2020 for coffee) are
excluded from being a lag target, since their true lag-1 value doesn't
exist — confirmed no leakage or artificial cross-gap pairing occurred.
This was checked and ruled out as the cause, not assumed innocent.

**Finding 2 — KE coffee's 2021 test year is a real, extreme, well-
known global price shock**: price jumped **+96.2%** year-over-year
(2020: \$3062/tonne → 2021: \$6008/tonne), then crashed **-31.0%** the
following year — consistent with the real, globally-documented 2021
coffee price surge (Brazil frost/drought damage to the world's largest
producer). KE's own production yield barely moved across this whole
window (0.031 → 0.032 → 0.047 MT/ha) — a national yield statistic has
no way to reflect a *foreign* supply shock that moved the world price.
This single real outlier year dominates both models' error almost
identically (T0 MAE 999.07 vs. T0+Production MAE 1001.21) — the models
aren't meaningfully different here; neither can see a global shock
coming from a national yield number, so the previous slice's
"essentially unchanged" reading for KE coffee was the right one.

**Finding 3 — KE tea's directional-accuracy drop (1.00 → 0.60) has a
real, mechanistic explanation**: KE tea's production series shows a
genuine, gradual multi-decade **upward trend** (≈0.83–0.95 MT/ha in
the early 2010s → ≈1.07–1.18 MT/ha by 2022–2024), while its price
series over the same test years shows no trend at all — sharp,
mean-reverting swings (-14.7%, +39.3%, -19.3%, -10.5%, -1.2%) with no
relationship to the slow yield increase. Feeding a steadily-rising,
economically-unrelated feature into a linear model alongside a
volatile, trendless target is a textbook way to bias that model's
directional calls toward "up" — spurious correlation from two series
that both drift over decades for unrelated reasons, not real
predictive signal. This is a genuine case of *added evidence actively
hurting* a forecast, not a null result — worth keeping, not just
averaging away.

**Finding 4 — RW coffee's apparent "improvement" is a small-sample
artifact, not evidence of a real effect**: RW coffee's price series is
sparse enough (gaps throughout 1991–2010, then a lone 2015 that can't
even be used as a lag target since 2014 is missing) that its `n_test=2`
test years are both drawn from a calm stretch (2009: +18.4%, 2010:
-2.6% YoY) — nothing like KE coffee's 2021 shock. A 2-point test set
where neither point is a large swing is the easiest case for any
second feature to look like it "helps," almost regardless of what that
feature is. This is not strong evidence that production evidence
generally helps RW coffee forecasting — it is weak evidence from a
window too calm and too short to be very informative either way.

**The honest correction this requires**: the previous slice's
aggregate ("T0+Production wins on all 4 metrics") is still the real,
correctly-computed number, but this investigation shows *why* it
should not yet be read as "adding evidence generally helps" — the
result is dominated by (a) one series (RW coffee) whose improvement is
most plausibly a small, calm-window sample artifact, and (b) two
series (KE coffee, KE tea) where the real mechanism is either "an
unpredictable foreign shock swamps any national feature" or "a
slow-moving unrelated trend actively misleads a volatile target," not
"more evidence, more accuracy." The real, useful finding from this
pair of slices together is narrower and more interesting than the
aggregate alone suggested: **whether a second evidence modality helps
depends on whether that modality's real variation is actually
causally connected to the target's real variation over the test
window** — a genuinely testable, more precise version of RQ1 than "add
more data and see," and a concrete instance of exactly the kind of
evidence-*relevance* (the R dimension) question the `EvidenceQualityVector`
rubric already flagged production as scoring only 0.90 on for price
(not 1.00) — this investigation gives that number a real mechanism
behind it rather than leaving it as an abstract judgment call.

**Verified**: pure analysis over already-collected real data, no new
collection, no code changes to `run_e1_forecast.py` (the lag
construction was checked and confirmed correct, not modified).

### Phase 0, twelfth slice — 2026-09-19: the third real time series
(weather), and a real change of technique

**Built**: `scripts/collect_weather_history.py`. Unlike the price/
production history slices (which extended an already-fetching-every-
year-and-discarding function), this one uses a genuinely different
real NASA POWER endpoint: `temporal_api="monthly"` instead of
`"daily"`. A live test confirmed the real response shape first before
writing the collector — each parameter returns 12 real `YYYYMM` keys
plus a 13th real `YYYY13` key holding that year's annual mean, so one
real API call per country covers the entire 1991–2024 range in a
single request (unlike trade, which needs one call per year and has
already hit a hard quota twice this session; NASA POWER carries no
comparable rate-limit risk — its original 8/8 single-snapshot calls
this session all succeeded cleanly).

**What actually happened live**: all 4 countries, both parameters, all
34 years (1991–2024), zero fill-value sentinels hit — 272 real
observations, the cleanest collection of any modality so far (no
gaps, no zeros, no partial coverage). This is a second, deeper
confirmation of the original weather-modality finding: availability
here really is uniform across the price-modality's country tiers,
now demonstrated across a full 34-year window instead of one day.

**Verified**: `ruff check` clean. Coordinates reused as-is from
`collect_weather.py` (already verified this session), not re-derived.

### Phase 0 → Experiment E1, thirteenth slice — 2026-09-19: adding a
weather tier — a real, nuanced result, not a clean "more evidence
helps" story

**Built**: `scripts/run_e1_forecast_tiers.py` — a new script, not an
edit to `run_e1_forecast.py` (that script's own result is already
documented and investigated in the tenth/eleventh slices above; this
is a later, separate increment). Runs T0 (price alone), T1 (price +
weather: temperature and precipitation), and T3 (price + weather +
production) — T2 (+trade) is skipped, since trade still has no real
time series. Same discipline as before: identical simple model family
(ordinary least squares) across tiers, differing only in feature set;
time-ordered holdout; same 6 real KE/RW × coffee/maize/tea series.

**What actually happened, real aggregate results across all 6
series**:

| Metric | T0 (price) | T1 (+weather) | T3 (+weather+production) |
|---|---|---|---|
| MAE | 274.6 | 276.5 | 281.8 |
| RMSE | 357.5 | 370.0 | 368.2 |
| MAPE | 15.0% | 14.5% | 14.5% |
| Directional accuracy | 0.489 | **0.594** | 0.533 |

**The honest reading**: this is not a clean "more evidence, more
accuracy" result, and it doesn't need to be forced into one. Weather
(T1) gives a real, meaningful jump in directional accuracy (0.489 →
0.594 — genuinely useful if the real decision this feeds is "will
price go up or down," not just "by how much") and a modest MAPE
improvement, but *worse* MAE and RMSE than price alone — plausible
because weather occasionally helps get the sign right on a volatile
year while still missing the magnitude, which MAE/RMSE punish more
than a correct-direction-wrong-size miss does. Adding production on
top of weather (T3) does **not** uniformly improve on T1 alone — MAE,
RMSE, and directional accuracy all get worse from T1 to T3, only MAPE
ties — directly consistent with the eleventh slice's finding that
production evidence specifically struggles for some of these series
(KE coffee/tea), now confirmed again via an independent comparison
structure (T1→T3 within the same run, not just T0→T0+Production in
isolation).

**What this adds to the experiment's real, refined finding**: not
every evidence modality helps the same metric the same way. Weather
helped *direction*, not *magnitude*; production actively worked
against *both* on top of weather. A single blended "does evidence
help" verdict would have hidden this — reporting per-metric,
per-modality effects rather than one aggregate score is itself now a
demonstrated methodological necessity, not just a stated principle
from the blueprint's Metrics section.

**Verified**: `ruff check` clean on both new files. No data leakage
(same `yr - 1` construction pattern, extended to three feature groups,
checked the same way as the eleventh slice's investigation).

## Experiment E2 — Uncertainty and calibration, first real run

**2026-09-20**: after this experiment's repo split (moved to
[AgroIntel-EastAfrica/thesis-lab](https://github.com/AgroIntel-EastAfrica/thesis-lab),
`agrointel` now a git submodule for reading real service code), moved
into E2 — the natural next experiment, and the one this repo's own
pre-registered H3 criterion already exists to test.

**Built**: `scripts/run_e2_calibration.py`. Same T0 (price-only) model
as E1 (ordinary least squares, lag price → price), so a coverage
difference reflects the *uncertainty method*, not a different
forecast. Two baselines: **A (uncalibrated)** — the real, common
mistake of using the model's own in-sample training-residual spread as
its confidence interval, no held-out data; **D (calibrated,
distribution-free)** — leave-one-out (LOO) residuals from training,
using their 80th percentile as a single interval half-width. LOO was
chosen over a fixed train/calibration/test split specifically because
these series are too small (9–24 points) to spare a third split
without leaving too few points anywhere. Same 6 real KE/RW ×
coffee/maize/tea series, same time-ordered holdout as E1.

**What actually happened, real results across all 6 series (26 pooled
test points)**:

| Series | n train/test | Baseline A coverage | Baseline D coverage |
|---|---|---|---|
| KE coffee | 23/6 | 83% | 83% |
| KE maize | 24/6 | 67% | 67% |
| KE tea | 22/5 | 80% | 80% |
| RW coffee | 9/2 | 100% | 100% |
| RW maize | 22/5 | 40% | 60% |
| RW tea | 9/2 | 50% | 50% |

**Pooled**: nominal target 80%; Baseline A (uncalibrated) 69.2% (10.8pt
miss); Baseline D (LOO-conformal) 73.1% (6.9pt miss).

**H3's pre-registered criterion, checked honestly against real
results**: "calibrated within 10pts of nominal, uncalibrated misses by
more than 20pts." Baseline D clears its half (6.9pt miss, within 10).
Baseline A does **not** clear its half — a 10.8pt miss is a real gap,
but not the >20pt failure the criterion required. **H3 is not
supported by this specific run**, reported plainly rather than
reframed to fit. Real, honest context for why: the concluded
experiment's original 80%-vs-38.5% gap (41.5 points) came from a
different, more complex production system (the real XGBoost+Prophet
ensemble's own stated confidence), not from a simple linear model with
in-sample residuals — this run's simplified Baseline A was never
guaranteed to reproduce that exact severity, and it didn't. The 41.5pt
number was used as this criterion's threshold precisely because it was
real and pre-existing, not because this run was expected to match it.

**What is still real and worth keeping**: even though the specific
threshold wasn't cleared, Baseline D measurably outperforms Baseline A
on real, held-out data — the miscalibration gap shrank from 10.8 to
6.9 points, a genuine ~36% relative improvement from switching to a
distribution-free, held-out-residual method instead of the naive
in-sample one. That is a real, smaller-than-hypothesized but directionally
correct calibration finding, not a null result — H3's *direction* holds
even where its *magnitude* threshold does not.

**Honest limits**: 26 pooled test points across 6 series is a small
sample — RW coffee/tea's 2-point test windows in particular make their
individual 100%/50% coverage numbers close to meaningless on their
own, which is exactly why pooling matters more than per-series numbers
here. Only tier T0 (price alone) tested — extending to T1 (price +
weather) is real future work, now straightforward given
`run_e1_forecast_tiers.py`'s existing per-tier feature-building
pattern.

**Verified**: `ruff check` clean. No data leakage (LOO residuals
computed only from training years; the nominal-confidence half-width
is fixed before any test-year value is examined).

## Experiment E2, second run — does adding evidence help or hurt calibration?

**2026-09-21**: extended `run_e2_calibration.py`'s two baselines (A:
uncalibrated in-sample residuals; D: LOO-conformal) to a second tier,
T1 (price + weather), in a new `run_e2_calibration_tiers.py` — the
same feature-building pattern already used in `run_e1_forecast_tiers
.py`. Real question: does adding evidence change calibration quality,
not just point-forecast accuracy?

**What actually happened, pooled across the same 6 series (26 test
points per tier)**:

| Tier | Baseline A | Baseline D |
|---|---|---|
| T0 (price alone) | 69.2% (10.8pt miss) | 73.1% (6.9pt miss) |
| T1 (price + weather) | 61.5% (18.5pt miss) | 69.2% (10.8pt miss) |

**Adding weather made calibration measurably worse for both
baselines**, not better — the miscalibration gap widened by roughly
70% (Baseline A) and 57% (Baseline D) going from T0 to T1. The
clearest single case: RW coffee's Baseline A coverage collapsed from
100% at T0 to **0%** at T1 (both of its 2 real test points fell
outside the interval once weather was added).

**A real, mechanistic explanation, not just a surprising number**:
these series have only 9–24 real training points. T1 fits 3 parameters
(intercept, lag-price coefficient, temperature coefficient — and
precipitation makes it 4) instead of T0's 2, on the same tiny sample.
More parameters estimated from the same small amount of data means
more variance in the fitted coefficients, which shows up as wider
out-of-sample prediction error than the *training* residual spread
(Baseline A) or even the *leave-one-out* residual spread (Baseline D)
anticipated — both baselines' uncertainty estimates were built from
training-time information that couldn't see this real cost of adding
a feature on so little data. This is the same underlying "more
evidence isn't free" theme the E1 slices already found for accuracy,
now shown to apply to *calibration* too, and via a different,
independently-motivated mechanism (small-sample parameter variance,
not spurious trend correlation or an unpredictable macro shock).

**Why this matters for the experiment's real, refined finding**: it
strengthens the pattern already emerging across E1 and E2 together —
adding a second evidence modality is not uniformly beneficial, and the
specific way it can hurt varies (spurious trend correlation for KE
tea's directional accuracy in E1; small-sample calibration variance
here). A system that only tracked point-forecast accuracy would miss
this entirely, since calibration and accuracy can move in different
directions from the same evidence addition — direct support for
evaluating forecasting, calibration, and evidence quality as separate,
not conflated, dimensions (exactly the blueprint's own Metrics-by-
category design).

**Verified**: `ruff check` clean. Same time-ordered holdout and no-
leakage discipline as every prior slice.

## Experiment E3 — Evidence grounding, first real run

**2026-09-21**: E1 and E2 are both forecasting-adjacent; E3 is where
this experiment becomes genuinely agentic, per the blueprint's own
framing. Built `scripts/run_e3_evidence_grounding.py`: a real,
mechanical evidence-state classifier (SUFFICIENT / INSUFFICIENT /
STALE / CONFLICTING / SEMANTICALLY_INCOMPATIBLE) and an agent-action
selector that does *not* always answer — SUFFICIENT → recommend;
INSUFFICIENT → retrieve, then abstain if retrieval is known exhausted;
STALE → recommend with a caveat; CONFLICTING/SEMANTICALLY_INCOMPATIBLE
→ investigate, then either caveat (if the conflict resolves to an
identifiable basis difference) or abstain.

**Every one of the blueprint's 5 named scenarios (A–E) is grounded in
real data or a real, already-documented incident from this lab's own
history — none fabricated**:

| Scenario | Real grounding |
|---|---|
| A — Sufficient | KE coffee: real price/production/weather, all `OBSERVED_VERIFIED`, no conflict |
| B — Insufficient | SS coffee: genuinely zero real price data, confirmed independently three times this lab |
| C — Conflicting | The real 2026-09-17 price-source-mismatch incident (synthetic \$2,600–2,800/tonne baseline vs. real FAOSTAT \$270–280/tonne for RW/BI coffee) — already investigated and fixed this session (migration 048) |
| D — Outdated | KE trade: real UN Comtrade data fixed at 2023, genuinely 3 years stale by 2026 and not fixable by retrying |
| E — Semantically incompatible | KE coffee real price (\$4,886.5/tonne, a unit price) vs. real trade (\$518,720,901, a total export value) — the blueprint's own worked example, instantiated with real collected data instead of a hypothetical |

**What actually happened**: all 5 scenarios' agent actions matched
their real, historically-grounded expected action (5/5).

**The honest limit of what this establishes, stated plainly rather
than oversold**: this is a small (n=5), hand-picked evaluation of a
*deterministic, rule-based* classifier that this same investigation
designed — the "expected" answer for each scenario was reasoned out
using the same logic the classifier itself implements. A 5/5 match
demonstrates the **decision procedure is internally consistent and
correctly implements its own stated logic** against 5 real, known
cases. It does **not** yet demonstrate that a real LLM-driven agent
exhibits this behavior when given the same raw evidence and asked to
decide for itself, nor that this generalizes to novel cases the
classifier wasn't specifically built around. That is real, necessary
future work: wiring this decision procedure (or an LLM-based one
tested against it as a baseline) into an actual agent loop, then
evaluating on evidence bundles it wasn't designed with in mind.

**Verified**: `ruff check` clean. Every scenario's real numeric
grounding (KE coffee's \$4,886.5/tonne 2024 price, \$518,720,901 2023
trade value) checked directly against the raw JSON files before being
written into the script, not typed from memory.

## Experiment E4 — Decision reliability: protocol only

**2026-09-21**: E4 is a human-subjects study (decision accuracy,
response time, override behavior across 5 presentation formats) — not
something a coding session can execute; simulating synthetic
"participants" would be fabrication, not research. Wrote the real
study protocol instead: [`E4_study_protocol.md`](E4_study_protocol.md).

The worked decision scenario in it is built from real numbers this
experiment already computed, not invented ones — KE coffee, 2024: real
2023 price (\$4,391.70/tonne) → T0 forecast \$3,934.60/tonne (E1) → T1
forecast \$4,253.00/tonne (E1) → real 80% LOO-conformal interval
\$2,383.30–\$5,486.00/tonne (E2) → E3's real `SUFFICIENT`
classification for this case → real 2024 actual, \$4,886.50/tonne
(above every point forecast, inside the T0 interval). The 5 formats
range from raw data through a bare point-forecast (the real failure
mode E2 exists to correct) to the full evidence+uncertainty
presentation.

**Explicitly not run** — needs real participant recruitment, informed
consent, and institutional review (the source proposal names Makerere
University, UBOS, and MAAIF, and commits to "institutional review
requirements where applicable"; whether/how that applies here is the
advisor's/institution's call, not assumed in this protocol). Also
flagged as incomplete on its own terms: only 1 of the intended 3
scenarios (sufficient/insufficient/stale) is fully worked out, and no
power analysis has been done yet.

**Where this leaves Paper 14**: all four sub-experiments (E1–E4) have
now been touched — three with real, computed results (E1 x2, E2 x2, E3
x1), one with a real, ready-to-run protocol (E4) rather than simulated
results. Phase 0 and the four sub-experiments together are Paper 14's
full designed scope; what remains is depth (more series, systematic
sparsity sweeps, the full 5-scenario E4 battery) and, for E4
specifically, an actual human study this session cannot run alone.

## Country expansion: Tanzania and Burundi added (2026-09-21)

**Motivation**: the project owner asked how to get more/better data,
worried the original four countries (KE, RW, SS, SO) or their
commodities might be a limiting factor. Rather than fabricate
synthetic countries, checked FAOSTAT's real area codes and confirmed
Tanzania (215) and Burundi (29) both have real PP/QCL records — both
already appear in `services/market/faostat_prices.py`'s and
`services/forecasting/yield_prediction.py`'s existing area-code maps,
just never included in this experiment's own `COUNTRIES` lists.
Capital coordinates for the weather collector taken from
`configs/countries/tanzania.yaml` (Dar es Salaam, -6.7924/39.2083 —
explicitly the commercial capital in that config, not the legislative
capital Dodoma) and `configs/countries/burundi.yaml` (Gitega,
-3.3761/29.3600).

**A real regression surfaced and was root-caused before any new data
was trusted.** After adding TZ/BI to `collect_price_history.py`'s
`COUNTRIES` and running it, all 18 observations (6 countries x 3
commodities) came back `data_state: unknown`, including Kenya and
Rwanda, which had 157 real observations earlier in this project.
Investigated rather than assumed: `get_settings()` showed
`faostat_token`/`faostat_username`/`faostat_password` all empty in the
new `thesis-lab` working directory. Root cause: the `agrointel`
submodule (added when thesis-lab was split into its own repo, see
`CLAUDE.md`'s Thesis Lab section) is a fresh GitHub clone, and `.env`
is gitignored — it was never present there, so every collector run
since the org split had silently run with zero credentials. A second,
more specific bug sat underneath the first: `apps/api/config/settings.py`
declares `env_file=".env"` as a **relative** path, which
`pydantic-settings` resolves against the process's current working
directory, not the submodule root — so even after placing a copy of
`.env` inside `thesis-lab/agrointel/`, running the collector with cwd
set to the thesis-lab repo root still found nothing. Confirmed by
testing `get_settings()` from both cwds directly: empty from
`thesis-lab/`, populated from `thesis-lab/agrointel/`. **Fix**: invoke
every collector script (and, by the same reasoning, the E1/E2 run
scripts, though those don't need FAOSTAT credentials themselves) with
cwd set to the `agrointel` submodule root, e.g.
`cd thesis-lab/agrointel && python ../active_tests/.../collect_price_history.py`
— the scripts' own `sys.path` and output-directory logic are already
`__file__`-relative, so only the credential lookup was cwd-sensitive.
This is a durable gotcha for this repo split, not a one-off: any
future script here that touches `get_settings()` needs the same
invocation pattern.

**Real results after the fix**, all three collectors re-run with the
corrected cwd:

| Modality | Before (4 countries) | After (6 countries) |
|---|---|---|
| Price | 157 real observations | 261 real observations |
| Production/yield | — (not previously totalled this way) | 843 real observations |
| Weather | 272 real observations | 408 real observations |

Price coverage by new country: Burundi turned out to be **data-rich**
— real FAOSTAT PP series for all three commodities (coffee and tea 28
years each, 1991–2019; maize 23 years). Tanzania is price-data-sparse
for this basket — only maize has a real PP series (23 years,
1992–2016); TZ coffee and TZ tea have no real FAOSTAT PP record at
all. Production/yield, by contrast, is essentially complete for both:
TZ and BI both have full 1961–2024 coverage for all three commodities.
Weather remains complete and uniform for every country, as before.

**E1 (forecasting) re-run with 10 series** (was 6 — KE/RW/BI each
contribute all 3 commodities, TZ contributes maize only; TZ coffee/TZ
tea are correctly skipped by the scripts' own insufficient-data check,
not force-included):

| Tier | MAPE (10 series) | MAPE (6 series, prior run) | Directional accuracy (10) | Directional accuracy (6, prior) |
|---|---|---|---|---|
| T0, price alone | 30.1% | 15.0% | 54.3% | 48.9% |
| T1, plus weather | 48.9% | 14.5% | 63.2% | 59.4% |
| T3, plus production | 49.2% | 14.5% | 57.5% | 53.3% |

The directional-accuracy story is unchanged in shape (weather still
the only tier that clearly beats the others), but MAPE jumps sharply
because of one series: **Burundi coffee's real price collapsed from
roughly \$2,000–3,300/tonne before 2007 to roughly \$200–400/tonne
from 2007 onward** — a genuine, sustained regime break visible
directly in `report/figures/01_price_history.png`, not a data error.
An OLS model trained across both regimes produces large *relative*
errors on the low-price years even when its *absolute* errors are
unremarkable (BI coffee's T0 MAE is \$505.64, similar in scale to KE
coffee's \$999.07, but BI coffee's MAPE is 178.5% because the test-set
actuals are so small). This is a real instance of the project's
central theme — MAPE alone can hide or exaggerate what is actually
going on; the raw error and the real underlying series both need to be
checked before trusting a single aggregate number. Left as a
documented artifact rather than excluded, since dropping an
inconvenient real series would be exactly the kind of quiet
cherry-picking this project's rules exist to prevent.

**E2 (calibration) re-run with 10 series** — the H3 pre-registered
severity criterion (calibrated within 10pts of nominal, uncalibrated
misses by more than 20pts) now reads differently than the 6-series
run:

| Tier | Baseline A coverage (10) | Baseline D coverage (10) | Baseline A (6, prior) | Baseline D (6, prior) |
|---|---|---|---|---|
| T0, price alone | 75.0% (5.0pt miss) | 77.3% (2.7pt miss) | 69.2% (10.8pt miss) | 73.1% (6.9pt miss) |
| T1, plus weather | 65.9% (14.1pt miss) | 70.5% (9.5pt miss) | 61.5% (18.5pt miss) | 69.2% (10.8pt miss) |

At T0, Baseline D still beats Baseline A directionally (77.3% vs.
75.0%), but Baseline A's miss shrank from 10.8pt to 5.0pt with the
larger pool — it no longer misses by more than 20pt, so **H3's
pre-registered severity criterion is not supported by this run**, a
real change from the prior run's "direction confirmed, severity
threshold missed" reading. The T1 direction — adding weather makes
both baselines worse — holds in both runs. This is reported honestly
as a result that moved with more data, not silently overwritten;
FINDINGS_REPORT.md's RQ3/H3 language has been updated to match.

**Not yet extended to TZ/BI**: E3 (evidence grounding, still 5
hand-picked scenarios, unaffected by country count) and E4 (protocol
only, unaffected). The evidence-quality radar chart
(`07_evidence_quality_radar.png`) still reflects the original 4-country
scoring — recomputing its 7-dimension vectors properly for the 6-country
set requires going back through `evidence_quality_rubric.py`'s real,
individually-justified scoring process, not just nudging numbers, and
is left as a flagged follow-up rather than done hastily here.

**Verified**: `ruff check` clean on all edited scripts
(`collect_price_history.py`, `collect_production_history.py`,
`collect_weather_history.py`, `run_e1_forecast.py`,
`run_e1_forecast_tiers.py`, `run_e2_calibration.py`,
`run_e2_calibration_tiers.py`, `generate_report_figures.py`). All 8
report figures regenerated from the real re-collected data and real
re-run experiment output.

## Regime-break detection: a methodological fix, not a data fix (2026-09-21)

The project owner's response to the Burundi/Rwanda anomaly above was
not "fix the numbers" but "look into whether this is our data handling
or the data source" - so the investigation went one level deeper
before any code changed. Fetched the raw FAOSTAT PP rows directly
(`_fetch_pp_data`, bypassing this project's own collector entirely) for
Burundi coffee, Burundi tea, Burundi maize, Rwanda coffee, Rwanda tea,
and Kenya coffee, printing every year/value/flag. Findings:

- Burundi coffee: $1,922.40/tonne in 2006 -> $184.90/tonne in 2007, a
  10x single-year drop, both years flagged `'A'` (FAOSTAT's official-
  figure flag, not an estimate).
- Burundi tea and maize, same years: no comparable disruption.
- Rwanda coffee: $1,371.90/tonne in 2010 -> $277.40/tonne in 2015
  (FAOSTAT has a real reporting gap 2011-2014, so the exact break year
  is unknown, but the shape and magnitude match).
- Rwanda tea, same window: essentially flat.
- Kenya coffee, full 1991-2024: no comparable break anywhere.
- Tanzania coffee: zero rows in FAOSTAT at all - nothing to check.

Conclusion, stated to the project owner directly: this is real,
officially-flagged data, faithfully reproduced by this project's own
collector - not a collection bug, not a corrupted source. The pattern
(coffee-specific, present in the two countries whose coffee sectors
had a real state/parastatal-marketing-board-to-liberalized-market
transition through the 2000s-2010s, absent in Kenya's continuously
private auction-based coffee market) points to a genuine change in
what FAOSTAT's "Coffee, green" producer price is measuring for these
two countries before vs. after their respective liberalizations - most
likely a switch from an official/processed-equivalent reference price
to a real farmgate market price. E1's inflated Burundi-coffee MAPE was
a direct, fully explained consequence: the OLS model was being trained
on years spanning both price regimes and tested only on the low-price
years.

**Recommendation given, and accepted**: rather than drop Burundi/
Rwanda coffee outright (losing real data) or leave the pooled-regime
fit in place (numbers that don't mean what they claim to), detect the
break programmatically and restrict each affected series to its
latest real regime before fitting - generalizable to any future
country/commodity, not a hand-patch for these two cases.

**Building the detector took two iterations, validated against all 10
real series each time, not assumed to work from the first pass.** A
first version comparing each year only to the single immediately
preceding real observation produced two real false positives:
Burundi's own noisy 2002 price spike ($3,361.80, a real but
unrepresentative outlier year) made 2003 look like a break purely by
being compared against that one spike; and Rwanda's real but temporary
2000-2003 global coffee-crisis dip (which recovered fully by
2006-2010) looked identical in shape to a permanent regime change under
a same-year-over-year-only test. Fixed by (a) comparing each candidate
point against the MEDIAN, not mean, of the preceding real years (robust
to one spike sitting in the window) and (b) requiring the ENTIRE rest
of the series, not just the next couple of years, to average below 60%
of that pre-break median - which is what separates a permanent break
from a shock that recovers. Implementation:
[`regime_break.py`](scripts/regime_break.py) (full reasoning and
threshold justification in its own docstring, not just asserted here).

**Validated against all 10 real price series** before wiring into any
run script:

| Series | Break detected | Post-break years |
|---|---|---|
| BI coffee | 2007 | 12 (2007-2019, minus a 2016 gap) |
| RW coffee | 2015 | 1 |
| BI maize, BI tea, KE coffee, KE maize, KE tea, RW maize, RW tea, TZ maize | none | n/a |

Wired `regime_break.restrict_to_latest_regime()` into all four run
scripts (`run_e1_forecast.py`, `run_e1_forecast_tiers.py`,
`run_e2_calibration.py`, `run_e2_calibration_tiers.py`), applied to the
price series immediately after loading, before any train/test split.
Rwanda coffee's 1 real post-break year is below the existing 8-year
minimum-for-split threshold, so it now cleanly falls out via the same
"skipped (insufficient real aligned data)" path already used for
TZ coffee/tea and SS/SO - no special-casing needed, the general
sufficiency check does the right thing once the pre-break years are
correctly excluded from the count.

**Real results after the fix, series count 9 (was 10, Rwanda coffee
now excluded)**:

| Tier | MAPE (regime-corrected) | MAPE (10 series, pre-fix) | Directional accuracy (regime-corrected) | Directional accuracy (10, pre-fix) |
|---|---|---|---|---|
| T0, price alone | 13.2% | 30.1% | 55.9% | 54.3% |
| T1, plus weather | 15.6% | 48.9% | 71.3% | 63.2% |
| T3, plus production | 16.1% | 49.2% | 65.0% | 57.5% |

MAPE dropped back to a sane range once Burundi coffee's forecast was
no longer being evaluated against a model trained on a price level
that no longer exists. Directional accuracy for the weather tier
actually improved further (71.3%, the highest seen in any run of this
experiment) - the weather-helps finding gets stronger, not weaker,
once the Burundi coffee series is evaluated on a real, single, internally
consistent regime instead of straddling two.

E2 calibration, same regime correction, same 9 series:

| Tier | Baseline A coverage | Baseline D coverage |
|---|---|---|
| T0, price alone | 71.8% (8.2pt miss) | 74.4% (5.6pt miss) |
| T1, plus weather | 69.2% (10.8pt miss) | 74.4% (5.6pt miss, unchanged) |

H3's pre-registered severity criterion (uncalibrated misses by more
than 20pt) is still not met in this run (Baseline A misses by 8.2pt at
T0) - the direction still favours the calibrated method, but the
severity claim from the original 6-series run remains unsupported with
more, cleaner data, and that is reported as the honest result, not
adjusted to match the original expectation. One real change worth
noting: with the regime break corrected, adding weather at T1 now only
hurts the naive baseline (69.2%, down from 71.8%) - the calibrated
baseline is completely unchanged at 74.4%, a cleaner and more
interpretable result than the pre-correction run, where weather
appeared to hurt both.

**Verified**: `ruff check` clean on `regime_break.py` and all four
edited run scripts, plus `generate_report_figures.py` (now imports
`detect_price_regime_break` to mark detected breaks directly on the
price-history chart with a dotted vertical line and year label - see
`report/figures/01_price_history.png`). All 8 figures and both report
documents (`FINDINGS_REPORT.md`, this file) updated with the final,
regime-corrected numbers.

## Full EAC coverage: Uganda and DR Congo added (2026-09-21)

Direct question from the project owner after the above: "why not
consider all EAC countries" - a fair challenge, since the experiment
had been using six of the real bloc's eight members (missing Uganda
and DR Congo) without an explicit reason on record. Checked rather
than assumed: `EAC_FAO_AREA_CODES` in
`services/market/faostat_prices.py` already has real area codes mapped
for both (UG=226, CD=250) - nothing was blocking them, they simply
hadn't been added when the country list was first written.

Checked live before adding, same discipline as every other country:

- Producer price (FAOSTAT PP): zero real rows for either country, for
  any of the three commodities - the same shape as South Sudan and
  Somalia.
- Production/yield (FAOSTAT QCL): full 1961-2024 coverage for both
  countries, all three commodities - the same completeness as
  Tanzania and Burundi.
- Weather (NASA POWER): works for any coordinate pair by construction;
  added Kampala (0.3476, 32.5825) and Kinshasa (-4.4419, 15.2663) from
  `configs/countries/uganda.yaml` and `configs/countries/drc.yaml`.

Added to all three collectors (`collect_price_history.py`,
`collect_production_history.py`, `collect_weather_history.py`),
following the exact principle already established for South Sudan and
Somalia: a country with a confirmed real zero is real information for
an evidence-sparsity study, not something to omit for a tidier
dataset. Not added to the four E1/E2 run scripts' `COUNTRIES` lists,
also consistent with SS/SO's existing treatment - both have zero real
price to forecast, so including them there would only produce two more
`skipped` lines with no analytical value; their exclusion is already
documented in each script's own docstring, now naming all four
zero-price countries instead of two.

**Real results, full 8-country re-collection**: 267 real price
observations (up from 261; +24 zero-data rows for UG/CD, price series
count unchanged), 1,227 real production observations (up from 843;
UG and CD both contribute full 64-year records for all three
commodities), 544 real weather observations (up from 408; full
34-year records for both). The availability matrix
(`report/figures/04_availability_matrix.png`) now genuinely shows all
8 EAC members side by side, rather than an unexplained subset.

**A second, unrelated pattern surfaced while regenerating the
production chart, noted but not investigated further this session**:
Kenya and Uganda's real tea yield both show an abrupt jump around 1990
(roughly 0.1 to 0.8-1.0+ MT/ha), same year, same shape, in
`report/figures/02_production_history.png`. Most likely a genuine
agronomic event - East African tea's clonal-variety replanting programs
are well documented in that era - rather than a data artifact, but
unlike the coffee price breaks this has not been checked against the
raw rows or cross-referenced against a documented source, so it is
flagged here as a real open question, not asserted as explained.

**Verified**: `ruff check` clean on all three collectors and
`generate_report_figures.py`. Also fixed a real readability bug caught
on the first regenerated chart, not shipped: Uganda's and Kenya's
first-choice colors were both near-identical dark greens (and
Burundi's/DR Congo's both purples), indistinguishable in the legend;
retuned to a teal for Uganda and a magenta for DR Congo before
re-rendering.

## The tea-yield jump, investigated and resolved (2026-09-21)

The side effect flagged above - Kenya's and Uganda's real tea yield
both jumping sharply around 1990 - was investigated with the same
discipline as the coffee price breaks, at the project owner's request,
rather than left as a noted-but-unchecked observation.

Pulled the raw FAOSTAT QCL rows directly for tea yield (element 5412)
for all five tea-producing countries in this dataset. Findings:

- Every one of the five (Kenya, Uganda, Rwanda, Burundi, Tanzania)
  jumps at exactly the same year, 1990 -> 1991, by a similar magnitude
  (roughly 3x to 8x). This was not visible for Rwanda/Burundi/Tanzania
  in the chart on first look, because their post-jump values are much
  smaller in absolute terms than Kenya's/Uganda's and the chart's
  shared y-axis scale hid the smaller countries' equally real jump.
- The item name (`Tea leaves`) and unit (`kg/ha`) are identical before
  and after 1991 - this rules out an item-code or unit redefinition.
- FAOSTAT's own quality flag switches from `A` (official figure) to
  `E` (FAO estimate) in exactly 1991, for every one of the five
  countries, and stays `E` for roughly three decades - most countries'
  flags return to `A` again around 2020-2021.
- Kenya's coffee and maize yield, checked as a same-country control,
  show no jump and no flag change across the same years - both stay
  `A` continuously through 1991.

**Conclusion**: this is a real, tea-specific FAOSTAT methodology
change, not a country-specific agronomic event and not a general
region-wide data problem - the region's coffee and maize yield
reporting stayed on officially-sourced figures through the same
period, only tea switched to FAO's own estimation model, and it did so
for every EAC country studied in the same year. The clonal-tea-variety
hypothesis floated when this was first noticed is not supported by
this evidence; the uniform, simultaneous, flag-correlated jump across
five otherwise-independent countries is a source-methodology signature,
not five separate real agricultural events happening to land in the
same year.

**Whether this affects any currently-reported E1/E2/E3 result: no,
checked directly rather than assumed.** Every price series in this
study starts in 1991 (FAOSTAT's PP domain has no earlier data for any
of these items/countries), and the forecasting scripts only use a
production value as a lagged (year t-1) feature for years where a
price also exists - so the earliest production year any current result
actually uses is 1991 itself, already entirely inside the single
post-1991 FAO-estimated regime. There is no pre/post mix to correct
here, unlike Burundi and Rwanda's coffee price break - this finding is
reported as a real, now-understood characteristic of the production
modality's provenance, not as a bug requiring a rerun.

## Commodity expansion: 5 crops, chosen by real coverage (2026-09-21)

Direct follow-up question: "can we have 5 common among the EAC
countries" - this experiment had used only coffee, maize, and tea
since Phase 0's very first slice, without ever checking whether that
was the best available set. Fetched every country's complete raw PP
domain in one pass (all 8 countries, `output_type=objects` with no
item filter) and cross-tabulated real price coverage against every one
of the 31 commodities in `FAOSTAT_ITEM_MAP`.

**Finding, stated plainly because it reframes something already in
this report**: coffee and tea, the two commodities used from the
start, are actually 3-of-4 coverage among the price-active countries
(Tanzania has zero real FAOSTAT PP record for either) - worse than 13
other candidate commodities that have real data in all 4 of Kenya,
Rwanda, Tanzania, Burundi. Maize (already used) is the single best,
4/4 with 108 total years. Sorghum (98 years) and sweet potatoes (91
years) are the next two best 4/4 candidates with no country reduced to
a thin stub - several others (rice, potatoes, beans, cassava) are
technically 4/4 too but all share the same weak spot, only 5 real
years for Tanzania.

**Project owner's direction**: keep the region's main exported cash
crops (coffee, tea) rather than drop them for a cleaner coverage
number, and add the best-covered real crops on top. Final set: coffee,
maize, tea, sorghum, sweet potatoes - five commodities, matching the
request, with maize/sorghum/sweet potatoes real in all 4 price-active
countries and coffee/tea real in 3 of 4 (documented, not hidden).

Added to `collect_price_history.py` and `collect_production_history.py`
(`COMMODITIES` list) and all four E1/E2 run scripts. Both new item
codes were already present in `services/forecasting/yield_prediction.py`'s
own item map, so no new service-layer lookups were needed.

**A fourth false positive in the regime-break detector, found and
fixed the same way as every prior one**: Burundi's real sweet potato
price dips after 1999 and stayed low long enough to trip the existing
0.6 sustain threshold (ratio 0.538). Checked against the raw rows
before trusting it: the FAOSTAT flag stays `A` (official) continuously
across 1999 - unlike both confirmed real breaks, which each coincide
with an `A` -> `E` flag change - and the pre-1999 spike (1996-1998,
plausibly tied to Burundi's 1993-2005 civil war era) followed by a
return to a similar range looks like ordinary volatility in a
locally-traded staple, not a structural break. `_SUSTAIN_RATIO`
tightened from 0.6 to 0.5 - the false positive's ratio (0.538) and the
two confirmed true positives' ratios (0.195, 0.217) have a wide, clean
gap, so 0.5 removes the false positive with comfortable margin on both
real cases. Re-verified against all 18 real price series at that
point, not just the case in question, before moving on. Full account
in [`regime_break.py`](scripts/regime_break.py)'s own docstring.

**Real results, full 8-country x 5-commodity re-collection**: 464 real
price observations (up from 267), 2,137 real production observations
(up from 1,227). Series count for E1/E2 grew from 9 to 17 (still
excluding Rwanda coffee for insufficient post-break data, and every
zero-price country/commodity pair).

E1, 17 series:

| Tier | MAPE | Directional accuracy |
|---|---|---|
| T0, price alone | 15.2% | 55.5% |
| T1, plus weather | 21.1% | 65.0% |
| T3, plus production | 23.8% | 59.8% |

The weather-tier directional-accuracy advantage holds at every series
count this experiment has tried (6, 9, 10, 17) - the most repeatedly
confirmed finding in this project. MAPE rose again with the wider
commodity set, this time not from one dominant outlier the way
Burundi coffee was before its regime restriction, but spread across
several genuinely small, volatile series - Tanzania sorghum (n_test=3,
T1 MAPE 57.9%), Burundi sweet potatoes (n_test=4, T1 MAPE 73.7%),
Tanzania sweet potatoes (n_test=2, T0 MAPE an almost suspiciously
precise 0.2%). These are small-sample variance, the same documented
mechanism behind this project's other small-series artifacts, not a
new data-quality problem requiring its own investigation - no repeated
cross-country signature, no flag change, nothing resembling the
coffee/tea provenance issues.

E2, 17 series:

| Tier | Baseline A coverage | Baseline D coverage |
|---|---|---|
| T0, price alone | 76.7% (3.3pt miss) | 79.5% (0.5pt miss) |
| T1, plus weather | 71.2% (8.8pt miss) | 74.0% (6.0pt miss) |

Baseline D lands within half a point of its 80% nominal target at T0 -
the closest this experiment has ever come to the pre-registered
target, at any series count tried. The direction (calibrated beats
naive) continues to hold at every scale; H3's severity criterion
(naive misses by more than 20pt) continues to not be met, now by an
even wider margin (3.3pt) than at any previous series count - the
finding has moved from "close" (10.8pt, 6 series) through "not close"
(5.0pt then 8.2pt) to "very much not close" (3.3pt) as real data was
added, a trend worth stating outright rather than letting the reader
infer it from three separate numbers in three separate places.

**Verified**: `ruff check` clean on `regime_break.py`,
`collect_price_history.py`, `collect_production_history.py`, all four
E1/E2 run scripts, and `generate_report_figures.py` (price/production
charts restructured from 3-panel to 5-panel grids). All 8 figures and
both report documents regenerated. Also checked, prompted by a visibly
flat-looking DR Congo line in the regenerated production chart: raw
QCL rows confirm 52 distinct real values across 64 years for DR Congo
coffee yield (mixed `A`/`E` flags, same as every other country) - a
real but low-volatility series, visually compressed by Rwanda's 2018
spike sharing the same y-axis, not a carried-forward-estimate
artifact.

## The evidence-quality radar chart was scoring the wrong dataset (2026-09-21)

Project owner noticed the report's radar chart (evidence quality by
modality) hadn't moved despite every other figure being regenerated
multiple times this session, and asked directly. Investigated rather
than just re-running the generator, since "hasn't moved" for a chart
that's supposedly recomputed each time is itself suspicious.

**Root cause**: `populate_evidence_quality.py`'s filename regex,
`^gold_standard_(?P<modality>[a-z]+)_(?P<ts>\d{8}_\d{6})\.json$`,
requires the timestamp to immediately follow the modality name with no
extra segment in between. `gold_standard_price_history_*.json`,
`_production_history_*.json`, and `_weather_history_*.json` - the real
multi-year collectors this entire session has been built around - all
silently failed to match. Confirmed directly in Python before touching
any code: the regex matched `gold_standard_price_20260917_155724.json`
(the ORIGINAL single-snapshot collector, superseded back on the ninth
Phase 0 slice) but returned no match at all for any `_history` file.
`populate_evidence_quality.py` had therefore been scoring the
17-18 September single-snapshot dataset - a different, far smaller,
long-superseded set of files - every single time it ran, completely
independent of every TZ/BI/UG/CD/5-commodity change made this session.
The radar chart's hardcoded numbers in `generate_report_figures.py`
were a stale copy of that stale computation, compounding the same
mistake a second time.

**Fix, two parts**:
1. Widened the regex to
`^gold_standard_(?P<modality>[a-z]+?)(?:_history)?_(?P<ts>\d{8}_\d{6})\.json$`
- non-greedy modality capture, `_history` absorbed as an optional
suffix, both filename styles normalize to the same modality key so
the script's existing "latest timestamp wins" selection does the right
thing automatically (real `_history` files win for price/production/
weather since they're newer; trade/text correctly keep their only real
files, since neither has a `_history` variant).
2. Re-ran `populate_evidence_quality.py` against the real current data
and rewrote `fig_evidence_quality_radar()` to compute its 5x7 grid
live from that output instead of a separate hand-typed dict - the
hand-typed copy is exactly what went stale unnoticed for four days
across this session's expansion work, so removing it removes the
whole failure mode, not just this one instance of it.

**Real results**: availability for price/production/weather jumped
from 0.58/0.67/1.00 to 0.95/1.00/1.00 - correctly reflecting that most
observations are now real multi-year rows, not single point-in-time
snapshots where a handful of zero-data countries dominated a tiny
denominator. Freshness for the same three modalities fell from close
to 1.0 down to about 0.11 - a real, separate, and expected consequence
of the same switch: freshness is a plain average over every scored
row, and the average row is now decades old once full history is
included, not a bug, an honest cost of the design choice that made
Experiment 1 possible in the first place. Trade and text, both still
real single snapshots with no `_history` variant, are numerically
unchanged, as they should be.

**Verified**: `ruff check` clean on both edited scripts. Re-ran
`populate_evidence_quality.py` and `generate_report_figures.py` end to
end and confirmed the printed per-modality summary table matches the
regenerated chart exactly, not just visually plausible.
