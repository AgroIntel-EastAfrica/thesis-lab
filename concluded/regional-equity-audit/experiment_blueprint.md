# Experiment: regional-equity-audit

- **Owner:**
- **Started:**
- **Status:** concluded, 2026-09-17 — reset into
  [`evidence-sparsity-reliability`](../../active_tests/evidence-sparsity-reliability/experiment_blueprint.md)
  (see the Concluding Note at the end of this file for why, and how this
  experiment's real findings carry forward rather than being discarded).
- **Paper:** Paper 14 — "Trustworthy Agricultural Intelligence Under
  Unequal Data Availability" (promoted 2026-09-12 from a sub-topic of
  Paper 13/Human-AI Decision Support into its own dedicated paper — same
  experiment, no new work, just its own paper bucket per the 15-paper
  publication roadmap revision. See `thesis-lab/PUBLICATION_ROADMAP.md`
  row 14 for the authoritative numbering — this line previously
  misnumbered itself "Paper 13" and misattributed the source as "Paper
  10," both corrected 2026-09-17).
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Section 6 ("Responsible and Trustworthy AI"):
  "A system that performs well for data-rich regions but poorly for
  marginalized areas could unintentionally amplify existing
  inequalities. Evaluation will therefore include performance across
  regions, commodities and levels of data availability."

## Objective

AgroIntel already covers all 8 EAC countries, but real data availability
is known to be uneven — this session's own work confirmed, for example,
that FAOSTAT producer-price data covers KE/TZ/RW/BI while UG/SS/SO/CD
fall back to `BASE_PRICES_USD` static estimates (see memory:
`project_faostat_prices`), and `_climate_alerts`'s NASA POWER checks only
run against the first two districts per country. This experiment
measures whether that real, known data-availability gap translates into
a real accuracy/service-quality gap for the countries with less real
data behind them — exactly the disparity the paper asks to check for,
not assume away.

## Hypothesis

Forecast accuracy (MAPE), recommendation confidence
(`RecommendationEngine`'s real `confidence` field), and evidence
sufficiency (this session's new `evidence_sufficient` gate) will all be
measurably worse, on average, for UG/SS/SO/CD (thinner real data — zero
real FAOSTAT PP rows per `project_faostat_prices`, falling back to
`BASE_PRICES_USD`) than for KE/TZ/RW/BI (richer real data — 574-1284
real FAOSTAT PP rows each) — and the gap will be largest specifically
for `evidence_sufficient`, since `supporting_signals` counts real pulse
signals, which are themselves downstream of the same uneven data
coverage.

*Correction 2026-09-13: an earlier draft of this hypothesis swapped UG
and BI into the wrong groups, contradicting this file's own Objective
section above (which had the grouping right). Fixed before running the
audit — the FAOSTAT sync results, not intuition, are the source of
truth for which group a country belongs to.*

## Core Variables

- **Held constant:** the evaluation window and metrics (MAPE, confidence,
  `evidence_sufficient` rate) — the same real fields already computed by
  production code, not new metrics invented for this audit.
- **Varied:** country grouping (data-rich vs. data-sparse, per the known
  FAOSTAT coverage split above) as the independent variable.
- **Real data:** this is a pure read/audit against real production
  outputs (forecast results, recommendation results) — no writes, no
  model changes, just measurement.

## Success Metrics

- Quantify the real gap, if any, in both raw numbers and relative terms
  (e.g. "SS's average recommendation confidence is X% lower than UG's").
- If a real, meaningful gap is confirmed, the honest next step is *not*
  to silently equalize the numbers (e.g. inflating confidence for
  data-sparse countries) but to make the disparity visible to the
  affected stakeholders — matching the paper's own framing that the goal
  is transparency about limitations, not hiding them.

## Results

**Run 1, 2026-09-13 (morning)** via `run_audit.py` — `forecast_evaluations`
was still empty (0 rows for all 8 countries), blocking the MAPE half. Root
cause traced and fixed the same day (see `forecast-confidence-calibration`'s
Results and `product/PRODUCTION_AUDIT.md`'s 2026-09-13 entries): no Celery
beat/worker had ever actually run against production. Stood up a local
worker + beat against the real production Supabase, then called
`update_price_forecasts`/`evaluate_forecast_accuracy` directly — real data
now exists, and the MAPE half below is a genuine, first-ever result, not
a placeholder.

**Run 2, 2026-09-13 (afternoon), after real data existed — both halves complete:**

**Forecast accuracy (MAPE) — real result, hypothesis REVERSED:**

| Country | n_evaluated | avg_mape | interval_coverage_rate |
|---|---|---|---|
| KE (rich) | 12 | 11.36% | 0.50 |
| TZ (rich) | 12 | 6.15% | 0.50 |
| RW (rich) | 12 | 12.25% | 0.42 |
| BI (rich) | 12 | 8.89% | 0.25 |
| UG (sparse) | 12 | 7.32% | 0.33 |
| SS (sparse) | 12 | 5.41% | 0.50 |
| SO (sparse) | 12 | 9.33% | 0.17 |
| CD (sparse) | 12 | 5.19% | 0.42 |
| **data-rich avg** | | **9.66%** | **0.42** |
| **data-sparse avg** | | **6.81%** | **0.35** |

MAPE is **reversed from the hypothesis**: data-sparse countries show
*lower* (better) MAPE than data-rich ones. Interval coverage is in the
hypothesized direction (data-rich higher) but both are far below the
80% the stated confidence implies — matching
`forecast-confidence-calibration`'s own finding of severe miscalibration
system-wide.

**Honest interpretation of the MAPE reversal**: this is very likely a
methodology artifact, not evidence the system serves data-sparse
countries better. `get_daily_price` for UG/SS/SO/CD walks from a
`BASE_PRICES_USD` synthetic anchor (no real FAOSTAT/EATTA/EAX/IMF data
reaches them) — a smoother, formula-generated random walk. Data-rich
countries' "actual_price" is real market data with genuine volatility.
Forecasting a synthetic random walk against itself is a fundamentally
easier task than forecasting a real market — so a *lower* MAPE for
data-sparse countries reflects an easier, less meaningful target, not
better real-world forecasting. This is itself a substantive finding:
naive MAPE comparison across data-rich/data-sparse countries is
apples-to-oranges as long as the data-sparse side's ground truth is
synthetic, and any paper using this result must state that caveat
explicitly rather than present the reversal as good news.

**Attempted a real fix for this caveat, 2026-09-13 — investigated,
partially resolved, one path stays genuinely blocked:**

- **`price_model.py`'s real priority chain** (`FAOSTAT → EATTA → EAX →
  IMF PCPS → Selina Wamucii → WFP DataBridges → BASE_PRICES_USD`) already
  has *two* real sources beyond FAOSTAT that explicitly target exactly
  this gap — checked both rather than assuming FAOSTAT is the only real
  option:
  - **Selina Wamucii** (`services/market/selina_wamucii_prices.py`): a
    real, credential-free scraper covering all 8 countries. Ran it live
    — found and fixed a genuine bug: its price-extraction regex silently
    fell back to grabbing the first stray 2-5 digit number on the page
    when the primary pattern didn't match, which was caching `2026.0` as
    the "price" for every commodity in every country (a copyright/date
    year, not a price). Root cause: selinawamucii.com's
    `/insights/prices/<country>/<commodity>/` pages no longer show a
    per-unit price at all — they now show aggregate national *export
    value* ("Uganda supplied maize worth 52.72m USD" - a yearly total).
    The site's content model changed since this integration was built;
    no regex fix can recover a per-unit price from a page that no longer
    has one. Removed the fallback so it now honestly returns "no data"
    instead of a fabricated number — a real correctness fix, but it
    does **not** close the data gap; Selina Wamucii cannot serve as a
    real price source for these countries as currently structured.
  - **WFP DataBridges** (`services/market/wfp_prices.py`): already coded
    and wired into the priority chain, and WFP explicitly tracks market
    prices in food-insecure/humanitarian-crisis contexts — a strong real
    candidate for exactly SS/SO. **Genuinely blocked**: `WFP_CLIENT_ID`/
    `WFP_CLIENT_SECRET` were never registered (only placeholders exist in
    `.env.example`) — registration is a human, external step
    (`wfp.economicanalysis@wfp.org`), not something fixable in code.
- **Net effect (before the credential test below)**: the MAPE-comparison
  caveat above still holds for UG/SS/SO/CD — no additional real
  market-data source became available today. The honest path to closing
  this gap for real is registering for WFP DataBridges credentials;
  that's a project-owner action item, not a coding one.

**Definitive live re-test, 2026-09-13, same day, with a real FAOSTAT
access token**: the project owner registered a free FAOSTAT account and
obtained a real, live Personal Access Token from FAO's own API Developer
Portal (`faostatservices.fao.org`), authenticated as `jericho555@yahoo.com`.
Used it to call the real PP (Producer Prices) endpoint directly for all
8 EAC countries via `sync_all_eac_countries` — not a cached/stale check,
a live, authenticated call made today:

| Country | Real rows returned | Synced (this run) |
|---|---|---|
| KE (rich) | 1,284 | 27 |
| RW (rich) | 824 | 21 |
| BI (rich) | 574 | 18 |
| TZ (rich) | 274 | 20 |
| UG (sparse) | **0** | 0 |
| SS (sparse) | **0** | 0 |
| SO (sparse) | **0** | 0 |
| CD (sparse) | **0** | 0 |

This **settles the question definitively**: it was never an
authentication wall hiding real data — FAOSTAT's own database has zero
Producer Price records for UG/SS/SO/CD, full stop, confirmed live with
valid credentials. The counts for KE/TZ/RW/BI exactly match the
2026-07-26 memory record, confirming FAO's real coverage has been
stable for ~2 months, not a fluke of that one earlier sync. The
data-rich countries' Redis price cache has been refreshed with this
real, live data as a side effect of the test.

**Real, honest conclusion for this thread**: the equity gap this
experiment set out to check for is not a measurement artifact or an
auth-configuration oversight — it is a genuine absence of data in FAO's
own dataset for these 4 countries.

**A 4th real source checked, 2026-09-13, same day — UN Comtrade
(international trade flows, `clients/comtrade.py`)**: not previously
wired into `price_model.py`'s chain at all. Investigated as an
alternative real signal (import/export trade value, a different kind
of data than domestic producer prices). The project owner's existing
`COMTRADE_API_KEY` was rejected (401) on first check; regenerated the
key via the UN Comtrade developer portal, which resolved the auth
error, then hit a `403 Out of call volume quota` wall on the very next
call.

**Resolved definitively, 2026-09-14, once the quota reset**: real,
authenticated, `200 OK` calls (not errors) for South Sudan and Somalia
— maize imports specifically, and then `TOTAL` (every commodity, every
trading partner combined) imports for both countries, 2022 and 2023 —
all returned **zero rows**. This isn't a maize-specific or single-year
gap: these two countries report *no* import trade data to UN Comtrade
at all for the years checked, independent of commodity. Most likely
cause: no functioning national statistics office submitting data to UN
systems, consistent with both countries' real conflict/state-fragility
context — a genuine, structural absence, not a query or credential
problem.

**Status of all 4 real sources checked for UG/SS/SO/CD:**
1. FAOSTAT — confirmed, definitively, zero real rows (see above).
2. Selina Wamucii — site's content model changed, no per-unit price
   recoverable regardless of credentials.
3. WFP DataBridges — blocked on registration (external, human step).
4. UN Comtrade — confirmed, definitively, zero real rows for SS/SO
   (checked directly; UG/CD not yet individually re-verified but expected
   to match given the same underlying cause).

**This is the strongest evidence yet for the equity gap being real and
structural**: two independent, major international statistical systems
(FAO and UN Comtrade) both report zero real data for South Sudan and
Somalia — not a coincidence isolated to one data provider's coverage
choices, but a consistent pattern across systems, most plausibly
reflecting the countries' own limited capacity to generate and submit
official statistics. WFP DataBridges (a system specifically designed to
monitor markets *despite* this kind of gap, via field data collection
rather than official government submissions) remains the one real,
unresolved candidate — still blocked on registration.

**RecommendationEngine (confidence, evidence_sufficient, supporting_signals) — real, live comparison:**

Two live runs, hours apart (real-time pulse signals shift between calls,
so exact counts differ — direction of the gap is what matters):

| Country | n_recs (run 1 / run 2) | avg_confidence (run 2) | evidence_sufficient_rate (run 2) | avg_supporting_signals (run 2) |
|---|---|---|---|---|
| KE (rich) | 21 / 20 | 83.75 | 0.400 | 1.70 |
| TZ (rich) | 24 / 26 | 86.35 | 0.308 | 1.54 |
| RW (rich) | 13 / 15 | 80.00 | 0.533 | 1.93 |
| BI (rich) | 17 / 15 | 80.00 | 0.533 | 1.93 |
| UG (sparse) | 24 / 24 | 85.63 | 0.333 | 1.58 |
| SS (sparse) | 16 / 15 | 80.00 | 0.533 | 1.93 |
| SO (sparse) | 11 / 12 | 76.25 | 0.667 | 2.17 |
| CD (sparse) | 18 / 17 | 81.76 | 0.471 | 1.82 |
| **data-rich avg** | | **82.52** | **0.444** | **1.78** |
| **data-sparse avg** | | **80.91** | **0.501** | **1.88** |

Both runs agree on direction: confidence gap in the hypothesized
direction (small, ~1.5-2 points); `evidence_sufficient_rate` and
`avg_supporting_signals` both reversed both times — this isn't run-to-run
noise, it's a consistent pattern across two independent live calls.

**Hypothesis only partially confirmed, and weakly:**
- `avg_confidence`: data-rich is higher by ~1.5 points (82.06 vs 80.59) —
  in the hypothesized direction, but a small gap relative to the
  per-country spread (74-85).
- `evidence_sufficient_rate` and `avg_supporting_signals`: **both
  reversed** — data-sparse countries show a *higher* rate/average than
  data-rich ones, the opposite of the hypothesis.

**Honest interpretation:** `RecommendationEngine`'s pulse-signal layer
(`IntelligencePulseService`, `ArbitrageRadarService`, etc.) draws on
real-time signals (news, health scores, arbitrage spreads) that aren't
the same data source distinction driving the FAOSTAT price-coverage
gap — so this layer doesn't inherit that specific gap the way price
forecasting would. The equity concern the concept paper raises is real
at the *price/forecast* layer (confirmed structurally above, even
though it can't be measured numerically yet) but is **not confirmed** at
the *recommendation* layer with current data. Don't extrapolate one
finding to the other — they measure different things, and this run
shows they disagree.

**Status: both halves now have real, complete results.** Neither confirms
the hypothesis cleanly:
- `RecommendationEngine`: not confirmed (reversed on 2 of 3 metrics,
  consistently across two independent runs).
- Forecast MAPE: apparently reversed, but confounded by data-sparse
  countries forecasting a synthetic ground truth — not a clean test of
  the hypothesis as stated.
- Interval coverage: weakly confirmed (data-rich higher), but both
  groups are far below the stated confidence level regardless of tier —
  the calibration problem (`forecast-confidence-calibration`) dominates
  over any equity gap at this layer.

**Phase 1 (this document) is ready to move to `thesis-lab/concluded/` once
Phase 2 below is scoped** — the honest overall finding so far is that
AgroIntel's real equity gap (confirmed to exist structurally: FAOSTAT
coverage genuinely differs by country) does **not** cleanly show up as a
service-quality gap in either of the two user-facing layers tested, once
methodology confounds are accounted for. That's a legitimate, if
unglamorous, result — but it is a *partial* answer to Paper 14's real
scope, not the full one. See below.

## Scope completeness check, 2026-09-14

Paper 14's original framing (per the adopted 15-paper reorganization
proposal, "E. Trustworthy AI") asks whether AI reliability changes
according to **geography, commodity, market, data availability, source
coverage**, investigated via **uncertainty, calibration, provenance,
transparency, abstention, subgroup performance**. Checked Phase 1's real
coverage against this full list honestly, rather than assuming "we wrote
an experiment about this" means "we covered it":

**Genuinely covered by Phase 1:**
- **geography** — the entire country-tier comparison above.
- **data availability** / **source coverage** — the FAOSTAT/Selina
  Wamucii/WFP/Comtrade investigation.
- **uncertainty** / **calibration** — the centerpiece finding (38.5%
  real coverage vs. ~80% stated).
- **abstention** — `evidence_sufficient_rate` /
  `_apply_evidence_gate`, this session's own real abstention mechanism.
- **subgroup performance** — the country-tier breakdown *is* this axis.

**Genuinely NOT covered — real, unscoped gaps, not just "waiting on
better data":**
- **commodity** — everything measured so far is a country-level
  aggregate across commodities. Whether reliability varies *by
  commodity* (e.g. is coffee forecasting more equitable across
  countries than maize forecasting?) has not been tested at all.
- **market** (geography *level*, not country) — `services/forecasting/price.py`
  has three real, distinct layers (LOCAL/XGBoost, SUB_NATIONAL/Prophet,
  NATIONAL/ensemble). Phase 1 only measured NATIONAL-level output;
  whether the equity picture differs at LOCAL or SUB_NATIONAL level is
  unknown.
- **provenance** — this codebase already has real `data_source`/
  `price_source`/`data_confidence` disclosure fields (from an earlier
  "stale data presented as live" audit). Whether that disclosure is
  itself equitable — i.e. does a data-sparse country's response
  honestly label the `BASE_PRICES_USD` fallback as clearly as a
  data-rich country's response labels its real FAOSTAT source? — has
  never been directly audited.
- **transparency** — the same gap as provenance, as its own axis:
  does the *user-facing* framing (not just an internal field) disclose
  the difference in evidence quality between tiers?

**Phase 2 (not started, blocked on real data)**: once WFP DataBridges
credentials or a working Comtrade quota provide real market prices for
UG/SS/SO/CD (see above), re-run this experiment properly scoped to all
six real dimensions — not just re-running the country-tier comparison
with better data, but adding commodity-level, geography-level, and
provenance/transparency audits that Phase 1 never attempted. Track this
as the actual reopen criterion, not "when the data shows up."

Correction, 2026-09-14: the provenance/transparency axis turned out to
be independently testable without WFP or Comtrade — see below. Only the
commodity-level and market/geography-level axes, and the
data-sparse-country forecast-quality comparison specifically, remain
genuinely blocked on real ground truth.

## Phase 2a: provenance & transparency audit, 2026-09-14

Tested whether the system's disclosure of *which* data backs a given
price is itself equitable across country tiers — both the internal
`price_source` field (`services/market/price_model.py`) and what the
dashboard actually shows a user.

**The disclosure design itself is honest, by inspection:**
`_compute_daily_price` tags every price with a specific `price_source`
(`faostat` / `eatta` / `eax` / `imf_pcps` / `selina_wamucii` / `wfp` /
`baseline`), not a generic "real vs. fake" boolean. The dashboard
(`CommoditiesPage.tsx`, `ForecastingPage.tsx`, `DashboardPage.tsx`,
`CommodityDetailPage.tsx`) renders a distinct, color-coded, localized
(en/sw/fr) badge per source, plus an aggregate summary line per
country ("Prices: 4 FAOSTAT · 28 Modeled — each card's own source
badge shows which applies to it"). A `baseline` price is explicitly
labeled "Modeled" (`t('commodities_page.price_source_modeled')`), not
silently presented as live. This is a real, working disclosure
mechanism, not a stub.

**One structural gap found**: the top-level response `meta.data_source`
field (`DATA_SOURCE_LABEL` in `price_model.py`) is a single static
string describing the *whole system's* methodology ("FAOSTAT... where
available... otherwise anchored to realistic EAC baselines"),
identical on every response regardless of which source that specific
response actually used. It's truthful as a system description but
isn't response-specific — a South Sudan response where every item is
`baseline` gets the same top-level string as a Kenya response that's
mostly `faostat`. The per-item badges (above) are what actually carry
the honest signal; the top-level meta field doesn't.

**A second, more consequential structural finding**: IMF PCPS
(`services/market/imf_prices.py`) is a *global* commodity benchmark —
the same number is written to all 8 countries' cache keys by design
(confirmed in code and live: `IMF_API_KEY` is configured in `.env` but
a live cache check on 2026-09-14 found zero synced PCPS prices for any
commodity/country — the source is configured but currently inert, so
this doesn't affect any live response today). If it starts syncing,
it would be tagged and badged identically to FAOSTAT ("real, live
source") despite carrying no country-specific signal at all — a real
equity distinction (country-specific-real vs. generic-real) the
current one-tier badge system doesn't encode. Worth a real fix if/when
IMF PCPS starts actually syncing; not urgent today since it's inert.

**Live incident found and fixed during this audit**: a direct,
read-only check of the real production price model (`get_daily_price`)
for South Sudan, Somalia, and Uganda maize found `price_source:
"selina_wamucii"` with prices of **$2,090 / $1,977 / $2,030 per MT** —
4-7x the intended baseline (SS $420, SO $380, UG $280) and badged with
the same "real, live source" treatment as FAOSTAT. Root cause: this
session's earlier fix to `services/market/selina_wamucii_prices.py`
(removing a fallback regex that was caching a stray copyright-year
digit, `2026.0`, as a fake price) stopped new fabrication but never
purged the already-cached bad values, which carry an 8-day Redis TTL.
Confirmed via direct cache inspection: 56 `selina_price:*` keys held
the stale `2026.0`-derived fabricated price across 8 commodities × 7
countries (every country except DRC, which had already fallen through
to `baseline`). Purged all 56 stale `selina_price:*` keys plus 3
downstream `price:*` result-cache keys (with explicit user approval
for both, since this touches live production Redis); re-verified
end-to-end afterward — SS/SO/UG maize now correctly returns
`price_source: "baseline"` at $433/$371/$281, matching intent.

**Why this matters for the equity claim, beyond being a bug**: until
this fix, the system wasn't just *missing* real data for South Sudan,
Somalia, and Uganda (the already-established finding) — it was
actively mislabeling fabricated data as equally trustworthy as Kenya's
real FAOSTAT data, for the exact countries this whole study is about.
An honest "Modeled" label on a wrong-but-transparent baseline is a
data-availability gap; a "real source" badge on fabricated data is a
transparency failure layered on top of it — arguably a worse form of
inequity, since it actively misleads rather than honestly discloses.
This is now fixed and verified live.

**Provenance/transparency verdict**: the disclosure *design* is sound
and equitable (same badge logic, same languages, same granularity,
regardless of country tier) — no fix needed there. The *data behind*
that design had a real, live equity-relevant bug, now fixed. This axis
is genuinely covered as of 2026-09-14, without needing WFP or Comtrade.

## Phase 2b: commodity-level audit, 2026-09-14

Tested whether forecast reliability varies *by commodity*, independent
of country — the other unscoped gap from the scope-completeness check.
Reused the real `forecast_evaluations` rows already behind the
forecast-confidence-calibration finding (same table, same n=96,
`thesis-lab/active_tests/regional-equity-audit/scripts/audit_by_commodity.py`),
re-sliced by commodity instead of country. No new data source needed —
all 8 countries are represented for every commodity, so this slice
isn't confounded by the country-tier gap the way the MAPE comparison
in Phase 1 was.

**Raw result** (avg MAPE and interval coverage per commodity, n=8
countries each):

```
commodity           n  countries  avg_mape  coverage  w/bounds
maize               8          8     18.35     0.000         8
cassava              8          8     17.39     0.500         8
tea                  8          8      9.30     0.375         8
sweet_potatoes       8          8      7.88     0.125         8
sesame               8          8      7.41     0.375         8
wheat                8          8      7.14     0.375         8
groundnuts           8          8      5.90     0.375         8
soybeans             8          8      5.73     0.500         8
rice                 8          8      5.18     0.375         8
coffee               8          8      5.04     0.625         8
beans                8          8      4.81     0.625         8
sorghum              8          8      4.70     0.375         8
```

**Real confound found before trusting this table at face value**:
maize's outlier status (worst MAPE *and* zero interval coverage) traced
directly to the same Selina Wamucii cache bug fixed in Phase 2a above,
not a genuine forecasting weakness. Confirmed precisely by reading
`services/forecasting/price.py`'s `get_price_forecast`: the forecaster
trains only on `get_price_history()` (line 512), which is purely
synthetic and anchors to the *correct* `BASE_PRICES_USD` baseline —
untouched by the cache bug — so `predicted_price` for SS/SO/UG maize
was fine. But `apps/workers/forecasting.py::evaluate_forecast_accuracy`
fills in `actual_price` via a direct call to `get_daily_price()` (line
223) — the exact function that was serving the fabricated ~$2,000+/MT
value for SS/SO/UG maize at whatever point these rows were evaluated.
A correct forecast compared against a fabricated "actual" produces
exactly this signature: enormous MAPE, zero coverage. This is a
measurement artifact, not evidence maize is hard to forecast.

**Scope of the confound**: the Selina cache bug (Phase 2a) affected 8
commodities — onions, maize, sorghum, rice, cassava, tomatoes, beans,
coffee — of which 6 overlap this table (maize, cassava, rice, sorghum,
beans, coffee). Only SS/SO/UG rows *within* those 6 commodities could
be affected (KE/TZ/RW/BI have FAOSTAT; CD falls through to the honestly-
labeled baseline) — at most 3 of each commodity's 8 country-rows. Maize
is confirmed contaminated (directly traced above). Cassava, rice,
sorghum, beans, and coffee are *unverified* — plausible but not
individually confirmed the way maize was, since coffee/beans/sorghum's
good calibration numbers argue against uniform contamination. Tea,
sweet_potatoes, sesame, wheat, groundnuts, and soybeans were **not** in
the Selina stale-key list at all — genuinely clean data, unaffected by
this bug.

**Trustworthy preliminary finding, restricted to the 6 clean
commodities**: sweet_potatoes has the worst interval coverage (12.5%,
1/8) of the clean set — worse than the 38.5% system-wide calibration
average — while tea has the highest MAPE (9.3%) among them. Soybeans
is the best-calibrated clean commodity (50% coverage, still well below
the stated ~80%). Maize and cassava's numbers should be treated as
unreliable until re-measured post-fix.

**Next step to close this properly**: re-run `update_price_forecasts` +
`evaluate_forecast_accuracy` now that the Selina cache is clean (same
method used to produce the original calibration number — stand up a
local worker against real Supabase and call both tasks directly) to
get a trustworthy maize/cassava/rice/sorghum/beans/coffee reading, then
re-run `audit_by_commodity.py`. Not done yet as part of this pass —
flagging as the honest next action rather than presenting the
contaminated numbers as final.

**Same n=96/single-day caveat as the calibration experiment applies**:
one row per (country, commodity) pair, not a longitudinal sample —
directionally informative, not a stable estimate.

## Post-fix verification + a bigger real finding, 2026-09-15

Set out to do the "next step" flagged above — re-run the evaluation now
that the Selina cache is clean — and confirmed the cache-bug fix held:
called `evaluate_forecast_accuracy` directly against real production
Supabase. SS/SO/UG maize now show realistic, sane values (e.g. SS:
predicted $383.91 vs actual $419.34; UG: predicted $304.67 vs actual
$276.42) — no trace of the ~$2,000+/MT fabricated figures. The fix is
confirmed durable, not just a one-time patch.

**Important scoping note**: this batch (`target_date=2026-09-15`) turned
out to be day+2 of a `horizon_days=30` batch generated 2026-09-13 — a
*different* forecast vintage than whatever produced the original
38.5%/8.24% calibration figure, not a clean "before vs after" pair.
Its aggregate numbers (96 evaluated, calibration 17.71%, MAPE 62.08%)
should **not** be read as "the fix made things worse" — they aren't
comparable to the original figure at all. Recorded here for honesty,
not presented as a fix-quality signal.

**But investigating that jump surfaced a real, well-evidenced, bigger
finding**: two commodities — coffee and tea — showed extreme,
commodity-specific MAPE (243% and 272% respectively) in this batch,
concentrated in exactly three countries: Rwanda, Burundi, and Kenya.
Traced to source:

```
                 BASE_PRICES_USD        real FAOSTAT       ratio
coffee  BI       $2,600 (guessed)   vs  ~$271-275/MT        ~9.5x over
coffee  RW       $2,800 (guessed)   vs  ~$277-279/MT        ~10x over
coffee  KE       $2,500 (guessed)   vs  ~$4,886-4,953/MT    ~2x under
tea     BI       $1,750 (guessed)   vs  $136.66/MT          ~13x over
tea     RW       $1,800 (guessed)   vs  $180.15/MT          ~10x over
tea     KE       $1,400 (guessed)   vs  $2,194.40/MT        ~1.6x under
maize   BI         $360 (guessed)   vs  ~$438.90/MT         ~1.2x under (for comparison)
```

Mechanism, confirmed by reading `services/forecasting/price.py`'s
`get_price_forecast`: `PriceForecaster.fit()` trains *only* on
`get_price_history()`, which is purely synthetic and anchors to
`BASE_PRICES_USD` — a hand-guessed "realistic EAC wholesale price"
table (per its own docstring) that has apparently **never been
cross-checked against real data**. `evaluate_forecast_accuracy`'s
`actual_price`, by contrast, comes from `get_daily_price()`, which
prefers real FAOSTAT data whenever it exists. So wherever FAOSTAT
happens to have real coverage for a commodity (coffee and tea for
KE/RW/BI specifically — TZ and the data-sparse countries have no real
FAOSTAT coffee/tea and show close predicted-vs-actual agreement,
confirming the mechanism), the forecast is being evaluated against a
real price the model was never trained anywhere near, because its
synthetic training anchor for that commodity/country was never
validated and turns out to be off by up to an order of magnitude.

**Why this matters more than the original equity hypothesis**: this is
the *inverse* of what Paper 14 set out to test. The concern was
data-sparse countries getting worse service from missing real data.
What's actually been found, now three times over (RecommendationEngine
comparison in Phase 1, and now this), is that in places real data
*does* exist, it can expose the synthetic fallback as badly wrong —
making data-rich countries look worse on this specific metric, for a
reason that has nothing to do with real-world forecasting difficulty
and everything to do with an unvalidated hardcoded table.

**Fixed properly, 2026-09-15** (not a data patch — a mechanism fix):
rather than hand-editing `BASE_PRICES_USD`'s coffee/tea numbers (which
would just be a new set of unvalidated guesses, and wouldn't help any
other commodity/country pair with the same latent problem), changed
the actual mechanism. Added `get_real_anchor_price()` to
`services/market/price_model.py` — reuses the exact same real-source
priority chain `_compute_daily_price` already resolves (FAOSTAT → EATTA
→ EAX → IMF PCPS → Selina Wamucii → WFP), returning `None` if nothing
real exists rather than silently falling through to the hardcoded
baseline. `get_price_history()` now accepts an optional `real_anchor`
parameter — when given, the deterministic backfill walk starts from
the real price instead of the `BASE_PRICES_USD` guess (day-to-day
movement is still a simulated walk either way — FAOSTAT gives one
current figure, not a real daily series — this only fixes the
*starting point*). `services/forecasting/price.py`'s
`get_price_forecast` now calls `get_real_anchor_price()` before
training and passes it through. All other ~15 existing callers of
`get_price_history()` (dashboard sparklines, AI assistant, momentum/
anomaly detectors, opportunity engine, etc.) are unaffected —
`real_anchor` is keyword-only and defaults to `None`, so their
behavior is byte-for-byte unchanged.

**Verified live, end-to-end**: called `forecast_country_commodity`
directly for the exact pairs that exposed the bug —

```
BI coffee: real_anchor=270.90   forecast[0]=273.85   (was anchored ~$2,600)
RW coffee: real_anchor=277.40   forecast[0]=265.84   (was anchored ~$2,800)
KE coffee: real_anchor=4886.50  forecast[0]=4654.84  (was anchored ~$2,500)
BI tea:    real_anchor=135.50   forecast[0]=125.51   (was anchored ~$1,750)
RW tea:    real_anchor=179.40   forecast[0]=182.80   (was anchored ~$1,800)
```

Every forecast now lands within a few percent of the real anchor,
instead of being off by an order of magnitude. Existing test suites
(`test_price_model.py`, `test_workers_forecasting.py`,
`test_forecasting_price.py`, `test_price_forecasting.py`) all still
pass unchanged. `ruff check` clean on both modified files.

**Scope note**: this fixes the verified path
(`forecast_country_commodity`, what `update_price_forecasts` actually
calls). `services/forecasting/base.py` and `services/forecasting/
ensemble.py` call `get_price_history()` the same unanchored way and
likely have the identical latent issue, but that wasn't independently
verified the way price.py's path was — flagged here rather than
assumed and fixed blind. `BASE_PRICES_USD` itself is untouched and
still the honest, disclosed fallback for the 4 data-sparse countries
and any commodity with no real coverage at all — this fix only changes
what happens when real data *does* exist and was previously being
ignored.

**Cross-reference**: this also bears directly on the
forecast-confidence-calibration experiment's (Paper 5) hypothesis —
noted there.

## Phase 2c: market / geography-level audit, 2026-09-15

Closes the last unscoped axis from the "Scope completeness check"
section: does the equity picture differ at LOCAL (XGBoost) vs
SUB_NATIONAL (Prophet) vs NATIONAL (ensemble) — the three real forecaster
layers `services/forecasting/price.py` implements — given Phase 1 only
ever exercised NATIONAL (`forecast_country_commodity` hardcodes
`GeographyLevel.NATIONAL`). New script:
`thesis-lab/active_tests/regional-equity-audit/scripts/audit_geography_levels.py`.

**Real bug found before any equity comparison was possible**: calling
`PriceForecaster.forecast_price()` with `GeographyLevel.LOCAL` or
`GeographyLevel.SUB_NATIONAL` directly — the natural, first-class enum
values, used exactly this way elsewhere in the codebase
(`services/opportunity_engine/scoring.py`, `ml/evaluation/*`) — silently
returned the **NATIONAL** ensemble forecast instead, identical
`model_type`, confidence, and value every time. Traced to
`services/forecasting/base.py`'s `get_layer_config`: its `layer_mapping`
dict had entries for the more granular `FARM`/`VILLAGE`/`CITY` → LOCAL
and `DISTRICT`/`REGION` → SUB_NATIONAL, but no entry for the `LOCAL` and
`SUB_NATIONAL` enum values themselves — both fell through to the
`"NATIONAL"` default. An existing test
(`test_forecasting_base.py::TestGetLayerConfig::test_unknown_defaults_to_national`)
had actually codified this exact bug as intended behavior, asserting
`get_layer_config(GeographyLevel.LOCAL).layer == "NATIONAL"` — which is
why it shipped untested against the direct-name case.

**Fixed**: added `"LOCAL": "LOCAL"` and `"SUB_NATIONAL": "SUB_NATIONAL"`
to `layer_mapping` (existing FARM/VILLAGE/DISTRICT/REGION routes
untouched). Updated the misleading test to assert the correct mapping,
added direct-value coverage for both, and repointed the "unknown
defaults to national" case at a genuinely unmapped value
(`GeographyLevel.SUPRA_NATIONAL`). Verified: the audit script now
returns three genuinely distinct layers (`xgboost`/`prophet`/`ensemble`)
instead of three copies of the same one. Full relevant test sweep (12
files, 520 tests) passes. **Live production blast radius**: none —
`forecast_country_commodity` (what `update_price_forecasts` actually
calls) hardcodes `GeographyLevel.NATIONAL` directly and was never
affected; this bug only mattered to a caller explicitly requesting
LOCAL/SUB_NATIONAL, which nothing production-facing currently does. Real
nonetheless — it defeated the layer architecture for exactly the two
enum values named after it, and blocked this audit from being possible
at all.

**Once routed correctly, the real geography-level comparison** (maize,
all 8 countries, with the 2026-09-15 real-anchor fix applied so results
reflect the current, fixed forecaster):

```
             LOCAL (xgboost)   SUB_NATIONAL (prophet)   NATIONAL (ensemble)
KE (rich)    conf 0.83          conf 0.80                 conf 0.812
TZ (rich)    conf 0.83          conf 0.80                 conf 0.812
RW (rich)    conf 0.83          conf 0.80                 conf 0.812
BI (rich)    conf 0.83          conf 0.80                 conf 0.812
UG (sparse)  conf 0.83          conf 0.80                 conf 0.812
SS (sparse)  conf 0.83          conf 0.80                 conf 0.812
SO (sparse)  conf 0.83          conf 0.80                 conf 0.812
CD (sparse)  conf 0.83          conf 0.80                 conf 0.812
```

**Finding**: confidence is a flat, hand-set constant per layer — 0.83
(LOCAL/XGBoost's horizon-1 value), 0.80 (SUB_NATIONAL/Prophet), 0.812
(NATIONAL, the documented 60/40 Prophet/XGBoost blend: 0.80×0.6 +
0.83×0.4 = 0.812, confirming these are the real formulas, not
approximations) — **identical across every country regardless of data
tier, at every geography level**. This closes the "market" axis
cleanly: the equity picture does *not* differ by geography level,
because none of the three layers' confidence values are sensitive to
country or data availability at all — the same root cause the
forecast-confidence-calibration experiment already found at the
NATIONAL layer (hand-set constants, not data-derived) turns out to hold
identically at LOCAL and SUB_NATIONAL too. Predicted *values* (not
shown above) stay close to each country's real-or-baseline anchor at
every layer, consistent with the 2026-09-15 real-anchor fix now
applying uniformly across all three forecasters (they all train on the
same `historical_data`).

**Geography/market axis verdict**: genuinely covered as of 2026-09-15.
No equity disparity found or introduced by geography level — but that's
because the confidence mechanism is uniformly disconnected from both
country and level, not because it's uniformly well-calibrated.

## Exploratory Data Analysis, 2026-09-15

All numbers below are live, queried directly against real production
Supabase/Redis on 2026-09-15, full pagination (not a partial page) where
row counts matter.

**1. `forecast_evaluations` (the calibration/MAPE dataset)**

```
Total rows:              2,880
Generation events:       1 (single batch, forecast_generated_at = 2026-09-13)
Horizon:                 30 days (every row), horizon_days=30
Countries x commodities: 8 x 12 = 96 pairs, x 30 target dates = 2,880 rows exactly
Target date range:       2026-09-13 to 2026-10-12 (30 consecutive days)
Rows per target date:    96 (perfectly balanced, no gaps)
predicted_lower/upper:   2,880 / 2,880 (100% - every row is calibration-checkable)
Evaluated so far:        192 / 2,880 (6.7%) - only 2 of 30 target dates have
                          arrived and been evaluated (2026-09-13: 96 rows,
                          2026-09-15: 96 rows); the other 28 days' worth
                          (2,688 rows) remain correctly pending until their
                          target_date naturally arrives, or evaluate_
                          forecast_accuracy is triggered manually per day.
```

This single-batch structure is why every calibration/MAPE number in this
document (the original 38.5%/8.24% figure, the day+2 17.71%/62.08%
figure, the commodity breakdown) is n=96 and single-vintage — not yet a
longitudinal sample. It also explains a subtlety worth being explicit
about: the two evaluated slices are *the same forecast batch* observed
2 days apart, not two independent experiments, which is why they aren't
directly comparable as "before/after" for anything except the specific
SS/SO/UG cache-bug cells that were individually traced and confirmed.

**2. Live price-model coverage matrix (real vs. synthetic, right now)**

Queried `get_daily_price()` for all 8 countries x all 51 commodities in
`BASE_PRICES_USD` (408 pairs) — this is what actually decides
`price_source` for every price the app ever serves:

```
                 baseline (synthetic)   faostat (real)   real coverage
UG (sparse)      51 / 51 (100%)         0 / 51 (0%)      0%
SS (sparse)      51 / 51 (100%)         0 / 51 (0%)      0%
SO (sparse)      51 / 51 (100%)         0 / 51 (0%)      0%
CD (sparse)      51 / 51 (100%)         0 / 51 (0%)      0%
KE (rich)        24 / 51 (47%)          27 / 51 (53%)    53%
TZ (rich)        31 / 51 (61%)          20 / 51 (39%)    39%
RW (rich)        30 / 51 (59%)          21 / 51 (41%)    41%
BI (rich)        33 / 51 (65%)          18 / 51 (35%)    35%
─────────────────────────────────────────────────────────────
Total (408 pairs) 322 (78.9%)           86 (21.1%)       21.1%
```

Only two source types appear anywhere in the live matrix: `faostat` and
`baseline`. EATTA, EAX, IMF PCPS, Selina Wamucii, and WFP — the other 5
links in the priority chain `_compute_daily_price` resolves — currently
contribute **zero** rows system-wide (confirmed separately this session:
IMF has a real key configured but has never synced; Selina's fallback
was the fabricated-data bug now fixed and its real path recovers no
data at all post-fix; EATTA/EAX/WFP are unsynced/uncredentialed). FAOSTAT
is, right now, the *only* functioning real data source in the entire
system. This is the single most load-bearing fact behind every other
finding in this document: the "data-rich vs data-sparse" split is not
approximate or historical — it is, at this exact moment, a 100%-vs-0%
real/synthetic split with nothing in between.

**3. FAOSTAT raw coverage** (source table, `faostat_prices.py`, confirmed
live 2026-09-13/14): Kenya 1,284 rows, Rwanda 824, Burundi 574, Tanzania
274, across ~32 commodities each, annual producer prices going back
multiple years per commodity. Uganda, South Sudan, Somalia, DRC: 0 rows,
confirmed via authenticated live API calls, not a credentials gap.

**4. UN Comtrade** (trade-flow cross-check): authenticated `200 OK`
responses for South Sudan and Somalia, `TOTAL` (every commodity, every
partner), 2022 and 2023 — 0 rows both years, both countries. A second,
independent international system agreeing with FAOSTAT's zero.

**5. `RecommendationEngine` live output** (n=139-149 recommendations
across two independent live runs, all 8 countries): confidence range
76.25-86.35 across countries, no clean split by data tier (data-rich avg
82.52 vs data-sparse avg 80.91 — a ~1.6-point gap, small relative to the
74-85 per-country spread); `evidence_sufficient_rate` 0.308-0.667 and
`avg_supporting_signals` 1.54-2.17, both *reversed* from the data-tier
hypothesis (data-sparse countries score higher on both).

**6. The Selina Wamucii incident, quantified**: 56 stale cache keys
(8 commodities x up to 7 countries) held a fabricated price derived from
a misread copyright-year digit, live in production for at least several
hours to potentially days before being caught and purged during this
audit — concrete evidence that a provenance/transparency bug can sit
undetected in a production system until an audit specifically goes
looking, not merely a theoretical risk.

## Complete answer: the 11-dimension framework, 2026-09-15

The original brief asked whether AI reliability changes according to
**geography, commodity, market, data availability, source coverage**,
investigated via **uncertainty, calibration, provenance, transparency,
abstention, subgroup performance**. All 11 are now genuinely answered
with real evidence — not assumed covered because a folder exists.

| # | Dimension | Answer | Evidence |
|---|---|---|---|
| 1 | **Geography** (country) | Real gap exists in *data*, but does **not** cleanly translate into a service-quality gap in either user-facing layer tested. FAOSTAT coverage is a genuine 0%-vs-35-53% split (EDA §2); `RecommendationEngine` confidence differs by only ~1.6 pts and reverses on 2 of 3 metrics. | Phase 1 (country-tier comparison), EDA §2/5 |
| 2 | **Commodity** | Reliability varies sharply by commodity, but the raw ranking was itself contaminated by the Selina cache bug for 6 of 12 commodities. On the 6 clean commodities: sweet potatoes worst-calibrated (12.5% coverage), soybeans best (50%) — both far below the stated ~80%. | Phase 2b |
| 3 | **Market** (geography level: LOCAL/SUB_NATIONAL/NATIONAL) | No equity disparity by level — but only because a real bug (`GeographyLevel.LOCAL`/`.SUB_NATIONAL` silently routing to NATIONAL) made the other two layers unreachable at all until fixed. Once fixed: confidence is a flat constant per layer (0.83/0.80/0.812), identical across every country regardless of tier, at every level. | Phase 2c |
| 4 | **Data availability** | Quantified precisely: 21.1% real coverage system-wide, 100%-vs-0% split by country tier, confirmed via live, authenticated calls, not inference. | EDA §2/3 |
| 5 | **Source coverage** | FAOSTAT is the *only* functioning real source right now (0 of 408 live pairs come from EATTA/EAX/IMF/Selina/WFP). Comtrade independently confirms the same zero for SS/SO on a different data type (trade flows, not prices) — cross-system agreement, not one provider's coverage choice. | EDA §2/4, Comtrade investigation |
| 6 | **Uncertainty** | The system reports a number (`ForecastPoint.confidence`) but it is a hand-set constant per model layer (0.65/0.70/0.80/0.85-decay/0.812), never derived from historical accuracy — confirmed identical at all 3 geography levels (Phase 2c) and all 8 countries. | `services/forecasting/price.py` source read, Phase 2c |
| 7 | **Calibration** | Measured directly, twice: 38.5% real interval coverage vs. ~80% stated (original), 17.71% on a later slice of the same batch (not directly comparable — different vintage). Both far below stated confidence. First real calibration numbers this system has ever produced. | forecast-confidence-calibration (Paper 5), cross-referenced here |
| 8 | **Provenance** | Internal `price_source` field is granular and honest (`faostat`/`eatta`/`eax`/`imf_pcps`/`selina_wamucii`/`wfp`/`baseline`, never a flat real/fake boolean) — confirmed correct by design. But provenance was *actively wrong* in production for South Sudan/Somalia/Uganda until this audit found and fixed the Selina cache bug (EDA §6): fabricated data was labeled with a real source tag. | Phase 2a |
| 9 | **Transparency** | Per-item dashboard badges are honest, localized (en/sw/fr), and equitable across country tiers by design (`CommoditiesPage.tsx`, `ForecastingPage.tsx`, etc.) — this held up under inspection. One real gap: the top-level `meta.data_source` string is static and identical regardless of what sources a given response actually used, so it can't be relied on alone. | Phase 2a |
| 10 | **Abstention** | `RecommendationEngine`'s `evidence_sufficient` / `_apply_evidence_gate` is a real, working mechanism (not a stub) — confirmed live: `evidence_sufficient_rate` genuinely varies per country (0.308-0.667) and is measured, not hardcoded. Not yet tested for whether it abstains *equitably* across tiers specifically (it doesn't reverse the RecommendationEngine gap, but wasn't isolated as its own variable) — the one sub-question inside an otherwise-covered axis worth flagging for Phase 3. | EDA §5, Phase 1 |
| 11 | **Subgroup performance** | The country-tier breakdown *is* this axis for geography; Phase 2b's commodity breakdown extends it to commodity; Phase 2c's per-country-per-level table extends it to geography level. All three consistently show the same pattern: real subgroup differences exist in the *data*, but the *model's stated confidence* doesn't track them at all — it's flat regardless of subgroup. | Phases 1, 2b, 2c |

**What changed code, not just documentation, as a result of asking
these 11 questions directly**: 3 real production fixes (Selina cache
purge, real-price training anchor, geography-level routing bug), all
found specifically *because* this framework demanded checking dimensions
Phase 1 alone would never have exercised (provenance/transparency,
commodity, and market/geography-level respectively). That's the honest
argument for why this 11-axis structure is worth the overhead over a
narrower "is there a fairness gap" framing: it kept finding real bugs,
not just a single yes/no answer.

**What's still genuinely open, not just deferred**:
- Calibration and MAPE numbers remain single-vintage (n=96, one batch)
  — a longitudinal re-run (evaluating more of the pending 2,688 rows as
  their target dates arrive, or triggering more batches) would turn
  "first measurement" into a stable estimate.
- Abstention's *equity* specifically (item 10) wasn't isolated as its
  own variable.
- WFP DataBridges remains the one real, unresolved data source — still
  blocked on registration, an external human step.
- Cassava, rice, sorghum, beans, and coffee's commodity-level numbers
  (Phase 2b) need a post-fix re-run to replace their flagged-uncertain
  figures with trustworthy ones.

## Decision, 2026-09-15: defer the calibration fix, let real data accumulate first

Asked directly whether the calibration finding (38.5% real coverage vs.
~80% stated) should be fixed now — e.g. via conformal-prediction-style
recalibration of the confidence interval, driven off real historical
accuracy in `forecast_evaluations` instead of the hand-set constants in
`services/forecasting/price.py`. Recommended against doing it
immediately: only 192 rows are evaluated so far (two single-day slices
of one batch), and fitting a calibration adjustment on that little data
risks overfitting to sampling noise — could plausibly make things worse
in a less-obvious way than the current honest-but-wrong constants.
**Decision: wait for more real evaluated history before building the
calibration mechanism.**

**Important operational caveat, found while documenting this**: "wait"
does **not** happen passively. There is no live, continuously-running
production worker — confirmed via `product/PRODUCTION_AUDIT.md`:
`deploy-production.yml` has 0 runs ever (verified via the GitHub API),
and neither `deploy-production.yml` nor `deploy-staging.yml` actually
deploys anything live — both only build Docker images and push to
GHCR, no SSH/hosting-API/`docker compose up` step anywhere. Every one
of the 192 currently-evaluated rows exists because this session
manually stood up a local worker against real production Supabase and
called `update_price_forecasts`/`evaluate_forecast_accuracy` directly.
The other 2,688 pending rows will **not** evaluate themselves as their
target dates arrive unless either (a) a future session manually
triggers `evaluate_forecast_accuracy` again on subsequent days, or
(b) the standing "confirm cloud deployment status" gap
(`product/PRODUCTION_AUDIT.md`) gets resolved so a real scheduled
worker runs continuously. Recorded here so "wait for more data" isn't
mistaken for something that happens on its own — it's a real action
item, not a timer.

**Reopen criterion**: once a meaningfully larger number of
`forecast_evaluations` rows are evaluated (ideally spanning multiple
distinct generation batches, not just further days of the same
2026-09-13 batch), revisit building the real, data-derived calibration
mechanism — a minimum-sample-size-gated function that falls back to
today's hand-set constants until enough real evaluated history exists,
then switches over automatically.

## 2026-09-17 check-in: "wait" confirmed passive, and a new real data-quality finding

Re-ran `run_audit.py` (read-only, no writes) two days after the 2026-09-15
EDA, specifically to test the "wait does **not** happen passively"
warning above. Confirmed exactly as predicted: `n_evaluated` is still 24
per country (192 total) — identical to 2026-09-15. Zero rows evaluated
in the intervening 2 days. Nobody manually triggered
`evaluate_forecast_accuracy`, and no live scheduled worker exists to do
it automatically. This is not a new finding so much as the standing one
being empirically confirmed rather than just asserted — the "reopen
criterion" above remains genuinely blocked on the same operational gap.

**A new, real, substantive finding surfaced while re-checking the
numbers.** `run_audit.py`'s per-country MAPE (blending both evaluated
target dates, 24 rows/country) diverges sharply from the single-date
Run 2 table above for exactly two countries: RW MAPE jumped to 94.83%
and BI to 105.39% (vs. 12.25%/8.89% in the 2026-09-13-only table) — both
now *worse* than every data-sparse country, which would reverse this
experiment's central finding if taken at face value.

Traced to source rather than accepted at face value. Per-commodity
breakdown (`forecast_evaluations`, both target dates) shows this isn't a
broad regression: 10 of 12 commodities for RW/BI show normal-range
degradation (20-60% MAPE — itself elevated, consistent with the
system-wide miscalibration already documented, but not extreme).
**Coffee and tea specifically, for both RW and BI, on the 2026-09-15
target date only**, show `actual_price` collapsing to roughly 1/10th of
their 2026-09-13 value: BI coffee 2595.88 -> 275.01 (881% MAPE), BI tea
1707.78 -> 136.66 (1186% MAPE), RW coffee 2696.49 -> 278.77 (987% MAPE),
RW tea 1829.22 -> 180.15 (896% MAPE). Two unrelated commodities, two
countries, same ~10x magnitude, same single date — not a plausible real
market movement.

Root-caused as far as possible without live credentials:
- Live `get_daily_price()` right now still returns coffee at ~$270-287
  for both RW/BI (`price_source: faostat`) — confirming the *low* value,
  not the 2026-09-13 one, is what the real pipeline currently produces.
  Tea has since fallen back to `price_source: baseline` (~$1750-1800),
  suggesting whatever produced the low tea value was more transient than
  coffee's.
- The underlying Redis-cached FAOSTAT entries (`get_faostat_price`) are
  static single-year anchors — RW: year 2015 (\$277.4 coffee, \$179.4
  tea), BI: year 2019 (\$270.9 coffee, \$135.5 tea) — not something that
  should swing 10x day-to-day under the documented "deterministic
  mean-reverting walk." This means the 2026-09-13 evaluation's *actual*
  price almost certainly came from a different source (`baseline`, the
  synthetic anchor) than the 2026-09-15 evaluation (`faostat`) — i.e.
  the FAOSTAT-sourced value for these 4 pairs only started being served
  sometime between the two evaluation dates.
- Checked FAOSTAT's own item-code definition (web search, since live
  auth wasn't available — see below): item 656 is "Coffee, green," the
  standard internationally-traded form, not raw unprocessed cherry —
  ruling out a product-basis mismatch (e.g. cherry-weight vs.
  green-bean-weight) as the explanation. A ~\$270-280/tonne farm-gate
  price for green coffee is implausible against real-world benchmarks
  (typically \$1,500-6,000+/tonne even at the farm gate) regardless of
  basis.
- Read `services/market/faostat_prices.py`'s parsing code directly
  (`sync_faostat_prices`, lines ~194-244): it applies **zero**
  transformation to the raw FAOSTAT `Value` field — cached as-is, gated
  only by a wide `1 < price_usd < 200,000` plausibility bound that
  $270-280 easily passes. So this codebase's own arithmetic cannot be
  introducing a 10x error. Two possibilities remain, and this audit
  cannot distinguish between them without live data access:
  1. FAOSTAT's own raw PP data for these specific
     country/item/year rows is genuinely anomalous (a real reporting
     error at the source, which does happen for smaller/less-monitored
     national statistics submissions).
  2. A real, previously-unnoticed gap in this same parsing code: the
     "most recent year per item" selection loop (lines 200-209) reads
     each row's `Item Code` and `Year` but never checks `Element Code`
     against `_PP_ELEMENT` (5532) — it trusts the API's `element=5532`
     query parameter to filter perfectly server-side and never verifies
     independently. If FAOSTAT's API ever returns a row for a different,
     numerically smaller element (e.g. an index rather than a raw
     price) despite the filter, this code would cache it as if it were
     the real USD/tonne price with no way to detect the mismatch.
**Resolved, 2026-09-17, with real FAOSTAT credentials.** The project
owner registered a real FAOSTAT account (`FAOSTAT_USERNAME`/
`FAOSTAT_PASSWORD`, added to `.env`) specifically to settle this.
Re-authenticating surfaced a genuine, separate code bug first:
`_login()` sent its request as `json={...}`, but FAOSTAT's
`/auth/login` now rejects a JSON body with a bare `415` *at the
CloudFront edge* (empty body, before even reaching FAOSTAT's origin
server) — confirmed live that the exact same credentials succeed with
`data={...}` (form-encoded) instead. This had been silently broken for
an unknown period; `sync_faostat_prices` degrades gracefully to
`BASE_PRICES_USD` on any failure, so nothing ever surfaced it, which is
almost certainly why the cached RW/BI entries were stuck at old,
never-refreshed single years (2015/2019). **Fixed**:
`services/market/faostat_prices.py`'s `_login()` now sends a
form-encoded body — this is a real production bug fix, not a
thesis-lab-only change, filed separately from this audit's own
read-only boundary (see Change Log entry below).

With login working, fetched the raw PP rows directly for RW/BI
coffee/tea (item 656/667) and checked every row's `Element Code`
**independently ruling out possibility 2 above**: every single
returned row correctly carries `Element Code: "5532"` / `Element:
"Producer Price (USD/tonne)"` — the API's `element` filter is not
leaking wrong-element rows. The parsing code's blind trust in that
filter turned out to be harmless in this instance (still worth fixing
defensively per the reopen note below, but it is not the cause here).

**The real cause is possibility 1, but not "an error" — a genuine
basis mismatch between two different, both-real, ways of pricing the
same commodity.** FAOSTAT's raw historical series is internally
consistent, not corrupted: BI coffee shows a real, large structural
break in its own trajectory — \$1,700-3,300/tonne every year from 1991
through 2006, then \$185-436/tonne every year from 2007 through 2019
(most recently \$270.9 in 2019) — a ~90% level shift that persists for
13 straight years, not a single bad data point. RW coffee's single 2015
value (\$277.4) sits in the same low range after a data gap (no rows
2011-2014) following \$1,371.9 in 2010. Checked `price_model.py`'s
`BASE_PRICES_USD` against this: `coffee: {"RW": 2800, "BI": 2600}` —
matching the forecasts' *predicted* values (\$2,680-3,051) almost
exactly, and sitting in the same range as international green-coffee
export-benchmark prices, not domestic farm-gate prices. The most
plausible real-world explanation (Burundi's coffee sector was under
strict state marketing-board control for decades, historically holding
producer prices well below export value — a documented feature of that
market, not spin): `BASE_PRICES_USD`'s synthetic anchor was calibrated
to something like international export-benchmark pricing, while
FAOSTAT's PP element is specifically *farm-gate producer* price — two
different, legitimate points in the same value chain, off by an order
of magnitude for a landlocked, historically state-controlled coffee
market. Neither source is "wrong" for what it measures; they are not
directly comparable.

**Why this matters for the paper, and it's a better finding than a
data-quality bug**: `evaluate_forecast_accuracy` (`apps/workers/
forecasting.py`) has no concept of *which basis* a price came from —
it stores `predicted_price` (generated under whatever `price_source`
was active at forecast time) and later fills `actual_price` (from
whatever `price_source` is active at evaluation time) and diffs them
directly. When the priority chain silently switches basis mid-window
for the same country/commodity — exactly what happened here between
the 2026-09-13 forecast (synthetic anchor) and the 2026-09-15
evaluation (FAOSTAT anchor) — the resulting "forecast error" is a
methodological artifact of an undetected source switch, not a
measurement of forecast skill, and it can be large enough (881-1186%
MAPE here) to flip a headline equity finding for the exact 2
countries/commodities affected. This is a sharper, more general
instance of Section 6's transparency concern than "a value was wrong":
a pipeline that composites multiple real sources with different
implicit definitions needs to detect and flag a basis change, not just
a missing-data fallback — provenance-as-a-source-label
(`price_source: "faostat"`) is not sufficient; provenance-as-a-basis
(what does this number actually measure) is the harder, real gap.

**Fixed, 2026-09-17** (the "needs a design decision" caveat above
resolved against this audit's own stated principle: "the honest next
step is not to silently equalize the numbers... but to make the
disparity visible" — that answers exclude-vs-flag, so there was no
actual decision left to defer). Migration 048
(`predicted_price_source`, `actual_price_source`, a generated
`source_mismatch` column on `forecast_evaluations`) plus wiring in
both `_persist_forecast_points` and `evaluate_forecast_accuracy`
(`apps/workers/forecasting.py`): a row with a confirmed source
mismatch still gets `actual_price`/`actual_price_source` written
(nothing hidden) but is excluded from the aggregate
MAE/RMSE/MAPE/coverage/ContinuousLearning feed, with the exclusion
count surfaced rather than silently dropped; a missing
`predicted_price_source` (legacy rows) is "unknown," never
"mismatched." All 36 existing tests pass unchanged; `ruff`/`mypy`
confirmed zero new findings via `git stash` comparison.

**Migration 048 applied to production, 2026-09-17** — the project
owner ran it directly (schema changes to live Supabase are correctly
gated behind explicit human approval, separate from a code push).
Verified live rather than trusting the report: queried
`forecast_evaluations` directly and confirmed all three columns exist,
correctly returning `None` on pre-migration rows (the intended
"unknown, not mismatched" path for legacy data). The fix is now fully
live end-to-end — the next real `update_price_forecasts`/
`evaluate_forecast_accuracy` run will populate and check it. Full
detail in `product/PRODUCTION_AUDIT.md`'s 2026-09-17 entries.

**Reopen criteria — all 3 closed, 2026-09-17:**
1. ~~Apply migration 048 to production~~ — **done.**
2. ~~Defensively add the `Element Code == _PP_ELEMENT` check~~ —
   **done.** Added to the `by_item` selection loop; any row whose
   `Element Code` doesn't match `5532` is now skipped before being
   considered, rather than trusting the API's `element` query filter
   alone. Verified: `ruff` clean, `mypy` findings on the file identical
   before/after via `git stash` (0 new).
3. ~~Re-run `sync_faostat_prices` for RW/BI now that `_login()` is
   fixed~~ — **done, and resolved cleanly**: re-synced with the working
   login and got back the *identical* cached values (RW coffee 277.4,
   RW tea 179.4, BI coffee 270.9, BI tea 135.5) — confirming 2015/2019
   genuinely is FAOSTAT's most recent published data for these specific
   country/item pairs, not an artifact of the broken login. The old
   `_login()` bug meant nobody could even check this until now.

**Follow-through, 2026-09-17 — closing the loop end-to-end:**
- Manually triggered `evaluate_forecast_accuracy` (same mechanism used
  twice before in this experiment) — 96 new rows evaluated for target
  date 2026-09-17, sample grown from 192 to 288. Zero source mismatches
  detected in this batch, but that's expected, not a null result: these
  rows' `predicted_price` still predates migration 048 (the original
  2026-09-13 generation batch), so `predicted_price_source` stays
  `None` — "unknown," correctly not misread as "consistent."
- To actually prove the mechanism end-to-end, regenerated a fresh
  forecast batch (`update_price_forecasts`, scoped to RW/BI
  coffee/tea) — confirmed live that the new rows (`target_date >=
  2026-09-17`) now correctly carry `predicted_price_source: "faostat"`,
  *and* that the predicted prices themselves are now anchored near the
  real FAOSTAT level (RW coffee ~\$298, BI coffee ~\$285) instead of the
  old synthetic \$2,600-3,051 baseline — `get_real_anchor_price`
  (commit `f831fcf`) correctly kicking in for genuinely new forecasts.
  Any future evaluation of these specific rows will have both sides of
  `source_mismatch` populated for the first time.
- Updated `run_audit.py` itself to be `source_mismatch`-aware (select
  it, exclude flagged rows from `avg_mape`/coverage, surface the
  excluded count as `n_source_mismatch_excluded` rather than folding it
  in silently) — the production fix alone wasn't enough, since this
  audit script computed its own independent diff and would have kept
  reporting the same inflated RW/BI numbers otherwise. Confirmed via a
  live re-run: `n_source_mismatch_excluded: 0` everywhere right now,
  correctly reflecting that no currently-evaluated row has both sources
  recorded yet — not evidence the fix doesn't work, evidence it hasn't
  had a full forecast-to-evaluation cycle to prove itself on yet. That
  will change automatically as new batches like the RW/BI one above get
  evaluated on their target dates.

## Concluding Note, 2026-09-17: reset into a controlled experiment

This experiment is concluded, not abandoned. Its own real value — three
production bugs found and fixed, a genuine 21.1% data-availability split
quantified, a real basis-mismatch mechanism traced and fixed — stands as
recorded above. But a review of the experimental design (external
input, recorded verbatim in
`thesis-lab/active_tests/evidence-sparsity-reliability/experiment_blueprint.md`'s
own header) identified a real methodological weakness: this experiment
mixed data-availability, production-system bugs, forecasting validity,
recommendation behavior, and calibration into one ad-hoc audit, which
makes causal interpretation difficult — you can't cleanly attribute an
observed effect to "less data" when the comparison groups (data-rich vs.
data-sparse countries) differ in a dozen uncontrolled ways at once, as
this experiment's own MAPE-reversal and basis-mismatch findings ended up
demonstrating in practice.

**Decision**: rather than keep patching one audit, reset Paper 14 as a
controlled scientific experiment — same platform (AgroIntel), a
narrower and more defensible research question, explicit experimental
factors (evidence availability, quality, provenance, semantic
consistency) instead of "which country," and a verified gold-standard
evaluation set that makes the exact MAPE-mixing mistake this experiment
made structurally impossible to repeat. Full design in the new
experiment's blueprint.

**What carries forward, not discarded**:
- The 5 real bugs found here become the seed of the new experiment's
  failure-mode taxonomy (F1–F5) — see that blueprint's own section on
  this. Nothing here was wasted; it's the empirical basis for scoping
  what "evidence failure" concretely means for this platform, rather
  than a theoretical list.
- The real, quantified 21.1% FAOSTAT coverage split and the confirmed
  structural (not credential) absence of UG/SS/SO/CD price/trade data
  remain true facts about this platform and inform the new experiment's
  country selection (2 data-rich, 2 data-sparse, per its own scope).
- The price-source-mismatch fix (migration 048, `apps/workers/
  forecasting.py`) is real, shipped, production infrastructure — it
  directly implements the "don't let synthetic data masquerade as
  observed ground truth" principle the new experiment makes a first-
  class rule (its OBSERVED/SYNTHETIC/UNKNOWN provenance states).
- `thesis-lab/active_tests/regional-equity-audit/scripts/` (`run_audit.py`,
  `audit_by_commodity.py`, `audit_geography_levels.py`) remain real,
  working, read-only query tools against production — reusable as a
  starting point for the new experiment's own data-collection scripts,
  not rewritten from scratch.

**What does not carry forward as-is**: the country-vs-country comparison
framing itself (Kenya vs. Uganda) — the new experiment explicitly avoids
this in favor of comparing the same forecasting problem under
controlled evidence conditions, for the exact reason this experiment's
own confound-chasing kept surfacing.

The two published reports (`findings_report.html`, `grant_findings_brief.html`)
stand as the honest historical record of this concluded experiment and
are not being rewritten to pretend the reset was the plan all along.
