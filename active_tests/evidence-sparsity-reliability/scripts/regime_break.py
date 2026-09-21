"""Detects a real structural break in a real price time series, so E1/E2
don't silently fit one model across two different price regimes.

Found 2026-09-21 while investigating why Burundi coffee's MAPE was
anomalously large after the TZ/BI expansion: the raw FAOSTAT PP rows
(fetched directly, bypassing this project's own collector, to rule out
a collection bug) show a real, officially-flagged ('A' = official
figure) 10x single-year drop for Burundi coffee between 2006 and 2007
($1,922.40 -> $184.90/tonne), with no comparable break in Burundi's own
tea or maize series over the same years, and no comparable break in
Kenya's coffee series at any point in its 1991-2024 run. Rwanda coffee
shows the same shape (a 2010 -> 2015 drop, $1,371.90 -> $277.40/tonne,
across a real FAOSTAT reporting gap so the exact break year is
unknown), while Rwanda tea barely moves over the same window. This
pattern - coffee-specific, not present in Kenya, present in two
countries whose coffee sectors both had a state/parastatal-marketing-
board-to-liberalized-market transition through the 2000s-2010s -
points to a real change in what is being measured (an official
reference/processed-equivalent price beforehand, a real farmgate
market price afterward), not a collection error. Fitting one ordinary
least squares model across both regimes is what produced Burundi
coffee's inflated MAPE: the model trains partly on $2,000-3,000/tonne
years and gets tested against $200-400/tonne years.

This module does not touch the raw collected data - the pre-break
years are real, officially-flagged observations and stay in the JSON
files exactly as collected. It only decides which years are safe to
pool into a single forecasting/calibration model, applied at analysis
time in the E1/E2 run scripts.

**Method, and why it needed two passes.** A first version compared
each year only to its immediately preceding real observation. That
produced two real false positives, found by validating against all 10
real series before wiring it into the run scripts, not assumed to
work: (1) Burundi coffee has a noisy one-year spike in 2002 (a real
value, $3,361.80, well above its neighbours) that made 2003 look like
a "break" purely because it was being compared against that one
unrepresentative spike year. (2) Rwanda coffee had a real but
temporary drop in the early 2000s (the globally documented 2000-2003
coffee crisis) that recovered by 2006-2010, long before its real,
permanent 2015 collapse - a single-year comparison couldn't tell a
temporary shock from a permanent regime change.

The fix: (a) compare each candidate point against the MEDIAN (not
mean) of up to the 4 preceding real years, which is robust to exactly
one noisy spike sitting in that window; (b) after a local drop is
found, additionally require the mean of every real observation from
that point to the END of the series to stay at or below the pre-break
median times `_SUSTAIN_RATIO` - not just the next few years - which is
what separates a permanent regime change from a shock that recovers.
Verified after retuning: correctly finds Burundi's coffee break at
2007 and Rwanda's coffee break at 2015, correctly rejects Burundi's
2002-2003 spike artifact and Rwanda's 2000-2003 temporary crisis, and
finds no candidate break in Kenya coffee or in any country's maize or
tea series.

**A third false positive, found when sorghum and sweet potatoes were
added 2026-09-21**, needed one more retune: Burundi's real sweet
potato price dips after 1999 (following a real 1996-1998 spike,
plausibly tied to Burundi's 1993-2005 civil war era) and stayed low
long enough to pass the original 0.6 sustain threshold (ratio 0.538).
Checked against the raw rows the same way as every other case: the
FAOSTAT flag stays `A` (official) continuously across 1999, unlike
both confirmed real breaks, which both coincide with an `A` -> `E`
flag change - ordinary volatility in a locally-traded staple crop, not
a structural break. `_SUSTAIN_RATIO` tightened from 0.6 to 0.5: the
false positive's ratio (0.538) and the two true positives' ratios
(0.195, 0.217) have a wide, clean gap between them, so 0.5 removes the
false positive with comfortable margin on both real cases, re-verified
against all 18 real price series in the dataset at that point, not
just the three cases in question.

Usage:
  from regime_break import restrict_to_latest_regime
"""

from __future__ import annotations

import statistics

_MIN_RATIO_DROP = 0.5      # trigger on a single-step drop of at least 50% vs the pre-break median
_SUSTAIN_RATIO = 0.5       # the ENTIRE remaining series must average <= 50% of the pre-break median
_LOCAL_WINDOW = 3          # near-term years (from the candidate) used for the initial drop check
_BEFORE_WINDOW = 4         # preceding real years used for the median baseline
_MIN_YEARS_EACH_SIDE = 3


def detect_price_regime_break(series: dict[int, float]) -> int | None:
    """Returns the first year of a new, real, sustained lower price regime, or None."""
    years = sorted(series.keys())
    if len(years) < _MIN_YEARS_EACH_SIDE * 2:
        return None

    for i in range(1, len(years)):
        before_years = years[:i]
        after_years = years[i:]
        if len(before_years) < _MIN_YEARS_EACH_SIDE or not after_years:
            continue

        baseline = statistics.median(series[y] for y in before_years[-_BEFORE_WINDOW:])
        if baseline <= 0:
            continue

        local_years = after_years[:_LOCAL_WINDOW]
        local_mean = sum(series[y] for y in local_years) / len(local_years)
        if local_mean > (1 - _MIN_RATIO_DROP) * baseline:
            continue  # not a big enough near-term drop

        full_remaining_mean = sum(series[y] for y in after_years) / len(after_years)
        if full_remaining_mean <= _SUSTAIN_RATIO * baseline:
            return years[i]

    return None


def restrict_to_latest_regime(series: dict[int, float]) -> tuple[dict[int, float], int | None]:
    """Returns (restricted series, break year or None). Drops nothing if no break found."""
    break_year = detect_price_regime_break(series)
    if break_year is None:
        return series, None
    return {y: v for y, v in series.items() if y >= break_year}, break_year
