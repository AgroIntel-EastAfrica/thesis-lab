# Experiment E4 — Decision Reliability: Study Protocol

**Status: protocol only. Not yet run — requires real participants,**
**informed consent, and institutional review before any data**
**collection.** This document specifies what the study *would* need,
using real materials this lab already computed (E1's forecasts, E2's
calibrated intervals, E3's evidence-state classification), so it's
ready to run rather than a placeholder — but running it is a decision
for the researcher/advisor/IRB, not something this session can do
unilaterally. See the blueprint's own E4 section for the original
design this protocol operationalizes.

## Why this can't be a code experiment

E1–E3 are all things a coding session can genuinely execute: real
data, real computation, real results. E4 measures how actual people
make decisions — response time, override behavior, decision accuracy
against ground truth only knowable in hindsight. Simulating synthetic
"participants" and reporting the output as results would be
fabrication, not research. This protocol exists so the thread isn't
silently dropped, matching the same honest-limits discipline this
whole experiment has followed throughout.

## Objective

Determine whether presenting the *same underlying real evidence* in
progressively more evidence-grounded, uncertainty-aware formats
changes decision quality, risk identification, and appropriate
reliance — holding the real data itself constant across all 5
conditions.

## Hypothesis

Per the source proposal's RQ6 ("Does proactive, evidence-grounded
support improve decision quality over reactive systems?"):
participants given format 4 (evidence-grounded) or 5
(uncertainty-aware) will show better-calibrated trust — appropriately
relying on the high-confidence call, appropriately hedging on the
wide-interval one — than participants given the same real numbers as
raw data or a conventional dashboard.

## The decision scenario (real, not hypothetical)

Built from this experiment's own real E1/E2/E3 outputs for **KE
coffee, 2024** — not invented numbers:

> *A cooperative in Kenya is deciding whether to increase coffee
> inventory ahead of the 2024 season. 2023's real producer price was
> \$4,391.70/tonne (FAOSTAT).*

| Format shown | What the participant sees |
|---|---|
| **1. Raw data** | The real 64-year FAOSTAT price series (1961–2024) and nothing else — no summary, no forecast, no interpretation. |
| **2. Conventional dashboard** | The same series as a line chart with a simple trailing-average trend line — no explicit forecast, confidence, or evidence framing (matches this lab's own definition of "conventional" elsewhere). |
| **3. AI forecast** | A single point prediction, no interval: *"Model forecast for 2024: \$3,934.60/tonne"* (T0, price-only — this experiment's own real E1 output) — presented with unwarranted-looking certainty, deliberately, since that is the real failure mode E2 exists to correct. |
| **4. Evidence-grounded agent** | The T1 forecast (\$4,253.00/tonne, price+weather) *plus* E3's real evidence-state classification for this case (`SUFFICIENT` — real, fresh, multi-modal, no conflict) and an explicit statement of what evidence was used and why. |
| **5. Uncertainty-aware agent** | Format 4's content *plus* E2's real 80% LOO-conformal interval: **\$2,383.30 – \$5,486.00/tonne**, with explicit language ("the model is not confident to within a narrow range — treat this as a wide-uncertainty year") rather than a bare point number. |

**Real ground truth, revealed only after the decision** (for scoring,
never shown during the task): 2024's actual real price was
**\$4,886.50/tonne** — above every point forecast, but inside the T0
80% interval. A participant who anchored tightly on format 3's bare
point prediction would have underestimated the real outcome by ~21%;
one who used format 5's interval would have seen the real outcome was
a plausible, if upper-range, result.

*(A second and third scenario — e.g. SS coffee, where evidence is
genuinely `INSUFFICIENT` per E3, and KE trade, where it's real but
`STALE` — should be added before running the actual study, so
decision quality can be compared across evidence conditions, not just
formats. Left as a single fully-worked example here rather than
three, to keep this protocol reviewable in one pass.)*

## Participants

- Real stakeholders across the role categories AgroIntel already
  serves: farmer, cooperative, trader, exporter, analyst,
  policymaker — recruitment and informed consent are real
  prerequisites, not implementation details.
- Between-subjects design (each participant sees only one of the 5
  formats, to avoid learning/anchoring effects across formats) —
  requires a correspondingly larger total sample than a within-subjects
  design would.
- **Institutional review**: the source proposal names Makerere
  University, UBOS, and MAAIF as potential collaborators and
  explicitly commits to "informed consent and institutional review
  requirements where applicable" — this study is exactly the kind of
  human-subjects work that commitment covers. Whether Makerere's
  process applies, and what it requires, needs the advisor/institution
  to confirm before recruitment — not assumed here.

## Procedure (per participant)

1. Present the decision scenario framing (cooperative, coffee,
   inventory decision) and the assigned format's real materials.
2. Ask: *"Would you recommend increasing inventory? How confident are
   you (0–100%)? What, if anything, concerns you about this
   evidence?"*
3. Record the decision, stated confidence, free-text risk
   identification, and response time.
4. Reveal the real 2024 outcome (\$4,886.50/tonne) and ask a brief
   post-hoc reflection question (would they decide differently now?).

## Metrics, operationalized

| Metric | How it's measured |
|---|---|
| Decision accuracy | Did the recommended action match what the real outcome would have supported, judged after the fact against the real \$4,886.50/tonne? |
| Risk identification | Free-text response coded for whether it names a real, relevant risk this scenario actually has (e.g. format 1/2's respondents not noticing the forecast is single-point/uncertain; format 3's respondents not questioning an oddly-precise number) |
| Confidence calibration | Stated confidence (0–100%) vs. whether the decision was actually correct — same calibration logic as E2, applied to human judgment instead of a model |
| Response time | Wall-clock time from scenario presentation to decision submission |
| Appropriate reliance | For formats 4/5: did the participant's confidence track the real evidence state (`SUFFICIENT`) and real interval width appropriately, rather than over- or under-trusting it? |
| Override behavior | For formats 3/4/5: did the participant accept, adjust, or reject the model's recommendation, and was that choice consistent with the real evidence quality shown? |

## Pre-registered analysis plan

Decided before any data collection, matching this experiment's own
established discipline (see the blueprint's Success Criteria section):
primary comparison is decision accuracy and confidence calibration in
format 5 (uncertainty-aware) vs. format 3 (bare AI forecast) — the
sharpest real contrast this protocol offers, since both show a model
output but only one shows its real uncertainty. A minimum detectable
effect size and required sample size should be computed (power
analysis) before recruitment begins, not after seeing partial results.

## What this protocol does not yet include

- Institutional review status (real prerequisite, not yet confirmed)
- A power analysis / target sample size
- The second and third scenarios (insufficient- and stale-evidence
  cases) needed for a full within-experiment comparison
- Piloting with a small group to catch confusing wording before a real
  run
