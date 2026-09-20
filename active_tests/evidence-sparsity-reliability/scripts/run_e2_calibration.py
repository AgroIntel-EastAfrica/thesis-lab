"""Experiment E2's first real run: uncertainty and calibration.

Tests H3 (calibration): confidence becomes less reliable as evidence
quality/availability deteriorates, unless uncertainty is explicitly
calibrated. Directly checked against the pre-registered criterion in
the blueprint's Success Metrics section, itself grounded in a real
prior number - the concluded regional-equity-audit experiment found
80% stated confidence vs. 38.5% observed interval coverage, a real
41.5-point miss. Supported if a calibrated baseline lands within 10
points of its 80% nominal target while an uncalibrated baseline misses
by more than 20 points.

**Two baselines, same T0 (price-only) model as run_e1_forecast.py** -
an ordinary least squares fit on year t-1's price predicting year t's
price - so a coverage difference reflects the *uncertainty method*,
not a different underlying forecast:

- **Baseline A (uncalibrated)**: the naive, common real-world mistake -
  use the model's own IN-SAMPLE training-residual spread as its
  confidence interval (pred +/- 1.2816*sigma for a nominal 80%
  two-sided interval, no held-out data). This is deliberately the
  failure mode: training error understates true predictive
  uncertainty, especially on n=9-24 point series, which is exactly
  the mechanism behind real overconfidence problems like the concluded
  experiment's 80%-vs-38.5% gap.
- **Baseline D (calibrated, distribution-free)**: leave-one-out (LOO)
  conformal-style intervals - for each training point, refit on every
  OTHER training point, collect that point's held-out residual, then
  use the 80th percentile of all these LOO residuals as a single
  interval half-width applied to every test prediction. Distribution-
  free (no normality assumption) and does not require a separate
  calibration split, which matters given how small these series are.

Same 6 real KE/RW x coffee/maize/tea series as E1, same time-ordered
holdout (never random shuffle) - a real backtest, not a leaky one.
Given each series' own test set is only 2-6 points, coverage is also
reported POOLED across all 6 series (36 total test points) for a more
statistically meaningful number than any single series' own coverage.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/run_e2_calibration.py
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
_Z_80 = 1.2816  # two-sided z-score for 80% nominal coverage


def _latest_file(data_dir: Path, prefix: str) -> Path:
    candidates = list(data_dir.glob(f"{prefix}_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No files matching {prefix}_*.json in {data_dir}")
    ts_re = re.compile(r"(\d{8}_\d{6})\.json$")
    return max(candidates, key=lambda p: ts_re.search(p.name).group(1))


def _load_series(path: Path) -> dict[tuple[str, str], dict[int, float]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    series: dict[tuple[str, str], dict[int, float]] = {}
    for row in rows:
        if row["data_state"] != DataState.OBSERVED_VERIFIED.value:
            continue
        key = (row["country_code"], row["commodity"])
        year = int(row["observation_date"][:4])
        series.setdefault(key, {})[year] = row["value"]
    return series


def _fit_predict(train_X: np.ndarray, train_y: np.ndarray, x: np.ndarray) -> float:
    model = LinearRegression().fit(train_X, train_y)
    return float(model.predict(x.reshape(1, -1))[0])


def run_one_series(price: dict[int, float]) -> dict | None:
    years = sorted(y for y in price if y - 1 in price)
    if len(years) < _MIN_YEARS_FOR_SPLIT:
        return None

    n_test = max(2, round(len(years) * 0.2))
    train_years, test_years = years[:-n_test], years[-n_test:]
    if len(train_years) < 4:
        return None

    X_train = np.array([[price[yr - 1]] for yr in train_years])
    y_train = np.array([price[yr] for yr in train_years])

    # Baseline A: in-sample training residuals, no held-out data.
    model_full = LinearRegression().fit(X_train, y_train)
    in_sample_pred = model_full.predict(X_train)
    sigma = float(np.std(y_train - in_sample_pred, ddof=1)) if len(y_train) > 1 else 0.0
    half_width_a = _Z_80 * sigma

    # Baseline D: leave-one-out residuals -> 80th percentile as half-width.
    loo_abs_residuals = []
    for i in range(len(train_years)):
        mask = np.ones(len(train_years), dtype=bool)
        mask[i] = False
        pred_i = _fit_predict(X_train[mask], y_train[mask], X_train[i])
        loo_abs_residuals.append(abs(y_train[i] - pred_i))
    half_width_d = float(np.percentile(loo_abs_residuals, _NOMINAL_CONFIDENCE * 100))

    covered_a, covered_d, widths_a, widths_d = [], [], [], []
    for yr in test_years:
        pred = _fit_predict(X_train, y_train, np.array([price[yr - 1]]))
        actual = price[yr]
        covered_a.append(abs(actual - pred) <= half_width_a)
        covered_d.append(abs(actual - pred) <= half_width_d)
        widths_a.append(2 * half_width_a)
        widths_d.append(2 * half_width_d)

    return {
        "n_train": len(train_years),
        "n_test": len(test_years),
        "covered_a": covered_a,
        "covered_d": covered_d,
        "width_a": float(np.mean(widths_a)),
        "width_d": float(np.mean(widths_d)),
    }


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    price_series = _load_series(_latest_file(data_dir, "gold_standard_price_history"))

    all_covered_a: list[bool] = []
    all_covered_d: list[bool] = []
    per_series = {}

    for cc in COUNTRIES:
        for comm in COMMODITIES:
            key = (cc, comm)
            result = run_one_series(price_series.get(key, {}))
            label = f"{cc} {comm}"
            if result is None:
                print(f"{label}: skipped (insufficient real aligned data)")
                continue
            per_series[label] = result
            all_covered_a.extend(result["covered_a"])
            all_covered_d.extend(result["covered_d"])
            cov_a = np.mean(result["covered_a"]) * 100
            cov_d = np.mean(result["covered_d"]) * 100
            print(
                f"{label}: n_train={result['n_train']} n_test={result['n_test']} | "
                f"Baseline A (uncalibrated): coverage={cov_a:.0f}% width={result['width_a']:.1f} | "
                f"Baseline D (LOO-conformal): coverage={cov_d:.0f}% width={result['width_d']:.1f}"
            )

    if not per_series:
        print("\nNo series had enough real aligned data to run.")
        return

    n = len(all_covered_a)
    pooled_a = float(np.mean(all_covered_a)) * 100
    pooled_d = float(np.mean(all_covered_d)) * 100
    nominal = _NOMINAL_CONFIDENCE * 100

    print(f"\n{'=' * 70}\nPooled coverage across {n} real test points, {len(per_series)} series:\n{'=' * 70}")
    print(f"  Nominal target:              {nominal:.0f}%")
    print(f"  Baseline A (uncalibrated):   {pooled_a:.1f}%  (miss: {abs(pooled_a - nominal):.1f} points)")
    print(f"  Baseline D (LOO-conformal):  {pooled_d:.1f}%  (miss: {abs(pooled_d - nominal):.1f} points)")

    print("\nH3 criterion check (calibrated within 10pts, uncalibrated misses by >20pts):")
    a_miss = abs(pooled_a - nominal)
    d_miss = abs(pooled_d - nominal)
    print(f"  Baseline D within 10pts of nominal: {'YES' if d_miss <= 10 else 'NO'} ({d_miss:.1f}pt miss)")
    print(f"  Baseline A misses by more than 20pts: {'YES' if a_miss > 20 else 'NO'} ({a_miss:.1f}pt miss)")
    print(f"  H3 supported by this run: {'YES' if (d_miss <= 10 and a_miss > 20) else 'NOT (on this evidence alone)'}")


if __name__ == "__main__":
    main()
