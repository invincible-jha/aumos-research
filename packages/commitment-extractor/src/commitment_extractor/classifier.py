# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
classifier.py — CommitmentClassifier: rule-based commitment type classification.

SIMULATION ONLY. Classifies extracted commitments into semantic type categories
using compiled regex patterns. Does NOT use LLM inference, embedding similarity,
or any production NLU system. All classification is rule-based. All data SYNTHETIC.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from commitment_extractor.model import Commitment, CommitmentType


# ---------------------------------------------------------------------------
# Pattern sets per commitment type — SIMULATION ONLY
# ---------------------------------------------------------------------------

# Patterns check the commitment text_span for primary keywords that strongly
# indicate the type. Evaluated in priority order: CONDITIONAL first.
_CLASSIFIER_PATTERNS: list[tuple[CommitmentType, list[re.Pattern[str]]]] = [
    (
        CommitmentType.CONDITIONAL,
        [
            re.compile(r"\b(?:if|once|provided that|assuming|unless)\b", re.IGNORECASE),
        ],
    ),
    (
        CommitmentType.DEADLINE,
        [
            re.compile(
                r"\b(?:by\s+end|by\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|"
                r"Saturday|Sunday|today|tomorrow)|before\s+\w|due\s+(?:by|on)|"
                r"no later than|within\s+\d+\s+(?:hour|day|week))\b",
                re.IGNORECASE,
            ),
        ],
    ),
    (
        CommitmentType.OBLIGATION,
        [
            re.compile(
                r"\b(?:must|need to|have to|ought to|required to|"
                r"obligated to|responsible for)\b",
                re.IGNORECASE,
            ),
        ],
    ),
    (
        CommitmentType.OFFER,
        [
            re.compile(
                r"\b(?:I can|I(?:'m| am) able to|I(?:'m| am) happy to|"
                r"I(?:'m| am) available to)\b",
                re.IGNORECASE,
            ),
        ],
    ),
    (
        CommitmentType.PROMISE,
        [
            re.compile(
                r"\b(?:I(?:'ll| will)|we(?:'ll| will)|going to|I promise)\b",
                re.IGNORECASE,
            ),
        ],
    ),
]


@dataclass(frozen=True)
class ClassificationResult:
    """Result of classifying a single commitment.

    SIMULATION ONLY. Holds the inferred type and a confidence-like score
    based solely on the number of pattern matches (not a true probability).

    Attributes:
        commitment_id: Identifier of the classified commitment.
        inferred_type: Best-matching CommitmentType from rule evaluation.
        original_type: CommitmentType assigned during extraction.
        pattern_match_count: Number of pattern groups that matched.
        reclassified: True when inferred_type differs from original_type.
    """

    commitment_id: str
    inferred_type: CommitmentType
    original_type: CommitmentType
    pattern_match_count: int
    reclassified: bool


class CommitmentClassifier:
    """Rule-based commitment type classifier.

    SIMULATION ONLY — does not contain production LLM-powered classification or
    Paper 21's semantic type system. All classification uses compiled regex
    patterns evaluated on commitment text spans. All input data is SYNTHETIC.

    Example::

        classifier = CommitmentClassifier()
        result = classifier.classify(commitment)
        print(result.inferred_type)   # CommitmentType.PROMISE
    """

    def classify(self, commitment: Commitment) -> ClassificationResult:
        """Classify a single commitment by evaluating rule patterns against its text span.

        SIMULATION ONLY. Evaluates compiled regex patterns against the commitment's
        text_span in priority order: CONDITIONAL > DEADLINE > OBLIGATION > OFFER > PROMISE.
        The first type whose patterns produce any match wins.

        Args:
            commitment: The Commitment to classify. Uses commitment.text_span as input.

        Returns:
            ClassificationResult with the inferred type and reclassification flag.
        """
        span = commitment.text_span
        total_matches = 0
        inferred_type = commitment.commitment_type  # default: keep original

        for candidate_type, patterns in _CLASSIFIER_PATTERNS:
            match_count = sum(
                1
                for pattern in patterns
                if pattern.search(span)
            )
            if match_count > 0:
                total_matches += match_count
                inferred_type = candidate_type
                break  # First matching type wins (priority order)

        return ClassificationResult(
            commitment_id=commitment.commitment_id,
            inferred_type=inferred_type,
            original_type=commitment.commitment_type,
            pattern_match_count=total_matches,
            reclassified=inferred_type != commitment.commitment_type,
        )

    def classify_batch(
        self, commitments: list[Commitment]
    ) -> list[ClassificationResult]:
        """Classify a batch of commitments.

        SIMULATION ONLY. Applies classify() to each commitment independently.
        All data is SYNTHETIC.

        Args:
            commitments: List of Commitment objects to classify.

        Returns:
            List of ClassificationResult objects, one per input commitment.
        """
        return [self.classify(commitment) for commitment in commitments]

    def type_distribution(
        self, results: list[ClassificationResult]
    ) -> dict[CommitmentType, int]:
        """Count the frequency of each inferred commitment type in a result set.

        SIMULATION ONLY. Returns a dict mapping each CommitmentType to its
        count among the classification results.

        Args:
            results: List of ClassificationResult objects to aggregate.

        Returns:
            Dict mapping CommitmentType to integer count.
        """
        distribution: dict[CommitmentType, int] = {
            commitment_type: 0 for commitment_type in CommitmentType
        }
        for result in results:
            distribution[result.inferred_type] += 1
        return distribution
