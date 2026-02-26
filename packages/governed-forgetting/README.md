# governed-forgetting

**Research companion for Paper 5: Memory Retention Policy Verification**

> SIMULATION ONLY — not production AMGP implementation.
> All memory records are synthetic. No real agent memory content is stored or processed.

---

## Overview

`governed-forgetting` is a Python research simulation package that accompanies
Paper 5 on formal verification of memory retention policies. It provides:

- Four **retention policy types** — time-based, relevance-decay, consent-based, and composite
- A **MemoryRetentionModel** that simulates policy decisions over synthetic memory streams
- A **RetentionVerifier** that checks four formal properties against policy configurations
- Four **predefined scenarios** matching the paper's figures, all reproducible with `seed=42`
- **Matplotlib figure generators** for all four paper figures
- **Precomputed JSON results** (populate with `results/precomputed/generate.py`)

This package does **not** implement the production Autonomous Memory Governance Protocol (AMGP).
The retention dynamics here are intentionally simplified for academic illustration.

---

## Installation

```bash
pip install governed-forgetting
# or from source:
pip install -e "packages/governed-forgetting"
```

Python 3.10+ required. Dependencies: `numpy>=1.24`, `matplotlib>=3.7`.

---

## Quick Start

```python
from governed_forgetting import (
    MemoryRetentionModel,
    SimulationConfig,
    TimeBasedPolicy,
    RetentionVerifier,
)

# Configure and run a simulation
policy = TimeBasedPolicy(ttl=100)
config = SimulationConfig(policies=[policy], seed=42)
model = MemoryRetentionModel(config)
stream = model.generate_synthetic_stream(n=500)
result = model.simulate(stream)

print(f"Retention rate: {result.retention_rate:.2%}")
print(f"Records retained: {len(result.retained)}")
print(f"Records forgotten: {len(result.forgotten)}")

# Verify formal properties
verifier = RetentionVerifier()
completeness = verifier.verify_completeness(policy, stream)
monotonic = verifier.verify_monotonic_forgetting(policy, stream)
bounded = verifier.verify_bounded_retention(result, max_retention=100)

print(f"Completeness holds: {completeness.holds}")
print(f"Monotonic forgetting holds: {monotonic.holds}")
print(f"Bounded retention holds: {bounded.holds}")
```

---

## Policy Types

### TimeBasedPolicy

Forgets a record once its age exceeds a fixed TTL (time-to-live) in simulation timesteps.

```python
from governed_forgetting import TimeBasedPolicy
policy = TimeBasedPolicy(ttl=100)
```

### RelevanceDecayPolicy

Forgets a record when its exponentially-decayed relevance score falls below a threshold.

```python
from governed_forgetting import RelevanceDecayPolicy
policy = RelevanceDecayPolicy(decay_rate=0.01, threshold=0.3)
```

### ConsentBasedPolicy

Forgets all records belonging to an owner as soon as their consent is revoked.

```python
from governed_forgetting import ConsentBasedPolicy
consent_store = {"user_0": True, "user_1": False}
policy = ConsentBasedPolicy(consent_store=consent_store)
policy.revoke("user_0")  # immediately forgets user_0's records
```

### CompositePolicy

Combines multiple policies with AND (``"all"``) or OR (``"any"``) semantics.

```python
from governed_forgetting import CompositePolicy, TimeBasedPolicy, RelevanceDecayPolicy

composite = CompositePolicy(
    policies=[TimeBasedPolicy(ttl=200), RelevanceDecayPolicy(decay_rate=0.01, threshold=0.3)],
    mode="all",  # forget when ANY policy rejects (AND logic on retention)
)
```

---

## Scenarios

Four predefined scenarios reproduce the paper figures:

```python
from governed_forgetting.scenarios import (
    scenario_time_based,         # Figure 1
    scenario_relevance_decay,    # Figure 2
    scenario_consent_revocation, # Figure 3
    scenario_composite_policy,   # Figure 4
)

bundle = scenario_time_based(n_memories=500, ttl=100, seed=42)
result = bundle.model.simulate(bundle.memory_stream)
```

---

## Running Experiments

```bash
cd packages/governed-forgetting

# Run individual experiments
python experiments/exp1_time_based_retention.py
python experiments/exp2_relevance_decay.py
python experiments/exp3_consent_revocation.py
python experiments/exp4_policy_composition.py

# Run all experiments
python experiments/run_all.py

# Generate precomputed JSON result files
python results/precomputed/generate.py
```

---

## Formal Property Verification

`RetentionVerifier` checks four properties:

| Method | Property |
|---|---|
| `verify_completeness` | Every record produces a definite True/False decision |
| `verify_monotonic_forgetting` | Once forgotten, a record is never resurrected |
| `verify_consent_compliance` | Revoked owners' records are forgotten within `max_delay` ticks |
| `verify_bounded_retention` | No retained record exceeds `max_retention` timesteps of age |

---

## Precomputed Results

Precomputed JSON files for all four figures are stored in `results/precomputed/`.
To regenerate with `seed=42`:

```bash
python results/precomputed/generate.py
```

---

## Fire Line

See `FIRE_LINE.md` for explicit boundaries on what this package must not implement.
Key constraints:

- No four-tier memory architecture
- No production AMGP implementation
- No adaptive or ML-based retention
- No real memory content — synthetic records only

---

## Citation

If you use this software, please cite the associated paper using `CITATION.cff`.

---

## License

MIT License. Copyright (c) 2026 MuVeraAI Corporation. See `LICENSE`.
