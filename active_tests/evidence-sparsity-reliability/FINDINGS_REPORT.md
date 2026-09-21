# Findings Report: Evidence Sparsity and Reliability

### Paper 14, Trustworthy Agricultural Intelligence Under Data Sparsity

This report is current as of 21 September 2026. Phase 0 (the gold
standard dataset and provenance layer) is complete. Experiments E1,
E2, and E3 have been run and produced real results. Experiment E4 has
a complete, ready to run protocol but has not yet been carried out,
since it requires human participants. The full chronological record of
every step, including dead ends and corrections, is kept in
[experiment_blueprint.md](experiment_blueprint.md). This report pulls
that record together into one readable account, with figures drawn
from the real data.

## What this research is actually about

It is worth being clear about this from the start, because it is easy
to read a report full of coffee and maize prices and conclude that the
subject is agriculture. It is not. The subject is a general problem in
artificial intelligence: how should a system behave when the evidence
available to it is incomplete, of uneven quality, or drawn from
sources that were never designed to be compared with one another. That
question matters for any AI system that has to act on real, messy,
partial information, whether it forecasts commodity prices, screens
medical images, monitors infrastructure, or assesses financial risk.

East African agriculture was chosen as the setting for this
investigation because it presents the problem in an unusually clear
and severe form. Some countries publish agricultural statistics going
back sixty years. Others publish almost nothing. Some crops are
tracked closely because they matter for food security. Others are
largely ignored because they are grown mainly for export and attract
less statistical attention. Weather satellites cover every country
equally, since they do not care about a country's data infrastructure,
while the agencies that compile price and trade statistics plainly do.
This creates something close to a natural experiment. The same
underlying question, whether evidence can be trusted and what a system
should do when it cannot, shows up again and again across different
data sources, for different reasons each time.

AgroIntel, the production agricultural intelligence platform this work
is built alongside, is the instrument used to carry out this
investigation. It is not the subject of the investigation. Working
against a real production system gave this research access to real
data, real APIs, and real forecasting code that a synthetic simulation
could not have provided, and it surfaced genuine software defects
along the way that would not have appeared in a toy dataset. But the
scientific question underneath stays general: what makes a piece of
evidence trustworthy, and how should an intelligent system respond
once that trust is not there.

## The datasets

Five evidence modalities were collected, all from real, live sources,
for four countries (Kenya, Rwanda, South Sudan, and Somalia) and three
commodities (coffee, maize, and tea). Kenya and Rwanda were chosen as
the data rich pair and South Sudan and Somalia as the data sparse
pair, based on a live check against FAOSTAT and UN Comtrade before any
collection began, not an assumption carried over from prior work.

**Producer price.** Sourced from FAOSTAT's Producer Prices domain,
element 5532, reported in United States dollars per tonne. A full
historical pull for Kenya and Rwanda returned 157 real observations
spanning 1991 to 2024. South Sudan and Somalia returned no real
observations for any of the three commodities across the same window.

**Production and yield.** Sourced from FAOSTAT's Crops and Livestock
Products domain, element 5412 (yield in hectograms per hectare,
converted to metric tonnes per hectare). This is FAOSTAT's longest
series in the dataset, running from 1961 to 2024, and produced 465
real observations. Kenya and Rwanda have the full 64 year record for
all three commodities. South Sudan has 13 years of maize and nothing
for coffee or tea. Somalia has the full 64 years of maize and, again,
nothing for coffee or tea.

**Weather.** Sourced from NASA POWER, using the MERRA-2 and GEOS
reanalysis products, for two variables: mean temperature at two
metres and corrected precipitation. Because satellite reanalysis has
no dependency on a country's own statistical office, this was the only
modality with complete, real coverage for all four countries across
the full 1991 to 2024 window, 272 observations in total. One real
limitation is worth stating plainly: each country's weather series is
read from a single point, the geographic coordinates of its capital
city, and used as a national proxy. That is a reasonable approximation
for a small, climatically uniform country and a weaker one for a
large, varied one.

**Trade.** Sourced from the UN Comtrade API, using the HS commodity
codes for coffee, maize, and tea, restricted to export flows for 2023,
the most recent year confirmed to have real data at the time of
collection. Kenya returned real, substantial export values for all
three commodities. Rwanda, South Sudan, and Somalia all returned a
genuine, confirmed zero, verified directly against the raw API
response rather than assumed from an error. Comtrade also has a real
operational rate limit that was hit twice during this project, which
is itself a finding rather than an inconvenience, discussed later in
this report.

**Text and news.** Sourced from GDELT, the Global Database of Events,
Language, and Tone, using its news article search and classification
pipeline. This modality behaved differently from the other four. The
problem was not that evidence was absent, but that the API itself was
unreliable: across three independent collection runs, only about two
in every twelve calls succeeded. That distinction, between evidence
being unavailable and evidence being available but delivered by an
unreliable source, turned out to be one of the more useful findings
of this project and is discussed in the next section.

Two of the five modalities, price and production, were later extended
from a single snapshot into full historical time series, since FAOSTAT
had already collected the complete history internally and the original
collectors were simply discarding all but the most recent year. That
extension is what makes the forecasting experiments in this report
possible at all.

## What the data actually looks like

The figure below shows the real producer price series for Kenya and
Rwanda. Kenya's series is continuous through 2024 for all three
commodities. Rwanda's maize series is equally complete, but its coffee
and tea series stop in 2015, a gap of more than a decade that is
invisible if you only look at the most recent year and only becomes
visible once the whole series is plotted.

![Price history](report/figures/01_price_history.png)

The production and yield series tell a related but distinct story.
Kenya and Rwanda again have the full 64 year record for all three
commodities. South Sudan and Somalia appear only in the maize panel.
They have never had FAOSTAT tracked coffee or tea production data, not
recently and not at any point since 1961. This is a structural gap
tied to what each country actually grows for export, not a recent
lapse in reporting.

![Production history](report/figures/02_production_history.png)

Weather is the cleanest dataset collected. All four countries have a
complete real record for the full window, which is exactly what you
would expect from a satellite based measurement that has no
dependency on any country's own statistical capacity.

![Weather uniformity](report/figures/03_weather_uniformity.png)

Putting price, production, weather, and trade side by side in a single
grid makes the central finding of this phase of the work visible at a
glance. No row and no column tells the same story.

![Availability matrix](report/figures/04_availability_matrix.png)

Price splits cleanly along one line, with Kenya and Rwanda on one side
and South Sudan and Somalia on the other. Weather does not split at
all. Production splits by commodity rather than by country. Trade
breaks the pattern set by price outright: Rwanda, which looked data
rich on every other measure, turns out to have no real trade data at
all for any of the three commodities. The conclusion this points to is
that data availability is not a property of a country. It is a
property of the combination of modality, commodity, and country
together, and none of those three factors can be dropped without
losing the real pattern.

## Evidence quality is a separate question from evidence availability

Having data is not the same as having good data. A rubric called the
Evidence Quality Vector was built to score each modality on seven
dimensions: availability, quality, relevance, freshness,
compatibility, provenance, and geographic coverage. Each score is a
first pass estimate, justified individually against a concrete fact
about that modality (for example, weather's geographic coverage score
is lower than its other scores specifically because of the
single point per country limitation described above), not a number
picked to look complete.

![Evidence quality radar](report/figures/07_evidence_quality_radar.png)

The clearest pattern in this chart is that no modality wins on every
dimension. Weather has the best source quality and the best provenance
of anything collected, since NASA POWER is a well documented,
official, satellite based product, but it has the worst geographic
coverage score for the reason already described. Trade has strong
provenance and strong geographic coverage but the weakest
compatibility score, because a raw total export value in dollars
conflates price and volume in a way that makes it hard to compare
directly against a per tonne price figure. Text scores lowest on
almost every dimension at once, which is a direct reflection of the
roughly one in six real success rate described above. A source can
exist, in other words, and still not be trustworthy, and those are
genuinely different failure modes that need to be measured separately.

## Experiment 1: does more evidence improve forecasting

The first experiment asks a simple question. If a forecasting model is
given a second, and then a third, source of real evidence in addition
to price history, does its forecast actually improve. The method was
kept deliberately simple: an ordinary linear regression, trained
separately for each of six real series (Kenya and Rwanda, each with
coffee, maize, and tea), using a strict time ordered holdout so that
no model was ever evaluated on a year it could have seen during
training. Three evidence tiers were compared: price alone, price plus
weather, and price plus weather plus production.

![E1 tiers](report/figures/05_e1_tiers.png)

Adding weather produced a real and meaningful improvement in
directional accuracy, from 48.9 percent, worse than a coin flip, to
59.4 percent. Adding production on top of that did not help further
and made the overall error (MAPE) marginally worse.

That aggregate number, on its own, would be easy to overstate. Looking
at the individual series tells a more honest and more interesting
story. Kenya's coffee forecast for 2021 was wrong by almost the same
margin whether or not the model had access to production data, because
2021 was the year of a real, well documented global coffee price
shock driven by frost and drought damage to Brazil's crop. No feature
built from a country's own yield statistics could plausibly have
anticipated a shock originating on a different continent. Kenya's tea
forecast actually got worse when production was added: tea yield in
Kenya has a genuine multi decade upward trend that has nothing to do
with short term price movements, and the model appears to have
mistaken that unrelated trend for a useful signal. Rwanda's apparent
improvement from adding production is most plausibly explained by the
fact that its test window happened to fall in an unusually calm period
for coffee prices, which is the easiest possible case for any extra
feature to look helpful by chance, given that only two years were
available to test against.

The conclusion is not that more evidence helps or that it does not. It
is that whether an additional source of evidence helps depends on
whether that evidence is genuinely, causally connected to what is
being predicted during the specific period being tested. A feature
that is real and well measured can still be irrelevant to the question
being asked, and a model cannot always tell the difference on its own.

## Experiment 2: is the model's stated confidence trustworthy

The second experiment turns from accuracy to honesty. A forecast that
is wrong is a normal, expected outcome. A forecast that claims to be
confident when it should not be is a more serious problem, because it
invites a decision maker to rely on it. Two ways of expressing
uncertainty were compared on the same six series. The first, which
this report calls the naive baseline, estimates its own uncertainty
from how well it fit the data it was trained on. This is a common and
easy mistake to make in practice, because a model almost always looks
more confident on its own training data than it deserves to be on new
data. The second, a leave one out method related to conformal
prediction, estimates uncertainty by repeatedly holding out one real
year at a time and measuring how wrong the model was on the year it
had not seen.

![E2 calibration](report/figures/06_e2_calibration.png)

Both methods were asked to produce an interval that should contain the
real outcome 80 percent of the time. Using price alone, the naive
method achieved 69.2 percent real coverage and the leave one out
method achieved 73.1 percent, both short of the target but the honest
method closer to it. Adding weather made both methods noticeably
worse, not better: coverage fell to 61.5 percent for the naive method
and 69.2 percent for the honest one. In one series, Rwanda's coffee
forecast, coverage collapsed from a perfect 100 percent to a
complete 0 percent once weather was added.

The explanation is not mysterious once the sample sizes are
considered. These series have only nine to twenty four real training
points. Adding a second feature means fitting an additional parameter
from that same small amount of data, and the extra uncertainty this
introduces is exactly the kind of thing that a training time estimate,
whether naive or leave one out, is poorly positioned to see coming.
This is the same underlying lesson as the first experiment, that
adding evidence is not free, showing up again through a completely
different mechanism: not a spurious trend and not an unpredictable
shock, but a straightforward cost of estimating more from less.

## Experiment 3: recognising when not to answer

The third experiment moves from forecasting to reasoning. A system
that always produces a confident answer, regardless of how good the
evidence behind that answer is, cannot be trusted the way a system
that knows when to hedge, ask for more information, or decline to
answer can be. A simple, rule based classifier was built to sort a
given piece of evidence into one of five states: sufficient,
insufficient, stale, conflicting, or semantically incompatible with
another source measuring something that looks similar but is not the
same thing. Each state maps to a corresponding action: sufficient
evidence leads to a recommendation, insufficient evidence leads to an
attempt to retrieve more and then an honest refusal if that attempt
fails, stale evidence leads to a recommendation with an explicit
caveat, and conflicting or incompatible evidence leads to an
investigation before any recommendation is made.

Every one of the five scenarios used to test this classifier was
grounded in something real, not invented for the purpose of the test.
Kenya coffee, with fresh, consistent, multi source evidence, was used
as the sufficient case. South Sudan coffee, with a genuine and
repeatedly confirmed absence of any real price data, was used as the
insufficient case. A real incident from earlier in this project, in
which a forecast was accidentally evaluated against a synthetic
baseline price roughly ten times higher than the real farm gate price
for the same commodity, was used as the conflicting case. Kenya's
trade data, genuinely fixed at 2023 and not obtainable any more
recently because that is the newest year Comtrade actually has, was
used as the stale case. Kenya coffee's real per tonne price compared
against its real total export value, two genuine numbers that measure
different things and could easily be confused for the same signal by
a system that did not check, was used as the semantically incompatible
case.

The classifier produced the expected action in all five cases. This is
a genuine result, but its scope should not be overstated. It
demonstrates that the decision rule is internally consistent and does
what it was designed to do against five known, carefully chosen
examples. It does not yet demonstrate that a real, learned or
language model driven agent would behave the same way when given the
same raw evidence and asked to decide for itself, and it does not yet
demonstrate that the rule generalises to cases it was not built
around. Both of those are real next steps, not settled questions.

## Experiment 4: a protocol, not a result

The fourth experiment concerns how real people make decisions when
given the same underlying evidence in different presentation formats:
raw numbers, a conventional chart, a bare model forecast, a forecast
accompanied by an explicit account of the evidence behind it, and a
forecast accompanied by an honest uncertainty interval. This is a
human subjects question. It has to be answered by observing real
people making real decisions, with informed consent and, where
applicable, institutional review. It cannot be answered by simulating
fictional participants and reporting the output as if it were data.
Doing so would not be a shortcut. It would be fabrication.

What exists instead is a complete, ready to run protocol, built using
real numbers this project already produced rather than invented ones.
The worked example concerns Kenya's coffee price in 2024. Using 2023's
real price of 4,391.70 dollars per tonne, the price only model
forecast 3,934.60 dollars and the price plus weather model forecast
4,253.00 dollars, both from Experiment 1. The leave one out method
from Experiment 2 produced an 80 percent interval of 2,383.30 to
5,486.00 dollars. The real 2024 outcome was 4,886.50 dollars.

![E4 scenario](report/figures/08_e4_scenario.png)

A participant shown only the bare point forecast would have seen a
number that looks precise and turned out to be wrong by up to 21
percent. A participant shown the same forecast together with its
honest interval would have seen that the real outcome, although above
the point estimate, still fell within a range the model itself
considered plausible. That distinction, between a number that looks
certain and a number that is honest about its own uncertainty, is
exactly what this experiment is designed to test with real
participants, once the protocol described in
[E4_study_protocol.md](E4_study_protocol.md) is actually run.

## The finding that connects everything

If this project has produced one result worth remembering above the
others, it is this. Adding a second source of evidence to a model is
not automatically an improvement, and when it fails to help, it fails
in genuinely different ways depending on the situation. In Experiment
1, a real global price shock overwhelmed any feature that could
plausibly have been built from local data. In the same experiment, a
real but unrelated long term trend quietly biased a different
forecast in the wrong direction. In Experiment 2, adding a feature
degraded the model's honesty about its own uncertainty, for a reason
that had nothing to do with either of the first two mechanisms. A
system that tracked only one blended accuracy number would have missed
all three of these, because they show up in different places and for
different reasons. Measuring forecasting accuracy, calibration, and
evidence quality as separate, independent questions, rather than
folding them into a single score, is what allowed each of these
mechanisms to be found and explained rather than averaged away.

## Honest limits of this work

Real time series data exists for three of the five modalities
collected. Trade remains a single snapshot, limited by Comtrade's real
rate quota, and text remains limited by the underlying API's own
reliability rather than by any decision made in this project. Only six
series have been tested in the forecasting and calibration
experiments, and South Sudan and Somalia are excluded from both
because there is no real price history to forecast against in either
country. Every forecast in this report is annual. The original
proposal's stated task was a thirty day forecast, which will require a
modality with that granularity that has not yet been built. No
systematic test of forecasting under artificially reduced data
availability, moving from complete data down to ten percent of it in
steps, has been run yet. Experiment 4 has no results, only a protocol,
because it correctly requires real people. Two of the five original
research hypotheses depend on work, evidence corruption scenarios and
the human study, that has not started yet.

None of this is hidden elsewhere in the project's records, and it is
repeated here deliberately. A report that only showed what worked
would misrepresent the actual state of the research.

---

The figures in this report were generated directly from the real
collected data by
[generate_report_figures.py](scripts/generate_report_figures.py),
which can be re-run at any time to regenerate them if the underlying
data or experiments change. The complete, unabridged chronological
record of this project, including every intermediate step, is kept in
[experiment_blueprint.md](experiment_blueprint.md).
