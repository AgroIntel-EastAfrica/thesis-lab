"""Gold-standard dataset schema — Phase 0 of the evidence-sparsity-reliability
experiment (Paper 14 redesign, thesis-lab/active_tests/evidence-sparsity-
reliability/experiment_blueprint.md).

Every observation this experiment ever evaluates against carries this
schema. The hard rule it exists to enforce: a SYNTHETIC value can never be
silently treated as OBSERVED ground truth — the exact mistake the
concluded regional-equity-audit experiment made with its original MAPE
figures (forecasting a synthetic random walk against itself, then blending
that with real-market forecasts into one number).

Thesis-lab sandbox rule (CLAUDE.md): read-only access to real production
data is fine for an audit-style experiment measuring real system behavior;
writes to production are not. This module and its companion collection
script only ever call get_daily_price() (a read) and write results to a
local file under this experiment's own data/ directory.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class DataState(str, Enum):
    """Three top-level states, deliberately never collapsed into two
    (real vs. fake) - see the blueprint's "Separate real, synthetic and
    unknown" section."""

    OBSERVED_VERIFIED = "observed_verified"
    OBSERVED_UNVERIFIED = "observed_unverified"
    SYNTHETIC_BASELINE = "synthetic_baseline"
    SYNTHETIC_IMPUTED = "synthetic_imputed"
    UNKNOWN = "unknown"

    @property
    def is_valid_ground_truth(self) -> bool:
        """Only OBSERVED_VERIFIED may be used as a forecasting-accuracy
        target. This is the one rule that matters most in this whole
        module - see the module docstring."""
        return self is DataState.OBSERVED_VERIFIED


class EvidenceQualityVector(BaseModel):
    """E = (A, Q, R, F, C, P, G) from the experiment blueprint. Each
    dimension is 0.0-1.0. Populated where real signal exists to compute
    it; left None where this first Phase 0 slice (price modality only)
    has no real basis to estimate a dimension yet - never guessed."""

    availability: float | None = Field(None, ge=0.0, le=1.0, description="A - was evidence present at all")
    quality: float | None = Field(None, ge=0.0, le=1.0, description="Q - how trustworthy is it")
    relevance: float | None = Field(None, ge=0.0, le=1.0, description="R - does it address the question")
    freshness: float | None = Field(None, ge=0.0, le=1.0, description="F - how old is it")
    compatibility: float | None = Field(None, ge=0.0, le=1.0, description="C - can it be legitimately combined with other evidence")
    provenance: float | None = Field(None, ge=0.0, le=1.0, description="P - how well-attested is the source")
    geographic_coverage: float | None = Field(None, ge=0.0, le=1.0, description="G - does it actually represent this country/commodity/geography")


class GoldStandardObservation(BaseModel):
    """One row of the gold-standard dataset. Field set matches the
    blueprint's spec exactly: country, commodity, market, geography,
    date, value, unit, price_basis, source, source_timestamp,
    data_quality, observed/synthetic."""

    country_code: str
    commodity: str
    market: str = "national"
    geography_level: str = "NATIONAL"
    observation_date: str  # ISO date this value applies to
    value: float
    unit: str
    price_basis: str
    source: str
    source_timestamp: str  # when this value was actually fetched, ISO datetime
    data_state: DataState
    evidence_quality: EvidenceQualityVector = Field(default_factory=EvidenceQualityVector)
    collected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_flat_dict(self) -> dict:
        """CSV/table-friendly flattening - evidence_quality's 7 sub-fields
        become 7 top-level columns instead of a nested object."""
        d = self.model_dump(mode="json")
        eq = d.pop("evidence_quality")
        for k, v in eq.items():
            d[f"evidence_quality_{k}"] = v
        return d
