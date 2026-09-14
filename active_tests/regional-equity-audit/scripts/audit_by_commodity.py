"""Real, read-only audit: does forecast reliability vary by commodity,
independent of country? Phase 2a's provenance/transparency check already
closed that axis; this is Phase 2's commodity axis (see the
"Scope completeness check" section of experiment_blueprint.md) - the same
forecast_evaluations rows used for the country-tier and calibration
findings, re-sliced by commodity instead of by country. No new data
source needed.

Reads only. Never writes to production.

Run from the repo root: python thesis-lab/active_tests/regional-equity-audit/scripts/audit_by_commodity.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))


def _mape(actual: float, predicted: float) -> float | None:
    if actual == 0:
        return None
    return abs(actual - predicted) / abs(actual) * 100


def audit_by_commodity() -> dict[str, dict]:
    from apps.api.config import get_supabase

    supabase = get_supabase()
    result = (
        supabase.table("forecast_evaluations")
        .select("country_code,commodity,predicted_price,predicted_lower,predicted_upper,actual_price")
        .not_.is_("actual_price", None)
        .execute()
    )
    rows = result.data or []

    by_commodity: dict[str, dict] = {}
    for row in rows:
        comm = row.get("commodity")
        if not comm:
            continue
        d = by_commodity.setdefault(comm, {"n": 0, "mapes": [], "covered": 0, "with_bounds": 0, "countries": set()})
        actual = row.get("actual_price")
        predicted = row.get("predicted_price")
        if actual is None or predicted is None:
            continue
        d["n"] += 1
        d["countries"].add(row.get("country_code"))
        m = _mape(float(actual), float(predicted))
        if m is not None:
            d["mapes"].append(m)
        lower, upper = row.get("predicted_lower"), row.get("predicted_upper")
        if lower is not None and upper is not None:
            d["with_bounds"] += 1
            if float(lower) <= float(actual) <= float(upper):
                d["covered"] += 1

    summary = {}
    for comm, d in by_commodity.items():
        avg_mape = sum(d["mapes"]) / len(d["mapes"]) if d["mapes"] else None
        coverage = d["covered"] / d["with_bounds"] if d["with_bounds"] else None
        summary[comm] = {
            "n_evaluated": d["n"],
            "n_countries": len(d["countries"]),
            "countries": sorted(d["countries"]),
            "avg_mape": round(avg_mape, 2) if avg_mape is not None else None,
            "n_with_bounds": d["with_bounds"],
            "interval_coverage_rate": round(coverage, 4) if coverage is not None else None,
        }
    return summary


if __name__ == "__main__":
    summary = audit_by_commodity()
    print(f"\n{'commodity':<16}{'n':>5}{'countries':>11}{'avg_mape':>10}{'coverage':>10}{'w/bounds':>10}")
    for comm, d in sorted(summary.items(), key=lambda kv: -(kv[1]["avg_mape"] or 0)):
        mape_s = f"{d['avg_mape']:.2f}" if d["avg_mape"] is not None else "n/a"
        cov_s = f"{d['interval_coverage_rate']:.3f}" if d["interval_coverage_rate"] is not None else "n/a"
        print(f"{comm:<16}{d['n_evaluated']:>5}{d['n_countries']:>11}{mape_s:>10}{cov_s:>10}{d['n_with_bounds']:>10}")
    print(f"\ntotal commodities: {len(summary)}")
