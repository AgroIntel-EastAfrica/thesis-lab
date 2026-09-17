"""Phase 0, fourth slice: collect real gold-standard production/yield
observations via services/forecasting/yield_prediction.py's
_fetch_faostat_yield_history() (real FAOSTAT QCL domain), for the same
finalized 4-country scope.

This modality only became usable today: _fetch_faostat_yield_history()
had two real, previously-undiscovered production bugs (missing auth,
wrong element code) that made every real call return {} since the
module shipped - both fixed in services/forecasting/yield_prediction.py
this session (see product/PRODUCTION_AUDIT.md's 2026-09-17 entry), and
verified live end-to-end before this collector was written.

_fetch_faostat_yield_history() returns a full year->MT/ha history, not
a single point-in-time reading (unlike price/weather). Each observation
here takes the single most recent real year in that history - the same
"most recent real reading" convention collect_weather.py already
established for a different reason (NASA POWER's fill-value walk-back).
Read-only against the real FAOSTAT API - no writes anywhere. Output is
a local JSON file under this experiment's own data/ directory.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/collect_production.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR.parents[3]))

from provenance import DataState, GoldStandardObservation  # noqa: E402

COUNTRIES = ["KE", "RW", "SS", "SO"]
COMMODITIES = ["coffee", "maize", "tea"]


async def collect_one(country: str, commodity: str) -> GoldStandardObservation:
    from services.forecasting.yield_prediction import _fetch_faostat_yield_history

    now = datetime.now(timezone.utc).isoformat()
    history = await _fetch_faostat_yield_history(commodity, country)

    if history:
        latest_year = max(history)
        value = history[latest_year]
        return GoldStandardObservation(
            country_code=country,
            modality="production",
            variable="yield_latest_year",
            commodity=commodity,
            observation_date=f"{latest_year}-12-31",
            value=value,
            unit="MT/ha",
            price_basis=f"faostat_qcl_element_5412_of_{len(history)}_years",
            source="faostat_qcl",
            source_timestamp=now,
            data_state=DataState.OBSERVED_VERIFIED,
        )

    return GoldStandardObservation(
        country_code=country,
        modality="production",
        variable="yield_latest_year",
        commodity=commodity,
        observation_date=now[:10],
        value=0.0,
        unit="MT/ha",
        price_basis="faostat_qcl_no_data",
        source="faostat_qcl_no_data",
        source_timestamp=now,
        data_state=DataState.UNKNOWN,
    )


async def collect_all() -> list[GoldStandardObservation]:
    tasks = [collect_one(cc, comm) for cc in COUNTRIES for comm in COMMODITIES]
    return await asyncio.gather(*tasks)


def main() -> None:
    observations = asyncio.run(collect_all())

    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"gold_standard_production_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(
        json.dumps([o.model_dump(mode="json") for o in observations], indent=2),
        encoding="utf-8",
    )

    print(f"Collected {len(observations)} observations -> {out_path}")
    by_state: dict[str, int] = {}
    for o in observations:
        by_state[o.data_state.value] = by_state.get(o.data_state.value, 0) + 1
        years = o.price_basis.split("_of_")[-1].replace("_years", "") if "_of_" in o.price_basis else "0"
        print(f"  {o.country_code} {o.commodity}: {o.value:.4f} MT/ha ({years} years, {o.data_state.value})")
    print()
    for state, count in sorted(by_state.items()):
        print(f"  {state}: {count}")


if __name__ == "__main__":
    main()
