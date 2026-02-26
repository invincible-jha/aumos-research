# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
commitment_extractor — Research companion for Paper 21.

SIMULATION ONLY. This package implements a simplified rule-based commitment
extraction and tracking system for synthetic agent message streams. It does
NOT contain Paper 21's full semantic extraction system, LLM-powered classifiers,
or production commitment management infrastructure.

All extraction uses REGEX PATTERN MATCHING ONLY. All conversation data is SYNTHETIC.
All results are generated from seed=42 deterministic simulation.
"""

from commitment_extractor.model import (
    Commitment,
    CommitmentExtractor,
    CommitmentType,
    FulfillmentStatus,
    Message,
)
from commitment_extractor.classifier import CommitmentClassifier
from commitment_extractor.tracker import CommitmentTracker

__version__ = "0.1.0"
__all__ = [
    # Model
    "CommitmentExtractor",
    "Commitment",
    "CommitmentType",
    "FulfillmentStatus",
    "Message",
    # Classifier
    "CommitmentClassifier",
    # Tracker
    "CommitmentTracker",
]
