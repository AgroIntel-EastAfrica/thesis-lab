"""Phase 0, ninth slice: the second real multi-year time series, for
the production modality - the cheap follow-up flagged at the end of
the price-history slice.

_fetch_faostat_yield_history() (services/forecasting/yield_prediction.py)
already returns a full year->MT/ha dict; collect_production.py (the
first production-modality collector) deliberately kept only the latest
year, matching the single-snapshot convention every other Phase 0
collector used before the price-history slice showed that convention
was blocking Experiment E1. This script keeps every year instead - no
new bugs, no new auth/element-code work: it's the exact same real,
already-fixed function, just not truncated down to one point.

Read-only against the real FAOSTAT QCL domain, reusing the same
auth/element-code fixes verified this session. No writes anywhere.
Output is a local JSON file under this experiment's own data/
directory.

UG and CD added 2026-09-21 alongside collect_price_history.py's same
addition, completing all 8 EAC countries. Checked live before adding:
both have full 1961-2024 QCL yield history for all three commodities,
the same completeness as TZ/BI.

Sorghum and sweet potatoes added 2026-09-21, alongside
collect_price_history.py's same addition - see that script's docstring
for the real coverage analysis behind the choice. Both item codes
were already present in services/forecasting/yield_prediction.py's own
item map, so no new lookups needed.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/collect_production_history.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR.parents[2] / "agrointel"))  # agrointel submodule, for services.*/clients.*/apps.*

from provenance import DataState, GoldStandardObservation  # noqa: E402

COUNTRIES = ["KE", "RW", "SS", "SO", "TZ", "BI", "UG", "CD"]
COMMODITIES = ["coffee", "maize", "tea", "sorghum", "sweet_potatoes"]


async def collect_one(country: str, commodity: str) -> list[GoldStandardObservation]:
    from services.forecasting.yield_prediction import _fetch_faostat_yield_history

    now = datetime.now(timezone.utc).isoformat()
    history = await _fetch_faostat_yield_history(commodity, country)

    if not history:
        return [GoldStandardObservation(
            country_code=country, modality="production", variable="yield_history",
            commodity=commodity, observation_date=now[:10], value=0.0, unit="MT/ha",
            price_basis="faostat_qcl_no_data", source="faostat_qcl_no_data",
            source_timestamp=now, data_state=DataState.UNKNOWN,
        )]

    return [
        GoldStandardObservation(
            country_code=country, modality="production", variable="yield_history",
            commodity=commodity, observation_date=f"{year}-12-31", value=round(value, 4),
            unit="MT/ha", price_basis=f"faostat_qcl_element_5412_of_{len(history)}_years",
            source="faostat_qcl", source_timestamp=now,
            data_state=DataState.OBSERVED_VERIFIED,
        )
        for year, value in sorted(history.items())
    ]


async def collect_all() -> list[GoldStandardObservation]:
    all_obs: list[GoldStandardObservation] = []
    for cc in COUNTRIES:
        for comm in COMMODITIES:
            all_obs.extend(await collect_one(cc, comm))
    return all_obs


def main() -> None:
    observations = asyncio.run(collect_all())

    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"gold_standard_production_history_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(
        json.dumps([o.model_dump(mode="json") for o in observations], indent=2),
        encoding="utf-8",
    )

    print(f"Collected {len(observations)} observations -> {out_path}")
    by_country_commodity: dict[tuple[str, str], list[GoldStandardObservation]] = {}
    for o in observations:
        by_country_commodity.setdefault((o.country_code, o.commodity or ""), []).append(o)

    for (cc, comm), obs_list in sorted(by_country_commodity.items()):
        real = [o for o in obs_list if o.data_state == DataState.OBSERVED_VERIFIED]
        if real:
            years = sorted(int(o.observation_date[:4]) for o in real)
            print(f"  {cc} {comm}: {len(real)} years ({years[0]}-{years[-1]})")
        else:
            print(f"  {cc} {comm}: no data ({obs_list[0].data_state.value})")


if __name__ == "__main__":
    main()
