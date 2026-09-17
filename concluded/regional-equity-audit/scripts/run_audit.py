"""Real, read-only audit: does AgroIntel's real data-availability gap
(KE/TZ/RW/BI have real FAOSTAT PP coverage; UG/SS/SO/CD fall back to
BASE_PRICES_USD - see memory project_faostat_prices) translate into a
real accuracy/service-quality gap?

Reads only. Never writes to production. Two real sources:
  1. forecast_evaluations (migration 046) - real evaluated forecasts
     with actual_price recorded, grouped by country: count, MAPE, and
     real interval-coverage rate (does actual_price fall inside
     [predicted_lower, predicted_upper] when both are present?). This
     doubles as the data-volume check for forecast-confidence-
     calibration (Paper 5) - same table, same query.
  2. RecommendationEngine.get_recommendations() called live per country
     - confidence, evidence_sufficient rate, supporting_signals.

Run from the repo root: python thesis-lab/active_tests/regional-equity-audit/scripts/run_audit.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

DATA_RICH = ["KE", "TZ", "RW", "BI"]
DATA_SPARSE = ["UG", "SS", "SO", "CD"]
ALL_COUNTRIES = DATA_RICH + DATA_SPARSE


def _mape(actual: float, predicted: float) -> float | None:
    if actual == 0:
        return None
    return abs(actual - predicted) / abs(actual) * 100


def audit_forecast_evaluations() -> dict[str, dict]:
    """Real, read-only MAPE/coverage per country.

    Migration 048 (2026-09-17) added source_mismatch, a generated column
    flagging rows where predicted_price and actual_price were computed
    under two different, non-comparable price bases (e.g. a synthetic
    BASE_PRICES_USD anchor vs. a real FAOSTAT farm-gate price) — exactly
    the cause of the RW/BI 881-1186% MAPE anomaly this audit found and
    traced. Rows flagged True are excluded from avg_mape/coverage (a
    basis mismatch isn't a forecast error) but still counted separately
    and surfaced (n_source_mismatch), never silently dropped — matching
    this audit's own transparency-over-silent-equalizing principle.
    source_mismatch is NULL (not True) for any row predating this
    migration or missing either source; those still count normally,
    since "unknown" isn't evidence of a mismatch.
    """
    from apps.api.config import get_supabase

    supabase = get_supabase()
    result = (
        supabase.table("forecast_evaluations")
        .select(
            "country_code,commodity,predicted_price,predicted_lower,predicted_upper,"
            "actual_price,source_mismatch"
        )
        .not_.is_("actual_price", None)
        .execute()
    )
    rows = result.data or []

    by_country: dict[str, dict] = {
        cc: {"n": 0, "mapes": [], "covered": 0, "with_bounds": 0, "source_mismatch": 0} for cc in ALL_COUNTRIES
    }
    for row in rows:
        cc = row.get("country_code")
        if cc not in by_country:
            continue
        actual = row.get("actual_price")
        predicted = row.get("predicted_price")
        if actual is None or predicted is None:
            continue
        if row.get("source_mismatch") is True:
            by_country[cc]["source_mismatch"] += 1
            continue  # excluded from n/mapes/coverage below - not a real forecast error
        by_country[cc]["n"] += 1
        m = _mape(float(actual), float(predicted))
        if m is not None:
            by_country[cc]["mapes"].append(m)
        lower, upper = row.get("predicted_lower"), row.get("predicted_upper")
        if lower is not None and upper is not None:
            by_country[cc]["with_bounds"] += 1
            if float(lower) <= float(actual) <= float(upper):
                by_country[cc]["covered"] += 1

    summary = {}
    for cc, d in by_country.items():
        avg_mape = sum(d["mapes"]) / len(d["mapes"]) if d["mapes"] else None
        coverage = d["covered"] / d["with_bounds"] if d["with_bounds"] else None
        summary[cc] = {
            "n_evaluated": d["n"],
            "n_source_mismatch_excluded": d["source_mismatch"],
            "avg_mape": avg_mape,
            "n_with_bounds": d["with_bounds"],
            "interval_coverage_rate": coverage,
        }
    return summary


def audit_recommendations() -> dict[str, dict]:
    from services.intelligence.recommendations import RecommendationEngine

    engine = RecommendationEngine()
    summary = {}
    for cc in ALL_COUNTRIES:
        try:
            result = engine.get_recommendations(country_code=cc, limit=1000)
            recs = result.data.get("recommendations", []) if result.is_success() and result.data else []
        except Exception as e:  # real, unmocked call - report the failure, don't hide it
            summary[cc] = {"error": str(e)}
            continue
        if not recs:
            summary[cc] = {"n_recs": 0, "avg_confidence": None, "evidence_sufficient_rate": None,
                           "avg_supporting_signals": None}
            continue
        confidences = [r["confidence"] for r in recs if r.get("confidence") is not None]
        sufficient = [r for r in recs if "evidence_sufficient" in r]
        supporting = [r["supporting_signals"] for r in recs if r.get("supporting_signals") is not None]
        summary[cc] = {
            "n_recs": len(recs),
            "avg_confidence": sum(confidences) / len(confidences) if confidences else None,
            "evidence_sufficient_rate": (
                sum(1 for r in sufficient if r["evidence_sufficient"]) / len(sufficient) if sufficient else None
            ),
            "avg_supporting_signals": sum(supporting) / len(supporting) if supporting else None,
        }
    return summary


def _group_avg(per_country: dict[str, dict], field: str, group: list[str]) -> float | None:
    vals = [per_country[cc][field] for cc in group if per_country.get(cc, {}).get(field) is not None]
    return sum(vals) / len(vals) if vals else None


def main() -> None:
    print("=== forecast_evaluations audit (real, read-only) ===")
    fc = audit_forecast_evaluations()
    for cc in ALL_COUNTRIES:
        print(f"  {cc}: {fc[cc]}")
    print(f"  data-rich (KE/TZ/RW/BI) avg MAPE: {_group_avg(fc, 'avg_mape', DATA_RICH)}")
    print(f"  data-sparse (UG/SS/SO/CD) avg MAPE: {_group_avg(fc, 'avg_mape', DATA_SPARSE)}")
    print(f"  data-rich avg interval coverage: {_group_avg(fc, 'interval_coverage_rate', DATA_RICH)}")
    print(f"  data-sparse avg interval coverage: {_group_avg(fc, 'interval_coverage_rate', DATA_SPARSE)}")

    print("\n=== RecommendationEngine audit (real, live call) ===")
    rc = audit_recommendations()
    for cc in ALL_COUNTRIES:
        print(f"  {cc}: {rc[cc]}")
    print(f"  data-rich avg confidence: {_group_avg(rc, 'avg_confidence', DATA_RICH)}")
    print(f"  data-sparse avg confidence: {_group_avg(rc, 'avg_confidence', DATA_SPARSE)}")
    print(f"  data-rich avg evidence_sufficient_rate: {_group_avg(rc, 'evidence_sufficient_rate', DATA_RICH)}")
    print(f"  data-sparse avg evidence_sufficient_rate: {_group_avg(rc, 'evidence_sufficient_rate', DATA_SPARSE)}")


if __name__ == "__main__":
    main()
