"""Phase 0, seventh slice: a first, explicit, inspectable rubric for
EvidenceQualityVector's 7 dimensions (A, Q, R, F, C, P, G), now that all
5 planned modalities have real, live-collected data to ground it in.

This is a constructed measurement instrument, not a physical constant -
every number below is a principled Phase 0 ESTIMATE, justified inline
against a real fact this session established (an actual login flow, an
actual observed success rate, an actual documented structural weakness),
never guessed to look complete. It is deliberately a flat, readable
lookup table rather than a learned or black-box score, so a later pass
can inspect, argue with, and revise any single number without touching
the others. Anything not yet real-data-computable stays a per-dimension
default rather than being silently invented.

Per-dimension approach:
  A (availability)  - mechanical, from DataState. The one dimension that
                       needs no judgment call: it already IS this
                       experiment's core instrument (see provenance.py).
  Q (quality)        - modality-level, from each source's real observed
                       reliability THIS session (a clean 403/a clean
                       200-zero-rows vs. GDELT's ~2-of-12 live success
                       rate) - not a guess about the source's reputation.
  R (relevance)      - modality-level, from real distance-to-decision-
                       variable: price IS the forecasting target; weather
                       and text are real but indirect leading indicators.
  F (freshness)      - mechanical, from the real gap between
                       observation_date and collected_at already in every
                       row - no modality-level judgment involved.
  C (compatibility)  - modality-level, from whether the real unit is a
                       directly poolable physical/economic quantity
                       (USD/tonne, °C, MT/ha) vs. an aggregate that
                       conflates other dimensions (trade's raw USD total
                       conflates price x volume; text's signal count has
                       no fixed scale week to week).
  P (provenance)     - modality-level, from how well-documented and
                       attributable the real source actually is (an
                       official UN/NASA methodology vs. GDELT's
                       aggregation of arbitrary, inconsistently-
                       attributed web sources).
  G (geographic coverage) - modality-level, from a real, named structural
                       limitation in this session's own collector code:
                       weather reads ONE point (the capital's lat/lon)
                       as a stand-in for the whole country
                       (collect_weather.py); text tags a country via
                       keyword matching in article text
                       (news_intelligence.py's COUNTRY_KEYWORDS), not
                       confirmed geolocation.
"""

from __future__ import annotations

from datetime import date, datetime

from provenance import DataState, EvidenceQualityVector, GoldStandardObservation

# A: mechanical, from DataState - the experiment's own core instrument.
_AVAILABILITY_BY_STATE: dict[DataState, float] = {
    DataState.OBSERVED_VERIFIED: 1.0,
    DataState.OBSERVED_UNVERIFIED: 0.7,
    DataState.SYNTHETIC_IMPUTED: 0.3,
    DataState.SYNTHETIC_BASELINE: 0.15,
    DataState.UNKNOWN: 0.0,
}

# Q, R, C, P, G: modality-level, justified per-field above and inline below.
# Each tuple is (quality, relevance, compatibility, provenance, geographic_coverage).
_MODALITY_PROFILE: dict[str, tuple[float, float, float, float, float]] = {
    # FAOSTAT PP, real login-authenticated API (faostat_prices.py, fixed
    # this session) - official UN methodology; producer price IS this
    # experiment's actual forecasting target, not a proxy for it; a
    # direct USD/tonne figure pools cleanly with other price observations.
    "price": (0.90, 1.00, 0.90, 0.90, 0.85),
    # NASA POWER MERRA-2/GEOS satellite reanalysis - official US federal
    # source, all 8/8 real observations this session came back clean with
    # genuine (non-fill-value) dates. Real weakness: it reads ONE point
    # (the capital city's lat/lon, collect_weather.py) as a stand-in for
    # the whole country - a real proxy for growing-region climate, not a
    # national average, hence the lower G despite the source itself being
    # excellent.
    "weather": (0.95, 0.60, 0.90, 0.95, 0.50),
    # FAOSTAT QCL, the same official UN methodology as price, same
    # real login flow - a direct determinant of supply, not just a leading
    # indicator, and a genuine national total/area-weighted MT/ha figure.
    "production": (0.90, 0.90, 0.85, 0.90, 0.85),
    # UN Comtrade - official UN customs-reported methodology, genuinely
    # national in scope, but this session hit real, repeated operational
    # friction (a full 403 quota lockout, persistent soft rate-limiting)
    # that FAOSTAT/NASA POWER never did - real evidence of a source with
    # good provenance but worse *availability reliability* than the
    # others. Raw USD export value also conflates price x volume, so it
    # doesn't pool with a per-unit price without further normalization.
    "trade": (0.75, 0.85, 0.50, 0.90, 0.90),
    # GDELT + ReliefWeb + EAC RSS - across 3 independent live runs this
    # session (two concurrent, one sequential after fixing a real
    # concurrency bug), only ~2 of 12 real calls ever succeeded - a real,
    # repeatedly-observed ~17% success rate, not an assumption. GDELT
    # itself aggregates from arbitrary, inconsistently-attributed web
    # sources (weak provenance); country tagging is keyword matching in
    # article text (news_intelligence.py's COUNTRY_KEYWORDS), not
    # confirmed geolocation (weak G); a signal count has no fixed scale
    # week to week, so it doesn't pool with a physical/economic unit.
    "text": (0.35, 0.50, 0.30, 0.40, 0.55),
}

# F: freshness decay horizon. 10 years chosen because this modality set's
# most structurally stale real data (trade's fixed 2023 reference year,
# production's FAOSTAT reporting lag) is measured in single-digit years,
# not decades - a 10y horizon keeps F meaningfully differentiated across
# same-day (price/weather) vs multi-year-old (trade/production) real
# observations instead of flattening everything near 0 or 1.
_FRESHNESS_HORIZON_DAYS = 3650


def _parse_date(value: str) -> date:
    # observation_date is either a plain ISO date or an ISO datetime.
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date() if "T" in value else date.fromisoformat(value)


def score_observation(obs: GoldStandardObservation) -> EvidenceQualityVector:
    """Real, inspectable scoring - see module docstring for the rubric
    and per-dimension justification. Falls back to the DataState-only A
    score (everything else None) for a modality not yet profiled above,
    rather than guessing a number with no real basis."""
    availability = _AVAILABILITY_BY_STATE[obs.data_state]

    profile = _MODALITY_PROFILE.get(obs.modality)

    obs_date = _parse_date(obs.observation_date)
    collected = _parse_date(obs.collected_at)
    days_stale = max((collected - obs_date).days, 0)
    freshness = max(0.0, 1.0 - days_stale / _FRESHNESS_HORIZON_DAYS)

    if profile is None:
        return EvidenceQualityVector(availability=availability, freshness=freshness)

    quality, relevance, compatibility, provenance, geographic_coverage = profile
    return EvidenceQualityVector(
        availability=availability,
        quality=quality,
        relevance=relevance,
        freshness=freshness,
        compatibility=compatibility,
        provenance=provenance,
        geographic_coverage=geographic_coverage,
    )
