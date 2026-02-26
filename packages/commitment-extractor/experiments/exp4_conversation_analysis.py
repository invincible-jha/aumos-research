# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp4_conversation_analysis.py — Full conversation analysis experiment.

SIMULATION ONLY. Analyses commitment density (commitments per message),
type diversity (Shannon entropy of type distribution), and fulfillment patterns
across the full synthetic conversation dataset. All data is SYNTHETIC.
Results reproduce Figure 4 of the commitment-extractor companion paper.

Run:
    python experiments/exp4_conversation_analysis.py
"""

from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from commitment_extractor.classifier import CommitmentClassifier
from commitment_extractor.model import CommitmentExtractor, CommitmentType
from commitment_extractor.scenarios import all_scenarios


def _type_entropy(type_counts: dict[CommitmentType, int]) -> float:
    """Compute Shannon entropy of a type distribution.

    SIMULATION ONLY. Treats type counts as an unnormalised distribution
    and returns entropy in bits. Returns 0.0 for empty or degenerate distributions.
    """
    total = sum(type_counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in type_counts.values():
        if count > 0:
            probability = count / total
            entropy -= probability * math.log2(probability)
    return round(entropy, 6)


def run_experiment() -> dict[str, object]:
    """Run Experiment 4: full conversation analysis.

    SIMULATION ONLY. For each synthetic scenario, computes:
    - commitment_density: commitments per message
    - type_entropy: Shannon entropy of extracted type distribution (bits)
    - reclassification_rate: fraction of commitments reclassified by CommitmentClassifier

    All data is SYNTHETIC.

    Returns:
        Dictionary with per-scenario metrics and aggregate analysis.
    """
    print("=" * 62)
    print("Exp 4 — Full Conversation Analysis")
    print("SIMULATION ONLY — synthetic data, rule-based extraction")
    print("=" * 62)

    extractor = CommitmentExtractor(model="rule-based")
    classifier = CommitmentClassifier()
    scenarios = all_scenarios()

    scenario_names: list[str] = []
    densities: list[float] = []
    entropies: list[float] = []
    reclassification_rates: list[float] = []

    per_scenario: list[dict[str, object]] = []

    for scenario in scenarios:
        message_count = len(scenario.messages)
        extracted = extractor.extract_from_conversation(scenario.messages)
        commitment_count = len(extracted)

        density = round(commitment_count / max(message_count, 1), 6)

        type_counts: dict[CommitmentType, int] = {t: 0 for t in CommitmentType}
        for commitment in extracted:
            type_counts[commitment.commitment_type] += 1

        entropy = _type_entropy(type_counts)

        reclassification_rate = 0.0
        if extracted:
            cls_results = classifier.classify_batch(extracted)
            reclassified = sum(1 for r in cls_results if r.reclassified)
            reclassification_rate = round(reclassified / len(cls_results), 6)

        print(f"\n  Scenario: {scenario.name!r}")
        print(
            f"    messages={message_count} | commitments={commitment_count} "
            f"| density={density:.4f} | entropy={entropy:.4f} "
            f"| reclassify_rate={reclassification_rate:.4f}"
        )

        scenario_names.append(scenario.name)
        densities.append(density)
        entropies.append(entropy)
        reclassification_rates.append(reclassification_rate)

        per_scenario.append({
            "name": scenario.name,
            "message_count": message_count,
            "commitment_count": commitment_count,
            "density": density,
            "type_entropy_bits": entropy,
            "reclassification_rate": reclassification_rate,
            "type_counts": {t.value: count for t, count in type_counts.items()},
        })

    # Aggregate statistics
    non_zero_densities = [d for d in densities if d > 0]
    mean_density = round(sum(densities) / max(len(densities), 1), 6)
    mean_entropy = round(sum(entropies) / max(len(entropies), 1), 6)

    print(f"\n  Aggregate: mean_density={mean_density:.4f} | mean_entropy={mean_entropy:.4f} bits")

    return {
        "experiment": "exp4_conversation_analysis",
        "description": (
            "Full conversation analysis: density, type entropy, reclassification. "
            "SIMULATION ONLY — rule-based, synthetic data."
        ),
        "x": scenario_names,
        "x_label": "scenario",
        "commitment_densities": densities,
        "type_entropies_bits": entropies,
        "reclassification_rates": reclassification_rates,
        "aggregate": {
            "mean_density": mean_density,
            "mean_entropy_bits": mean_entropy,
            "scenarios_with_commitments": len(non_zero_densities),
        },
        "per_scenario": per_scenario,
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
    print("SIMULATION ONLY — do not use for production analysis.")


if __name__ == "__main__":
    main()
