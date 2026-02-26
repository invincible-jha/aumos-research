# Fire Line — AumOS Research Companions

## What is a Fire Line?

A fire line defines the absolute boundary between open-source code and proprietary IP. Code on the open side is freely available. Code beyond the fire line is proprietary to MuVeraAI Corporation.

## Global Research Companion Fire Line

### IN (Open Source — MIT)

- Simplified simulation models for paper reproduction
- Synthetic data generators
- Convergence/stability/safety metric computation
- Experiment scripts reproducing paper figures
- Pre-computed results for verification
- Matplotlib/Seaborn visualization code

### EXCLUDED (Proprietary)

- Production algorithms (trust progression, memory governance, economic enforcement)
- Real-world agent behavioral data
- Production tuning parameters, thresholds, decay rates
- Multi-dimensional trust vectors
- 4-tier memory architecture (sensory/working/episodic/semantic)
- Paper 22 full 25-theorem proofs
- Cross-protocol orchestration logic (GOVERNANCE_PIPELINE)
- Behavioral scoring algorithms

## Per-Package Fire Lines

See each package's individual FIRE_LINE.md for specific boundaries.

## Enforcement

- CI grep scans for forbidden identifiers
- All simulation models include "NOT production algorithm" disclaimers
- All data must be synthetic (no real agent behavior data)
