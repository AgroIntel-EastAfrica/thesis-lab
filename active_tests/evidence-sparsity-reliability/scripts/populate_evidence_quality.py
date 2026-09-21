"""Phase 0, seventh slice: apply evidence_quality_rubric.py's scoring to
every real observation collected so far (one latest file per modality),
and write one consolidated dataset with EvidenceQualityVector actually
populated instead of all-None.

Pure local computation over already-collected data - no network calls,
no external services, nothing to verify live. Reads every
gold_standard_<modality>_*.json in data/, keeps only the most recent
file per modality (later collections supersede earlier ones - e.g.
trade's first two runs were real, honestly-recorded quota-blocked
attempts, superseded by the third, unblocked one), scores each
observation, and writes the union to one file.

**Real bug found and fixed 2026-09-21**, prompted by the project owner
noticing the report's evidence-quality radar chart looked stale: the
filename regex required `gold_standard_<modality>_<timestamp>.json`
with no separator inside `<modality>`, so it silently failed to match
`gold_standard_price_history_*.json`,
`gold_standard_production_history_*.json`, and
`gold_standard_weather_history_*.json` - the real multi-year
collectors built and used throughout this session for price,
production, and weather. This script had been running against the
original single-snapshot `gold_standard_price_*.json` /
`_production_*.json` / `_weather_*.json` files from 2026-09-17, a
different, far smaller, long-superseded dataset, the entire time -
every evidence-quality number in the report traced back to that stale
source, not to any of the TZ/BI/UG/CD or 5-commodity work. Fixed by
making the modality capture non-greedy and the `_history` suffix
optional-but-absorbed, so both filename styles normalize to the same
modality key and the existing "latest timestamp wins" logic picks the
real `_history` files for price/production/weather (always more recent
than the old singles) while correctly still picking trade/text's own
files (no `_history` variant exists for those two - they remain real
single snapshots).

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/populate_evidence_quality.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR.parents[2] / "agrointel"))  # agrointel submodule, for services.*/clients.*/apps.*

from evidence_quality_rubric import score_observation  # noqa: E402
from provenance import GoldStandardObservation  # noqa: E402

_FILENAME_RE = re.compile(r"^gold_standard_(?P<modality>[a-z]+?)(?:_history)?_(?P<ts>\d{8}_\d{6})\.json$")


def latest_file_per_modality(data_dir: Path) -> dict[str, Path]:
    by_modality: dict[str, list[tuple[str, Path]]] = defaultdict(list)
    for path in data_dir.glob("gold_standard_*.json"):
        m = _FILENAME_RE.match(path.name)
        if not m:
            continue
        by_modality[m.group("modality")].append((m.group("ts"), path))

    return {modality: max(entries, key=lambda e: e[0])[1] for modality, entries in by_modality.items()}


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    latest = latest_file_per_modality(data_dir)

    all_scored: list[GoldStandardObservation] = []
    for modality, path in sorted(latest.items()):
        rows = json.loads(path.read_text(encoding="utf-8"))
        for row in rows:
            obs = GoldStandardObservation(**row)
            obs.evidence_quality = score_observation(obs)
            all_scored.append(obs)
        print(f"{modality}: scored {len(rows)} observations from {path.name}")

    out_path = data_dir / f"gold_standard_all_with_quality_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(
        json.dumps([o.model_dump(mode="json") for o in all_scored], indent=2),
        encoding="utf-8",
    )
    print(f"\nWrote {len(all_scored)} scored observations -> {out_path}\n")

    # Per-modality mean of each dimension, for a quick sanity read.
    dims = ["availability", "quality", "relevance", "freshness", "compatibility", "provenance", "geographic_coverage"]
    by_modality: dict[str, list[GoldStandardObservation]] = defaultdict(list)
    for obs in all_scored:
        by_modality[obs.modality].append(obs)

    header = "modality".ljust(12) + "".join(d[:4].rjust(8) for d in dims)
    print(header)
    print("-" * len(header))
    for modality, obs_list in sorted(by_modality.items()):
        row = modality.ljust(12)
        for dim in dims:
            values = [getattr(o.evidence_quality, dim) for o in obs_list if getattr(o.evidence_quality, dim) is not None]
            mean = sum(values) / len(values) if values else None
            row += (f"{mean:.2f}" if mean is not None else "  n/a").rjust(8)
        print(row)


if __name__ == "__main__":
    main()
