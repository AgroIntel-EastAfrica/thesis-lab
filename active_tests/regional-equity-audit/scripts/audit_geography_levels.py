"""Real, read-only audit: does the equity picture differ by forecaster
geography level (LOCAL/XGBoost, SUB_NATIONAL/Prophet, NATIONAL/ensemble)?

Phase 1 only ever exercised the NATIONAL layer (forecast_country_commodity
hardcodes GeographyLevel.NATIONAL - see services/forecasting/price.py). This
is Phase 2c: the last unscoped axis from the "Scope completeness check"
section of experiment_blueprint.md ("market" - geography level, not country).

Calls PriceForecaster directly at each level for the same commodity/country
pairs, replicating forecast_country_commodity's real-anchor resolution
(2026-09-15 fix) so this audit reflects the fixed forecaster, not the
pre-fix behavior.

Reads only. Never writes to production.

Run from the repo root: python thesis-lab/active_tests/regional-equity-audit/scripts/audit_geography_levels.py
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

DATA_RICH = ["KE", "TZ", "RW", "BI"]
DATA_SPARSE = ["UG", "SS", "SO", "CD"]
ALL_COUNTRIES = DATA_RICH + DATA_SPARSE
COMMODITY = "maize"


async def audit_geography_levels() -> dict:
    from services.forecasting.price import PriceDataPoint, PriceForecaster
    from services.market.price_model import get_price_history, get_real_anchor_price
    from services.pipeline_context import GeographyLevel, PipelineContext

    levels = [GeographyLevel.LOCAL, GeographyLevel.SUB_NATIONAL, GeographyLevel.NATIONAL]
    results: dict[str, dict] = {}

    for cc in ALL_COUNTRIES:
        real_anchor = await get_real_anchor_price(COMMODITY, cc)
        raw_history = get_price_history(COMMODITY, cc, days=60, real_anchor=real_anchor)
        historical_data = [
            PriceDataPoint(date=datetime.strptime(h["date"], "%Y-%m-%d"), price=h["price_usd"], currency="USD")
            for h in raw_history
        ]
        results[cc] = {"real_anchor": real_anchor, "levels": {}}
        for level in levels:
            context = PipelineContext(country_code=cc, commodity=COMMODITY, geography_level=level)
            forecaster = PriceForecaster()
            try:
                await forecaster.fit(historical_data, context)
                forecast = await forecaster.forecast_price(context, horizon_days=5)
                results[cc]["levels"][level.value] = {
                    "mean_confidence": round(forecast.mean_confidence, 4),
                    "model_type": forecast.model_type.value,
                    "first_value": round(forecast.forecast_points[0].value, 2),
                }
            except Exception as e:  # real, unmocked call - report the failure, don't hide it
                results[cc]["levels"][level.value] = {"error": str(e)}

    return results


if __name__ == "__main__":
    results = asyncio.run(audit_geography_levels())
    print(f"\n{'country':<9}{'tier':<12}{'level':<14}{'model':<10}{'confidence':>12}{'value':>10}")
    for cc in ALL_COUNTRIES:
        tier = "data-rich" if cc in DATA_RICH else "data-sparse"
        for level_name, d in results[cc]["levels"].items():
            if "error" in d:
                print(f"{cc:<9}{tier:<12}{level_name:<14}ERROR: {d['error']}")
            else:
                print(f"{cc:<9}{tier:<12}{level_name:<14}{d['model_type']:<10}{d['mean_confidence']:>12}{d['first_value']:>10}")
