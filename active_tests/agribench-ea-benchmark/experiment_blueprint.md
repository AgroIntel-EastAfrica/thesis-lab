# Experiment: agribench-ea-benchmark

- **Owner:**
- **Started:**
- **Status:** active
- **Paper:** Paper 11 — "AgriBench-EA: A Multimodal Benchmark for
  Agricultural Forecasting and Decision Intelligence in Data-Sparse
  Environments"
- **Source:** 12-paper publication roadmap.

## Important: this is a dataset-release effort, not a modeling experiment

Unlike the forecasting/reasoning experiments in this lab, the
deliverable here is a *public, standardized dataset + task
definitions*, not a trained model. It has real prerequisites the other
experiments don't: data licensing review for every source before
anything is released publicly, and a decision on hosting (Hugging Face
Datasets, Zenodo, or similar) — neither of which a coding session can
resolve alone.

## Objective

AgroIntel already aggregates real, live multimodal data across all 8 EAC
countries — prices (`services/market/price_model.py`), trade (Comtrade
client), climate (`services/satellite/climate_data.py`, NASA POWER),
satellite NDVI (Sentinel-2, per this session's memory of prior work),
production statistics, and news (GDELT). No standardized, citable,
public benchmark currently exists assembling comparable East African
agricultural data for forecasting/decision-intelligence research — the
paper explicitly frames this scarcity as itself a real research problem
worth addressing.

## Hypothesis

N/A in the modeling sense. The real, checkable claim: a benchmark built
from AgroIntel's real live data sources (not synthetic placeholders)
will expose genuine data-sparsity patterns already documented elsewhere
in this codebase (e.g. `project_faostat_prices` memory: UG/SS/SO/CD lack
real FAOSTAT coverage and fall back to static estimates) — meaning the
benchmark's own documentation must honestly label which country/
commodity/year cells are backed by real vs. estimated data, not present
a uniform-quality dataset that doesn't exist.

## Core Variables

- **Licensing check required first, per source:** FAOSTAT, Comtrade,
  NASA POWER, GDELT, and any UBOS/MAAIF-collaborator data each have their
  own terms — this must be resolved before any data leaves this
  codebase, not assumed permissive.
- **Modalities to include** (per the paper's own table): markets, trade,
  climate, satellite, production, socioeconomic, news, policy.
- **Countries:** UG, KE, TZ, RW at minimum (real data coverage
  confirmed this session); BI/SS/SO/CD only if genuinely real data is
  available for them, not backfilled just to hit "all 8."

## Success Metrics

- Every cell in the released dataset must be traceable to a real source
  and carry a `data_quality`/`data_source` label (matching this
  codebase's own established disclosure pattern for exactly this
  problem — see `product/PRODUCTION_AUDIT.md`'s "stale data presented as
  live" fixes) — never a synthetic value presented as real.
- A minimal standardized task (e.g. 30-day price forecasting for a fixed
  commodity/country set) with a documented, reproducible train/test
  split, so other researchers can actually compare against it.

## Results

*Not started — blocked on real data-licensing review per source before
any release.*
