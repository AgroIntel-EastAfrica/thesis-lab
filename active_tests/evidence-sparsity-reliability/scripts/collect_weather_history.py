"""Phase 0, twelfth slice: the third real multi-year time series, for
the weather modality - extends E1's evidence tiers past price+
production for the first time.

Unlike collect_weather.py (the original single-snapshot collector,
which reads NASA POWER's `daily` endpoint and walks backward through
real fill-value sentinels to find the most recent genuinely-processed
day), this script uses the `monthly` temporal API instead. A live test
confirmed NASA POWER's real monthly endpoint returns, per parameter,
12 real `YYYYMM` keys plus a 13th real `YYYY13` key holding that
year's annual mean - a single real API call per country covers the
entire 1991-2024 range (matching price/production's real span) with
no rate-limit risk (unlike UN Comtrade, which has already hit a hard
quota lockout twice this session; NASA POWER's original 8/8 single-
snapshot calls this session all succeeded cleanly, and this is the
same low-risk source, just a different, already-supported endpoint).

Capped at 2024 (not the current year) deliberately: 2026 isn't
complete yet, and an annual mean built from a partial year would be a
real but misleading number - matching price/production's own real
practical range rather than reaching into an incomplete year.

Read-only against the real NASA POWER API, same capital-city
coordinates already verified and used by collect_weather.py. No writes
anywhere. Output is a local JSON file under this experiment's own
data/ directory.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/collect_weather_history.py
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

# Same real capital coordinates already verified and used by
# collect_weather.py - reused as-is, not re-derived. TZ and BI added
# 2026-09-21, read from configs/countries/*.yaml - TZ's config
# explicitly labels its coordinates as the commercial capital, Dar es
# Salaam, not the legislative capital, Dodoma. UG and CD added the
# same day, completing all 8 EAC countries, also read from
# configs/countries/*.yaml.
_COUNTRY_COORDS = {
    "KE": (-1.2921, 36.8219),  # Nairobi
    "RW": (-1.9536, 30.0606),  # Kigali
    "SS": (4.8517, 31.5825),   # Juba
    "SO": (2.0469, 45.3182),   # Mogadishu
    "TZ": (-6.7924, 39.2083),  # Dar es Salaam (commercial capital)
    "BI": (-3.3761, 29.3600),  # Gitega
    "UG": (0.3476, 32.5825),   # Kampala
    "CD": (-4.4419, 15.2663),  # Kinshasa
}
_PARAMETERS = {"T2M": ("temperature_2m", "celsius"), "PRECTOTCORR": ("precipitation_corrected", "mm/day")}
_START_YEAR = "1991"
_END_YEAR = "2024"


async def collect_country(country: str) -> list[GoldStandardObservation]:
    from clients.nasa_power import NASAPowerClient

    now = datetime.now(timezone.utc).isoformat()
    lat, lon = _COUNTRY_COORDS[country]

    async with NASAPowerClient() as client:
        data = await client.get_point_data(
            latitude=lat, longitude=lon,
            start_date=_START_YEAR, end_date=_END_YEAR,
            parameters=list(_PARAMETERS.keys()),
            temporal_api="monthly",
        )

    params = data.get("properties", {}).get("parameter", {})
    observations: list[GoldStandardObservation] = []
    for param_code, (variable, unit) in _PARAMETERS.items():
        series = params.get(param_code, {})
        for key, value in sorted(series.items()):
            if not key.endswith("13"):  # only the annual-mean key, skip the 12 monthly ones
                continue
            year = int(key[:4])
            if value is None or value <= -900:  # real NASA POWER fill-value sentinel
                continue
            observations.append(GoldStandardObservation(
                country_code=country, modality="weather", variable=variable,
                commodity=None, observation_date=f"{year}-12-31", value=round(float(value), 4),
                unit=unit, price_basis="nasa_power_merra2_geosit_monthly_annual_mean",
                source="nasa_power", source_timestamp=now,
                data_state=DataState.OBSERVED_VERIFIED,
            ))
    return observations


async def collect_all() -> list[GoldStandardObservation]:
    all_obs: list[GoldStandardObservation] = []
    for country in ["KE", "RW", "SS", "SO", "TZ", "BI", "UG", "CD"]:
        all_obs.extend(await collect_country(country))
    return all_obs


def main() -> None:
    observations = asyncio.run(collect_all())

    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"gold_standard_weather_history_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(
        json.dumps([o.model_dump(mode="json") for o in observations], indent=2),
        encoding="utf-8",
    )

    print(f"Collected {len(observations)} observations -> {out_path}")
    by_country_var: dict[tuple[str, str], list[GoldStandardObservation]] = {}
    for o in observations:
        by_country_var.setdefault((o.country_code, o.variable), []).append(o)
    for (cc, var), obs_list in sorted(by_country_var.items()):
        years = sorted(int(o.observation_date[:4]) for o in obs_list)
        print(f"  {cc} {var}: {len(obs_list)} years ({years[0]}-{years[-1]})")


if __name__ == "__main__":
    main()
