# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp1_basic_planning.py — Basic trust-filtered planning experiment.

SIMULATION ONLY. Demonstrates how TrustFilteredPlanner finds plans across
the linear pipeline and branching domains at trust level 5 (full access).
Compares with SimplePlanner (unconstrained baseline). All data SYNTHETIC.
Results reproduce Figure 1 of the trust-filtered-planning companion paper.

Run:
    python experiments/exp1_basic_planning.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from trust_planning.evaluator import PlanEvaluator
from trust_planning.model import TrustFilteredPlanner
from trust_planning.planner import SimplePlanner
from trust_planning.scenarios import domain_branching, domain_linear_pipeline


def run_experiment() -> dict[str, object]:
    """Run Experiment 1: basic trust-filtered planning at full trust.

    SIMULATION ONLY. Applies TrustFilteredPlanner (trust=5) and SimplePlanner
    to the linear pipeline and branching domains. Reports plan length, cost,
    and action diversity. All data SYNTHETIC.

    Returns:
        Dictionary with per-domain, per-goal results.
    """
    print("=" * 62)
    print("Exp 1 — Basic Trust-Filtered Planning")
    print("SIMULATION ONLY — synthetic data, forward-search BFS")
    print("=" * 62)

    evaluator = PlanEvaluator()
    domains = [domain_linear_pipeline(), domain_branching()]

    results_by_domain: list[dict[str, object]] = []
    scenario_labels: list[str] = []
    plan_lengths: list[int] = []
    plan_costs: list[int] = []

    for domain in domains:
        print(f"\n  Domain: {domain.name!r}")
        simple_planner = SimplePlanner(domain)
        trust_planner = TrustFilteredPlanner(domain, trust_level=5)

        domain_results: list[dict[str, object]] = []

        for goal in domain.goals:
            simple_plan = simple_planner.plan(goal)
            filtered_plan = trust_planner.plan(goal)

            simple_metrics = evaluator.evaluate(simple_plan)
            filtered_metrics = evaluator.evaluate(filtered_plan, baseline_optimal_cost=simple_plan.total_cost)

            print(f"\n    Goal: {goal.goal_id!r} — {goal.description}")
            print(
                f"      SimplePlanner: length={simple_metrics.step_count} "
                f"cost={simple_metrics.total_cost} diversity={simple_metrics.action_diversity:.4f}"
            )
            print(
                f"      FilteredPlanner (trust=5): length={filtered_metrics.step_count} "
                f"cost={filtered_metrics.total_cost} gap={filtered_metrics.optimality_gap:.4f}"
            )

            if filtered_plan.actions:
                print(f"      Plan actions: {[a.name for a in filtered_plan.actions]}")

            scenario_labels.append(f"{domain.name}/{goal.goal_id}")
            plan_lengths.append(filtered_metrics.step_count)
            plan_costs.append(filtered_metrics.total_cost)

            domain_results.append({
                "goal_id": goal.goal_id,
                "simple_length": simple_metrics.step_count,
                "simple_cost": simple_metrics.total_cost,
                "filtered_length": filtered_metrics.step_count,
                "filtered_cost": filtered_metrics.total_cost,
                "optimality_gap": filtered_metrics.optimality_gap,
                "action_diversity": filtered_metrics.action_diversity,
                "reachable": filtered_metrics.reachable,
                "plan_action_names": [a.name for a in filtered_plan.actions],
            })

        results_by_domain.append({
            "domain": domain.name,
            "goals": domain_results,
        })

    return {
        "experiment": "exp1_basic_planning",
        "description": (
            "Basic trust-filtered planning at trust_level=5. "
            "SIMULATION ONLY — forward BFS, synthetic data."
        ),
        "x": scenario_labels,
        "x_label": "domain/goal",
        "y_label": "plan_length",
        "plan_lengths": plan_lengths,
        "plan_costs": plan_costs,
        "results_by_domain": results_by_domain,
    }


def main() -> None:
    """Entry point for Experiment 1. SIMULATION ONLY."""
    results = run_experiment()

    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fig1_data.json")

    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(results, file_handle, indent=2)

    print(f"\nSaved results to: {output_path}")
    print("SIMULATION ONLY — do not use for production planning.")


if __name__ == "__main__":
    main()
