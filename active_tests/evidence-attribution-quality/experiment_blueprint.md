# Experiment: evidence-attribution-quality

- **Owner:**
- **Started:**
- **Status:** active
- **Source:** Concept paper "Agentic Agricultural Intelligence..." (Masaba,
  Makerere University) — Objective 3 / RQ3, and directly motivated by
  Asai et al. 2021 ("evidentiality"), which the paper cites explicitly:
  "retrieval alone does not guarantee that retrieved information
  supports a generated claim."

## Objective

AgroIntel has two real, live evidence-presenting mechanisms today:
`IntelligenceEngine`'s structured `evidence=[...]` lists (programmatic,
attached by calling code — can't hallucinate a citation because it never
generates one) and the RAG grounding check
(`services/rag/citation_check.py::check_grounding`, real and tested but
still architecturally orphaned — `RAGPipeline` has zero real callers, as
this session's own investigation confirmed). This experiment evaluates
whether *either* mechanism's evidence actually supports the claims it's
attached to — the paper's real ask, evidentiality, not just "is there a
citation present."

## Hypothesis

`IntelligenceEngine`'s structured evidence (numeric values pulled
directly from real data, e.g. `f"7d change: {change:+.1f}%"`) is
trivially well-attributed by construction — there's little to test
there. `check_grounding`'s cheap substring-match approach (does a
`[Source: X]` marker match a retrieved chunk's source name) is a much
weaker guarantee: it can confirm a *source* was real without confirming
the specific *claim* near that citation is actually supported by that
source's text. The hypothesis: feeding `check_grounding` a summary where
the LLM cites a real source correctly but states a fact contradicting
that source's actual content will still return `grounded=True` — a real
gap between what the check verifies and what evidentiality actually
requires.

## Core Variables

- **Held constant:** `services/rag/citation_check.py`'s real,
  unmodified implementation.
- **Varied:** test cases — (a) a correct citation supporting a correct
  claim (expected: grounded), (b) a correct citation next to a claim the
  cited chunk doesn't actually support (expected, if the hypothesis
  holds: still reports grounded — the real gap), (c) a fabricated
  citation to a source never retrieved (expected: not grounded, this
  case should already work).

## Success Metrics

- Confirming the (b) gap exists is itself the useful result — it
  precisely scopes what a real fix would need (per-claim entailment
  checking, e.g. an NLI model or a second LLM verification call, both
  already named as the real follow-on in
  `product/PRODUCTION_AUDIT.md`'s Technical Debt Register) rather than
  leaving "make grounding checking more rigorous" as a vague aspiration.
- Document real cost/latency implications of any proposed fix (an NLI
  model call or second LLM call per generated summary is not free) —
  the paper's own framing treats trustworthiness as a real engineering
  tradeoff, not something to add unconditionally.

## Results

*Not yet run.*
