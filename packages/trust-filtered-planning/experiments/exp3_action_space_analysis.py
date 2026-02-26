# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp3_action_space_analysis.py — Action space size analysis experiment.

SIMULATION ONLY. Analyses how the available action space grows monotonically
as trust level increases, measuring absolute action counts, fraction of total
actions, and the relationship between action space size and plan optimality.
All data SYNTHETIC. Results reproduce Figure 3 of the companion paper.

Run:
    python experiments/exp3_action_space_analysis.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from trust_planning.model import TrustFilteredPlanner
from trust_planning.scenarios import all_domains


_TRUST_LEVELS: list[int] = [0, 1, 2, 3, 4, 5]


def run_experiment() -> dict[str, object]:
    """Run Experiment 3: action space size analysis across trust levels.

    SIMULATION ONLY. For each domain and trust level, counts available actions,
    computes available fraction, and measures the resulting plan quality.
    All data SYNTHETIC.

    Returns:
        Dictionary with per-domain action space profiles.
    """
    print("=" * 62)
    print("Exp 3 — Action Space Size Analysis")
    print("SIMULATION ONLY — synthetic data, forward-search BFS")
    print("=" * 62)

    domains = all_domains()
    all_domain_results: list[dict[str, object]] = []

    for domain in domains:
        total_actions = len(domain.actions)
        print(f"\n  Domain: {domain.name!r} | Total actions: {total_actions}")

        action_counts: list[int] = []
        fractions: list[float] = []
        reachability_by_trust: list[bool] = []

        goal = domain.goals[0]

        for trust_level in _TRUST_LEVELS:
            planner = TrustFilteredPlanner(domain, trust_level=trust_level)
            available = planner.available_actions()
            count = len(available)
            fraction = round(count / max(total_actions, 1), 6)

            plan = planner.plan(goal)

            action_counts.append(count)
            fractions.append(fraction)
            reachability_by_trust.append(plan.reachable)

            action_names = [a.name for a in available]
            print(
                f"    trust={trust_level}: available={count} ({fraction:.3f} of total) "
                f"reachable={plan.reachable} "
                f"actions={action_names}"
            )

        # Correlation: does more available actions = better reachability?
        reachable_trusts = [
            level for level, r in zip(_TRUST_LEVELS, reachability_by_trust) if r
        ]
        min_trust_for_reachability = min(reachable_trusts) if reachable_trusts else -1

        all_domain_results.append({
            "domain": domain.name,
            "total_actions": total_actions,
            "goal_id": goal.goal_id,
            "trust_levels": _TRUST_LEVELS,
            "action_counts": action_counts,
            "fractions": fractions,
            "reachability": reachability_by_trust,
            "min_trust_for_reachability": min_trust_for_reachability,
        })

    # Build cross-domain comparison arrays
    domain_names = [r["domain"] for r in all_domain_results]
    min_trust_thresholds = [r["min_trust_for_reachability"] for r in all_domain_results]
    total_action_counts = [r["total_actions"] for r in all_domain_results]

    print("\n  Cross-domain summary:")
    for name, threshold, total in zip(domain_names, min_trust_thresholds, total_action_counts):
        print(f"    {name}: total_actions={total} min_trust_for_reachability={threshold}")

    return {
        "experiment": "exp3_action_space_analysis",
        "description": (
            "Action space size vs trust level across all domains. "
            "SIMULATION ONLY — forward BFS, synthetic data."
        ),
        "trust_levels": _TRUST_LEVELS,
        "domain_names": domain_names,
        "min_trust_thresholds": min_trust_thresholds,
        "total_action_counts": total_action_counts,
        "results_by_domain": all_domain_results,
    }


def main() -> None:
    """Entry point for Experiment 3. SIMULATION ONLY."""
    results = run_experiment()

    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fig3_data.json")

    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(results, file_handle, indent=2)

    print(f"\nSaved results to: {output_path}")
    print("SIMULATION ONLY — do not use for production planning.")


if __name__ == "__main__":
    main()
