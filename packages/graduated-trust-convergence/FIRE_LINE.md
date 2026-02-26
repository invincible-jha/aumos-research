# FIRE LINE — graduated-trust-convergence

This document records the constraints and boundaries that govern this package.
All contributors MUST read this before making changes.

---

## What This Package Is

A **research simulation** package that accompanies Paper 13:
*"Graduated Trust Convergence: Formal Properties of Multi-Level Trust Progression"*

It exists solely to:
1. Allow reproduction of the paper's figures and numerical results
2. Provide a clean reference implementation of the simplified dynamics described in the paper
3. Serve as a baseline for future academic comparisons

---

## Hard Constraints

### Simulation Boundary
- All code in `src/trust_convergence/` implements **SIMPLIFIED dynamics only**
- The simulation does NOT contain, reverse-engineer, or approximate the production
  trust progression algorithm used in any deployed system
- Any contributor who believes they are inadvertently implementing production logic
  MUST stop and file an issue before continuing

### Data Boundary
- ALL data used in this package is **SYNTHETIC**
- No real agent behavior data, no real interaction logs, no real trust scores
- Pre-computed results in `results/precomputed/` are generated deterministically
  from the simulation with `seed=42` — they are not sourced from real systems

### Identifier Constraint
The following identifiers are **PROHIBITED** in this codebase:
- `progressLevel`
- `promoteLevel`
- `computeTrustScore`
- `behavioralScore`
- Any identifier that matches production system internals

If a linter or reviewer flags an identifier as potentially matching production
internals, rename it immediately. No exceptions.

### Vector Constraint
- Trust is represented as a **scalar float** in `[0, num_levels - 1]`
- Multi-dimensional trust vectors are **NOT implemented** here
- This constraint exists to ensure the simulation cannot be confused with or
  substituted for more sophisticated production representations

---

## Disclosure Requirements

Every public-facing docstring in `src/trust_convergence/` MUST contain one of:
- `"NOT production"` — for core simulation classes and functions
- `"SIMULATION"` or `"synthetic"` — for data-generating utilities

The `README.md` MUST retain the disclaimer section unchanged.

---

## Change Approval

Changes to the following files require review from the research lead:
- `src/trust_convergence/model.py` — core simulation dynamics
- `scenarios.py` — paper's canonical scenario configurations
- `results/precomputed/*.json` — frozen reference data

Experiments and visualization changes are lower-risk but MUST NOT alter the
parameters that would change any pre-computed result without regenerating all
four JSON files and bumping the package version.

---

*Last reviewed: 2026-02-26*
*Package version at last review: 0.1.0*
