"""Phase 0, eighth slice: the first real, genuine multi-year TIME
SERIES in this experiment's gold-standard dataset, for the price
modality - a real prerequisite for Experiment E1 (forecasting under
controlled data availability), which needs historical observations to
fit/evaluate a forecast against, not a single snapshot.

Every collector so far (price/weather/production/trade/text) recorded
one point-in-time observation per (country, commodity) - Phase 0's own
blueprint flagged this explicitly as unfinished business. Production
turned out to already have full multi-year history available
internally (services/forecasting/yield_prediction.py's
_fetch_faostat_yield_history(), used in collect_production.py but only
its latest year kept). Price has the same real shape:
services/market/faostat_prices.py's sync_faostat_prices() already
fetches every real year via _fetch_pp_data(), then deliberately keeps
only the most-recent year per item for its own caching purpose - this
script calls _fetch_pp_data() directly and keeps every year instead,
exactly the same pattern already applied to production.

Read-only against the real FAOSTAT PP domain - reuses the same
login/auth flow already fixed and verified this session
(services/market/faostat_prices.py's own 2026-09-17 fix). No writes
anywhere. Output is a local JSON file under this experiment's own
data/ directory.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/collect_price_history.py
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
_PP_ELEMENT = "5532"  # USD/tonne - same element faostat_prices.py itself uses


async def collect_country(country: str) -> list[GoldStandardObservation]:
    from apps.api.config import get_settings
    from services.market.faostat_prices import (
        EAC_FAO_AREA_CODES,
        FAOSTAT_ITEM_MAP,
        _fetch_pp_data,
        _login,
    )

    now = datetime.now(timezone.utc).isoformat()
    area_code = EAC_FAO_AREA_CODES.get(country)
    if not area_code:
        return []

    settings = get_settings()
    token = settings.faostat_token
    if not token and settings.faostat_username and settings.faostat_password:
        token = await asyncio.to_thread(_login, settings.faostat_username, settings.faostat_password)
    if not token:
        return [
            GoldStandardObservation(
                country_code=country, modality="price", variable="producer_price_history",
                commodity=comm, observation_date=now[:10], value=0.0, unit="USD/tonne",
                price_basis="faostat_pp_no_credentials", source="faostat_pp_no_credentials",
                source_timestamp=now, data_state=DataState.UNKNOWN,
            )
            for comm in COMMODITIES
        ]

    item_codes = {comm: FAOSTAT_ITEM_MAP[comm] for comm in COMMODITIES}
    rows = await asyncio.to_thread(_fetch_pp_data, area_code, token)

    by_item: dict[str, dict[int, float]] = {code: {} for code in item_codes.values()}
    for row in rows:
        if str(row.get("Element Code", "")) != _PP_ELEMENT:
            continue
        item_code = str(row.get("Item Code", ""))
        if item_code not in by_item:
            continue
        try:
            year = int(row.get("Year") or 0)
            val = row.get("Value")
            if year and val is not None:
                by_item[item_code][year] = float(val)
        except (ValueError, TypeError):
            continue

    observations: list[GoldStandardObservation] = []
    for comm, item_code in item_codes.items():
        history = by_item[item_code]
        if not history:
            observations.append(GoldStandardObservation(
                country_code=country, modality="price", variable="producer_price_history",
                commodity=comm, observation_date=now[:10], value=0.0, unit="USD/tonne",
                price_basis="faostat_pp_no_data", source="faostat_pp_no_data",
                source_timestamp=now, data_state=DataState.UNKNOWN,
            ))
            continue
        for year, price_usd in sorted(history.items()):
            observations.append(GoldStandardObservation(
                country_code=country, modality="price", variable="producer_price_history",
                commodity=comm, observation_date=f"{year}-12-31", value=round(price_usd, 2),
                unit="USD/tonne", price_basis=f"faostat_pp_annual_of_{len(history)}_years",
                source="faostat_pp_usd", source_timestamp=now,
                data_state=DataState.OBSERVED_VERIFIED,
            ))

    return observations


async def collect_all() -> list[GoldStandardObservation]:
    all_obs: list[GoldStandardObservation] = []
    for country in COUNTRIES:
        all_obs.extend(await collect_country(country))
    return all_obs


def main() -> None:
    observations = asyncio.run(collect_all())

    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"gold_standard_price_history_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
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
