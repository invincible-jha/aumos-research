# FIRE LINE — delegation-trust-model

This document records the constraints and boundaries that govern this package.
All contributors MUST read this before making changes.

---

## What This Package Is

A **research simulation** package that accompanies Paper 18:
*"Trust Dynamics in Agent Delegation Chains"*

It exists solely to:
1. Allow reproduction of the paper's figures and numerical results
2. Provide a clean reference implementation of the simplified multiplicative
   decay model described in the paper
3. Serve as a baseline for future academic comparisons

---

## Hard Constraints

### Simulation Boundary

- All code in `src/delegation_trust/` implements **SIMPLIFIED multiplicative decay ONLY**
- The simulation does NOT contain, reverse-engineer, or approximate any production
  trust propagation or delegation management system
- This package does NOT implement the full trust dynamics theorems from Paper 18
  in their complete formal form — only the simplified corollaries used for figure
  reproduction
- Any contributor who believes they are inadvertently implementing production logic
  MUST stop and file an issue before continuing

### Data Boundary

- ALL agent data and delegation graphs used in this package are **SYNTHETIC**
- No real agent identities, delegation records, or trust measurements
- Pre-computed results in `results/precomputed/` are generated deterministically
  from the simulation with `seed=42` — they are not sourced from real systems

### Algorithm Boundary

- Trust propagation is **MULTIPLICATIVE DECAY ONLY** — each hop multiplies
  trust by the pairwise delegation trust level
- There is NO adaptive trust progression logic in this package
- Trust changes are **STATIC** — set at delegation creation, never automatically
  updated based on observed behavior
- Path reliability is **arithmetic combination only** — no ML-based inference

### Identifier Constraint

The following identifiers are **PROHIBITED** in this codebase:
- `progressLevel`, `promoteLevel`, `computeTrustScore`, `behavioralScore`
- `adaptiveBudget`, `optimizeBudget`, `predictSpending`
- `detectAnomaly`, `generateCounterfactual`
- `PersonalWorldModel`, `MissionAlignment`, `SocialTrust`
- `CognitiveLoop`, `AttentionFilter`, `GOVERNANCE_PIPELINE`

If a linter or reviewer flags an identifier as potentially matching production
internals, rename it immediately. No exceptions.

### Graph Constraint

- Delegation graphs are represented as **simple directed weighted graphs**
- No multi-dimensional trust vectors are implemented here
- Path finding uses **BFS only** — no production-grade graph algorithms

---

## What Is NOT Here

The following are intentionally absent from this package and MUST NOT be added:

- **Paper 18's full theorem proofs** — these are proprietary to MuVeraAI Corporation
- **Production delegation management algorithms** — the real system is not OSS
- **Adaptive trust progression** — trust levels are static per delegation edge
- **Real agent delegation data** — all graphs and agents are synthetic
- **Behavioral scoring** — no inference from observed behavior
- **Three-tier attention filter logic** — not implemented

---

## Disclosure Requirements

Every public-facing docstring in `src/delegation_trust/` MUST contain one of:
- `"SIMULATION ONLY"` — for core simulation classes and functions
- `"SIMULATION"` or `"synthetic"` — for data-generating utilities

The `README.md` MUST retain the disclaimer section unchanged.

---

## Change Approval

Changes to the following files require review from the research lead:
- `src/delegation_trust/model.py` — core simulation dynamics
- `src/delegation_trust/metrics.py` — metric definitions
- `scenarios.py` — paper's canonical scenario configurations
- `results/precomputed/*.json` — frozen reference data

Experiments and visualization changes are lower-risk but MUST NOT alter the
parameters that would change any pre-computed result without regenerating all
four JSON files and bumping the package version.

---

*Last reviewed: 2026-02-26*
*Package version at last review: 0.1.0*
