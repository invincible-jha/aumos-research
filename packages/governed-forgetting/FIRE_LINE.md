# FIRE LINE — governed-forgetting

This document defines the hard boundaries for this package.
Crossing any fire line is a critical IP/safety violation.

---

## What this package IS

- A **research simulation** of simplified memory retention dynamics
- A tool for academic reproducibility of Paper 5 figures
- A demonstration of formal property checking on toy retention policies
- Uses **synthetic, randomly generated** memory records only (content_hash placeholders)

---

## What this package IS NOT — NEVER IMPLEMENT

1. **NO four-tier memory architecture** (sensory / working / episodic / semantic)
   - Any tiered memory system is core production IP and must not appear here

2. **NO production AMGP implementation**
   - Do not implement the Autonomous Memory Governance Protocol
   - Do not reference, reverse-engineer, or approximate production retention logic

3. **NO adaptive retention** — forgetting thresholds are fixed constants, never learned
   - No ML-based decay parameter tuning
   - No behavior-based retention adjustment

4. **NO real content** — MemoryRecord.content_hash is an opaque placeholder only
   - Never store, process, or transmit actual agent memory content

5. **NO cross-protocol orchestration**
   - This package is standalone; do not wire it to trust layers, budget systems,
     or any other governance protocol

6. **NO forbidden identifiers** — these strings must never appear in source code:
   ```
   progressLevel   promoteLevel    computeTrustScore   behavioralScore
   adaptiveBudget  optimizeBudget  predictSpending
   detectAnomaly   generateCounterfactual
   PersonalWorldModel   MissionAlignment   SocialTrust
   CognitiveLoop   AttentionFilter   GOVERNANCE_PIPELINE
   ```

7. **NO latency targets or specific production threshold values**

---

## Permitted scope

- `TimeBasedPolicy`, `RelevanceDecayPolicy`, `ConsentBasedPolicy`, `CompositePolicy`
- `MemoryRetentionModel` — simplified AND-of-policies simulation loop
- `RetentionVerifier` — completeness, monotonicity, consent compliance, bounded retention
- `ScenarioBundle` — predefined scenarios matching Paper 5 figures 1–4
- Matplotlib visualization helpers
- Precomputed seed=42 JSON results

---

## Enforcement

All pull requests touching this package must be reviewed against this fire line.
If in doubt, do not implement — ask the research team.
