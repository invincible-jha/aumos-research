# FIRE LINE — economic-safety-verifier

This document records the constraints and boundaries that govern this package.
All contributors MUST read this before making changes.

---

## What This Package Is

A **research simulation** package that accompanies Paper 22:
*"Economic Safety Verification: Properties of Agent Spending Envelopes"*

It exists solely to:
1. Allow reproduction of the paper's figures and numerical results
2. Provide a clean reference implementation of the simplified arithmetic verification
   described in the paper
3. Serve as a baseline for future academic comparisons

---

## Hard Constraints

### Simulation Boundary

- All code in `src/economic_safety/` implements **SIMPLIFIED arithmetic verification only**
- The simulation does NOT contain, reverse-engineer, or approximate the production
  AEAP (Agent Economic Accountability Protocol) budget enforcement system
- This package does NOT implement any of the 25 theorems from Paper 22 in their
  full formal form — only the simplified corollaries used for figure reproduction
- Any contributor who believes they are inadvertently implementing production logic
  MUST stop and file an issue before continuing

### Data Boundary

- ALL transaction and spending data used in this package is **SYNTHETIC**
- No real agent spending records, no real budget data, no real economic signals
- Pre-computed results in `results/precomputed/` are generated deterministically
  from the simulation with `seed=42` — they are not sourced from real systems

### Algorithm Boundary

- Budget allocation is **STATIC ONLY** — limits are fixed at envelope creation
- Spending enforcement uses **simple arithmetic** — no ML, no prediction, no adaptive logic
- There is NO saga-pattern compensation logic in this package
- There is NO adaptive budget reallocation logic in this package
- Verification is **post-hoc arithmetic checking** — not formal theorem proving

### Identifier Constraint

The following identifiers are **PROHIBITED** in this codebase:
- `adaptiveBudget`, `optimizeBudget`, `predictSpending`
- `detectAnomaly`, `generateCounterfactual`
- Any identifier referencing AEAP internals or Paper 22's theorem prover
- Any identifier matching production AEAP system internals

If a linter or reviewer flags an identifier as potentially matching production
internals, rename it immediately. No exceptions.

### Vector/Representation Constraint

- Spending limits and balances are represented as **scalar floats**
- No multi-dimensional budget vectors are implemented here
- This constraint ensures the simulation cannot be confused with or substituted
  for more sophisticated production representations

---

## What Is NOT Here

The following are intentionally absent from this package and MUST NOT be added:

- **Paper 22's 25 theorem proofs** — these are proprietary to MuVeraAI Corporation
- **Production AEAP algorithms** — the real enforcement system is not OSS
- **Saga-pattern compensation logic** — compensating transactions are not implemented
- **Real agent spending data** — all data is synthetic
- **Adaptive budget reallocation** — budgets are static in this simulation
- **Anomaly detection on spending patterns** — recording only, no inference

---

## Disclosure Requirements

Every public-facing docstring in `src/economic_safety/` MUST contain one of:
- `"SIMULATION ONLY"` — for core simulation classes and functions
- `"SIMULATION"` or `"synthetic"` — for data-generating utilities

The `README.md` MUST retain the disclaimer section unchanged.

---

## Change Approval

Changes to the following files require review from the research lead:
- `src/economic_safety/model.py` — core simulation dynamics
- `src/economic_safety/properties.py` — safety property definitions
- `scenarios.py` — paper's canonical scenario configurations
- `results/precomputed/*.json` — frozen reference data

Experiments and visualization changes are lower-risk but MUST NOT alter the
parameters that would change any pre-computed result without regenerating all
three JSON files and bumping the package version.

---

*Last reviewed: 2026-02-26*
*Package version at last review: 0.1.0*
