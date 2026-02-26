# protocol-composition-verifier

**Research companion code for Papers 9/25 — Formal verification of protocol composition.**

> RESEARCH TOOL — not production orchestration. All state machines are synthetic.
> See [FIRE_LINE.md](FIRE_LINE.md) for the explicit scope boundary.

---

## Overview

This package implements a bounded model checker for three formal properties of composed
governance protocol state machines:

| Property | Section | Claim |
|---|---|---|
| Monotonic Restriction | §4.1 | Composition never expands permissions |
| Deadlock Freedom | §4.2 | No reachable state blocks all actions |
| Priority Ordering | §4.3 | Higher-priority protocol denials cannot be overridden |

Each protocol is modeled as a small finite state machine (3–5 states, 4–5 actions).
The verifier enumerates the Cartesian product of component state spaces and checks
each property via breadth-first search, bounded at 10,000 composed states by default.

---

## Installation

```bash
pip install -e .
```

Requires Python 3.10+. Visualization functions additionally require `matplotlib` and
`numpy`, which are installed as part of the default dependencies.

---

## Quick start

```python
from composition_verifier.scenarios import standard_composition
from composition_verifier.verifier import ProtocolCompositionVerifier

# Build [ATP, ASP, AEAP] — the three standard synthetic protocols
protocols = standard_composition()

verifier = ProtocolCompositionVerifier()

# Check all three properties at once
results = verifier.verify_all(protocols, priority=["ASP", "ATP", "AEAP"])

for name, result in results.items():
    verdict = "HOLDS" if result.holds else "VIOLATED"
    print(f"{name}: {verdict} ({result.states_checked} states checked)")
```

Expected output:

```
monotonic_restriction: HOLDS (27 states checked)
deadlock_freedom: HOLDS (3 states checked)
priority_ordering: HOLDS (27 states checked)
```

---

## Protocols

Three synthetic protocol models are provided in `scenarios.py`:

### ATP — Adaptive Trust Protocol

Three states: `low`, `medium`, `high`.
Models a simplified trust tier. Trust advances on benign actions and resets on
escalation. Only `read` is permitted at `low`; all actions are permitted at `high`.

### ASP — Adaptive Security Protocol

Three states: `normal`, `elevated`, `lockdown`.
Models a simplified security posture. Executing an action from `normal` triggers
`elevated` review. The `lockdown` state denies all actions.

### AEAP — Adaptive Efficiency and Allocation Protocol

Three states: `available`, `warning`, `exhausted`.
Models a simplified resource budget. Write and delete actions consume budget,
advancing state toward `exhausted`. Only `read` is permitted when exhausted.

### BROKEN — Intentional deadlock protocol (Experiment 2 only)

A single sink state that denies every action. Used to demonstrate that the deadlock
freedom check correctly identifies unsafe compositions.

---

## Experiments

Run individual experiments:

```bash
python experiments/exp1_monotonic_restriction.py
python experiments/exp2_deadlock_freedom.py
python experiments/exp3_priority_ordering.py
```

Run all experiments and write a JSON summary:

```bash
python experiments/run_all.py
```

This writes `results/precomputed/run_all_summary.json`.

### Experiment 1 — Monotonic Restriction

Verifies that composing ATP+ASP, and then ATP+ASP+AEAP, never increases permissions
relative to any single component. Reports the permission reduction from the most
permissive single protocol to the composed system in the initial joint state.

### Experiment 2 — Deadlock Freedom

Verifies that the standard [ATP, ASP, AEAP] composition is deadlock-free, then
introduces BROKEN to demonstrate that the verifier correctly identifies a deadlock
at the initial joint state.

### Experiment 3 — Priority Ordering

Verifies the priority ordering SAFETY (ASP) > COMPLIANCE (ATP) > EFFICIENCY (AEAP).
Reports which protocol provides the dominant denial in each of the 27 joint states.

---

## Visualization

```python
from composition_verifier.composer import ProtocolComposer
from composition_verifier.scenarios import standard_composition
from composition_verifier.visualization import (
    plot_state_space,
    plot_verification_result,
    plot_priority_heatmap,
    plot_composition_summary,
)

protocols = standard_composition()
composer = ProtocolComposer(protocols)

# Reachable state space grid
plot_state_space(composer, save_path="state_space.png")

# Priority permission heatmap
plot_priority_heatmap(protocols, ["ASP", "ATP", "AEAP"], save_path="heatmap.png")
```

---

## Package structure

```
src/composition_verifier/
    __init__.py          Public API
    model.py             State, Transition, ProtocolModel, VerificationResult
    composer.py          ProtocolComposer — product state machine
    properties.py        PropertySpec catalogue
    verifier.py          ProtocolCompositionVerifier — bounded model checker
    scenarios.py         Synthetic protocol builders
    visualization.py     Matplotlib figure helpers

experiments/
    exp1_monotonic_restriction.py
    exp2_deadlock_freedom.py
    exp3_priority_ordering.py
    run_all.py

results/precomputed/
    fig1_data.json       Monotonic restriction data
    fig2_data.json       Deadlock freedom data
    fig3_data.json       Priority ordering heatmap data
```

---

## Citing this work

If you use this software, please cite as directed in [CITATION.cff](CITATION.cff).

---

## License

MIT — see [LICENSE](LICENSE).

---

## Scope

This package is a **research simulation tool**. See [FIRE_LINE.md](FIRE_LINE.md) for a
precise description of what this package is and is not. No production orchestration
logic is present in this repository.
