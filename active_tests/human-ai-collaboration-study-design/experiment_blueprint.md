# Experiment: human-ai-collaboration-study-design

- **Owner:**
- **Started:**
- **Status:** active
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Objective 6 / RQ6.

## Important: this is not a code experiment

Every other blueprint in this sandbox tests something with code and
real/synthetic data. This one can't be — Objective 6 asks whether real
recommendations, shown to real stakeholders, improve real decisions
compared with a conventional dashboard. That requires real human
participants (farmers, cooperatives, traders, policymakers), a real study
protocol, and almost certainly some form of informed consent / ethics
review given the paper's own collaborators (UBOS, MAAIF, Makerere
University). This file exists so the thread isn't silently dropped from
the research agenda — it documents what the study *would* need, not
something a coding session can execute alone.

## Objective

Determine whether AgroIntel's real, evidence-linked, uncertainty-aware
recommendations (this session shipped the two pieces Objective 6
presupposes: `causal_evidence` linking forecasts to real graph evidence,
and the `evidence_sufficient` gate withholding low-confidence calls)
measurably improve stakeholder decision quality compared with a
conventional dashboard showing the same underlying data without those
two features.

## Hypothesis

Per the paper's own framing (Section 4, "Methodology"): stakeholders
given evidence-linked, uncertainty-flagged recommendations will show
better-calibrated trust (appropriately relying on high-confidence calls,
appropriately overriding or ignoring low-confidence/`WATCH`-downgraded
ones) than stakeholders given the same data through a conventional
dashboard with no explicit evidence or confidence framing.

## Core Variables (study design, not code)

- **Participants**: real stakeholders across at least the role
  categories AgroIntel already serves (farmer, cooperative, trader,
  exporter, analyst, policymaker) — recruitment and consent are real
  prerequisites, not implementation details.
- **Conditions**: (A) the real AgroIntel briefing/recommendation flow as
  it exists today, (B) a stripped-down version showing the same
  underlying numbers with no evidence links or confidence/`WATCH`
  framing — a real, deliberately weaker comparison condition.
- **What's held constant**: the underlying data and time period shown to
  both groups.

## Success Metrics

Per the paper's own Section 4 language — not just user satisfaction:
- Decision quality (did the action taken match what the underlying data
  actually supported, judged after the fact).
- Calibration of confidence (did participants' stated trust in a
  recommendation track its real, later-verified accuracy).
- Ability to identify risks.
- Response time.
- Appropriate reliance vs. override (did participants correctly discount
  `WATCH`-downgraded / low-`evidence_sufficient` recommendations, and
  correctly act on high-confidence ones).

## Results

*Not started — requires a real study protocol, participant recruitment,
and likely ethics/IRB-equivalent review before any data collection. Out
of scope for a coding session; tracked here so it isn't lost from the
research agenda the paper actually proposes.*
