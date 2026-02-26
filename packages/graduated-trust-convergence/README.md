# graduated-trust-convergence

Research companion code for **Paper 13: Graduated Trust Convergence — Formal Properties of Multi-Level Trust Progression**.

> **DISCLAIMER: This is research simulation code, not the production algorithm.**
> All dynamics are simplified for academic analysis. All data is synthetic.
> This package does NOT contain or approximate any production trust system.

---

## Overview

This package provides a reproducible simulation environment for studying convergence
properties of graduated trust progression systems. The model simulates how an agent's
trust level evolves over time under various behavioral patterns and policy configurations.

The simulation is intentionally simplified: trust is a scalar in `[0, L-1]` where `L`
is the number of levels, updated by a linear rule combining action quality and decay.
This simplified model is sufficient to reproduce the paper's theoretical results and
figures without encoding any production system logic.

---

## Installation

```bash
pip install graduated-trust-convergence
# or, from source:
pip install -e ".[dev]"
```

**Requirements:** Python 3.10+, numpy >= 1.24, matplotlib >= 3.7

---

## Quick Start

```python
from trust_convergence.scenarios import SCENARIOS
from trust_convergence.model import TrustProgressionModel
from trust_convergence.agents import CompliantAgent
from trust_convergence.metrics import convergence_rate, stability_index

config = SCENARIOS["baseline"]
model = TrustProgressionModel(config)
agent = CompliantAgent(quality=0.8, seed=42)

result = model.simulate(agent, timesteps=1000)

print(f"Final level:       {result.final_level:.3f}")
print(f"Convergence rate:  {result.convergence_rate:.4f}")
print(f"Stability index:   {result.stability:.4f}")
```

---

## Running Experiments

Each experiment script reproduces one figure from the paper:

```bash
# Individual experiments
python experiments/exp1_basic_convergence.py
python experiments/exp2_decay_impact.py
python experiments/exp3_multi_scope.py
python experiments/exp4_adversarial.py

# All experiments at once (saves figures to results/figures/)
python experiments/run_all.py
```

---

## Package Structure

```
src/trust_convergence/
    model.py          # TrustProgressionModel — core simulation (SIMPLIFIED, NOT production)
    agents.py         # Synthetic agent behavior generators
    metrics.py        # Convergence and stability metrics
    scenarios.py      # Paper's canonical scenario configurations
    visualization.py  # Matplotlib figure generators
experiments/
    exp1_basic_convergence.py   -> Fig. 1
    exp2_decay_impact.py        -> Fig. 2
    exp3_multi_scope.py         -> Fig. 3
    exp4_adversarial.py         -> Fig. 4
    run_all.py                  -> Generates all figures
results/
    precomputed/                # Frozen JSON data for offline verification
    figures/                    # Generated figure output directory
```

---

## Reproducing Paper Results

Pre-computed trajectory data is stored in `results/precomputed/fig{1-4}_data.json`.
These files were generated with `seed=42` and can be used to verify that your
installation produces identical results:

```python
import json
import numpy as np
from trust_convergence.scenarios import SCENARIOS
from trust_convergence.model import TrustProgressionModel
from trust_convergence.agents import CompliantAgent

with open("results/precomputed/fig1_data.json") as f:
    reference = json.load(f)

config = SCENARIOS["baseline"]
model = TrustProgressionModel(config)
agent = CompliantAgent(quality=0.8, seed=42)
result = model.simulate(agent, timesteps=1000)

trajectory_match = np.allclose(
    result.trajectory, reference["trajectory"], atol=1e-9
)
print(f"Trajectory matches reference: {trajectory_match}")
```

---

## Citing

```bibtex
@software{muveraai_gtc_2026,
  title  = {Graduated Trust Convergence: Formal Properties of Multi-Level Trust Progression},
  author = {{MuVeraAI Research}},
  year   = {2026},
  url    = {https://github.com/aumos-ai/aumos-research},
  note   = {Research companion code for Paper 13}
}
```

Or use the `CITATION.cff` file at the root of this package.

---

## Constraints and Boundaries

See `FIRE_LINE.md` for the full constraint specification. Key points:

- Simulation uses **simplified linear dynamics** — NOT the production algorithm
- All data is **synthetic** — no real behavior logs
- Trust is a **scalar** — no multi-dimensional vectors
- Several identifier names are prohibited (see `FIRE_LINE.md`)

---

## License

MIT License — Copyright (c) 2026 MuVeraAI Corporation. See `LICENSE`.
