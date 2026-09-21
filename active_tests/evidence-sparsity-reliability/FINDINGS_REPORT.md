# Findings Report: Evidence Sparsity and Reliability

### Paper 14, Trustworthy Agricultural Intelligence Under Data Sparsity

Status as of 21 September 2026: Phase 0 complete, now covering all
eight countries of the East African Community and five commodities.
Experiments E1, E2, and E3 run with real results. Experiment E4 has a
complete protocol, not yet run. Full chronological log in
[experiment_blueprint.md](experiment_blueprint.md).

## What this investigates

This project studies a general problem in artificial intelligence: how
a system should behave when its evidence is incomplete, uneven in
quality, or drawn from sources that were never designed to be compared
with one another. East African agriculture is the testbed for that
question, chosen because it exhibits the problem in an unusually clear
form. AgroIntel, the production platform this work is embedded in, is
the instrument used to run the investigation. It is not the subject of
the investigation.

## Research objectives and questions

This work is organised around the three objectives and six research
questions set out in the original proposal. The table below states
each one and its current status in this project.

| Objective | Description | Status |
|---|---|---|
| O1 | Multi-modal forecasting across market, trade, climate, and textual signals | Tested in E1 |
| O2 | Evidence-grounded agentic reasoning: retrieve, reconcile, quantify uncertainty, recommend or defer | Tested in E2 and E3 |
| O3 | Controlled continual learning and human-AI decision support | E3 addresses part of this; continual learning not yet tested; human-AI study (E4) not yet run |

| Question | Text | Addressed by | Result |
|---|---|---|---|
| RQ1 | Can multi-modal representations improve forecasting over single-source models? | E1 | Partially. Weather improved directional accuracy; production did not improve overall error. |
| RQ2 | Can temporal and relational representations improve forecasting during structural change and shocks? | E1 (partial) | Not directly tested. A real price shock case was analysed but no dedicated shock-forecasting method was built. |
| RQ3 | Can retrieval and structured knowledge improve factual grounding and reliability? | E3 | Yes, on a small hand-graded test. Not yet tested with a learned or language model agent. Calibration (E2) partly overlaps here: the calibrated method still beats the naive one at every scale tried, but the pre-registered severity criterion is not met, and is met less well as more real data is added. |
| RQ4 | When should an agent retrieve more evidence, recommend, or abstain? | E3 | A rule-based classifier answered this correctly on all five test scenarios. |
| RQ5 | Can controlled continual learning improve adaptation without drift or overconfidence? | Not started | No continual learning experiment has been built yet. |
| RQ6 | Does proactive, evidence-grounded support improve decision quality over reactive systems? | E4 | Protocol written, not run. Requires real human participants. |

## Datasets

Five real evidence modalities were collected for all eight countries
of the East African Community (Kenya, Rwanda, Tanzania, Burundi,
Uganda, DR Congo, South Sudan, Somalia) and five commodities (coffee,
maize, tea, sorghum, sweet potatoes). Kenya, Rwanda, Tanzania, and
Burundi were confirmed as the price-data-rich group, and Uganda, DR
Congo, South Sudan, and Somalia as the price-data-sparse group, by a
live check against FAOSTAT and UN Comtrade, not assumed from country
size or income level. Tanzania and Burundi were added on 21 September
2026 after the original four-country set raised the question of
whether the country selection was limiting the study; Uganda and DR
Congo were added the same day after a direct follow-up question about
why the full EAC bloc was not already covered. Sorghum and sweet
potatoes were added the same day again, after a question about whether
five commodities common across the EAC could be identified: a full
scan of all 31 candidate FAOSTAT items showed coffee and tea, the two
commodities used from the start, are only 3-of-4 covered among the
price-rich countries (Tanzania has no real price record for either),
while 13 other commodities are fully 4-of-4 covered. Coffee and tea
were kept as the region's main exported cash crops per the project
owner's explicit direction, and sorghum and sweet potatoes were added
as the two best-covered real alternatives.

| Modality | Source | Real observations | Time range | Coverage |
|---|---|---|---|---|
| Producer price | FAOSTAT Producer Prices, element 5532, USD/tonne | 464 | 1991 to 2024 | Kenya, Rwanda, Burundi full (5/5); Tanzania 3/5 (maize, sorghum, sweet potatoes); Uganda, DR Congo, South Sudan, Somalia return zero |
| Production and yield | FAOSTAT Crops and Livestock Products, element 5412, MT/ha | 2,137 | 1961 to 2024 | Kenya, Rwanda, Tanzania, Burundi, Uganda, DR Congo full (5/5); South Sudan 2/5, Somalia 3/5 |
| Weather | NASA POWER, MERRA-2 and GEOS reanalysis, temperature and precipitation | 544 | 1991 to 2024 | All eight countries, complete |
| Trade | UN Comtrade, export flows by HS code | 12 pairs tested | 2023 | Kenya only real and nonzero; others confirmed genuine zero |
| Text and news | GDELT news search and classification | 2 of 12 calls succeeded | Single snapshot | Limited by API reliability, not by evidence absence |

Uganda and DR Congo behave like South Sudan and Somalia for price
(zero real FAOSTAT producer price records for any commodity) but like
Tanzania and Burundi for production (a complete 1961-2024 record for
all five). This is included as a further, concrete illustration of
this project's central point: none of the eight countries share the
same availability pattern across all modalities, and a country's
overall "data richness" cannot be predicted from any single modality's
coverage, or from which crops are its best-known exports.

Three limitations are worth stating directly. Weather is read from a
single point, each country's capital city, used as a national proxy.
Trade is limited by a real UN Comtrade rate quota, hit twice during
this project, and has not yet been extended to the new countries.
Price and production were extended from a single snapshot into full
historical series, using history FAOSTAT already had but the original
collectors were discarding; trade and text remain single snapshots for
all six countries.

A fourth limitation surfaced only after adding Tanzania and Burundi,
and is worth its own paragraph because it changed how the price data
is used, not just how much of it there is. Burundi's coffee price and
Rwanda's coffee price each contain a real, officially reported break:
Burundi's fell from about \$1,900 to about \$180 a tonne between 2006
and 2007, and Rwanda's fell from about \$1,370 to about \$280 a tonne
between 2010 and 2015. Neither country's tea price moved anything like
this over the same years, and Kenya's coffee price, the one country
whose coffee market never went through a state-to-private transition
in this period, shows no such break at any point in its record. The
most likely explanation is that FAOSTAT's reported price basis for
coffee changed in each country when its coffee marketing board was
liberalised, not that anything is wrong with the collected numbers. A
model fitted across both price levels as though they were one series
produces meaningless error figures, so a break-detection check was
added and both series are now restricted to their real, single-regime
window before any forecasting or calibration model sees them. See
[regime_break.py](scripts/regime_break.py) for the method and its
validation against every other series before use.

## What the data looks like

![Price history](report/figures/01_price_history.png)

Kenya's price series runs continuously to 2024 for coffee, maize, and
tea, and covers most of sorghum and sweet potatoes' real range too.
Rwanda's maize, sorghum, and sweet potato series are equally complete,
but its coffee and tea series stop in 2015. Burundi's coffee and tea
series stop in 2019; coffee shows a real, sustained price collapse
after 2007, from roughly two to three thousand dollars a tonne down to
two to four hundred (marked with a dotted line in the chart, where the
same real break shows up in Rwanda's coffee price too, in 2015).
Tanzania has real price series for maize, sorghum, and sweet potatoes;
FAOSTAT has no producer price record for Tanzanian coffee or tea at
all.

![Production history](report/figures/02_production_history.png)

Tanzania, Burundi, Uganda, and DR Congo all have a complete 1961 to
2024 production record for all five commodities, the same
completeness as Kenya and Rwanda. South Sudan appears only in the
maize and sorghum panels (2 of 5); Somalia additionally has a real
sweet potato record (3 of 5). Neither has ever had FAOSTAT-tracked
coffee or tea production data.

A second real provenance issue was found and resolved in the tea
panel, the same way the coffee price breaks were. Kenya's and Uganda's
tea yield both jump sharply around 1990; checking the raw FAOSTAT rows
showed the same jump, by a similar factor, in Rwanda, Burundi, and
Tanzania too, just harder to see on this chart's shared scale because
their post-jump values are smaller in absolute terms. All five happen
in the same year, 1990 to 1991, and all five coincide exactly with
FAOSTAT's own quality flag switching from official figure to FAO
estimate, where it stays for about three decades before mostly
reverting around 2020. Kenya's coffee and maize yield, checked as a
control, show no jump and no flag change across the same years. This
is a real, tea-specific change in how FAOSTAT produces this one
figure, not a farming event and not a general regional data problem.
It does not affect any forecasting result in this report: every price
series here starts in 1991, so no forecast ever uses a production
value from before the switch.

![Weather uniformity](report/figures/03_weather_uniformity.png)

Weather is the only modality with complete, uniform coverage across
all eight countries.

![Availability matrix](report/figures/04_availability_matrix.png)

| Modality | KE | RW | TZ | BI | UG | CD | SS | SO |
|---|---|---|---|---|---|---|---|---|
| Price | 100% | 100% | 60% | 100% | 0% | 0% | 0% | 0% |
| Production | 100% | 100% | 100% | 100% | 100% | 100% | 40% | 60% |
| Weather | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% |
| Trade | 100% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |

No row and no column matches another. Data availability is a property
of the modality, the commodity, and the country together, not any one
of the three alone. Completing the full eight-country, five-commodity
set did not make this cleaner; it confirmed the pattern at full scale.
Uganda and DR Congo, in particular, are price-sparse like South Sudan
and Somalia but production-rich like Tanzania and Burundi, a sixth
distinct combination that did not exist in the smaller country set.
South Sudan and Somalia are also no longer identical to each other:
adding sweet potatoes gave Somalia a third real production series
while South Sudan stayed at two.

![Evidence quality radar](report/figures/07_evidence_quality_radar.png)

A seven-dimension quality score (availability, quality, relevance,
freshness, compatibility, provenance, geographic coverage) was
computed for each modality, averaged directly over every real
observation currently collected rather than typed in by hand, so this
chart cannot go stale the way an earlier version of it did (see below).
No modality scores well on every dimension. Weather has the best
source quality but the worst geographic coverage, because of the
single-point proxy. Trade has strong provenance but the weakest
compatibility, since a total export value in dollars cannot be
compared directly to a per-tonne price. Text scores lowest overall,
reflecting its real reliability problem.

Price, production, and weather now score near the maximum on
availability, a real change from an earlier version of this chart,
which showed price at 0.58 and production at 0.67. That earlier chart
was not simply out of date; the script computing it had a filename
bug that made it silently keep scoring the original single-snapshot
collectors from 17 September, never the multi-year collectors used for
every other result in this report, so it was never actually looking at
this project's current data at all. Fixed by widening the filename
pattern the scoring script matches. The same three modalities now show
sharply lower freshness (around 0.1, down from close to 1.0) for a
real and different reason: switching from one snapshot per country to
a full historical series means the average observation being scored is
now decades old rather than current-year, and freshness is a plain
average over every real row. This is an honest cost of the same design
choice that made Experiment 1 possible in the first place, not a new
problem, and it is a fair trade: forecasting needs the history,
knowing the average row is old is more informative than a stale chart
implying everything is current.

## Experiment 1: forecasting (RQ1, RQ2)

Question: does adding a second or third source of real evidence
improve forecast accuracy?

Method: ordinary least squares, seventeen series (Kenya and Burundi
each with all five commodities; Rwanda with four, coffee excluded;
Tanzania with three, since it has no real coffee or tea price
history), time-ordered holdout. Three tiers: price alone (T0), price
plus weather (T1), price plus weather plus production (T3). Every
series is passed through the break check described above first;
Burundi coffee is fit only on its real 2007-2019 window, and Rwanda
coffee is excluded entirely, since only one real year remains once its
own break is respected, too few to fit or test a model on.

![E1 tiers](report/figures/05_e1_tiers.png)

| Tier | MAPE | Directional accuracy |
|---|---|---|
| T0, price alone | 15.2% | 55.5% |
| T1, plus weather | 21.1% | 65.0% |
| T3, plus production | 23.8% | 59.8% |

Weather still produces a real improvement in directional accuracy, the
same pattern found in every run of this experiment so far, at every
series count tried (6, 9, 10, and now 17). Production still does not
add further improvement on average. MAPE rose again with the wider
commodity set, this time without one dominant outlier the way Burundi
coffee was before its own regime restriction; it is spread across
several genuinely small, volatile series instead.

| Series | Real cause |
|---|---|
| Kenya coffee | A documented 2021 global price shock (Brazil frost) that no local yield feature could predict |
| Kenya tea | A genuine multi-decade production trend unrelated to price, which biased the model's direction |
| Burundi coffee | Only 12 real years survive the regime restriction, 8 training and 2 test points; one prediction still swings the tier-level MAPE |
| Tanzania sorghum, Burundi sweet potatoes | Test sets of 2 to 4 points; this project's small-sample variance mechanism, already documented above, not a new data-quality issue |

Conclusion: whether added evidence helps depends on whether it is
causally connected to the target during the period being tested, not
simply on how much evidence is added. A single aggregate accuracy
number is also sensitive to which real series happen to be in the
pool and to how each series is prepared, which is itself a reason to
report the individual series, not just the average.

## Experiment 2: calibration (O2, part of RQ4)

Question: is a model's stated confidence trustworthy, and does
explicit calibration correct it?

Method: same seventeen series as E1, same regime restriction applied
to Burundi and Rwanda coffee. Baseline A estimates uncertainty from
its own training error, a common real mistake. Baseline D uses
leave-one-out residuals, a distribution-free method related to
conformal prediction. Both target 80 percent coverage.

![E2 calibration](report/figures/06_e2_calibration.png)

| Tier | Baseline A coverage | Baseline D coverage |
|---|---|---|
| T0, price alone | 76.7% | 79.5% |
| T1, plus weather | 71.2% | 74.0% |

The calibrated method still beats the naive one at T0, the same
direction found in every run of this experiment. Baseline D now lands
within half a point of its 80 percent nominal target, the closest this
project has measured at any series count. The pre-registered pass
condition for H3 required the naive baseline to miss by more than 20
points while the calibrated one stayed within 10; here Baseline A
misses by only 3.3 points, so H3's severity criterion is not met, and
by a wider margin than in any earlier run of this experiment (10.8
points at 6 series, 5.0 at 10, 8.2 at 9 after the first regime
correction, 3.3 now). The direction of H3 keeps being confirmed; its
severity claim keeps getting less supported as more real data is
added, and that trend is reported outright rather than left for a
reader to notice across separate numbers in separate places. Weather
still only hurts the naive baseline (76.7 percent down to 71.2
percent) more than the calibrated one (79.5 down to 74.0). With
training sets as small as eight to twenty-four points per series,
fitting one more parameter still introduces real out-of-sample
variance that a naive training-time estimate does not anticipate,
which is why the calibrated method continues to be the safer choice
even where it does not clear the pre-registered severity bar.

## Experiment 3: evidence grounding (O2, RQ3, RQ4)

Question: can a system recognise when to recommend, retrieve more
evidence, investigate a conflict, or abstain, instead of always
answering?

Method: a rule-based classifier sorting evidence into five states,
each mapped to an action.

| State | Action | Real test case |
|---|---|---|
| Sufficient | Recommend | Kenya coffee, fresh and consistent data |
| Insufficient | Retrieve, then abstain | South Sudan coffee, confirmed zero data |
| Conflicting | Investigate | A real 2026-09-17 incident, a forecast evaluated against a synthetic price ten times the real one |
| Stale | Recommend with caveat | Kenya trade, fixed at 2023, not obtainable more recently |
| Semantically incompatible | Investigate | Kenya coffee's real per-tonne price against its real total export value |

All five cases produced the expected action. This shows the rule is
internally consistent on known cases. It does not yet show that a
learned or language model agent would behave the same way, or that the
rule generalises beyond the cases it was built on.

## Experiment 4: decision reliability, protocol only (RQ6)

This experiment measures real human decisions across five presentation
formats and requires informed consent and institutional review.
Simulating participants would be fabrication, not research. A complete
protocol exists in
[E4_study_protocol.md](E4_study_protocol.md), built from real numbers
already produced by this project.

![E4 scenario](report/figures/08_e4_scenario.png)

| Format | Value shown |
|---|---|
| Bare point forecast | $3,934.60 or $4,253.00 per tonne |
| With 80 percent interval | $2,383.30 to $5,486.00 per tonne |
| Real 2024 outcome | $4,886.50 per tonne |

The point forecast alone understated the real outcome by up to 21
percent. The interval correctly signalled that the real outcome, while
above the point estimate, was still a plausible result.

## The finding that connects everything

Adding evidence is not automatically an improvement, and it fails
differently depending on the case: a real shock, a spurious trend, a
sustained regime break, or a small-sample calibration cost. A single
blended accuracy score would have hidden all of these. Measuring
forecasting accuracy, calibration, and evidence quality separately is
what made each mechanism visible. Widening the country pool did not
resolve this; it surfaced a new instance of the same pattern, and it
was not enough to notice the instance and move on. Burundi and
Rwanda's coffee prices needed their own investigation, back to the raw
source rows, before it was possible to say whether the anomaly was
this project's handling of the data or the data itself. It turned out
to be neither in the usual sense: the data is real and officially
reported, but it silently changed what it measures partway through
each series, most likely when each country's coffee sector moved from
a state-controlled to a liberalised market. Once that was understood,
the correct response was not to discard the affected series but to
detect the change and restrict each series to a single real regime, a
general method now applied automatically, not a manual patch for these
two cases. Which pre-registered thresholds were met also changed
across this process, which is itself evidence that conclusions in this
domain are sensitive to real sample composition and to real,
undocumented shifts inside individual data sources, and should be
checked again as the dataset grows, not assumed stable. A second,
independent case of the same lesson turned up almost immediately
afterward, in a different modality: real tea yield jumps across five
countries at once in 1991, tracing back to FAOSTAT's own estimation
methodology rather than any farm-level change. It happened not to
affect this report's numbers, but only because every price series here
starts after the switch; a wider study using this same production data
back to 1961 would need to check for it directly, not assume the
coffee case was the only one.

## Honest limits

| Limitation | Detail |
|---|---|
| Modality depth | Only price, production, and weather have real time series; trade and text remain single snapshots, and were not extended past Kenya |
| Series count | Seventeen series tested; Uganda, DR Congo, South Sudan, and Somalia excluded from forecasting, since none has real price history; Tanzania contributes three series (maize, sorghum, sweet potatoes) rather than five; Rwanda coffee is excluded because only one real year survives its own regime restriction |
| Cash crop coverage | Coffee and tea, the region's main exported cash crops, are the two weakest-covered commodities in this study by design, kept deliberately rather than dropped for a tidier number; every other finding involving them should be read with that in mind |
| Tea yield provenance | Every country's real tea yield is a FAOSTAT estimate, not an official figure, for 1991 through roughly 2020 (confirmed via the source's own quality flag); does not affect this report's forecasting results, since no price series here predates 1991, but any future work using tea yield levels before 1991 alongside levels after it would need the same regime treatment already applied to Burundi and Rwanda's coffee price |
| Regime breaks | Detected and corrected for Burundi and Rwanda coffee using a rule checked against all ten collected series; a real possibility remains that a smaller, undetected break exists in another series this method's thresholds are not sensitive enough to catch |
| Freshness metric | Price, production, and weather now score near zero on the freshness dimension by construction, once scoring covers full multi-year history instead of one snapshot; a plain average over all real rows is the honest number, but it means this dimension no longer distinguishes "the source updates promptly" from "this project chose to score old rows too" |
| Forecast granularity | Annual only; the proposal's stated task was 30-day forecasting |
| Sparsity sweep | No systematic test from full data down to 10 percent has been run |
| E4 | Protocol only, requires real participants and institutional review |
| RQ5 | Continual learning has not been started |

---

Figures generated by
[generate_report_figures.py](scripts/generate_report_figures.py).
Full chronological record in
[experiment_blueprint.md](experiment_blueprint.md).
