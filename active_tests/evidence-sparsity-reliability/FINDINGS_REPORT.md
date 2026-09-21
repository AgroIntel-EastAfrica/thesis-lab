# Findings Report — Evidence Sparsity & Reliability (Paper 14)

**Trustworthy Agricultural Intelligence Under Data Sparsity: An Empirical
Study of Evidence Availability, Uncertainty, and Reliability**

*Status: Phase 0 complete; E1, E2, E3 run with real results; E4 is a
real, ready-to-run protocol, not yet executed (human-subjects study).
This report consolidates the chronological log in
[`experiment_blueprint.md`](experiment_blueprint.md) into one
narrative, with real charts generated from the real data — see
[`scripts/generate_report_figures.py`](scripts/generate_report_figures.py)
to regenerate them. Every number here is real: collected live from
FAOSTAT, NASA POWER, UN Comtrade, and GDELT, or computed directly from
that real data. Nothing in this report is simulated or invented.*

---

## 1. Research question

Does evidence availability, quality, and calibration affect the
reliability of agricultural AI intelligence under real data-sparse
conditions? Tested across a real gold-standard dataset spanning 5
evidence modalities (price, weather, production, trade, textual/news
signals) for Kenya, Rwanda, South Sudan, and Somalia — coffee, maize,
and tea.

## 2. Exploratory data analysis — what's actually in the dataset

### 2.1 Producer price (FAOSTAT), 1991–2024

![Price history](report/figures/01_price_history.png)

Kenya has real, continuous FAOSTAT price data for all three
commodities through 2024. Rwanda's maize series is equally complete,
but its **coffee and tea series stop at 2015** — a decade-plus real
reporting gap invisible in a single-year snapshot, only visible once
the full time series is plotted.

### 2.2 Production/yield (FAOSTAT QCL), 1961–2024

![Production history](report/figures/02_production_history.png)

Kenya and Rwanda have the full 64-year record for all three
commodities. South Sudan and Somalia (orange/red) appear **only in the
maize panel** — they have never had FAOSTAT-tracked coffee or tea
production data, going back to 1961. This is a structural,
commodity-driven gap, not a recent one.

### 2.3 Weather (NASA POWER), 1991–2024

![Weather uniformity](report/figures/03_weather_uniformity.png)

All four countries have complete, real weather data for the entire
window — the cleanest modality collected. Satellite coverage doesn't
care about a country's national statistical capacity.

### 2.4 Real coverage matrix

![Availability matrix](report/figures/04_availability_matrix.png)

Putting price, production, weather, and trade side by side makes the
core Phase 0 finding visible at a glance: **no single row and no
single column tells the same story.** Price splits along one line
(KE/RW vs. SS/SO); weather doesn't split at all; production splits by
commodity, not country; trade breaks the price-tier pattern outright —
Rwanda, otherwise "data-rich," is genuinely zero on trade. (Text/news
is excluded from this grid — its problem isn't availability, see §2.5.)

### 2.5 Evidence quality, not just availability

![Evidence quality radar](report/figures/07_evidence_quality_radar.png)

A first, individually-justified `EvidenceQualityVector` scored across
all 56 Phase 0 observations (see `evidence_quality_rubric.py` for the
full justification behind every number). **No modality wins on every
dimension.** Weather has the best source quality (Q) and provenance
(P) of any modality, but the worst geographic fidelity (G) — a real,
named limitation: it reads one point (the capital city) as a stand-in
for the whole country. Trade has strong provenance and geography but
the weakest compatibility (C) — a raw USD total that conflates price
and volume. Text is weakest on nearly every dimension: its ~17% real
success rate (§4, Experiment E1's text-modality note) shows up
directly as low Q.

**Core Phase 0 finding**: evidence availability and quality are
properties of the **(modality, commodity, country) triple** — not
reducible to any single dimension, not even "this country is
data-rich" as a general trait.

## 3. Experiment E1 — Forecasting under controlled evidence availability

**Question**: does adding a second (or third) evidence modality reduce
real, backtested price-forecast error?

**Method**: ordinary least squares, KE/RW × coffee/maize/tea (6 real
series with aligned price+production+weather history), time-ordered
holdout (never random shuffle) on the last ~20% of each series' real
years. T0 = price alone; T1 = price + weather; T3 = price + weather +
production.

![E1 tiers](report/figures/05_e1_tiers.png)

| Metric | T0 | T1 | T3 |
|---|---|---|---|
| MAPE | 15.0% | 14.5% | 14.5% |
| Directional accuracy | 48.9% | **59.4%** | 53.3% |

Weather gives a real, meaningful lift in directional accuracy — a
coin-flip baseline (50%) beaten only once evidence is added. But this
aggregate hides real mechanism: a follow-up investigation found KE
coffee's error is dominated by a real, documented 2021 global price
shock (+96% YoY, Brazil frost) that no national yield feature could
ever predict; KE tea's directional accuracy actually *dropped*
(1.00→0.60) because production's real long-term upward trend
spuriously biased the model against a volatile, trendless price
target; and Rwanda coffee's apparent improvement is most plausibly a
2-point calm-test-window sample artifact, not a real effect.

**Finding**: whether added evidence helps depends on whether its real
variation is *causally connected* to the target's real variation over
the test window — not "more evidence, more accuracy."

## 4. Experiment E2 — Uncertainty and calibration

**Question**: does explicit, distribution-free uncertainty
quantification beat naive in-sample confidence — and does adding
evidence help calibration the way it (partially) helped accuracy?

**Method**: same 6 series, same OLS point forecast. Baseline A
(uncalibrated) uses the model's own training-residual spread as an 80%
interval — the real, common mistake of trusting in-sample error.
Baseline D (LOO-conformal) uses leave-one-out residuals instead —
distribution-free, no separate calibration split needed.

![E2 calibration](report/figures/06_e2_calibration.png)

| Tier | Baseline A | Baseline D |
|---|---|---|
| T0 (price) | 69.2% (10.8pt miss) | 73.1% (6.9pt miss) |
| T1 (+weather) | 61.5% (18.5pt miss) | 69.2% (10.8pt miss) |

Two real findings. First: the calibrated method (D) beats the naive
one (A) in every comparison — confirming H3's *direction*, though not
its pre-registered *severity* (the concluded experiment's original
80%-vs-38.5% gap came from a more complex production system; this
simpler model's naive baseline was never guaranteed to fail that
badly, and didn't). Second, and more striking: **adding weather made
calibration measurably worse for both baselines** — the miscalibration
gap widened ~70% (A) and ~57% (D) from T0 to T1. Mechanism: these
series have only 9–24 real training points; T1 fits 2 extra
parameters on the same tiny sample, and neither baseline's
uncertainty estimate anticipated the resulting out-of-sample variance.

**Finding**: the same "more evidence isn't free" lesson as E1, now
shown for *calibration* via a completely independent mechanism
(small-sample parameter variance, not a spurious trend or a macro
shock) — real support for measuring forecasting accuracy and
calibration as separate dimensions, not one blended score.

## 5. Experiment E3 — Evidence grounding

**Question**: can a real agent recognize *when* to recommend, retrieve
more evidence, investigate a conflict, or abstain — instead of always
answering?

**Method**: a real, mechanical evidence-state classifier
(SUFFICIENT / INSUFFICIENT / STALE / CONFLICTING /
SEMANTICALLY_INCOMPATIBLE) and action selector, tested against the
blueprint's 5 named scenarios — every one grounded in real data or a
real documented incident from this lab's own history, none fabricated:

| Scenario | Real grounding | Result |
|---|---|---|
| A — Sufficient | KE coffee: real, fresh, multi-modal, no conflict | ✅ recommend |
| B — Insufficient | SS coffee: genuinely zero real price data | ✅ retrieve → abstain |
| C — Conflicting | The real 2026-09-17 price-source-mismatch incident (\$270–280/tonne real FAOSTAT vs. \$2,600–2,800/tonne synthetic baseline) | ✅ investigate → caveat |
| D — Outdated | KE trade: real data fixed at 2023, 3 years stale | ✅ recommend with caveat |
| E — Semantically incompatible | KE coffee's real \$4,886.5/tonne price vs. real \$518,720,901 total trade value | ✅ investigate → caveat |

**5/5 scenarios matched their expected action.** Honest limit: this
validates the decision procedure's own internal consistency against 5
known, hand-picked cases — it does not yet show that a real
LLM-driven agent behaves this way, or that it generalizes to novel
cases the classifier wasn't built around.

## 6. Experiment E4 — Decision reliability (protocol only)

E4 measures real human decisions — response time, override behavior,
decision accuracy — across 5 presentation formats. That requires real
participants, informed consent, and institutional review; simulating
synthetic participants would be fabrication, not research. A real,
ready-to-run protocol exists at
[`E4_study_protocol.md`](E4_study_protocol.md), built from real E1/E2/E3
outputs rather than invented numbers:

![E4 scenario](report/figures/08_e4_scenario.png)

A bare point forecast ($3,934.60 or $4,253.00/tonne) looks precise but
was wrong by up to 21% against the real 2024 actual ($4,886.50/tonne).
The same forecast shown with its real 80% interval ($2,383.30–
$5,486.00) correctly signals that the real outcome, while above the
point estimate, was still a plausible result — the entire premise E2
exists to test, made visible as a decision-relevant fact rather than
just a coverage percentage.

## 7. Cross-cutting finding

The single strongest result spanning E1 and E2 together: **adding
evidence is not uniformly beneficial, and it fails in genuinely
different ways depending on the case** — a real macro shock swamping
any feature (E1, KE coffee), a spurious trend biasing directional
calls (E1, KE tea), small-sample parameter variance degrading
calibration (E2, all series). A system that only tracked one blended
accuracy number would have missed all three mechanisms. This is direct
empirical support for the blueprint's own Metrics-by-category design —
forecasting, calibration, and evidence quality genuinely need
independent measurement.

## 8. What's still open

- Real time-series data exists for only 3 of 5 modalities (price,
  production, weather) — trade is a single real snapshot (quota-limited
  by UN Comtrade), text is reliability-limited by design
- Only 6 series tested (KE/RW × coffee/maize/tea) — SS/SO excluded
  since they have no real price to forecast against
- Annual granularity only — the source proposal's actual task (30-day
  forecasting) needs a modality with that granularity, which none yet
  has
- No systematic sparsity sweep (100%→10%) as the blueprint's own
  Experiment B design calls for
- E4 has no results — needs real participants and institutional review
- H2 and H5 remain completely untested (they depend on Experiment C's
  corruption conditions and E4 respectively, neither built/run yet)

---

*Figures generated from real data by
[`scripts/generate_report_figures.py`](scripts/generate_report_figures.py).
Full chronological log with every intermediate slice, investigation,
and honest dead-end in [`experiment_blueprint.md`](experiment_blueprint.md).*
