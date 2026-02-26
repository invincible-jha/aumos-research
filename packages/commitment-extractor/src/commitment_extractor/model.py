# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
model.py — CommitmentExtractor and core dataclasses for commitment extraction simulation.

SIMULATION ONLY. This module implements a simplified rule-based commitment
extraction system for agent message streams. It does NOT contain production
LLM-powered extraction algorithms, Paper 21's full semantic extraction system,
adaptive classifiers, or vector-based similarity matching.

All extraction uses REGEX PATTERN MATCHING ONLY. All conversation data is SYNTHETIC.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class CommitmentType(str, Enum):
    """Classification of extracted commitment by semantic type.

    SIMULATION ONLY. These categories are assigned by rule-based regex — not
    by LLM inference or semantic understanding.
    """

    PROMISE = "promise"          # "I will...", "I'll...", "We will..."
    OBLIGATION = "obligation"    # "I must...", "I need to...", "required to..."
    DEADLINE = "deadline"        # "by [date/time]", "before [event]", "due [time]"
    CONDITIONAL = "conditional"  # "If ..., then I will...", "once ... I will..."
    OFFER = "offer"              # "I can...", "I am able to...", "happy to..."


class FulfillmentStatus(str, Enum):
    """Lifecycle state of a tracked commitment.

    SIMULATION ONLY.
    """

    ACTIVE = "active"        # Extracted, not yet fulfilled or expired
    FULFILLED = "fulfilled"  # Fulfillment evidence found in follow-up messages
    EXPIRED = "expired"      # TTL elapsed without fulfillment evidence
    CANCELLED = "cancelled"  # Explicit cancellation detected


# ---------------------------------------------------------------------------
# Core dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Message:
    """A single synthetic agent communication message.

    SIMULATION ONLY. Represents a text message in a synthetic conversation.
    No real agent communications are stored here.

    Attributes:
        message_id: Unique message identifier.
        sender: Identifier of the sending agent.
        recipient: Identifier of the receiving agent.
        text: Raw message text to be processed.
        timestamp: Ordinal position in the conversation sequence.
    """

    message_id: str
    sender: str
    recipient: str
    text: str
    timestamp: int = 0


@dataclass
class Commitment:
    """A single extracted commitment from an agent message.

    SIMULATION ONLY. Represents a rule-based extraction result — not a
    semantically verified commitment record.

    Attributes:
        commitment_id: Unique commitment identifier.
        commitment_type: Classified commitment type (regex-based).
        text_span: The substring of the source message that triggered extraction.
        source_message_id: Identifier of the message this was extracted from.
        sender: Agent making the commitment.
        recipient: Agent to whom the commitment is directed.
        timestamp: Ordinal timestamp of the source message.
        deadline_text: Extracted deadline phrase, if any.
        condition_text: Extracted condition clause, if any.
        status: Current fulfillment lifecycle status.
    """

    commitment_id: str
    commitment_type: CommitmentType
    text_span: str
    source_message_id: str
    sender: str
    recipient: str
    timestamp: int = 0
    deadline_text: Optional[str] = None
    condition_text: Optional[str] = None
    status: FulfillmentStatus = FulfillmentStatus.ACTIVE


# ---------------------------------------------------------------------------
# CommitmentExtractor
# ---------------------------------------------------------------------------

# Compiled regex patterns for commitment extraction.
# SIMULATION ONLY — simplified patterns, not production NLU.
_PROMISE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bI(?:'ll| will)\b[^.!?]{3,80}", re.IGNORECASE),
    re.compile(r"\bWe(?:'ll| will)\b[^.!?]{3,80}", re.IGNORECASE),
    re.compile(r"\bI(?:'m| am) going to\b[^.!?]{3,60}", re.IGNORECASE),
    re.compile(r"\bI promise\b[^.!?]{3,80}", re.IGNORECASE),
]

_OBLIGATION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bI (?:must|need to|have to|ought to|am required to)\b[^.!?]{3,80}", re.IGNORECASE),
    re.compile(r"\bI(?:'m| am) responsible for\b[^.!?]{3,60}", re.IGNORECASE),
    re.compile(r"\bI(?:'m| am) obligated to\b[^.!?]{3,60}", re.IGNORECASE),
]

_DEADLINE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bby\s+(?:end of\s+)?(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|today|tomorrow|[A-Za-z]+ \d+)", re.IGNORECASE),
    re.compile(r"\bbefore\s+[A-Za-z0-9 ]+\b", re.IGNORECASE),
    re.compile(r"\bdue\s+(?:by\s+)?(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|today|tomorrow|\d{1,2}/\d{1,2})", re.IGNORECASE),
    re.compile(r"\bno later than\s+[A-Za-z0-9 ]+\b", re.IGNORECASE),
    re.compile(r"\bwithin\s+\d+\s+(?:hours?|days?|weeks?)\b", re.IGNORECASE),
]

_CONDITIONAL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bIf\b[^,]{3,60},\s*(?:I(?:'ll| will)|I(?:'m| am) going to)[^.!?]{3,60}", re.IGNORECASE),
    re.compile(r"\bOnce\b[^,]{3,60},?\s*I(?:'ll| will)[^.!?]{3,60}", re.IGNORECASE),
    re.compile(r"\bProvided that\b[^,]{3,60},?\s*I(?:'ll| will)[^.!?]{3,60}", re.IGNORECASE),
    re.compile(r"\bAssuming\b[^,]{3,60},?\s*I(?:'ll| will)[^.!?]{3,60}", re.IGNORECASE),
]

_OFFER_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bI can\b[^.!?]{3,80}", re.IGNORECASE),
    re.compile(r"\bI(?:'m| am) able to\b[^.!?]{3,60}", re.IGNORECASE),
    re.compile(r"\bI(?:'m| am) happy to\b[^.!?]{3,60}", re.IGNORECASE),
    re.compile(r"\bI(?:'m| am) available to\b[^.!?]{3,60}", re.IGNORECASE),
]

_PATTERN_MAP: list[tuple[CommitmentType, list[re.Pattern[str]]]] = [
    (CommitmentType.CONDITIONAL, _CONDITIONAL_PATTERNS),  # Check conditionals first
    (CommitmentType.PROMISE, _PROMISE_PATTERNS),
    (CommitmentType.OBLIGATION, _OBLIGATION_PATTERNS),
    (CommitmentType.DEADLINE, _DEADLINE_PATTERNS),
    (CommitmentType.OFFER, _OFFER_PATTERNS),
]

# Patterns for extracting deadline and condition sub-spans
_DEADLINE_SUBPATTERN = re.compile(
    r"\b(?:by|before|due|no later than|within)\s+[A-Za-z0-9/ ]+", re.IGNORECASE
)
_CONDITION_SUBPATTERN = re.compile(
    r"\b(?:if|once|provided that|assuming)\s+[^,]{3,60}", re.IGNORECASE
)

# Fulfillment evidence patterns for follow-up checking
_FULFILLMENT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(?:done|completed|finished|delivered|sent|submitted|uploaded)\b", re.IGNORECASE),
    re.compile(r"\bI(?:'ve| have)\b[^.!?]{3,60}", re.IGNORECASE),
    re.compile(r"\bhere(?:'s| is)\b[^.!?]{3,60}", re.IGNORECASE),
    re.compile(r"\bplease find\b[^.!?]{3,60}", re.IGNORECASE),
]


class CommitmentExtractor:
    """Extract commitments from agent messages using rule-based pattern matching.

    SIMULATION ONLY — does not contain production LLM-powered extraction or
    Paper 21's semantic understanding system. All extraction uses regex patterns
    only. All conversation data processed here is SYNTHETIC.

    Example::

        extractor = CommitmentExtractor()
        message = "I will complete the report by Friday."
        commitments = extractor.extract(message, sender="agent-a", recipient="agent-b")
        print(commitments[0].commitment_type)  # CommitmentType.PROMISE
    """

    def __init__(self, model: str = "rule-based") -> None:
        """Initialise the extractor.

        SIMULATION ONLY.

        Args:
            model: Extraction model identifier. Only "rule-based" is supported.
                Future modes are NOT implemented to prevent confusion with
                production LLM-based extractors.

        Raises:
            ValueError: If model is not "rule-based".
        """
        if model != "rule-based":
            raise ValueError(
                f"Only 'rule-based' model is supported in this research simulation. "
                f"Got: '{model}'. This package does NOT implement LLM-based extraction."
            )
        self.model = model

    def extract(
        self,
        message_text: str,
        sender: str,
        recipient: str,
        message_id: Optional[str] = None,
        timestamp: int = 0,
    ) -> list[Commitment]:
        """Extract commitments from a single message using regex pattern matching.

        SIMULATION ONLY. Scans the message text against compiled regex patterns
        for each CommitmentType. Returns one Commitment per matched span. Does NOT
        use LLM inference, vector similarity, or semantic understanding. All
        matches are RULE-BASED and operate on SYNTHETIC data.

        Commitments are deduplicated by span start position — the first matching
        pattern type wins for each span position.

        Args:
            message_text: Raw text of the agent message.
            sender: Identifier of the sending agent.
            recipient: Identifier of the receiving agent.
            message_id: Optional explicit message identifier; auto-generated if None.
            timestamp: Ordinal position in the conversation sequence.

        Returns:
            List of extracted Commitment objects. Empty list if no patterns match.
        """
        resolved_message_id = message_id if message_id is not None else str(uuid.uuid4())
        commitments: list[Commitment] = []
        seen_spans: set[int] = set()

        for commitment_type, patterns in _PATTERN_MAP:
            for pattern in patterns:
                for match in pattern.finditer(message_text):
                    start = match.start()
                    if start in seen_spans:
                        continue
                    seen_spans.add(start)

                    span_text = match.group(0).strip()

                    # Extract deadline sub-phrase if present
                    deadline_match = _DEADLINE_SUBPATTERN.search(span_text)
                    deadline_text = deadline_match.group(0).strip() if deadline_match else None

                    # Extract condition sub-phrase if present
                    condition_match = _CONDITION_SUBPATTERN.search(span_text)
                    condition_text = condition_match.group(0).strip() if condition_match else None

                    commitment = Commitment(
                        commitment_id=str(uuid.uuid4()),
                        commitment_type=commitment_type,
                        text_span=span_text,
                        source_message_id=resolved_message_id,
                        sender=sender,
                        recipient=recipient,
                        timestamp=timestamp,
                        deadline_text=deadline_text,
                        condition_text=condition_text,
                        status=FulfillmentStatus.ACTIVE,
                    )
                    commitments.append(commitment)

        return commitments

    def check_fulfillment(
        self,
        commitment: Commitment,
        follow_up_messages: list[Message],
    ) -> FulfillmentStatus:
        """Check whether a commitment has been fulfilled based on follow-up messages.

        SIMULATION ONLY. Scans follow-up messages from the commitment's sender
        for fulfillment evidence keywords/phrases using simple regex matching.
        Does NOT use semantic understanding or LLM inference.

        Args:
            commitment: The commitment to check for fulfillment evidence.
            follow_up_messages: Messages received after the commitment was made.
                Only messages from commitment.sender are checked.

        Returns:
            FulfillmentStatus.FULFILLED if fulfillment evidence is found;
            FulfillmentStatus.ACTIVE otherwise (caller manages expiry logic).
        """
        relevant = [
            msg for msg in follow_up_messages
            if msg.sender == commitment.sender
            and msg.timestamp > commitment.timestamp
        ]

        for message in relevant:
            for pattern in _FULFILLMENT_PATTERNS:
                if pattern.search(message.text):
                    return FulfillmentStatus.FULFILLED

        return FulfillmentStatus.ACTIVE

    def extract_from_conversation(
        self,
        messages: list[Message],
    ) -> list[Commitment]:
        """Extract all commitments from an ordered sequence of messages.

        SIMULATION ONLY. Processes each message in turn and aggregates all
        extracted commitments. All data is SYNTHETIC.

        Args:
            messages: Ordered list of Message objects forming the conversation.

        Returns:
            Flat list of all extracted Commitment objects across all messages.
        """
        all_commitments: list[Commitment] = []
        for message in messages:
            extracted = self.extract(
                message_text=message.text,
                sender=message.sender,
                recipient=message.recipient,
                message_id=message.message_id,
                timestamp=message.timestamp,
            )
            all_commitments.extend(extracted)
        return all_commitments
