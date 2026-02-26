# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp4_quality_degradation.py — Plan quality degradation experiment.

SIMULATION ONLY. Quantifies how plan quality (cost, optimality gap) degrades
as trust level decreases from 5 to 0. Uses the tiered access and high-restriction
domains to demonstrate sharp quality drops at specific trust thresholds.
All data SYNTHETIC. Results reproduce Figure 4 of the companion paper.

Run:
    python experiments/exp4_quality_degradation.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from trust_planning.evaluator import PlanEvaluator
from trust_planning.model import TrustFilteredPlanner
from trust_planning.scenarios import (
    all_domains,
    domain_high_restriction,
    domain_tiered_access,
)
from trust_planning.visualization import plot_quality_degradation, plot_domain_comparison


_TRUST_LEVELS: list[int] = [0, 1, 2, 3, 4, 5]


def run_experiment() -> dict[str, object]:
    """Run Experiment 4: plan quality degradation as trust decreases.

    SIMULATION ONLY. Sweeps trust levels 5 down to 0 for the tiered access
    and high-restriction domains. Computes cost degradation rate and generates
    degradation plots. All data SYNTHETIC.

    Returns:
        Dictionary with per-domain degradation profiles.
    """
    print("=" * 62)
    print("Exp 4 — Plan Quality Degradation")
    print("SIMULATION ONLY — synthetic data, forward-search BFS")
    print("=" * 62)

    evaluator = PlanEvaluator()
    focus_domains = [domain_tiered_access(), domain_high_restriction()]
    all_simulation_domains = all_domains()

    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "figures")
    os.makedirs(output_dir, exist_ok=True)

    per_domain_degradation: list[dict[str, object]] = []

    for domain in focus_domains:
        print(f"\n  Domain: {domain.name!r}")
        goal = domain.goals[0]
        print(f"    Goal: {goal.goal_id!r}")

        planner = TrustFilteredPlanner(domain, trust_level=5)
        plans = planner.compare_trust_levels(goal, trust_levels=_TRUST_LEVELS)

        reachable_plans = [p for p in plans if p.reachable]
        baseline_cost = (
            min(p.total_cost for p in reachable_plans) if reachable_plans else 0
        )

        degradation = evaluator.quality_degradation_rate(plans, baseline_cost)
        reachable_flags = [p.reachable for p in plans]

        print(f"    Baseline cost: {baseline_cost}")
        for plan, deg in zip(plans, degradation):
            deg_str = f"{deg:.4f}" if deg != float("inf") else "inf (unreachable)"
            print(
                f"      trust={plan.trust_level}: reachable={plan.reachable} "
                f"cost={plan.total_cost} degradation={deg_str}"
            )

        # Generate degradation figure
        fig = plot_quality_degradation(
            trust_levels=_TRUST_LEVELS,
            degradation_rates=degradation,
            reachable_flags=reachable_flags,
            domain_name=domain.name,
            save_path=os.path.join(output_dir, f"fig4_{domain.name}_degradation.png"),
            show=False,
        )
        fig.clf()

        per_domain_degradation.append({
            "domain": domain.name,
            "goal_id": goal.goal_id,
            "baseline_cost": baseline_cost,
            "trust_levels": _TRUST_LEVELS,
            "plan_costs": [p.total_cost for p in plans],
            "reachable": reachable_flags,
            "degradation_rates": [
                0.0 if d == float("inf") else d for d in degradation
            ],
        })

    # Cross-domain comparison figure
    domain_names_all: list[str] = []
    min_trust_for_reach: list[int] = []
    optimal_costs: list[int] = []

    for domain in all_simulation_domains:
        goal = domain.goals[0]
        planner = TrustFilteredPlanner(domain, trust_level=5)
        plans = planner.compare_trust_levels(goal, trust_levels=_TRUST_LEVELS)

        min_trust = next((p.trust_level for p in plans if p.reachable), 6)
        reachable_plans = [p for p in plans if p.reachable]
        opt_cost = min(p.total_cost for p in reachable_plans) if reachable_plans else 0

        domain_names_all.append(domain.name)
        min_trust_for_reach.append(min_trust)
        optimal_costs.append(opt_cost)

    fig_cmp = plot_domain_comparison(
        domain_names=domain_names_all,
        min_trust_for_reachability=min_trust_for_reach,
        optimal_costs=optimal_costs,
        save_path=os.path.join(output_dir, "fig4_domain_comparison.png"),
        show=False,
    )
    fig_cmp.clf()

    return {
        "experiment": "exp4_quality_degradation",
        "description": (
            "Plan quality degradation as trust level decreases. "
            "SIMULATION ONLY — forward BFS, synthetic data."
        ),
        "trust_levels": _TRUST_LEVELS,
        "focus_domains": [r["domain"] for r in per_domain_degradation],
        "per_domain_degradation": per_domain_degradation,
        "cross_domain_comparison": {
            "domain_names": domain_names_all,
            "min_trust_for_reachability": min_trust_for_reach,
            "optimal_costs": optimal_costs,
        },
    }


def main() -> None:
    """Entry point for Experiment 4. SIMULATION ONLY."""
    results = run_experiment()

    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fig4_data.json")

    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(results, file_handle, indent=2)

    print(f"\nSaved results to: {output_path}")
    print("SIMULATION ONLY — do not use for production planning.")


if __name__ == "__main__":
    main()
