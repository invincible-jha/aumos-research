# delegation-trust-model

Research companion code for **Paper 18: Trust Dynamics in Agent Delegation Chains**.

> **DISCLAIMER: This is research simulation code, not the production algorithm.**
> All dynamics are simplified for academic analysis. All data is synthetic.
> This package does NOT contain Paper 18's full trust dynamics theorems or any
> production delegation management implementation.

---

## Overview

This package provides a reproducible simulation environment for studying trust
propagation across multi-agent delegation chains. The model simulates how trust
attenuates as authority is delegated through chains of agents, using a simple
multiplicative decay model where each hop in the chain reduces the effective trust
by the pairwise delegation trust level.

The simulation is intentionally simplified: trust is a scalar float per delegation
edge, propagation uses multiplicative composition, path finding uses BFS, and all
agent graphs are synthetically generated. This simplified model is sufficient to
reproduce the paper's figures without encoding any production system logic.

**Four core phenomena are studied:**

1. **Transitive trust decay** — effective trust decreases multiplicatively over hops
2. **Chain length effects** — longer delegation chains produce lower terminal trust
3. **Adversarial delegation** — malicious agents in a chain degrade overall trust
4. **Topology comparison** — chain vs. tree vs. mesh delegation graph structures

---

## Installation

```bash
pip install delegation-trust-model
# or, from source:
pip install -e ".[dev]"
```

**Requirements:** Python 3.10+, numpy >= 1.24, matplotlib >= 3.7

---

## Quick Start

```python
from delegation_trust.model import DelegationTrustModel, SimulationConfig
from delegation_trust.scenarios import SCENARIOS

config = SimulationConfig(seed=42)
model = DelegationTrustModel(config)
scenario = SCENARIOS["linear_chain_5hop"]

result = model.simulate_scenario(scenario)
print(f"Terminal trust: {result.terminal_trust:.4f}")
print(f"Hops: {result.path_length}")
print(f"Decay per hop: {result.decay_per_hop:.4f}")
```

---

## Running Experiments

Each experiment script reproduces one figure from the paper:

```bash
# Individual experiments
python experiments/exp1_basic_delegation.py
python experiments/exp2_chain_decay.py
python experiments/exp3_adversarial_delegation.py
python experiments/exp4_network_topology.py

# All experiments at once (saves figures to results/figures/)
python experiments/run_all.py
```

---

## Package Structure

```
src/delegation_trust/
    model.py          # DelegationTrustModel — chain simulation (SIMPLIFIED, NOT production)
    agents.py         # Synthetic agent scenario types (Compliant/Adversarial/Mixed/etc.)
    metrics.py        # Trust metrics (transitivity_score, decay_over_hops, etc.)
    scenarios.py      # Paper's canonical delegation topology configurations
    visualization.py  # Matplotlib figure generators
experiments/
    exp1_basic_delegation.py    -> Fig. 1: Basic delegation trust propagation
    exp2_chain_decay.py         -> Fig. 2: Decay rate vs. chain length
    exp3_adversarial_delegation.py -> Fig. 3: Adversarial agent impact
    exp4_network_topology.py    -> Fig. 4: Topology comparison
    run_all.py                  -> Generates all figures
results/
    precomputed/                # Frozen JSON data for offline verification
    figures/                    # Generated figure output directory
```

---

## Reproducing Paper Results

Pre-computed result data is stored in `results/precomputed/fig{1-4}_data.json`.
These files were generated with `seed=42` and can be used to verify that your
installation produces identical results:

```python
import json
from delegation_trust.model import DelegationTrustModel, SimulationConfig
from delegation_trust.scenarios import SCENARIOS

with open("results/precomputed/fig1_data.json") as f:
    reference = json.load(f)

config = SimulationConfig(seed=42)
model = DelegationTrustModel(config)
scenario = SCENARIOS["linear_chain_5hop"]
result = model.simulate_scenario(scenario)

print(f"Terminal trust matches: {abs(result.terminal_trust - reference['terminal_trust']) < 1e-9}")
```

---

## Citing

```bibtex
@software{muveraai_dtm_2026,
  title  = {Delegation Trust Model: Trust Dynamics in Agent Delegation Chains},
  author = {{MuVeraAI Research}},
  year   = {2026},
  url    = {https://github.com/aumos-ai/aumos-research},
  note   = {Research companion code for Paper 18}
}
```

Or use the `CITATION.cff` file at the root of this package.

---

## Constraints and Boundaries

See `FIRE_LINE.md` for the full constraint specification. Key points:

- Trust propagation uses **multiplicative decay ONLY** — NOT production trust algorithms
- Paper 18's **full theorem proofs are proprietary** and NOT included here
- All data is **synthetic** — no real agent delegation records
- Trust levels are **scalar floats per edge** — no multi-dimensional representations
- **No adaptive trust progression** is implemented

---

## License

MIT License — Copyright (c) 2026 MuVeraAI Corporation. See `LICENSE`.
