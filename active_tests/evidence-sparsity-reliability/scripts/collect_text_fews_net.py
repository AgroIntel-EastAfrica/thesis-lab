"""Adds FEWS NET (Famine Early Warning Systems Network) as a second,
independent real text/news source, alongside the existing GDELT-based
collect_text.py, rather than editing it - see below for why.

**Why a new script instead of extending the shared production service.**
collect_text.py goes through services/intelligence/news_intelligence.py's
NewsIntelligenceService, a real, shared AgroIntel production service (it
powers the live app's briefings/alerts, not just this experiment). This
project's own CLAUDE.md is explicit that the dependency between
thesis-lab and agrointel runs one way - thesis-lab reads agrointel's
code through the submodule, never the reverse - so a new evidence
source added for this experiment's own purposes does not belong inside
that shared service. This script fetches FEWS NET directly instead,
and reuses NewsIntelligenceService.classify_article() read-only (an
existing, unmodified method) to score real fetched articles with the
same 15 price-up / 10 price-down regex patterns and 17-commodity
keyword list every other text source in this project already uses -
so results are directly comparable to collect_text.py's GDELT-based
numbers, not a new, incompatible scoring scheme.

**Why FEWS NET specifically.** Investigated 2026-09-22 after GDELT's
real live run that day fetched real articles for only 3 of 12
country/commodity pairs (connection timeouts and 60s rate-limit
responses, both genuine, already documented) and classified zero real
signals from ANY of them, even the 3 with real article data - checked
against classify_article()'s own logic before assuming a bug: it
requires a commodity keyword AND a specific price-impact regex match,
so an ordinary week's general agriculture news usually and correctly
produces nothing. FEWS NET is different in kind, not just another
GDELT-like general search: it is a purpose-built USAID food-security
early-warning service, publishing dated Food Security Outlook, Key
Message Update, and IPC Acute Food Insecurity Classification reports
specifically for droughts, harvest forecasts, and price shocks in
these exact countries - verified live before writing any code
(fetched https://fews.net/feeds and 3 of the resulting per-country
feed URLs directly, confirmed real RSS 2.0 XML, and read real recent
titles like "Risk of Famine (IPC Phase 5) persists despite
better-than-anticipated xagaa rains" for Somalia and "Pastoral areas
to remain in Crisis (IPC Phase 3), recovery hinges on short rains" for
Kenya - exactly the topic-dense content classify_article()'s real
patterns are built to catch, unlike a generic keyword search).

Scoped to coffee/maize/tea, matching collect_text.py's original
commodity scope, not this project's full 5-commodity set: sorghum has
real keyword support in COMMODITY_KEYWORDS, but sweet_potatoes does
not, and passing an unsupported commodity name to classify_article()
silently degrades every match to the generic "general" bucket rather
than erroring - producing real but misleading per-commodity numbers.
Left out rather than silently mislabeled.

Read-only against the real FEWS NET RSS feeds - no writes anywhere, no
API key required. Output is a local JSON file under this experiment's
own data/ directory.

Usage:
  python thesis-lab/active_tests/evidence-sparsity-reliability/scripts/collect_text_fews_net.py
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

COUNTRIES = ["KE", "RW", "TZ", "BI", "UG", "CD", "SS", "SO"]
COMMODITIES = ["coffee", "maize", "tea"]

# Verified live 2026-09-22 by fetching https://fews.net/feeds and, for
# KE/SO/CD, the feed URL itself (real RSS 2.0, real current-dated items) -
# not guessed. One taxonomy term per country's real FEWS NET RSS feed.
FEWS_NET_FEEDS: dict[str, str] = {
    "KE": "https://fews.net/taxonomy/term/535/feed",
    "UG": "https://fews.net/taxonomy/term/541/feed",
    "TZ": "https://fews.net/taxonomy/term/540/feed",
    "RW": "https://fews.net/taxonomy/term/536/feed",
    "BI": "https://fews.net/taxonomy/term/532/feed",
    "SS": "https://fews.net/taxonomy/term/539/feed",
    "SO": "https://fews.net/taxonomy/term/537/feed",
    "CD": "https://fews.net/taxonomy/term/552/feed",
}


async def _fetch_fews_net_articles(country: str) -> list:
    """Real RSS fetch + parse, same defusedxml pattern news_intelligence.py's
    own _fetch_rss_feeds uses, reimplemented locally rather than importing a
    private method across the thesis-lab/agrointel boundary."""
    import aiohttp
    import defusedxml.ElementTree as ET

    from services.intelligence.news_intelligence import NewsArticle

    url = FEWS_NET_FEEDS[country]
    articles: list[NewsArticle] = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=15),
                headers={"User-Agent": "AgroIntelResearchBot/1.0 (Paper 14, thesis-lab)"},
            ) as resp:
                if resp.status != 200:
                    print(f"  {country}: HTTP {resp.status}")
                    return []
                text = await resp.text(errors="replace")
        root = ET.fromstring(text)
        items = root.findall(".//item")
        for item in items:
            title_el, link_el, desc_el = item.find("title"), item.find("link"), item.find("description")
            title = (title_el.text or "").strip() if title_el is not None else ""
            if not title:
                continue
            articles.append(NewsArticle(
                title=title,
                url=(link_el.text or "").strip() if link_el is not None else "",
                source="fews_net",
                source_type="fews_net",
                country_code=country,
                content_snippet=(desc_el.text or "")[:500].strip() if desc_el is not None else "",
            ))
    except Exception as exc:
        print(f"  {country}: fetch failed ({exc})")
    return articles


async def collect_one(country: str) -> list[GoldStandardObservation]:
    from services.intelligence.news_intelligence import NewsIntelligenceService

    now = datetime.now(timezone.utc).isoformat()
    svc = NewsIntelligenceService()
    articles = await _fetch_fews_net_articles(country)

    observations = []
    for comm in COMMODITIES:
        signals = []
        for article in articles:
            signals.extend(svc.classify_article(article, commodities=[comm]))
        observations.append(GoldStandardObservation(
            country_code=country,
            modality="text",
            variable="signals_extracted",
            commodity=comm,
            observation_date=now[:10],
            value=float(len(signals)),
            unit="count",
            price_basis=f"fews_net_over_{len(articles)}_articles_analyzed",
            source="fews_net",
            source_timestamp=now,
            data_state=DataState.OBSERVED_VERIFIED if articles else DataState.UNKNOWN,
        ))
    return observations


async def collect_all() -> list[GoldStandardObservation]:
    all_obs: list[GoldStandardObservation] = []
    for cc in COUNTRIES:
        obs = await collect_one(cc)
        all_obs.extend(obs)
        n_articles = obs[0].price_basis.split("_over_")[1].split("_articles")[0] if obs else "0"
        print(f"  {cc}: {n_articles} real articles fetched")
        await asyncio.sleep(0.5)
    return all_obs


def main() -> None:
    observations = asyncio.run(collect_all())

    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"gold_standard_text_fews_net_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(
        json.dumps([o.model_dump(mode="json") for o in observations], indent=2),
        encoding="utf-8",
    )

    print(f"\nCollected {len(observations)} observations -> {out_path}")
    by_state: dict[str, int] = {}
    for o in observations:
        by_state[o.data_state.value] = by_state.get(o.data_state.value, 0) + 1
        print(f"  {o.country_code} {o.commodity}: {int(o.value)} signals ({o.price_basis}, {o.data_state.value})")
    print()
    for state, count in sorted(by_state.items()):
        print(f"  {state}: {count}")


if __name__ == "__main__":
    main()
