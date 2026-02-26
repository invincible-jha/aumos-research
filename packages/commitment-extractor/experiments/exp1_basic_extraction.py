# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp1_basic_extraction.py — Basic commitment extraction experiment.

SIMULATION ONLY. Demonstrates rule-based commitment extraction from synthetic
agent conversations. Measures how many commitments are extracted per message
across the full synthetic scenario dataset. All data is SYNTHETIC.
Results reproduce Figure 1 of the commitment-extractor companion paper.

Run:
    python experiments/exp1_basic_extraction.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from commitment_extractor.model import CommitmentExtractor, CommitmentType
from commitment_extractor.scenarios import all_scenarios


def run_experiment() -> dict[str, object]:
    """Run Experiment 1: basic commitment extraction from synthetic conversations.

    SIMULATION ONLY. Applies CommitmentExtractor to all synthetic scenarios and
    reports per-scenario and per-type extraction counts. All data is SYNTHETIC.

    Returns:
        Dictionary with scenario names, extraction counts, and type distributions.
    """
    print("=" * 62)
    print("Exp 1 — Basic Commitment Extraction")
    print("SIMULATION ONLY — synthetic data, rule-based extraction")
    print("=" * 62)

    extractor = CommitmentExtractor(model="rule-based")
    scenarios = all_scenarios()

    scenario_names: list[str] = []
    extracted_counts: list[int] = []
    ground_truth_counts: list[int] = []
    type_distribution: dict[str, int] = {t.value: 0 for t in CommitmentType}

    per_scenario: list[dict[str, object]] = []

    for scenario in scenarios:
        extracted = extractor.extract_from_conversation(scenario.messages)
        count = len(extracted)

        type_breakdown: dict[str, int] = {t.value: 0 for t in CommitmentType}
        for commitment in extracted:
            type_breakdown[commitment.commitment_type.value] += 1
            type_distribution[commitment.commitment_type.value] += 1

        scenario_names.append(scenario.name)
        extracted_counts.append(count)
        ground_truth_counts.append(scenario.ground_truth_count)

        print(f"\n  Scenario: {scenario.name!r}")
        print(f"    Ground truth: {scenario.ground_truth_count} | Extracted: {count}")
        print(f"    Type breakdown: {type_breakdown}")

        for commitment in extracted:
            print(
                f"      [{commitment.commitment_type.value}] "
                f"sender={commitment.sender!r} "
                f'span="{commitment.text_span[:60]}"'
            )

        per_scenario.append({
            "name": scenario.name,
            "ground_truth": scenario.ground_truth_count,
            "extracted": count,
            "type_breakdown": type_breakdown,
        })

    print(f"\n  Overall type distribution: {type_distribution}")
    print(
        f"\n  Total extracted: {sum(extracted_counts)} "
        f"across {len(scenarios)} scenarios"
    )

    return {
        "experiment": "exp1_basic_extraction",
        "description": (
            "Basic commitment extraction from synthetic conversations. "
            "SIMULATION ONLY — rule-based regex, seed=42."
        ),
        "x": scenario_names,
        "x_label": "scenario",
        "y_label": "commitment_count",
        "extracted_counts": extracted_counts,
        "ground_truth_counts": ground_truth_counts,
        "type_distribution": type_distribution,
        "per_scenario": per_scenario,
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
    print("SIMULATION ONLY — do not use for production commitment tracking.")


if __name__ == "__main__":
    main()
