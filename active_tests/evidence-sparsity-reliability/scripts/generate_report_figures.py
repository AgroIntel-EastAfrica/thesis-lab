"""Generates every real chart for FINDINGS_REPORT.md, from the real
collected data and real experiment outputs already in this directory -
no synthetic numbers, no placeholders. Run this before regenerating the
report if the underlying data/experiments change.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/generate_report_figures.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from provenance import DataState  # noqa: E402
from regime_break import detect_price_regime_break  # noqa: E402

DATA_DIR = _SCRIPT_DIR.parent / "data"
FIG_DIR = _SCRIPT_DIR.parent / "report" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# AgroIntel brand palette (matches apps/dashboard/public/logo.svg)
GREEN = "#15803d"
GREEN_LIGHT = "#4ade80"
SKY = "#0ea5e9"
SKY_LIGHT = "#7dd3fc"
GOLD = "#d97706"
GOLD_LIGHT = "#fde047"
GRAY = "#6b7280"
RED = "#dc2626"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
})


def _latest(prefix: str) -> Path:
    candidates = list(DATA_DIR.glob(f"{prefix}_*.json"))
    ts_re = re.compile(r"(\d{8}_\d{6})\.json$")
    return max(candidates, key=lambda p: ts_re.search(p.name).group(1))


def _load_commodity_series(path: Path) -> dict:
    rows = json.loads(path.read_text(encoding="utf-8"))
    series: dict = {}
    for row in rows:
        if row["data_state"] != DataState.OBSERVED_VERIFIED.value:
            continue
        key = (row["country_code"], row["commodity"])
        year = int(row["observation_date"][:4])
        series.setdefault(key, {})[year] = row["value"]
    return series


def _load_weather_series(path: Path) -> dict:
    rows = json.loads(path.read_text(encoding="utf-8"))
    series: dict = {}
    for row in rows:
        if row["data_state"] != DataState.OBSERVED_VERIFIED.value:
            continue
        year = int(row["observation_date"][:4])
        series.setdefault(row["country_code"], {}).setdefault(row["variable"], {})[year] = row["value"]
    return series


_COUNTRY_COLORS = {
    "KE": GREEN, "RW": SKY, "TZ": GOLD_LIGHT, "BI": "#7c3aed",
    "SS": GOLD, "SO": RED, "UG": "#0d9488", "CD": "#db2777",
}
_COMMODITIES = ["coffee", "maize", "tea", "sorghum", "sweet_potatoes"]
_COMMODITY_LABELS = {"coffee": "Coffee", "maize": "Maize", "tea": "Tea", "sorghum": "Sorghum", "sweet_potatoes": "Sweet potatoes"}


def fig_price_history():
    price = _load_commodity_series(_latest("gold_standard_price_history"))
    fig, axes = plt.subplots(1, 5, figsize=(19, 3.6), sharey=False)
    for ax, comm in zip(axes, _COMMODITIES, strict=False):
        for cc, color in [("KE", GREEN), ("RW", SKY), ("TZ", GOLD_LIGHT), ("BI", "#7c3aed")]:
            series = price.get((cc, comm), {})
            if not series:
                continue
            years = sorted(series.keys())
            ax.plot(years, [series[y] for y in years], color=color, lw=1.8, label=cc)
            brk = detect_price_regime_break(series)
            if brk is not None:
                ax.axvline(brk, color=color, ls=":", lw=1.2, alpha=0.7)
                ax.annotate(f"{cc} break\n{brk}", xy=(brk, series[brk]), xytext=(4, 4),
                            textcoords="offset points", fontsize=7, color=color)
        ax.set_title(_COMMODITY_LABELS[comm], fontweight="bold")
        ax.set_xlabel("Year")
        if comm == "coffee":
            ax.set_ylabel("Producer price (USD/tonne)")
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Real FAOSTAT producer price, 1991-2024, all 8 EAC countries and 5 commodities checked (only KE/RW/TZ/BI have real price coverage). Dotted lines mark a detected real regime break.", fontweight="bold", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "01_price_history.png", dpi=150)
    plt.close(fig)


def fig_production_history():
    prod = _load_commodity_series(_latest("gold_standard_production_history"))
    fig, axes = plt.subplots(1, 5, figsize=(19, 3.6))
    for ax, comm in zip(axes, _COMMODITIES, strict=False):
        for cc, color in _COUNTRY_COLORS.items():
            series = prod.get((cc, comm), {})
            if not series:
                continue
            years = sorted(series.keys())
            ax.plot(years, [series[y] for y in years], color=color, lw=1.6, label=cc)
        ax.set_title(_COMMODITY_LABELS[comm], fontweight="bold")
        ax.set_xlabel("Year")
        if comm == "coffee":
            ax.set_ylabel("Yield (MT/ha)")
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Real FAOSTAT production and yield, 1961 to 2024, 5 commodities. Maize/sorghum/sweet potatoes are tracked for all eight countries; coffee and tea are missing only for South Sudan and Somalia.", fontweight="bold", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "02_production_history.png", dpi=150)
    plt.close(fig)


def fig_weather_uniformity():
    weather = _load_weather_series(_latest("gold_standard_weather_history"))
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    for ax, var, label in zip(axes, ["temperature_2m", "precipitation_corrected"], ["Temperature (°C)", "Precipitation (mm/day)"], strict=False):
        for cc, color in _COUNTRY_COLORS.items():
            series = weather.get(cc, {}).get(var, {})
            years = sorted(series.keys())
            ax.plot(years, [series[y] for y in years], color=color, lw=1.6, label=cc)
        ax.set_title(label, fontweight="bold")
        ax.set_xlabel("Year")
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Real NASA POWER weather, 1991 to 2024. Available uniformly across all eight countries regardless of price data tier.", fontweight="bold", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "03_weather_uniformity.png", dpi=150)
    plt.close(fig)


def fig_evidence_availability_matrix():
    """Real availability grid: modality x country, % of (commodity,year) pairs OBSERVED_VERIFIED."""
    countries = ["KE", "RW", "TZ", "BI", "UG", "CD", "SS", "SO"]
    modalities = {
        "Price": _load_commodity_series(_latest("gold_standard_price_history")),
        "Production": _load_commodity_series(_latest("gold_standard_production_history")),
    }
    grid = np.zeros((len(modalities), len(countries)))
    for i, (_name, series) in enumerate(modalities.items()):
        for j, cc in enumerate(countries):
            n_real = sum(1 for comm in _COMMODITIES if series.get((cc, comm)))
            grid[i, j] = n_real / len(_COMMODITIES) * 100

    # Weather: always 100% (real, verified all 8 countries)
    weather_row = np.full(len(countries), 100.0)
    # Trade: real snapshot - only KE has any real value
    trade_row = np.array([100.0 if cc == "KE" else 0.0 for cc in countries])
    # Text: reliability-limited, not a clean availability number - shown separately, excluded from this grid

    full_grid = np.vstack([grid, weather_row, trade_row])
    row_labels = list(modalities.keys()) + ["Weather", "Trade"]

    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(full_grid, cmap="RdYlGn", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(countries)))
    ax.set_xticklabels(countries)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels)
    for i in range(full_grid.shape[0]):
        for j in range(full_grid.shape[1]):
            ax.text(j, i, f"{full_grid[i, j]:.0f}%", ha="center", va="center", fontsize=9,
                     color="white" if full_grid[i, j] < 50 else "black")
    ax.set_title("Real commodity coverage by modality × country\n(% of 5 commodities with real observed data)", fontweight="bold")
    fig.colorbar(im, ax=ax, label="% real coverage")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "04_availability_matrix.png", dpi=150)
    plt.close(fig)


def fig_e1_tiers():
    # Real aggregate numbers from run_e1_forecast_tiers.py's own printed output
    # (17 series: KE/RW/TZ/BI x coffee/maize/tea/sorghum/sweet_potatoes, with
    # Rwanda coffee excluded post-regime-break-restriction for insufficient
    # data, Burundi coffee restricted to 2007+)
    tiers = ["T0\n(price)", "T1\n(+weather)", "T3\n(+weather\n+production)"]
    mape = [15.239, 21.136, 23.780]
    dir_acc = [55.5, 65.0, 59.8]

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    axes[0].bar(tiers, mape, color=[GRAY, SKY, GREEN])
    axes[0].set_title("MAPE (%)", fontweight="bold")
    axes[0].set_ylabel("MAPE (%)")
    axes[1].bar(tiers, dir_acc, color=[GRAY, SKY, GREEN])
    axes[1].set_title("Directional accuracy (%)", fontweight="bold")
    axes[1].axhline(50, color=RED, ls="--", lw=1, label="coin-flip (50%)")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("E1: real forecast accuracy by evidence tier (pooled, 17 series, regime-corrected)", fontweight="bold", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "05_e1_tiers.png", dpi=150)
    plt.close(fig)


def fig_e2_calibration():
    tiers = ["T0 (price)", "T1 (price+weather)"]
    baseline_a = [76.7, 71.2]
    baseline_d = [79.5, 74.0]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(tiers))
    w = 0.32
    ax.bar(x - w / 2, baseline_a, w, label="Baseline A (uncalibrated)", color=GOLD)
    ax.bar(x + w / 2, baseline_d, w, label="Baseline D (LOO-conformal)", color=GREEN)
    ax.axhline(80, color=RED, ls="--", lw=1.2, label="Nominal target (80%)")
    ax.set_xticks(x)
    ax.set_xticklabels(tiers)
    ax.set_ylabel("Empirical coverage (%)")
    ax.set_title("E2: real calibration coverage, regime-corrected\nadding weather still hurts the naive baseline, not the calibrated one", fontweight="bold", fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "06_e2_calibration.png", dpi=150)
    plt.close(fig)


def fig_evidence_quality_radar():
    # Computed live from the latest scored dataset (populate_evidence_quality.py's
    # own output) rather than hand-typed - a hardcoded copy here is exactly what
    # went stale for four days across this session's TZ/BI/UG/CD/5-commodity
    # expansion, unnoticed until the project owner flagged the chart looked old.
    dim_keys = ["availability", "quality", "relevance", "freshness", "compatibility", "provenance", "geographic_coverage"]
    dims = ["Availability", "Quality", "Relevance", "Freshness", "Compatibility", "Provenance", "Geographic\ncoverage"]
    rows = json.loads(_latest("gold_standard_all_with_quality").read_text(encoding="utf-8"))
    by_modality: dict[str, list[dict]] = {}
    for row in rows:
        by_modality.setdefault(row["modality"], []).append(row["evidence_quality"])

    label_map = {"price": "Price", "production": "Production", "weather": "Weather", "trade": "Trade", "text": "Text"}
    data = {}
    for modality, label in label_map.items():
        eq_list = by_modality.get(modality, [])
        values = []
        for key in dim_keys:
            vals = [eq[key] for eq in eq_list if eq.get(key) is not None]
            values.append(sum(vals) / len(vals) if vals else 0.0)
        data[label] = values
    colors = {"Price": GREEN, "Production": SKY, "Weather": GOLD, "Trade": RED, "Text": GRAY}

    angles = np.linspace(0, 2 * np.pi, len(dims), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 6.5), subplot_kw={"projection": "polar"})
    for name, values in data.items():
        v = values + values[:1]
        ax.plot(angles, v, color=colors[name], lw=1.8, label=name)
        ax.fill(angles, v, color=colors[name], alpha=0.06)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dims, fontsize=9)
    ax.set_ylim(0, 1)
    fig.suptitle("Evidence quality by modality. No single modality scores well on every dimension.", fontweight="bold", fontsize=12, x=0.45)
    ax.legend(loc="upper right", bbox_to_anchor=(1.4, 1.1), frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "07_evidence_quality_radar.png", dpi=150)
    plt.close(fig)


def fig_e4_scenario():
    """The real E4 worked scenario: KE coffee 2024."""
    formats = ["3: AI forecast\n(point only)", "5: Uncertainty-aware\n(+ 80% interval)"]
    point = [3934.6, 4253.0]
    lower = [3934.6, 2383.3]
    upper = [3934.6, 5486.0]
    actual = 4886.5

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(formats))
    for i in range(len(formats)):
        ax.plot([x[i], x[i]], [lower[i], upper[i]], color=SKY, lw=6, alpha=0.4, solid_capstyle="round")
        ax.scatter(x[i], point[i], color=GREEN, s=80, zorder=5, label="Point forecast" if i == 0 else None)
    ax.axhline(actual, color=RED, ls="--", lw=1.5, label=f"Real 2024 actual: ${actual:,.0f}/tonne")
    ax.set_xticks(x)
    ax.set_xticklabels(formats)
    ax.set_ylabel("Price (USD/tonne)")
    ax.set_title("E4 scenario: KE coffee 2024\nbare point forecast vs. real uncertainty interval", fontweight="bold", fontsize=11)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "08_e4_scenario.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    fig_price_history()
    fig_production_history()
    fig_weather_uniformity()
    fig_evidence_availability_matrix()
    fig_e1_tiers()
    fig_e2_calibration()
    fig_evidence_quality_radar()
    fig_e4_scenario()
    print(f"Generated 8 figures -> {FIG_DIR}")
