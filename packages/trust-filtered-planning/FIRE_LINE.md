# FIRE LINE — trust-filtered-planning

This document records the constraints and boundaries that govern this package.
All contributors MUST read this before making changes.

---

## What This Package Is

A **research simulation** package that accompanies Paper 12:
*"How Trust Levels Constrain Agent Planning and Action Selection"*

It exists solely to:
1. Allow reproduction of the paper's figures and numerical results
2. Provide a clean reference implementation of the simplified forward-search
   planner with trust-filtered action spaces described in the paper
3. Serve as a baseline for future academic comparisons

---

## Hard Constraints

### Simulation Boundary

- All code in `src/trust_planning/` implements **SIMPLE FORWARD-SEARCH ONLY**
- The simulation does NOT contain, reverse-engineer, or approximate any production
  cognitive planning loop or trust-gated action execution system
- This package does NOT implement the full trust-constrained planning theory from
  Paper 12 — only the simplified forward-search corollaries used for figure reproduction
- Any contributor who believes they are inadvertently implementing production logic
  MUST stop and file an issue before continuing

### Data Boundary

- ALL planning scenarios, goals, and action sets in this package are **SYNTHETIC**
- No real agent tasks, no real planning traces, no real trust assignments
- Pre-computed results in `results/precomputed/` are generated deterministically
  from the simulation with `seed=42` — they are not sourced from real systems

### Algorithm Boundary

- Planning is **FORWARD SEARCH ONLY** — simple BFS/greedy forward expansion
- Trust filtering is **STATIC THRESHOLD** — actions with required trust level
  above the agent's assigned level are simply excluded from the search space
- Trust levels are **INTEGERS 0–5** — no fractional or dynamic trust values
- There is NO cognitive loop, attention filter, or adaptive planning in this package
- Plan quality metrics use **SIMPLE ARITHMETIC** — step count, action diversity

### Identifier Constraint

The following identifiers are **PROHIBITED** in this codebase:
- `progressLevel`, `promoteLevel`, `computeTrustScore`, `behavioralScore`
- `adaptiveBudget`, `optimizeBudget`, `predictSpending`
- `detectAnomaly`, `generateCounterfactual`
- `PersonalWorldModel`, `MissionAlignment`, `SocialTrust`
- `CognitiveLoop`, `AttentionFilter`, `GOVERNANCE_PIPELINE`

If a linter or reviewer flags an identifier as potentially matching production
internals, rename it immediately. No exceptions.

### Planner Constraint

- Action spaces are **DISCRETE ENUMERATED SETS** — no continuous action spaces
- State transitions are **DETERMINISTIC** — no stochastic planning
- This constraint ensures the simulation cannot be confused with or substituted
  for more sophisticated production planning systems

---

## What Is NOT Here

The following are intentionally absent from this package and MUST NOT be added:

- **Paper 12's full planning theory** — proprietary to MuVeraAI Corporation
- **Production cognitive loop** — the real agent execution system is not OSS
- **Adaptive trust assignment** — trust levels are externally set, never automatic
- **Real agent planning traces** — all plans are synthetically generated
- **Stochastic planning** — all dynamics are deterministic given seed=42
- **Three-tier attention filter** — not implemented

---

## Disclosure Requirements

Every public-facing docstring in `src/trust_planning/` MUST contain one of:
- `"SIMULATION ONLY"` — for core simulation classes and functions
- `"SIMULATION"` or `"synthetic"` — for data-generating utilities

The `README.md` MUST retain the disclaimer section unchanged.

---

## Change Approval

Changes to the following files require review from the research lead:
- `src/trust_planning/model.py` — core planning simulation
- `src/trust_planning/planner.py` — forward search implementation
- `scenarios.py` — paper's canonical planning scenarios
- `results/precomputed/*.json` — frozen reference data

Experiments and visualization changes are lower-risk but MUST NOT alter the
parameters that would change any pre-computed result without regenerating all
four JSON files and bumping the package version.

---

*Last reviewed: 2026-02-26*
*Package version at last review: 0.1.0*
