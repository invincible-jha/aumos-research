# FIRE LINE — commitment-extractor

This document records the constraints and boundaries that govern this package.
All contributors MUST read this before making changes.

---

## What This Package Is

A **research simulation** package that accompanies Paper 21:
*"Extracting and Tracking Commitments from Agent Communications"*

It exists solely to:
1. Allow reproduction of the paper's figures and numerical results
2. Provide a clean reference implementation of the simplified rule-based
   commitment extraction described in the paper
3. Serve as a baseline for future academic comparisons

---

## Hard Constraints

### Simulation Boundary

- All code in `src/commitment_extractor/` implements **RULE-BASED NLP ONLY**
- The simulation does NOT contain, reverse-engineer, or approximate any production
  LLM-powered commitment extraction or agent communication monitoring system
- This package does NOT implement the full semantic understanding from Paper 21
  in their complete form — only the simplified regex-based corollaries
- Any contributor who believes they are inadvertently implementing production logic
  MUST stop and file an issue before continuing

### Data Boundary

- ALL conversation data and agent messages used in this package are **SYNTHETIC**
- No real agent communications, no real commitment records
- Pre-computed results in `results/precomputed/` are generated deterministically
  from the simulation with `seed=42` — they are not sourced from real systems

### Algorithm Boundary

- Commitment extraction is **REGEX PATTERN MATCHING ONLY** — no LLM inference
- Classification is **RULE-BASED** — predetermined regex categories only
- Fulfillment checking is **KEYWORD MATCHING** — simple follow-up detection
- There is NO semantic embedding or vector similarity in this package
- There is NO LLM-powered production extraction logic in this package

### Identifier Constraint

The following identifiers are **PROHIBITED** in this codebase:
- `progressLevel`, `promoteLevel`, `computeTrustScore`, `behavioralScore`
- `adaptiveBudget`, `optimizeBudget`, `predictSpending`
- `detectAnomaly`, `generateCounterfactual`
- `PersonalWorldModel`, `MissionAlignment`, `SocialTrust`
- `CognitiveLoop`, `AttentionFilter`, `GOVERNANCE_PIPELINE`

If a linter or reviewer flags an identifier as potentially matching production
internals, rename it immediately. No exceptions.

### NLP Constraint

- All text analysis uses **Python standard library `re` module only**
- No third-party NLP libraries (spaCy, NLTK, transformers) are imported
- Pattern matching is case-insensitive regex — not semantic understanding
- This constraint ensures the simulation cannot be confused with production
  LLM-powered extraction systems

---

## What Is NOT Here

The following are intentionally absent from this package and MUST NOT be added:

- **Paper 21's full semantic extraction system** — proprietary to MuVeraAI Corporation
- **Production LLM-powered commitment extraction** — the real system is not OSS
- **Vector embeddings** — no semantic similarity computation
- **Real agent communication data** — all messages are synthetic
- **Adaptive classification** — classifiers are static regex, not learned
- **Cross-agent commitment negotiation logic** — not implemented

---

## Disclosure Requirements

Every public-facing docstring in `src/commitment_extractor/` MUST contain one of:
- `"SIMULATION ONLY"` — for core simulation classes and functions
- `"SIMULATION"` or `"synthetic"` — for data-generating utilities

The `README.md` MUST retain the disclaimer section unchanged.

---

## Change Approval

Changes to the following files require review from the research lead:
- `src/commitment_extractor/model.py` — core extraction logic
- `src/commitment_extractor/classifier.py` — pattern definitions
- `scenarios.py` — paper's canonical conversation datasets
- `results/precomputed/*.json` — frozen reference data

Experiments and visualization changes are lower-risk but MUST NOT alter the
parameters that would change any pre-computed result without regenerating all
four JSON files and bumping the package version.

---

*Last reviewed: 2026-02-26*
*Package version at last review: 0.1.0*
