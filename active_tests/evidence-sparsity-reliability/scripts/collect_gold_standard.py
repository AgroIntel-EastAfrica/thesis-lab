"""Phase 0, first slice: collect real gold-standard price observations for
the finalized scope (KE/RW/SS/SO x coffee/maize/tea) via the real,
production get_daily_price() priority chain.

Read-only against real production Redis/config - no writes anywhere.
Output is a local JSON file under this experiment's own data/ directory,
never a production table (thesis-lab sandbox rule, CLAUDE.md).

Scope note: this slice covers the price modality only. Weather, trade,
production, and textual-event modalities (the blueprint's "4-5 evidence
modalities") are separate, not-yet-built collection scripts - price was
chosen first because get_daily_price()'s real/synthetic distinction is
already fully verified and trustworthy (this session's own price-source-
mismatch investigation), giving Phase 0 a solid first foundation rather
than guessing at provenance for a modality nobody has audited yet.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/collect_gold_standard.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))  # for provenance.py, same directory
sys.path.insert(0, str(_SCRIPT_DIR.parents[2] / "agrointel"))  # agrointel submodule, for services.*/clients.*/apps.*

from provenance import DataState, GoldStandardObservation  # noqa: E402

COUNTRIES_RICH = ["KE", "RW"]
COUNTRIES_SPARSE = ["SS", "SO"]
ALL_COUNTRIES = COUNTRIES_RICH + COUNTRIES_SPARSE
COMMODITIES = ["coffee", "maize", "tea"]

_PRICE_BASIS_BY_SOURCE = {
    "faostat": "producer_price_faostat_usd_tonne",
    "baseline": "synthetic_wholesale_baseline_usd_tonne",
}

_DATA_STATE_BY_SOURCE = {
    "faostat": DataState.OBSERVED_VERIFIED,
    "baseline": DataState.SYNTHETIC_BASELINE,
}


async def collect_one(country: str, commodity: str) -> GoldStandardObservation:
    from services.market.price_model import get_daily_price

    result = await get_daily_price(commodity, country)
    source = result.get("price_source", "unknown")
    now = datetime.now(timezone.utc).isoformat()

    return GoldStandardObservation(
        country_code=country,
        modality="price",
        variable="producer_price",
        commodity=commodity,
        observation_date=result.get("date", now[:10]),
        value=result["price_usd"],
        unit="USD/tonne",
        price_basis=_PRICE_BASIS_BY_SOURCE.get(source, f"unverified_{source}"),
        source=source,
        source_timestamp=now,
        data_state=_DATA_STATE_BY_SOURCE.get(source, DataState.OBSERVED_UNVERIFIED),
    )


async def collect_all() -> list[GoldStandardObservation]:
    tasks = [collect_one(cc, comm) for cc in ALL_COUNTRIES for comm in COMMODITIES]
    return await asyncio.gather(*tasks)


def main() -> None:
    observations = asyncio.run(collect_all())

    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"gold_standard_price_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(
        json.dumps([o.model_dump(mode="json") for o in observations], indent=2),
        encoding="utf-8",
    )

    print(f"Collected {len(observations)} observations -> {out_path}")
    by_state: dict[str, int] = {}
    for o in observations:
        by_state[o.data_state.value] = by_state.get(o.data_state.value, 0) + 1
    for state, count in sorted(by_state.items()):
        print(f"  {state}: {count}")


if __name__ == "__main__":
    main()
