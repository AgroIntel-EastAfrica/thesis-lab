"""Experiment E2's second real run: does adding evidence (not just
changing the point-forecast model) affect calibration quality?

run_e2_calibration.py tested T0 (price alone) only. This extends the
same two baselines (A: uncalibrated in-sample residuals, D: LOO-
conformal) to T1 (price + weather), using the same feature-building
pattern as run_e1_forecast_tiers.py. A genuinely new question from the
blueprint's E2 design ("record confidence, coverage, calibration error
per evidence level") - here "level" is evidence composition (T0 vs T1)
rather than sparsity percentage, since real sparsity-level data
doesn't exist yet (every modality is still a single real time series,
not resampled at multiple completeness levels).

Same 6 real KE/RW x coffee/maize/tea series, same time-ordered
holdout, same 80% nominal target as run_e2_calibration.py - a
comparable, not a new, benchmark.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/run_e2_calibration_tiers.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from provenance import DataState  # noqa: E402

COUNTRIES = ["KE", "RW"]
COMMODITIES = ["coffee", "maize", "tea"]
_MIN_YEARS_FOR_SPLIT = 8
_NOMINAL_CONFIDENCE = 0.80
_Z_80 = 1.2816
_TIERS = ["t0_price", "t1_price_weather"]


def _latest_file(data_dir: Path, prefix: str) -> Path:
    candidates = list(data_dir.glob(f"{prefix}_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No files matching {prefix}_*.json in {data_dir}")
    ts_re = re.compile(r"(\d{8}_\d{6})\.json$")
    return max(candidates, key=lambda p: ts_re.search(p.name).group(1))


def _load_commodity_series(path: Path) -> dict[tuple[str, str], dict[int, float]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    series: dict[tuple[str, str], dict[int, float]] = {}
    for row in rows:
        if row["data_state"] != DataState.OBSERVED_VERIFIED.value:
            continue
        key = (row["country_code"], row["commodity"])
        year = int(row["observation_date"][:4])
        series.setdefault(key, {})[year] = row["value"]
    return series


def _load_weather_series(path: Path) -> dict[str, dict[str, dict[int, float]]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    series: dict[str, dict[str, dict[int, float]]] = {}
    for row in rows:
        if row["data_state"] != DataState.OBSERVED_VERIFIED.value:
            continue
        year = int(row["observation_date"][:4])
        series.setdefault(row["country_code"], {}).setdefault(row["variable"], {})[year] = row["value"]
    return series


def _build_row(yr: int, price: dict, temp: dict, precip: dict, tier: str) -> list[float] | None:
    lag = yr - 1
    if lag not in price:
        return None
    row = [price[lag]]
    if tier == "t1_price_weather":
        if lag not in temp or lag not in precip:
            return None
        row += [temp[lag], precip[lag]]
    return row


def run_one_series(price: dict[int, float], temp: dict[int, float], precip: dict[int, float]) -> dict | None:
    years = sorted(y for y in price if y - 1 in price)
    if len(years) < _MIN_YEARS_FOR_SPLIT:
        return None

    n_test = max(2, round(len(years) * 0.2))
    train_years, test_years = years[:-n_test], years[-n_test:]
    if len(train_years) < 4:
        return None

    results: dict[str, dict] = {}
    for tier in _TIERS:
        X_train_rows, y_train = [], []
        for yr in train_years:
            row = _build_row(yr, price, temp, precip, tier)
            if row is None:
                continue
            X_train_rows.append(row)
            y_train.append(price[yr])
        if len(y_train) < 4:
            continue
        X_train = np.array(X_train_rows)
        y_train = np.array(y_train)

        model_full = LinearRegression().fit(X_train, y_train)
        sigma = float(np.std(y_train - model_full.predict(X_train), ddof=1))
        half_width_a = _Z_80 * sigma

        loo_abs = []
        for i in range(len(X_train)):
            mask = np.ones(len(X_train), dtype=bool)
            mask[i] = False
            m = LinearRegression().fit(X_train[mask], y_train[mask])
            loo_abs.append(abs(y_train[i] - m.predict(X_train[i].reshape(1, -1))[0]))
        half_width_d = float(np.percentile(loo_abs, _NOMINAL_CONFIDENCE * 100))

        covered_a, covered_d = [], []
        for yr in test_years:
            row = _build_row(yr, price, temp, precip, tier)
            if row is None:
                continue
            pred = float(model_full.predict(np.array(row).reshape(1, -1))[0])
            actual = price[yr]
            covered_a.append(abs(actual - pred) <= half_width_a)
            covered_d.append(abs(actual - pred) <= half_width_d)

        if covered_a:
            results[tier] = {"covered_a": covered_a, "covered_d": covered_d}

    if len(results) < 2:
        return None
    return {"n_train": len(train_years), "n_test": len(test_years), "results": results}


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    price_series = _load_commodity_series(_latest_file(data_dir, "gold_standard_price_history"))
    weather_series = _load_weather_series(_latest_file(data_dir, "gold_standard_weather_history"))

    pooled: dict[str, dict[str, list[bool]]] = {tier: {"a": [], "d": []} for tier in _TIERS}
    n_series = 0

    for cc in COUNTRIES:
        temp = weather_series.get(cc, {}).get("temperature_2m", {})
        precip = weather_series.get(cc, {}).get("precipitation_corrected", {})
        for comm in COMMODITIES:
            key = (cc, comm)
            result = run_one_series(price_series.get(key, {}), temp, precip)
            label = f"{cc} {comm}"
            if result is None:
                print(f"{label}: skipped (insufficient real aligned data)")
                continue
            n_series += 1
            parts = [f"n_train={result['n_train']} n_test={result['n_test']}"]
            for tier in _TIERS:
                if tier not in result["results"]:
                    continue
                r = result["results"][tier]
                cov_a = np.mean(r["covered_a"]) * 100
                cov_d = np.mean(r["covered_d"]) * 100
                pooled[tier]["a"].extend(r["covered_a"])
                pooled[tier]["d"].extend(r["covered_d"])
                parts.append(f"{tier}: A={cov_a:.0f}% D={cov_d:.0f}%")
            print(f"{label}: " + " | ".join(parts))

    if n_series == 0:
        print("\nNo series had enough real aligned data to run.")
        return

    nominal = _NOMINAL_CONFIDENCE * 100
    print(f"\n{'=' * 70}\nPooled coverage by tier, {n_series} series:\n{'=' * 70}")
    for tier in _TIERS:
        n = len(pooled[tier]["a"])
        if n == 0:
            continue
        cov_a = float(np.mean(pooled[tier]["a"])) * 100
        cov_d = float(np.mean(pooled[tier]["d"])) * 100
        print(
            f"  {tier:20s} (n={n:2d})  Baseline A: {cov_a:5.1f}% (miss {abs(cov_a - nominal):4.1f}pt)   "
            f"Baseline D: {cov_d:5.1f}% (miss {abs(cov_d - nominal):4.1f}pt)"
        )


if __name__ == "__main__":
    main()
