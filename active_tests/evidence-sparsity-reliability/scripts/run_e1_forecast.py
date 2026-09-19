"""Phase 0 -> Experiment E1's first real run: does adding a second real
evidence modality (production) reduce price-forecast error versus price
alone?

**A real, honest scope narrowing, stated up front**: the blueprint's
Success Metrics section names 30-day price forecasting as the primary
task. No modality collected so far has real daily/monthly historical
series - FAOSTAT PP/QCL (the only two modalities with any real time
series yet) are both annual publications. This script runs *annual*
next-year price forecasting instead, on the only real historical data
that exists. That is a genuinely different, narrower task than the
blueprint's stated one, not silently substituted for it - 30-day
forecasting is real future work, blocked on a modality with real daily/
monthly ground truth (none collected yet).

**Design**: only T0 (price alone) vs. price+production is tested -
not the full T0-T4 tier ladder, because weather/trade/text have no
real historical series yet (single-snapshot only, see the blueprint's
Phase 0 ninth-slice writeup) and fabricating synthetic history for
them would violate this whole experiment's founding rule (never treat
synthetic as observed ground truth). Both models are deliberately the
same simple family (ordinary least squares) differing only in feature
set, so an accuracy difference reflects the evidence added, not a
fancier model - T0 (price alone) predicts year t's price from year
t-1's price; T0+Production adds year t-1's yield as a second feature.
Time-ordered holdout (last ~20% of each series' real years, never
random shuffle) - a real backtest, not a leaky one.

Only run for KE/RW x coffee/maize/tea: the 6 (country, commodity)
pairs with real, non-empty price AND production histories. SS/SO are
excluded from this run, not silently dropped - both are OBSERVED_
UNKNOWN for the price modality (synthetic-baseline territory), and
this experiment's core rule is that only real observed data may be a
forecasting target.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/run_e1_forecast.py
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


def _latest_file(data_dir: Path, prefix: str) -> Path:
    candidates = list(data_dir.glob(f"{prefix}_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No files matching {prefix}_*.json in {data_dir}")
    ts_re = re.compile(r"(\d{8}_\d{6})\.json$")
    return max(candidates, key=lambda p: ts_re.search(p.name).group(1))


def _load_series(path: Path) -> dict[tuple[str, str], dict[int, float]]:
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


def _metrics(y_true: np.ndarray, y_pred: np.ndarray, prev: np.ndarray) -> dict[str, float]:
    errors = y_true - y_pred
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors**2)))
    mape = float(np.mean(np.abs(errors / y_true)) * 100)
    actual_dir = np.sign(y_true - prev)
    pred_dir = np.sign(y_pred - prev)
    directional_accuracy = float(np.mean(actual_dir == pred_dir))
    return {"mae": mae, "rmse": rmse, "mape": mape, "directional_accuracy": directional_accuracy}


def run_one_series(
    price: dict[int, float], production: dict[int, float]
) -> tuple[int, int, dict[str, float], dict[str, float]] | None:
    years = sorted(y for y in price if y - 1 in price)  # need lag-1 price
    if len(years) < _MIN_YEARS_FOR_SPLIT:
        return None

    n_test = max(2, round(len(years) * 0.2))
    train_years, test_years = years[:-n_test], years[-n_test:]
    if len(train_years) < 3:
        return None

    def build_xy(target_years: list[int], with_production: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
        X, y, prev = [], [], []
        for yr in target_years:
            lag_price = price[yr - 1]
            if with_production:
                if (yr - 1) not in production:
                    continue
                X.append([lag_price, production[yr - 1]])
            else:
                X.append([lag_price])
            y.append(price[yr])
            prev.append(lag_price)
        if len(y) < 2:
            return None
        return np.array(X), np.array(y), np.array(prev)

    results: dict[str, dict[str, float]] = {}
    for label, with_prod in [("t0_price_only", False), ("t0_plus_production", True)]:
        train = build_xy(train_years, with_prod)
        test = build_xy(test_years, with_prod)
        if train is None or test is None:
            continue
        X_train, y_train, _ = train
        X_test, y_test, prev_test = test
        model = LinearRegression().fit(X_train, y_train)
        y_pred = model.predict(X_test)
        results[label] = _metrics(y_test, y_pred, prev_test)

    if "t0_price_only" not in results or "t0_plus_production" not in results:
        return None
    return len(train_years), len(test_years), results["t0_price_only"], results["t0_plus_production"]


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    price_series = _load_series(_latest_file(data_dir, "gold_standard_price_history"))
    production_series = _load_series(_latest_file(data_dir, "gold_standard_production_history"))

    per_series: dict[str, tuple[dict[str, float], dict[str, float]]] = {}
    for cc in COUNTRIES:
        for comm in COMMODITIES:
            key = (cc, comm)
            price = price_series.get(key, {})
            production = production_series.get(key, {})
            result = run_one_series(price, production)
            label = f"{cc} {comm}"
            if result is None:
                print(f"{label}: skipped (insufficient real aligned data)")
                continue
            n_train, n_test, t0, t0p = result
            per_series[label] = (t0, t0p)
            print(
                f"{label}: n_train={n_train} n_test={n_test} | "
                f"T0 MAE={t0['mae']:.2f} RMSE={t0['rmse']:.2f} MAPE={t0['mape']:.1f}% dir={t0['directional_accuracy']:.2f} | "
                f"T0+Prod MAE={t0p['mae']:.2f} RMSE={t0p['rmse']:.2f} MAPE={t0p['mape']:.1f}% dir={t0p['directional_accuracy']:.2f}"
            )

    if not per_series:
        print("\nNo series had enough real aligned data to run - nothing to aggregate.")
        return

    print(f"\n{'=' * 70}\nAggregate across {len(per_series)} real series:\n{'=' * 70}")
    for metric in ["mae", "rmse", "mape", "directional_accuracy"]:
        t0_mean = np.mean([t0[metric] for t0, _ in per_series.values()])
        t0p_mean = np.mean([t0p[metric] for _, t0p in per_series.values()])
        better = "T0+Production" if (t0p_mean < t0_mean if metric != "directional_accuracy" else t0p_mean > t0_mean) else "T0 (price only)"
        print(f"  {metric:22s}  T0={t0_mean:8.3f}   T0+Production={t0p_mean:8.3f}   better: {better}")


if __name__ == "__main__":
    main()
