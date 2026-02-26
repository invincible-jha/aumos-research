# trust-filtered-planning

Research companion code for **Paper 12: How Trust Levels Constrain Agent Planning and Action Selection**.

> **DISCLAIMER: This is research simulation code, not the production algorithm.**
> All dynamics are simplified for academic analysis. All data is synthetic.
> This package does NOT contain Paper 12's full planning theory or any production
> cognitive loop or trust-gated execution implementation.

---

## Overview

This package provides a reproducible simulation environment for studying how
assigned trust levels constrain the action spaces available to agents during
planning, and how this constraint affects plan quality. The model uses a simple
forward-search planner that filters its action space to only include actions whose
required trust level is at or below the agent's assigned trust level, then compares
plan quality metrics across trust levels 0 through 5.

The simulation is intentionally simplified: planning is forward BFS/greedy search,
trust filtering is a static integer threshold, action spaces are discrete enumerated
sets, and all scenarios are synthetically generated. This simplified model is
sufficient to reproduce the paper's figures without encoding any production logic.

**Four core phenomena are studied:**

1. **Trust-filtered plan quality** — how plan quality degrades at lower trust levels
2. **Trust level comparison** — side-by-side quality metrics across all trust levels
3. **Action space analysis** — which action categories are gated at each trust level
4. **Quality degradation curve** — the relationship between trust level and optimality gap

---

## Installation

```bash
pip install trust-filtered-planning
# or, from source:
pip install -e ".[dev]"
```

**Requirements:** Python 3.10+, numpy >= 1.24, matplotlib >= 3.7

---

## Quick Start

```python
from trust_planning.model import TrustFilteredPlanner, PlannerConfig
from trust_planning.scenarios import SCENARIOS

config = PlannerConfig(seed=42)
planner = TrustFilteredPlanner(config)
scenario = SCENARIOS["office_assistant"]

# Plan at trust level 3
plan = planner.plan(scenario.goal, trust_level=3)
print(f"Steps to goal: {plan.steps_to_goal}")
print(f"Actions taken: {[a.name for a in plan.actions]}")

# Compare across all trust levels
comparison = planner.compare_trust_levels(scenario.goal)
for level, metrics in comparison.results_by_level.items():
    print(f"Level {level}: steps={metrics.steps_to_goal}, gap={metrics.optimality_gap:.3f}")
```

---

## Running Experiments

Each experiment script reproduces one figure from the paper:

```bash
# Individual experiments
python experiments/exp1_basic_planning.py
python experiments/exp2_trust_comparison.py
python experiments/exp3_action_space_analysis.py
python experiments/exp4_quality_degradation.py

# All experiments at once (saves figures to results/figures/)
python experiments/run_all.py
```

---

## Package Structure

```
src/trust_planning/
    model.py          # TrustFilteredPlanner — trust-gated forward search (SIMPLIFIED, NOT production)
    planner.py        # SimplePlanner — forward search through allowed action space
    evaluator.py      # PlanEvaluator — quality metrics under trust constraints
    scenarios.py      # Paper's canonical planning scenarios with action sets
    visualization.py  # Matplotlib figure generators
experiments/
    exp1_basic_planning.py         -> Fig. 1: Basic trust-filtered planning trace
    exp2_trust_comparison.py       -> Fig. 2: Plan quality across trust levels 0–5
    exp3_action_space_analysis.py  -> Fig. 3: Available action counts per trust level
    exp4_quality_degradation.py    -> Fig. 4: Optimality gap vs. trust level curve
    run_all.py                     -> Generates all figures
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
from trust_planning.model import TrustFilteredPlanner, PlannerConfig
from trust_planning.scenarios import SCENARIOS

with open("results/precomputed/fig2_data.json") as f:
    reference = json.load(f)

config = PlannerConfig(seed=42)
planner = TrustFilteredPlanner(config)
scenario = SCENARIOS["office_assistant"]
comparison = planner.compare_trust_levels(scenario.goal)

level_5_steps = comparison.results_by_level[5].steps_to_goal
ref_steps = reference["results_by_level"]["5"]["steps_to_goal"]
print(f"Level 5 steps match: {level_5_steps == ref_steps}")
```

---

## Citing

```bibtex
@software{muveraai_tfp_2026,
  title  = {Trust-Filtered Planning: How Trust Levels Constrain Agent Planning and Action Selection},
  author = {{MuVeraAI Research}},
  year   = {2026},
  url    = {https://github.com/aumos-ai/aumos-research},
  note   = {Research companion code for Paper 12}
}
```

Or use the `CITATION.cff` file at the root of this package.

---

## Constraints and Boundaries

See `FIRE_LINE.md` for the full constraint specification. Key points:

- Planning uses **simple forward search ONLY** — NOT production cognitive loop
- Paper 12's **full planning theory is proprietary** and NOT included here
- All data is **synthetic** — no real agent tasks or planning traces
- Trust filtering is **static integer threshold** — no adaptive trust assignment
- **No stochastic planning or continuous action spaces** are implemented

---

## License

MIT License — Copyright (c) 2026 MuVeraAI Corporation. See `LICENSE`.
