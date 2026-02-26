# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
evaluation.py — Precision/recall evaluation of CommitmentExtractor on synthetic data.

SIMULATION ONLY. Measures extraction quality (precision, recall, F1) against
synthetic conversation datasets where ground-truth commitment spans are known.
All datasets are SYNTHETIC. No real agent communication data is used.
"""

from __future__ import annotations

from dataclasses import dataclass

from commitment_extractor.model import Commitment, CommitmentExtractor, CommitmentType
from commitment_extractor.scenarios import LabeledConversation


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExtractionMetrics:
    """Precision, recall, and F1 for a single extraction evaluation run.

    SIMULATION ONLY. Computed by comparing extracted commitment count against
    the known ground-truth count in a LabeledConversation.

    Attributes:
        scenario_name: Name of the synthetic scenario evaluated.
        true_positives: Extracted commitments matching a ground-truth entry.
        false_positives: Extracted commitments with no ground-truth match.
        false_negatives: Ground-truth commitments not extracted.
        precision: TP / (TP + FP). 0.0 when no extractions were made.
        recall: TP / (TP + FN). 0.0 when no ground-truth commitments exist.
        f1_score: Harmonic mean of precision and recall.
    """

    scenario_name: str
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float


@dataclass(frozen=True)
class TypeBreakdown:
    """Per-type precision and recall across a scenario set.

    SIMULATION ONLY.

    Attributes:
        commitment_type: The CommitmentType this breakdown covers.
        true_positives: Correctly extracted commitments of this type.
        false_positives: Over-extractions of this type.
        false_negatives: Missed ground-truth commitments of this type.
        precision: TP / (TP + FP).
        recall: TP / (TP + FN).
    """

    commitment_type: CommitmentType
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float


# ---------------------------------------------------------------------------
# Matching logic — SIMULATION ONLY
# ---------------------------------------------------------------------------


def _match_extracted_to_ground_truth(
    extracted: list[Commitment],
    ground_truth_count: int,
) -> tuple[int, int, int]:
    """Match extracted commitments to ground-truth count (count-based, not span-based).

    SIMULATION ONLY. Uses a simplified count-based matching rather than
    exact span overlap. True positives = min(extracted count, ground_truth count).
    This approximation is intentional for the simulation — production evaluation
    uses span-level matching, which is not implemented here.

    Args:
        extracted: Commitments returned by CommitmentExtractor.
        ground_truth_count: Number of ground-truth commitments in the scenario.

    Returns:
        (true_positives, false_positives, false_negatives) integer tuple.
    """
    extracted_count = len(extracted)
    true_positives = min(extracted_count, ground_truth_count)
    false_positives = max(0, extracted_count - ground_truth_count)
    false_negatives = max(0, ground_truth_count - extracted_count)
    return true_positives, false_positives, false_negatives


def _compute_precision_recall(
    true_positives: int,
    false_positives: int,
    false_negatives: int,
) -> tuple[float, float, float]:
    """Compute precision, recall, and F1 from TP/FP/FN counts.

    SIMULATION ONLY.

    Args:
        true_positives: TP count.
        false_positives: FP count.
        false_negatives: FN count.

    Returns:
        (precision, recall, f1_score) float tuple.
    """
    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0.0
    )
    f1_score = (
        2.0 * precision * recall / (precision + recall)
        if (precision + recall) > 0.0
        else 0.0
    )
    return round(precision, 6), round(recall, 6), round(f1_score, 6)


# ---------------------------------------------------------------------------
# Evaluation functions
# ---------------------------------------------------------------------------


def evaluate_scenario(
    scenario: LabeledConversation,
    extractor: CommitmentExtractor,
) -> ExtractionMetrics:
    """Evaluate extraction precision and recall on a single labeled scenario.

    SIMULATION ONLY. Extracts commitments from all messages in the scenario,
    then compares the extracted count to the ground-truth commitment count
    using count-based matching. All data is SYNTHETIC.

    Args:
        scenario: A LabeledConversation with messages and ground_truth_count.
        extractor: The CommitmentExtractor instance to evaluate.

    Returns:
        ExtractionMetrics with precision, recall, and F1 for this scenario.
    """
    extracted = extractor.extract_from_conversation(scenario.messages)
    tp, fp, fn = _match_extracted_to_ground_truth(extracted, scenario.ground_truth_count)
    precision, recall, f1 = _compute_precision_recall(tp, fp, fn)

    return ExtractionMetrics(
        scenario_name=scenario.name,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        precision=precision,
        recall=recall,
        f1_score=f1,
    )


def evaluate_dataset(
    scenarios: list[LabeledConversation],
    extractor: CommitmentExtractor,
) -> list[ExtractionMetrics]:
    """Evaluate extraction quality across a dataset of labeled scenarios.

    SIMULATION ONLY. Applies evaluate_scenario to each scenario and returns
    per-scenario metrics. All data is SYNTHETIC.

    Args:
        scenarios: List of LabeledConversation synthetic scenarios.
        extractor: The CommitmentExtractor instance to evaluate.

    Returns:
        List of ExtractionMetrics, one per scenario.
    """
    return [evaluate_scenario(scenario, extractor) for scenario in scenarios]


def aggregate_metrics(results: list[ExtractionMetrics]) -> ExtractionMetrics:
    """Aggregate per-scenario metrics into a macro-average result.

    SIMULATION ONLY. Computes macro-averaged precision, recall, and F1
    across all scenario results. All data is SYNTHETIC.

    Args:
        results: List of per-scenario ExtractionMetrics.

    Returns:
        A single ExtractionMetrics representing the macro average.

    Raises:
        ValueError: If results is empty.
    """
    if not results:
        raise ValueError("Cannot aggregate empty results list.")

    total_tp = sum(r.true_positives for r in results)
    total_fp = sum(r.false_positives for r in results)
    total_fn = sum(r.false_negatives for r in results)
    precision, recall, f1 = _compute_precision_recall(total_tp, total_fp, total_fn)

    return ExtractionMetrics(
        scenario_name="aggregate",
        true_positives=total_tp,
        false_positives=total_fp,
        false_negatives=total_fn,
        precision=precision,
        recall=recall,
        f1_score=f1,
    )


def per_type_breakdown(
    scenarios: list[LabeledConversation],
    extractor: CommitmentExtractor,
) -> list[TypeBreakdown]:
    """Compute per-type precision and recall across the scenario dataset.

    SIMULATION ONLY. Extracts commitments for each scenario, groups them by
    CommitmentType, and compares to per-type ground-truth counts where provided.
    Uses count-based matching. All data is SYNTHETIC.

    Args:
        scenarios: List of LabeledConversation synthetic scenarios.
        extractor: The CommitmentExtractor to evaluate.

    Returns:
        List of TypeBreakdown, one per CommitmentType.
    """
    tp_by_type: dict[CommitmentType, int] = {t: 0 for t in CommitmentType}
    fp_by_type: dict[CommitmentType, int] = {t: 0 for t in CommitmentType}
    fn_by_type: dict[CommitmentType, int] = {t: 0 for t in CommitmentType}

    for scenario in scenarios:
        extracted = extractor.extract_from_conversation(scenario.messages)
        extracted_by_type: dict[CommitmentType, int] = {t: 0 for t in CommitmentType}
        for commitment in extracted:
            extracted_by_type[commitment.commitment_type] += 1

        gt_by_type = scenario.ground_truth_by_type

        for commitment_type in CommitmentType:
            extracted_count = extracted_by_type[commitment_type]
            gt_count = gt_by_type.get(commitment_type, 0)
            tp = min(extracted_count, gt_count)
            fp = max(0, extracted_count - gt_count)
            fn = max(0, gt_count - extracted_count)
            tp_by_type[commitment_type] += tp
            fp_by_type[commitment_type] += fp
            fn_by_type[commitment_type] += fn

    breakdowns: list[TypeBreakdown] = []
    for commitment_type in CommitmentType:
        tp = tp_by_type[commitment_type]
        fp = fp_by_type[commitment_type]
        fn = fn_by_type[commitment_type]
        precision, recall, _f1 = _compute_precision_recall(tp, fp, fn)
        breakdowns.append(TypeBreakdown(
            commitment_type=commitment_type,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            precision=precision,
            recall=recall,
        ))

    return breakdowns
