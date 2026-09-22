"""Merges the two real, independent text/news sources - GDELT
(collect_text.py) and FEWS NET (collect_text_fews_net.py) - into one
combined gold_standard_text_<timestamp>.json.

**Why this needs its own step, unlike price/production/weather.** Every
other modality's "keep only the latest file" convention
(populate_evidence_quality.py's latest_file_per_modality) is correct
because each new collector run of the same modality is a strict
re-measurement of the same real thing - a newer price-history run
supersedes an older one. GDELT and FEWS NET are not that: they are two
different real sources for the same "text" modality, collected via
different scripts, and a newer FEWS NET file should not silently make
populate_evidence_quality.py forget GDELT's real (if mostly zero-
signal) results, or vice versa. This script produces one combined
file, using the standard gold_standard_text_<timestamp>.json name (no
extra suffix), so it becomes the new "latest text file" and both real
sources' observations are counted, not just whichever ran most
recently.

Read-only over already-collected local files - no network calls.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/merge_text_sources.py
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_TS_RE = re.compile(r"(\d{8}_\d{6})\.json$")


def _latest(pattern: str) -> Path:
    candidates = list(DATA_DIR.glob(pattern))
    if not candidates:
        raise FileNotFoundError(f"No files matching {pattern} in {DATA_DIR}")
    return max(candidates, key=lambda p: _TS_RE.search(p.name).group(1))


def main() -> None:
    gdelt_path = _latest("gold_standard_text_[0-9]*.json")
    fews_path = _latest("gold_standard_text_fews_net_*.json")

    gdelt_rows = json.loads(gdelt_path.read_text(encoding="utf-8"))
    fews_rows = json.loads(fews_path.read_text(encoding="utf-8"))
    combined = gdelt_rows + fews_rows

    out_path = DATA_DIR / f"gold_standard_text_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")

    print(f"Merged {gdelt_path.name} ({len(gdelt_rows)} rows, source=news_intelligence)")
    print(f"     + {fews_path.name} ({len(fews_rows)} rows, source=fews_net)")
    print(f"  -> {out_path.name} ({len(combined)} rows total)")


if __name__ == "__main__":
    main()
