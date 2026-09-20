# AgroIntel Thesis Lab

PhD research lab for **"Agentic Intelligence Under Uncertainty"** — a set of
controlled experiments studying how agentic AI systems should behave when
evidence is sparse, unreliable, or heterogeneous, grounded in a real
production agricultural-intelligence platform
([`agrointel`](https://github.com/AgroIntel-EastAfrica/agrointel)) rather
than synthetic benchmarks alone.

## Structure

```
thesis-lab/
├── templates/          # experiment_blueprint.md — the starting shape for a new experiment
├── active_tests/        # one folder per in-progress experiment
├── concluded/           # finished experiments (successful or not — a disproved
│                         #   hypothesis is still a real result), full write-up included
├── agrointel/            # git submodule — real, read-only access to production service code
└── PUBLICATION_ROADMAP.md  # maps this lab's experiments to a 16-paper PhD structure
```

## Setup

This repo includes [`agrointel`](https://github.com/AgroIntel-EastAfrica/agrointel)
as a git submodule, since most experiment scripts import real service code
directly (e.g. `from services.market.faostat_prices import ...`) rather than
mocking it — several experiments are audit-style, measuring the real
system's real behavior, which a synthetic substitute would defeat.

```bash
git clone --recurse-submodules https://github.com/AgroIntel-EastAfrica/thesis-lab.git
# or, if already cloned without submodules:
git submodule update --init
```

The submodule tracks `agrointel`'s `develop` branch. To pull the latest:

```bash
git submodule update --remote agrointel
```

## Ground rules

- **No production writes.** Experiments never write to or mutate production
  Supabase tables, and never call a paid production external service for
  exploratory/throwaway work. **Read-only** access to real production data
  is fine for audit-style experiments whose entire point is measuring real
  system behavior — a mocked substitute would defeat the experiment.
- **One-directional boundary.** Nothing in `agrointel`'s own codebase
  (`apps/`, `services/`, `core/`) imports from this lab. An experiment that
  proves out gets *rewritten* into the real `agrointel` codebase — with real
  tests and real error handling — never wired in directly.
- **Isolated dependencies.** A package an experiment needs goes in a
  `requirements.txt` inside that experiment's own folder, not a shared one.
- **Same code style, different bar.** Experiment code passes `ruff check .`
  but isn't held to production-readiness or coverage requirements.
- **Lifecycle.** Start a new experiment by copying
  `templates/experiment_blueprint.md` into `active_tests/<name>/`. When it
  concludes, fill in its Results section and move it to `concluded/<name>/`.

## Current focus

The active flagship experiment is
[`evidence-sparsity-reliability`](active_tests/evidence-sparsity-reliability/experiment_blueprint.md)
(Paper 14): does evidence availability, quality, and calibration affect the
reliability of agricultural AI intelligence under real data-sparse
conditions? Built on a real gold-standard dataset spanning five evidence
modalities (price, weather, production, trade, and textual/news signals)
across Kenya, Rwanda, South Sudan, and Somalia — see the experiment's own
blueprint for the full, continuously-updated results log, and
[`PUBLICATION_ROADMAP.md`](PUBLICATION_ROADMAP.md) for how it and the other
19 experiments map onto the PhD's 16-paper structure.
