"""Phase 0 -> Experiment E1's second real run: extends run_e1_forecast.py
with the weather modality, now that it has a real multi-year time series
too (collect_weather_history.py). A new, separate script rather than an
edit to run_e1_forecast.py - that script's own result is already
documented and investigated in the blueprint's tenth/eleventh slices;
this one is a genuinely new, later increment, not a silent revision of
an already-reported number.

**Tiers actually run** (not the full blueprint T0-T4 ladder): T0
(price alone), T1 (price + weather: temperature and precipitation),
and T3 (price + weather + production) - T2 (+trade) is skipped, since
trade still has no real time series (blocked on its own quota-limited
collection, see the blueprint's third/fifth slices). Every tier is the
same simple model family (ordinary least squares) differing only in
feature set, same discipline as run_e1_forecast.py: T0 uses year t-1's
price; T1 adds year t-1's temperature and precipitation; T3 adds year
t-1's yield on top of that. Time-ordered holdout (last ~20% of each
series' real years), no random shuffle - a real backtest.

Same 6 (country, commodity) series as before (KE/RW x coffee/maize/
tea) - SS/SO still excluded, same reason: no real observed price to
forecast against.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/run_e1_forecast_tiers.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from provenance import DataState  # noqa: E402

COUNTRIES = ["KE", "RW"]
COMMODITIES = ["coffee", "maize", "tea"]
_MIN_YEARS_FOR_SPLIT = 8
_TIERS = ["t0_price", "t1_price_weather", "t3_price_weather_production"]


def _latest_file(data_dir: Path, prefix: str) -> Path:
    candidates = list(data_dir.glob(f"{prefix}_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No files matching {prefix}_*.json in {data_dir}")
    ts_re = re.compile(r"(\d{8}_\d{6})\.json$")
    return max(candidates, key=lambda p: ts_re.search(p.name).group(1))


def _load_commodity_series(path: Path) -> dict[tuple[str, str], dict[int, float]]:
    """(country, commodity) -> {year: value}, OBSERVED_VERIFIED rows only."""
    rows = json.loads(path.read_text(encoding="utf-8"))
    series: dict[tuple[str, str], dict[int, float]] = defaultdict(dict)
    for row in rows:
        if row["data_state"] != DataState.OBSERVED_VERIFIED.value:
            continue
        key = (row["country_code"], row["commodity"])
        year = int(row["observation_date"][:4])
        series[key][year] = row["value"]
    return series


def _load_weather_series(path: Path) -> dict[str, dict[str, dict[int, float]]]:
    """country -> variable -> {year: value} (weather has no commodity)."""
    rows = json.loads(path.read_text(encoding="utf-8"))
    series: dict[str, dict[str, dict[int, float]]] = defaultdict(lambda: defaultdict(dict))
    for row in rows:
        if row["data_state"] != DataState.OBSERVED_VERIFIED.value:
            continue
        year = int(row["observation_date"][:4])
        series[row["country_code"]][row["variable"]][year] = row["value"]
    return series


def _metrics(y_true: np.ndarray, y_pred: np.ndarray, prev: np.ndarray) -> dict[str, float]:
    errors = y_true - y_pred
    actual_dir = np.sign(y_true - prev)
    pred_dir = np.sign(y_pred - prev)
    return {
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(errors**2))),
        "mape": float(np.mean(np.abs(errors / y_true)) * 100),
        "directional_accuracy": float(np.mean(actual_dir == pred_dir)),
    }


def _build_xy(
    target_years: list[int], price: dict[int, float],
    temp: dict[int, float], precip: dict[int, float],
    production: dict[int, float], tier: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    X, y, prev = [], [], []
    for yr in target_years:
        lag = yr - 1
        if lag not in price:
            continue
        row = [price[lag]]
        if tier in ("t1_price_weather", "t3_price_weather_production"):
            if lag not in temp or lag not in precip:
                continue
            row += [temp[lag], precip[lag]]
        if tier == "t3_price_weather_production":
            if lag not in production:
                continue
            row.append(production[lag])
        X.append(row)
        y.append(price[yr])
        prev.append(price[lag])
    if len(y) < 2:
        return None
    return np.array(X), np.array(y), np.array(prev)


def run_one_series(
    price: dict[int, float], temp: dict[int, float], precip: dict[int, float], production: dict[int, float]
) -> tuple[int, int, dict[str, dict[str, float]]] | None:
    years = sorted(y for y in price if y - 1 in price)
    if len(years) < _MIN_YEARS_FOR_SPLIT:
        return None

    n_test = max(2, round(len(years) * 0.2))
    train_years, test_years = years[:-n_test], years[-n_test:]
    if len(train_years) < 3:
        return None

    results: dict[str, dict[str, float]] = {}
    for tier in _TIERS:
        train = _build_xy(train_years, price, temp, precip, production, tier)
        test = _build_xy(test_years, price, temp, precip, production, tier)
        if train is None or test is None:
            continue
        X_train, y_train, _ = train
        X_test, y_test, prev_test = test
        model = LinearRegression().fit(X_train, y_train)
        y_pred = model.predict(X_test)
        results[tier] = _metrics(y_test, y_pred, prev_test)

    if len(results) < 2:
        return None
    return len(train_years), len(test_years), results


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    price_series = _load_commodity_series(_latest_file(data_dir, "gold_standard_price_history"))
    production_series = _load_commodity_series(_latest_file(data_dir, "gold_standard_production_history"))
    weather_series = _load_weather_series(_latest_file(data_dir, "gold_standard_weather_history"))

    per_series: dict[str, dict[str, dict[str, float]]] = {}
    for cc in COUNTRIES:
        temp = weather_series.get(cc, {}).get("temperature_2m", {})
        precip = weather_series.get(cc, {}).get("precipitation_corrected", {})
        for comm in COMMODITIES:
            key = (cc, comm)
            price = price_series.get(key, {})
            production = production_series.get(key, {})
            result = run_one_series(price, temp, precip, production)
            label = f"{cc} {comm}"
            if result is None:
                print(f"{label}: skipped (insufficient real aligned data)")
                continue
            n_train, n_test, results = result
            per_series[label] = results
            parts = [f"n_train={n_train} n_test={n_test}"]
            for tier in _TIERS:
                if tier in results:
                    m = results[tier]
                    parts.append(f"{tier}: MAPE={m['mape']:.1f}% dir={m['directional_accuracy']:.2f}")
            print(f"{label}: " + " | ".join(parts))

    if not per_series:
        print("\nNo series had enough real aligned data to run - nothing to aggregate.")
        return

    print(f"\n{'=' * 70}\nAggregate across series with each tier available:\n{'=' * 70}")
    for metric in ["mae", "rmse", "mape", "directional_accuracy"]:
        row = []
        for tier in _TIERS:
            values = [r[tier][metric] for r in per_series.values() if tier in r]
            if values:
                row.append(f"{tier}={np.mean(values):.3f} (n={len(values)})")
        print(f"  {metric:22s}  " + "   ".join(row))


if __name__ == "__main__":
    main()
