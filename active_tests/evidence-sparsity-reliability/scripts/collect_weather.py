"""Phase 0, second slice: collect real gold-standard weather observations
via the real NASA POWER API (clients/nasa_power.py), for the same
finalized 4-country scope as the price modality.

Real nuance handled here, confirmed via a live test call before writing
this script: NASA POWER returns -999.0 as a fill-value sentinel for a
date it hasn't finished processing yet (recent days lag by a few days,
not the "-3-4 months" the client's docstring suggests as a worst case).
Naively treating -999.0 as a real temperature/precipitation value would
be exactly the kind of provenance mistake this whole experiment exists
to catch - so this script walks backward from today to find the most
recent date with a real, non-fill-value reading, and records that actual
date as observation_date (an honest freshness signal - see the
DataState/EvidenceQualityVector design in provenance.py) rather than
claiming today's date for a value that isn't really today's.

Read-only against the real NASA POWER API - no writes anywhere. Output
is a local JSON file under this experiment's own data/ directory.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/collect_weather.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR.parents[2] / "agrointel"))  # agrointel submodule, for services.*/clients.*/apps.*

from provenance import DataState, GoldStandardObservation  # noqa: E402

# Real capital coordinates, read directly from configs/countries/<name>.yaml
# rather than re-derived or guessed.
_COUNTRY_COORDS = {
    "KE": (-1.2921, 36.8219),  # Nairobi
    "RW": (-1.9536, 30.0606),  # Kigali
    "SS": (4.8517, 31.5825),   # Juba
    "SO": (2.0469, 45.3182),   # Mogadishu
}

_PARAMETERS = {
    "T2M": {"variable": "temperature_2m", "unit": "celsius"},
    "PRECTOTCORR": {"variable": "precipitation_corrected", "unit": "mm/day"},
}

_FILL_VALUE = -999.0
_LOOKBACK_DAYS = 10  # window to search backward for the most recent real reading


async def collect_for_country(country: str) -> list[GoldStandardObservation]:
    from clients.nasa_power import NASAPowerClient

    lat, lon = _COUNTRY_COORDS[country]
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=_LOOKBACK_DAYS)
    now_iso = datetime.now(timezone.utc).isoformat()

    async with NASAPowerClient() as client:
        raw = await client.get_point_data(
            latitude=lat, longitude=lon,
            start_date=start.strftime("%Y%m%d"), end_date=end.strftime("%Y%m%d"),
            parameters=list(_PARAMETERS.keys()),
        )

    observations: list[GoldStandardObservation] = []
    params = raw.get("properties", {}).get("parameter", {})
    for power_code, meta in _PARAMETERS.items():
        series = params.get(power_code, {})
        # Walk dates newest-first, take the first real (non-fill-value) reading.
        for date_str in sorted(series.keys(), reverse=True):
            value = series[date_str]
            if value == _FILL_VALUE:
                continue
            obs_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
            observations.append(GoldStandardObservation(
                country_code=country,
                modality="weather",
                variable=meta["variable"],
                commodity=None,
                observation_date=obs_date,
                value=value,
                unit=meta["unit"],
                price_basis="nasa_power_merra2_geosit",
                source="nasa_power",
                source_timestamp=now_iso,
                data_state=DataState.OBSERVED_VERIFIED,
            ))
            break
        else:
            # Every date in the lookback window was a fill value - a real,
            # honest gap, not something to paper over with a guess.
            print(f"  WARNING: {country} {power_code} - no real reading in the last {_LOOKBACK_DAYS} days")

    return observations


async def collect_all() -> list[GoldStandardObservation]:
    results = await asyncio.gather(*(collect_for_country(cc) for cc in _COUNTRY_COORDS))
    return [obs for country_obs in results for obs in country_obs]


def main() -> None:
    observations = asyncio.run(collect_all())

    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"gold_standard_weather_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(
        json.dumps([o.model_dump(mode="json") for o in observations], indent=2),
        encoding="utf-8",
    )

    print(f"Collected {len(observations)} observations -> {out_path}")
    for o in observations:
        print(f"  {o.country_code} {o.variable}: {o.value} {o.unit} (as of {o.observation_date})")


if __name__ == "__main__":
    main()
