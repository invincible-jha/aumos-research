# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp2_classification_accuracy.py — Classification accuracy experiment.

SIMULATION ONLY. Evaluates precision, recall, and F1 of CommitmentExtractor
across the synthetic evaluation dataset, and measures per-type classification
accuracy using CommitmentClassifier re-classification. All data is SYNTHETIC.
Results reproduce Figure 2 of the commitment-extractor companion paper.

Run:
    python experiments/exp2_classification_accuracy.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from commitment_extractor.classifier import CommitmentClassifier
from commitment_extractor.evaluation import (
    aggregate_metrics,
    evaluate_dataset,
    per_type_breakdown,
)
from commitment_extractor.model import CommitmentExtractor
from commitment_extractor.scenarios import all_scenarios, evaluation_scenarios


def run_experiment() -> dict[str, object]:
    """Run Experiment 2: classification accuracy evaluation.

    SIMULATION ONLY. Evaluates precision, recall, and F1 for each synthetic
    scenario, and then per-type accuracy via CommitmentClassifier. All SYNTHETIC.

    Returns:
        Dictionary with per-scenario metrics, aggregate metrics, and type breakdowns.
    """
    print("=" * 62)
    print("Exp 2 — Commitment Classification Accuracy")
    print("SIMULATION ONLY — rule-based classification, synthetic data")
    print("=" * 62)

    extractor = CommitmentExtractor(model="rule-based")
    classifier = CommitmentClassifier()

    eval_set = evaluation_scenarios()
    full_set = all_scenarios()

    # Per-scenario precision/recall/F1
    print("\n  Per-scenario extraction metrics:")
    per_scenario_metrics = evaluate_dataset(eval_set, extractor)
    scenario_results: list[dict[str, object]] = []

    for metrics in per_scenario_metrics:
        print(
            f"    {metrics.scenario_name}: P={metrics.precision:.4f} "
            f"R={metrics.recall:.4f} F1={metrics.f1_score:.4f}"
        )
        scenario_results.append({
            "name": metrics.scenario_name,
            "precision": metrics.precision,
            "recall": metrics.recall,
            "f1_score": metrics.f1_score,
            "true_positives": metrics.true_positives,
            "false_positives": metrics.false_positives,
            "false_negatives": metrics.false_negatives,
        })

    # Aggregate metrics
    aggregate = aggregate_metrics(per_scenario_metrics)
    print(
        f"\n  Aggregate (eval set): P={aggregate.precision:.4f} "
        f"R={aggregate.recall:.4f} F1={aggregate.f1_score:.4f}"
    )

    # Per-type breakdown across full dataset
    print("\n  Per-type precision/recall (full dataset):")
    type_breakdowns = per_type_breakdown(full_set, extractor)
    type_results: list[dict[str, object]] = []

    for breakdown in type_breakdowns:
        print(
            f"    {breakdown.commitment_type.value}: "
            f"P={breakdown.precision:.4f} R={breakdown.recall:.4f} "
            f"TP={breakdown.true_positives} FP={breakdown.false_positives} "
            f"FN={breakdown.false_negatives}"
        )
        type_results.append({
            "type": breakdown.commitment_type.value,
            "precision": breakdown.precision,
            "recall": breakdown.recall,
            "true_positives": breakdown.true_positives,
            "false_positives": breakdown.false_positives,
            "false_negatives": breakdown.false_negatives,
        })

    # Classifier reclassification rate across all extracted commitments
    all_commitments = []
    for scenario in full_set:
        extracted = extractor.extract_from_conversation(scenario.messages)
        all_commitments.extend(extracted)

    if all_commitments:
        classification_results = classifier.classify_batch(all_commitments)
        reclassified_count = sum(1 for r in classification_results if r.reclassified)
        reclassification_rate = reclassified_count / len(classification_results)
        print(
            f"\n  Classifier reclassification rate: "
            f"{reclassified_count}/{len(classification_results)} "
            f"= {reclassification_rate:.4f}"
        )
    else:
        reclassification_rate = 0.0
        reclassified_count = 0

    return {
        "experiment": "exp2_classification_accuracy",
        "description": (
            "Commitment classification accuracy on synthetic evaluation dataset. "
            "SIMULATION ONLY — rule-based, seed=42."
        ),
        "x": [r["name"] for r in scenario_results],
        "x_label": "scenario",
        "y_label": "score",
        "per_scenario_metrics": scenario_results,
        "aggregate": {
            "precision": aggregate.precision,
            "recall": aggregate.recall,
            "f1_score": aggregate.f1_score,
        },
        "type_breakdown": type_results,
        "reclassification_rate": round(reclassification_rate, 6),
        "total_commitments_evaluated": len(all_commitments),
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
    print("SIMULATION ONLY — do not use for production classification.")


if __name__ == "__main__":
    main()
