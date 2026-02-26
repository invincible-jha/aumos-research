# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
scenarios.py — Synthetic conversation datasets with known commitments.

SIMULATION ONLY. All conversations, agents, and commitment spans in this module
are SYNTHETIC. No real agent communications are used. Scenarios are designed
to test specific commitment types and lifecycle states against known ground truths.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from commitment_extractor.model import CommitmentType, FulfillmentStatus, Message


# ---------------------------------------------------------------------------
# LabeledConversation dataclass
# ---------------------------------------------------------------------------


@dataclass
class LabeledConversation:
    """A synthetic conversation with known ground-truth commitment counts.

    SIMULATION ONLY. Contains a sequence of synthetic messages and the expected
    number and types of commitments for evaluation purposes.

    Attributes:
        name: Short identifier for the scenario.
        description: Human-readable description of what this scenario tests.
        messages: Ordered list of Message objects forming the conversation.
        ground_truth_count: Total number of commitments expected to be extracted.
        ground_truth_by_type: Per-type breakdown of expected commitment counts.
        fulfillment_sequence: Optional list of (message_index, fulfillment_status)
            describing which messages contain fulfillment evidence.
    """

    name: str
    description: str
    messages: list[Message]
    ground_truth_count: int
    ground_truth_by_type: dict[CommitmentType, int] = field(default_factory=dict)
    fulfillment_sequence: list[tuple[int, FulfillmentStatus]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helper to build Message objects
# ---------------------------------------------------------------------------


def _msg(
    sender: str,
    recipient: str,
    text: str,
    timestamp: int,
) -> Message:
    """Build a synthetic Message with an auto-generated ID. SIMULATION ONLY."""
    return Message(
        message_id=str(uuid.uuid4()),
        sender=sender,
        recipient=recipient,
        text=text,
        timestamp=timestamp,
    )


# ---------------------------------------------------------------------------
# Scenario definitions — SIMULATION ONLY, all data synthetic
# ---------------------------------------------------------------------------


def scenario_simple_promise() -> LabeledConversation:
    """Single promise commitment in a two-message exchange.

    SIMULATION ONLY. Agent-A makes one clear promise to Agent-B.
    Ground truth: 1 PROMISE commitment.
    """
    return LabeledConversation(
        name="simple_promise",
        description=(
            "Agent-A makes a single direct promise. "
            "Expected: 1 PROMISE. SIMULATION ONLY."
        ),
        messages=[
            _msg("agent-a", "agent-b", "I will submit the report by end of day.", 1),
            _msg("agent-b", "agent-a", "Thank you, noted.", 2),
        ],
        ground_truth_count=1,
        ground_truth_by_type={CommitmentType.PROMISE: 1},
    )


def scenario_obligation_chain() -> LabeledConversation:
    """Sequential obligation messages across a three-agent exchange.

    SIMULATION ONLY. Two agents each state an obligation. Ground truth: 2 OBLIGATION.
    """
    return LabeledConversation(
        name="obligation_chain",
        description=(
            "Two obligation statements from two agents. "
            "Expected: 2 OBLIGATION. SIMULATION ONLY."
        ),
        messages=[
            _msg("agent-a", "agent-b", "I must complete the data validation before handoff.", 1),
            _msg("agent-b", "agent-c", "I need to review agent-a's output prior to deployment.", 2),
            _msg("agent-c", "agent-a", "Understood. Proceed when ready.", 3),
        ],
        ground_truth_count=2,
        ground_truth_by_type={CommitmentType.OBLIGATION: 2},
    )


def scenario_deadline_commitment() -> LabeledConversation:
    """Deadline-phrased commitment with a fulfillment follow-up.

    SIMULATION ONLY. Agent-A commits to a deadline; Agent-A later confirms completion.
    Ground truth: 1 DEADLINE commitment, 1 fulfillment message.
    """
    return LabeledConversation(
        name="deadline_commitment",
        description=(
            "Deadline commitment followed by fulfillment confirmation. "
            "Expected: 1 DEADLINE. SIMULATION ONLY."
        ),
        messages=[
            _msg("agent-a", "agent-b", "I will have the analysis ready by Friday.", 1),
            _msg("agent-b", "agent-a", "Friday is fine.", 2),
            _msg("agent-a", "agent-b", "I've completed the analysis. Please find it attached.", 5),
        ],
        ground_truth_count=1,
        ground_truth_by_type={CommitmentType.PROMISE: 1},
        fulfillment_sequence=[(2, FulfillmentStatus.FULFILLED)],
    )


def scenario_conditional_commitment() -> LabeledConversation:
    """Conditional commitment requiring a precondition.

    SIMULATION ONLY. Agent-A makes a conditional promise dependent on Agent-B's action.
    Ground truth: 1 CONDITIONAL commitment.
    """
    return LabeledConversation(
        name="conditional_commitment",
        description=(
            "Conditional promise: 'If you approve, I will proceed.' "
            "Expected: 1 CONDITIONAL. SIMULATION ONLY."
        ),
        messages=[
            _msg(
                "agent-a",
                "agent-b",
                "If you approve the plan, I will begin execution immediately.",
                1,
            ),
            _msg("agent-b", "agent-a", "Approval is pending review.", 2),
        ],
        ground_truth_count=1,
        ground_truth_by_type={CommitmentType.CONDITIONAL: 1},
    )


def scenario_offer_acceptance() -> LabeledConversation:
    """Offer commitment from one agent to another.

    SIMULATION ONLY. Agent-A offers assistance; Agent-B accepts.
    Ground truth: 1 OFFER commitment.
    """
    return LabeledConversation(
        name="offer_acceptance",
        description=(
            "Agent-A offers to help. Expected: 1 OFFER. SIMULATION ONLY."
        ),
        messages=[
            _msg("agent-a", "agent-b", "I can assist with the integration testing if needed.", 1),
            _msg("agent-b", "agent-a", "That would be helpful, thanks.", 2),
        ],
        ground_truth_count=1,
        ground_truth_by_type={CommitmentType.OFFER: 1},
    )


def scenario_mixed_types() -> LabeledConversation:
    """Conversation with multiple commitment types across several messages.

    SIMULATION ONLY. Includes PROMISE, OBLIGATION, CONDITIONAL in one exchange.
    Ground truth: 3 commitments total.
    """
    return LabeledConversation(
        name="mixed_types",
        description=(
            "Conversation with PROMISE + OBLIGATION + CONDITIONAL. "
            "Expected: 3 commitments. SIMULATION ONLY."
        ),
        messages=[
            _msg("agent-a", "agent-b", "I will deliver the metrics dashboard by Monday.", 1),
            _msg("agent-b", "agent-a", "I must review it before we push to staging.", 2),
            _msg(
                "agent-c",
                "agent-b",
                "If agent-a delivers on time, I'll handle the deployment pipeline.",
                3,
            ),
        ],
        ground_truth_count=3,
        ground_truth_by_type={
            CommitmentType.PROMISE: 1,
            CommitmentType.OBLIGATION: 1,
            CommitmentType.CONDITIONAL: 1,
        },
    )


def scenario_fulfillment_tracking() -> LabeledConversation:
    """Two commitments, one fulfilled and one left active.

    SIMULATION ONLY. Tests that CommitmentTracker correctly identifies
    fulfilled vs. still-active commitments. All data SYNTHETIC.
    """
    return LabeledConversation(
        name="fulfillment_tracking",
        description=(
            "Two promises; one later fulfilled, one left active. "
            "Expected: 2 PROMISE. SIMULATION ONLY."
        ),
        messages=[
            _msg("agent-a", "agent-b", "I'll prepare the configuration file.", 1),
            _msg("agent-a", "agent-b", "I'll also write the test suite.", 2),
            _msg("agent-b", "agent-a", "Both sound good.", 3),
            _msg("agent-a", "agent-b", "Done — here is the configuration file.", 6),
        ],
        ground_truth_count=2,
        ground_truth_by_type={CommitmentType.PROMISE: 2},
        fulfillment_sequence=[(0, FulfillmentStatus.FULFILLED)],
    )


def scenario_expired_commitment() -> LabeledConversation:
    """A commitment that is never followed up on and should expire.

    SIMULATION ONLY. Tests TTL-based expiry in CommitmentTracker. All SYNTHETIC.
    """
    return LabeledConversation(
        name="expired_commitment",
        description=(
            "Promise made but never fulfilled within the TTL window. "
            "Expected: 1 PROMISE, status EXPIRED. SIMULATION ONLY."
        ),
        messages=[
            _msg("agent-a", "agent-b", "I will send the summary report by tomorrow.", 1),
            _msg("agent-b", "agent-a", "Looking forward to it.", 2),
            # No follow-up from agent-a — commitment should expire
        ],
        ground_truth_count=1,
        ground_truth_by_type={CommitmentType.PROMISE: 1},
    )


def scenario_no_commitments() -> LabeledConversation:
    """Conversation with no commitment-bearing messages.

    SIMULATION ONLY. Verifies the extractor produces no false positives on
    neutral factual messages. Ground truth: 0 commitments.
    """
    return LabeledConversation(
        name="no_commitments",
        description=(
            "Neutral factual exchange with no commitments. "
            "Expected: 0 commitments. SIMULATION ONLY."
        ),
        messages=[
            _msg("agent-a", "agent-b", "The server is running on port 8080.", 1),
            _msg("agent-b", "agent-a", "Status check passed at 14:32 UTC.", 2),
            _msg("agent-c", "agent-b", "All health checks are green.", 3),
        ],
        ground_truth_count=0,
        ground_truth_by_type={},
    )


# ---------------------------------------------------------------------------
# Dataset collections
# ---------------------------------------------------------------------------


def all_scenarios() -> list[LabeledConversation]:
    """Return the full synthetic evaluation dataset.

    SIMULATION ONLY. All scenarios are SYNTHETIC — no real agent data.

    Returns:
        List of all LabeledConversation scenario instances.
    """
    return [
        scenario_simple_promise(),
        scenario_obligation_chain(),
        scenario_deadline_commitment(),
        scenario_conditional_commitment(),
        scenario_offer_acceptance(),
        scenario_mixed_types(),
        scenario_fulfillment_tracking(),
        scenario_expired_commitment(),
        scenario_no_commitments(),
    ]


def training_scenarios() -> list[LabeledConversation]:
    """Return a subset of scenarios suitable for parameter exploration.

    SIMULATION ONLY. Returns scenarios with unambiguous single-type commitments.
    """
    return [
        scenario_simple_promise(),
        scenario_obligation_chain(),
        scenario_conditional_commitment(),
        scenario_offer_acceptance(),
        scenario_no_commitments(),
    ]


def evaluation_scenarios() -> list[LabeledConversation]:
    """Return scenarios designed for precision/recall evaluation.

    SIMULATION ONLY. Includes mixed-type and lifecycle tracking scenarios.
    """
    return [
        scenario_mixed_types(),
        scenario_fulfillment_tracking(),
        scenario_expired_commitment(),
        scenario_deadline_commitment(),
    ]
