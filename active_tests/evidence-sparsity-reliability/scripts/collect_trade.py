"""Phase 0, third slice: collect real gold-standard trade observations via
the real UN Comtrade API (clients/comtrade.py), for the same finalized
4-country scope.

Real shape difference from price/weather, confirmed via a live test call
before writing this script: get_trade_flows() returns one row per trading
PARTNER (73 rows for Kenya coffee exports, 2023), not one aggregate
number. Trade flows measure total export VALUE (USD), not a unit price -
a fundamentally different kind of measurement than the price modality's
USD/tonne, so this is recorded honestly as its own variable name rather
than conflated with "price". Each country/commodity observation here is
the real sum of primaryValue (USD) across every partner row Comtrade
returned for that reporter+commodity+year - an honest aggregation of real
per-partner data, not a single API-provided total (Comtrade's REST API
was not confirmed to expose a direct "World" aggregate in the live test
that produced this script).

Read-only against the real Comtrade API - no writes anywhere. Output is
a local JSON file under this experiment's own data/ directory.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/collect_trade.py
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

COUNTRIES = ["KE", "RW", "SS", "SO"]
COMMODITIES = ["coffee", "maize", "tea"]
_YEAR = 2023  # most recent year confirmed to have real data via a live test call


async def collect_one(country: str, commodity: str) -> GoldStandardObservation:
    from apps.api.config import get_settings
    from clients.comtrade import ComtradeClient

    hs_code = ComtradeClient.get_hs_code(commodity)
    now = datetime.now(timezone.utc).isoformat()

    async with ComtradeClient(api_key=get_settings().comtrade_api_key) as client:
        rows = await client.get_trade_flows(
            reporter=country, commodity_code=hs_code, flow="exports", year=_YEAR,
        )

    total_value_usd = sum(r.get("primaryValue") or 0.0 for r in rows)
    is_real = len(rows) > 0 and total_value_usd > 0

    return GoldStandardObservation(
        country_code=country,
        modality="trade",
        variable="export_value_total",
        commodity=commodity,
        observation_date=f"{_YEAR}-12-31",  # Comtrade annual data - represents the full year
        value=total_value_usd,
        unit="USD",
        price_basis=f"un_comtrade_annual_sum_of_{len(rows)}_partner_rows",
        source="un_comtrade" if is_real else "un_comtrade_zero_rows",
        source_timestamp=now,
        data_state=DataState.OBSERVED_VERIFIED if is_real else DataState.UNKNOWN,
    )


async def collect_all() -> list[GoldStandardObservation]:
    tasks = [collect_one(cc, comm) for cc in COUNTRIES for comm in COMMODITIES]
    return await asyncio.gather(*tasks)


def main() -> None:
    observations = asyncio.run(collect_all())

    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"gold_standard_trade_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(
        json.dumps([o.model_dump(mode="json") for o in observations], indent=2),
        encoding="utf-8",
    )

    print(f"Collected {len(observations)} observations -> {out_path}")
    by_state: dict[str, int] = {}
    for o in observations:
        by_state[o.data_state.value] = by_state.get(o.data_state.value, 0) + 1
        print(f"  {o.country_code} {o.commodity}: ${o.value:,.0f} ({o.data_state.value})")
    print()
    for state, count in sorted(by_state.items()):
        print(f"  {state}: {count}")


if __name__ == "__main__":
    main()
