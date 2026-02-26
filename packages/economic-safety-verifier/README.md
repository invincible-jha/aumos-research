# economic-safety-verifier

Research companion code for **Paper 22: Economic Safety Verification — Properties of Agent Spending Envelopes**.

> **DISCLAIMER: This is research simulation code, not the production algorithm.**
> All dynamics are simplified for academic analysis. All data is synthetic.
> This package does NOT contain Paper 22's 25 theorem proofs or any production
> AEAP (Agent Economic Accountability Protocol) implementation.

---

## Overview

This package provides a reproducible simulation environment for studying economic
safety properties of agent spending envelope systems. The model simulates how
agents spend within budget envelopes under various concurrency and commitment
patterns, and verifies that safety properties hold under a simple arithmetic
enforcement regime.

The simulation is intentionally simplified: budgets are scalar float limits,
enforcement is arithmetic comparison, and all spending data is synthetically
generated. This simplified model is sufficient to reproduce the paper's figures
without encoding any production system logic.

**Three core safety properties are verified:**

1. **No-overspend** — cumulative spending never exceeds the envelope limit
2. **Commitment-bounded** — committed reserves plus actual spending never exceed the limit
3. **Non-negative balance** — the remaining balance never drops below zero

---

## Installation

```bash
pip install economic-safety-verifier
# or, from source:
pip install -e ".[dev]"
```

**Requirements:** Python 3.10+, numpy >= 1.24, matplotlib >= 3.7

---

## Quick Start

```python
from economic_safety.scenarios import SCENARIOS
from economic_safety.model import EconomicModel, SimulationConfig
from economic_safety.verifier import EconomicSafetyVerifier

config = SimulationConfig(seed=42)
model = EconomicModel(config)
scenario = SCENARIOS["safe_single_agent"]

envelope = model.create_envelope(
    category=scenario.category,
    limit=scenario.envelope_limit,
)
result = model.simulate_spending(scenario.agents, timesteps=scenario.timesteps)

verifier = EconomicSafetyVerifier()
verification = verifier.verify_no_overspend(
    envelopes=list(model.envelopes.values()),
    transactions=model.transactions,
)

print(f"No-overspend holds: {verification.holds}")
print(f"Transactions checked: {verification.transactions_checked}")
print(f"Detail: {verification.detail}")
```

---

## Running Experiments

Each experiment script reproduces one figure from the paper:

```bash
# Individual experiments
python experiments/exp1_no_overspend.py
python experiments/exp2_commitment_safety.py
python experiments/exp3_concurrent_spending.py

# All experiments at once (saves figures to results/figures/)
python experiments/run_all.py
```

---

## Package Structure

```
src/economic_safety/
    model.py          # EconomicModel — spending simulation (SIMPLIFIED, NOT production)
    properties.py     # Safety property definitions (arithmetic, NOT theorem proofs)
    verifier.py       # EconomicSafetyVerifier — property verification engine
    scenarios.py      # Paper's canonical scenario configurations
    visualization.py  # Matplotlib figure generators
experiments/
    exp1_no_overspend.py        -> Fig. 1: Enforcement prevents overspend
    exp2_commitment_safety.py   -> Fig. 2: Commitment + spent bounded by limit
    exp3_concurrent_spending.py -> Fig. 3: Concurrent agent safety
    run_all.py                  -> Generates all figures
results/
    precomputed/                # Frozen JSON data for offline verification
    figures/                    # Generated figure output directory
```

---

## Reproducing Paper Results

Pre-computed result data is stored in `results/precomputed/fig{1-3}_data.json`.
These files were generated with `seed=42` and can be used to verify that your
installation produces identical results:

```python
import json
import numpy as np
from economic_safety.scenarios import SCENARIOS
from economic_safety.model import EconomicModel, SimulationConfig
from economic_safety.verifier import EconomicSafetyVerifier

with open("results/precomputed/fig1_data.json") as f:
    reference = json.load(f)

config = SimulationConfig(seed=42)
model = EconomicModel(config)
scenario = SCENARIOS["safe_single_agent"]
model.create_envelope(category=scenario.category, limit=scenario.envelope_limit)
result = model.simulate_spending(scenario.agents, timesteps=scenario.timesteps)

trajectory_match = np.allclose(
    result.balance_timeline, reference["balance_timeline"], atol=1e-9
)
print(f"Trajectory matches reference: {trajectory_match}")
```

---

## Citing

```bibtex
@software{muveraai_esv_2026,
  title  = {Economic Safety Verification: Properties of Agent Spending Envelopes},
  author = {{MuVeraAI Research}},
  year   = {2026},
  url    = {https://github.com/aumos-ai/aumos-research},
  note   = {Research companion code for Paper 22}
}
```

Or use the `CITATION.cff` file at the root of this package.

---

## Constraints and Boundaries

See `FIRE_LINE.md` for the full constraint specification. Key points:

- Simulation uses **simple arithmetic enforcement** — NOT the production AEAP
- Paper 22's **25 theorem proofs are proprietary** and NOT included here
- All data is **synthetic** — no real agent spending records
- Budget limits are **scalar floats** — no multi-dimensional representations
- **No saga-pattern compensation logic** is implemented

---

## License

MIT License — Copyright (c) 2026 MuVeraAI Corporation. See `LICENSE`.
