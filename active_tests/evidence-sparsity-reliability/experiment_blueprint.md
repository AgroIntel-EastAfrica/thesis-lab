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
