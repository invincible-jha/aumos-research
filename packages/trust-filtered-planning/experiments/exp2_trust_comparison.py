# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp2_trust_comparison.py — Trust level comparison experiment.

SIMULATION ONLY. Compares plan quality (length, cost, reachability) across
all six trust levels (0–5) for each domain and goal. Demonstrates how trust
level monotonically constrains the planning search space. All data SYNTHETIC.
Results reproduce Figure 2 of the trust-filtered-planning companion paper.

Run:
    python experiments/exp2_trust_comparison.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from trust_planning.evaluator import PlanEvaluator
from trust_planning.model import TrustFilteredPlanner
from trust_planning.scenarios import all_domains


_TRUST_LEVELS: list[int] = [0, 1, 2, 3, 4, 5]


def run_experiment() -> dict[str, object]:
    """Run Experiment 2: trust level comparison across all domains.

    SIMULATION ONLY. For each domain and primary goal, sweeps trust levels 0–5,
    recording plan reachability, length, cost, and optimality gap. All SYNTHETIC.

    Returns:
        Dictionary with per-domain trust-level comparison tables.
    """
    print("=" * 62)
    print("Exp 2 — Trust Level Comparison")
    print("SIMULATION ONLY — synthetic data, forward-search BFS")
    print("=" * 62)

    evaluator = PlanEvaluator()
    domains = all_domains()

    all_results: list[dict[str, object]] = []
    domain_labels: list[str] = []
    reachability_thresholds: list[int] = []

    for domain in domains:
        print(f"\n  Domain: {domain.name!r}")
        goal = domain.goals[0]  # Use primary goal for comparison
        print(f"    Goal: {goal.goal_id!r}")

        planner = TrustFilteredPlanner(domain, trust_level=5)
        plans = planner.compare_trust_levels(goal, trust_levels=_TRUST_LEVELS)

        # Compute baseline from highest-trust reachable plan
        reachable_plans = [plan for plan in plans if plan.reachable]
        baseline_cost = (
            min(plan.total_cost for plan in reachable_plans)
            if reachable_plans else 0
        )

        rows = evaluator.compare_across_trust_levels(plans, total_domain_actions=len(domain.actions))
        degradation = evaluator.quality_degradation_rate(plans, baseline_cost)

        # Find minimum trust for reachability
        min_trust = next(
            (plan.trust_level for plan in plans if plan.reachable), -1
        )
        domain_labels.append(domain.name)
        reachability_thresholds.append(min_trust)

        print(
            f"    Baseline cost (min across reachable): {baseline_cost} | "
            f"Min reachable trust: {min_trust}"
        )

        trust_rows: list[dict[str, object]] = []
        for plan, row, deg in zip(plans, rows, degradation):
            deg_val: object = deg if deg != float("inf") else "unreachable"
            print(
                f"      trust={plan.trust_level}: "
                f"reachable={plan.reachable} length={plan.length} "
                f"cost={plan.total_cost} gap={row.optimality_gap:.4f} "
                f"degradation={deg_val}"
            )
            trust_rows.append({
                "trust_level": plan.trust_level,
                "reachable": plan.reachable,
                "step_count": plan.length,
                "total_cost": plan.total_cost,
                "optimality_gap": row.optimality_gap,
                "available_actions": row.available_action_count,
                "degradation": 0.0 if deg == float("inf") else deg,
            })

        all_results.append({
            "domain": domain.name,
            "goal_id": goal.goal_id,
            "baseline_cost": baseline_cost,
            "min_reachable_trust": min_trust,
            "trust_rows": trust_rows,
        })

    return {
        "experiment": "exp2_trust_comparison",
        "description": (
            "Plan quality comparison across trust levels 0–5 for all domains. "
            "SIMULATION ONLY — forward BFS, synthetic data."
        ),
        "trust_levels": _TRUST_LEVELS,
        "domain_labels": domain_labels,
        "reachability_thresholds": reachability_thresholds,
        "results_by_domain": all_results,
    }


def main() -> None:
    """Entry point for Experiment 2. SIMULATION ONLY."""
    results = run_experiment()

    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fig2_data.json")

    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(results, file_handle, indent=2)

    print(f"\nSaved results to: {output_path}")
    print("SIMULATION ONLY — do not use for production planning.")


if __name__ == "__main__":
    main()
