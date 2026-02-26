# FIRE LINE — Protocol Composition Verifier

This document defines the explicit boundary between what this package IS and what it is NOT.

---

## What This Package IS

- A **research simulation tool** for exploring formal properties of protocol composition
- A **bounded model checker** operating on **synthetic, hand-crafted state machines**
- A **companion codebase** for Papers 9/25 on protocol composition
- A **pedagogical artifact** — designed for clarity over completeness
- **MIT-licensed open-source software** intended for academic use and peer review

---

## What This Package IS NOT

### NOT Production Orchestration

This package does **not** implement, simulate, or expose any part of the proprietary
GOVERNANCE_PIPELINE or any production orchestration logic. The protocol models here
are stand-alone research constructs.

### NOT Complete Models

Each protocol is modeled with **3–5 states** and **3–5 actions**. Real governance
protocols have substantially richer state spaces, guard conditions, probabilistic
transitions, and contextual metadata. The simplifications here are intentional and
documented.

### NOT Exhaustive Verification

The verifier uses **bounded model checking** with a default ceiling of **10,000
composed states**. It provides no guarantee of correctness beyond that bound. It is
not a theorem prover, SMT solver, or certified verifier.

### NOT Real Agent Behavior

No code in this package controls, directs, or communicates with any AI agent.
All "decisions" are simple state-machine lookups on synthetic data.

---

## Synthetic Data Notice

All state machines, transitions, and verification results in this package — including
precomputed JSON in `results/precomputed/` — are **entirely synthetic**. They were
constructed to illustrate the formal properties described in Papers 9/25 and do not
represent any real system's behavior.

---

## Forbidden Identifiers

The following identifiers are intentionally absent from this codebase:

- Any reference to internal pipeline identifiers
- Any production service endpoints or credentials
- Any non-public model names or configuration keys

---

## Reproduction Note

All experiments in `experiments/` are deterministic given fixed inputs. Running
`experiments/run_all.py` will reproduce results consistent with (but not identical
to) `results/precomputed/` due to bounded enumeration order. Precomputed results
were generated with the same code at version `0.1.0`.

---

*This FIRE_LINE document must be preserved in all forks and derivative works.*
