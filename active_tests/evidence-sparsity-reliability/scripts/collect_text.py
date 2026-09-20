"""Phase 0, sixth slice: collect real gold-standard textual/news-event
observations via services/intelligence/news_intelligence.py's
NewsIntelligenceService (real GDELT + ReliefWeb + EAC media RSS
sources), for the same finalized 4-country scope. The last of the
planned 4-5 evidence modalities.

Unlike price/weather/production/trade (a single numeric measurement),
"evidence" for this modality is fundamentally about *coverage*: how
much real textual signal exists about a given country/commodity at
all. The observation here is `signals_extracted` - the count of real,
classified market signals NewsIntelligenceService found for that
(country, commodity) pair, not a price or volume. `articles_analyzed`
(the raw pre-classification count) is recorded in `price_basis` for
transparency rather than conflated with the classified-signal count.

fetch_and_analyze() fetches all of a country's recent articles once
(country-level, not commodity-scoped - GDELT/RSS have no per-commodity
query), then classify_article() restricts signal EXTRACTION to the
given commodities - so one real call per (country, commodity) pair,
matching this experiment's established 4x3 matrix.

Read-only against real GDELT/ReliefWeb/RSS sources - no writes
anywhere, no API key required (GDELT is always available). Output is
a local JSON file under this experiment's own data/ directory.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/collect_text.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR.parents[2] / "agrointel"))  # agrointel submodule, for services.*/clients.*/apps.*

from provenance import DataState, GoldStandardObservation  # noqa: E402

COUNTRIES = ["KE", "RW", "SS", "SO"]
COMMODITIES = ["coffee", "maize", "tea"]
_TIMESPAN = "1w"


async def collect_one(country: str, commodity: str) -> GoldStandardObservation:
    from services.intelligence.news_intelligence import NewsIntelligenceService

    now = datetime.now(timezone.utc).isoformat()
    svc = NewsIntelligenceService()
    result = await svc.fetch_and_analyze(country_code=country, commodities=[commodity], timespan=_TIMESPAN)

    articles = result["articles_analyzed"]
    signals = result["signals_extracted"]
    sources = ",".join(result["sources_checked"])

    return GoldStandardObservation(
        country_code=country,
        modality="text",
        variable="signals_extracted",
        commodity=commodity,
        observation_date=now[:10],
        value=float(signals),
        unit="count",
        price_basis=f"{sources}_over_{_TIMESPAN}_of_{articles}_articles_analyzed",
        source="news_intelligence",
        source_timestamp=now,
        data_state=DataState.OBSERVED_VERIFIED if articles > 0 else DataState.UNKNOWN,
    )


async def collect_all() -> list[GoldStandardObservation]:
    # Sequential, not gathered: NewsIntelligenceService._fetch_all_sources
    # opens a fresh GDELTClient per call, so its own built-in
    # rate_limit_per_second=1.0 only throttles within one call, not across
    # them. A live test proved 12 concurrent calls (asyncio.gather) make
    # GDELT's free, unauthenticated API silently time out on all but 1-2
    # of them - a real, self-inflicted rate-limit collision, not a
    # genuine "no news" finding or a GDELT outage (confirmed by re-running
    # the exact same query standalone and getting a real result once
    # nothing else was competing for a connection).
    observations = []
    for cc in COUNTRIES:
        for comm in COMMODITIES:
            observations.append(await collect_one(cc, comm))
            await asyncio.sleep(1.1)
    return observations


def main() -> None:
    observations = asyncio.run(collect_all())

    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"gold_standard_text_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(
        json.dumps([o.model_dump(mode="json") for o in observations], indent=2),
        encoding="utf-8",
    )

    print(f"Collected {len(observations)} observations -> {out_path}")
    by_state: dict[str, int] = {}
    for o in observations:
        by_state[o.data_state.value] = by_state.get(o.data_state.value, 0) + 1
        print(f"  {o.country_code} {o.commodity}: {int(o.value)} signals ({o.price_basis}, {o.data_state.value})")
    print()
    for state, count in sorted(by_state.items()):
        print(f"  {state}: {count}")


if __name__ == "__main__":
    main()
