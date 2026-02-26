# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
tracker.py — CommitmentTracker: register, check_status, mark_fulfilled, mark_expired.

SIMULATION ONLY. Tracks the lifecycle of extracted commitments through their
ACTIVE -> FULFILLED/EXPIRED/CANCELLED states. No production commitment management
infrastructure, no persistent storage, and no real agent data. All data SYNTHETIC.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from commitment_extractor.model import (
    Commitment,
    CommitmentExtractor,
    FulfillmentStatus,
    Message,
)


@dataclass(frozen=True)
class TrackingSnapshot:
    """Snapshot of tracker state at a given point in time.

    SIMULATION ONLY. Summarises how many commitments are in each lifecycle
    state and which are overdue based on a TTL threshold.

    Attributes:
        total: Total number of registered commitments.
        active: Count of ACTIVE commitments.
        fulfilled: Count of FULFILLED commitments.
        expired: Count of EXPIRED commitments.
        cancelled: Count of CANCELLED commitments.
        fulfillment_rate: Fraction of non-active commitments that are FULFILLED.
    """

    total: int
    active: int
    fulfilled: int
    expired: int
    cancelled: int
    fulfillment_rate: float


class CommitmentTracker:
    """Track the lifecycle of extracted commitments through fulfillment states.

    SIMULATION ONLY — does not implement production commitment management or
    Paper 21's full lifecycle tracking system. State transitions are manual
    (mark_fulfilled, mark_expired) or driven by check_status against a list
    of follow-up messages. No persistent storage. All data is SYNTHETIC.

    Example::

        tracker = CommitmentTracker()
        tracker.register(commitment)
        tracker.check_status(commitment_id, follow_up_messages)
        snapshot = tracker.snapshot()
        print(snapshot.fulfillment_rate)
    """

    def __init__(self) -> None:
        """Initialise an empty CommitmentTracker. SIMULATION ONLY."""
        self._commitments: dict[str, Commitment] = {}
        self._extractor: CommitmentExtractor = CommitmentExtractor(model="rule-based")

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, commitment: Commitment) -> None:
        """Register a commitment for lifecycle tracking.

        SIMULATION ONLY. Stores the commitment by its commitment_id.
        Overwrites any previously registered commitment with the same ID.

        Args:
            commitment: The Commitment to track.
        """
        self._commitments[commitment.commitment_id] = commitment

    def register_batch(self, commitments: list[Commitment]) -> None:
        """Register a batch of commitments.

        SIMULATION ONLY. Calls register() for each commitment in the list.

        Args:
            commitments: List of Commitment objects to register.
        """
        for commitment in commitments:
            self.register(commitment)

    # ------------------------------------------------------------------
    # Status queries
    # ------------------------------------------------------------------

    def get(self, commitment_id: str) -> Optional[Commitment]:
        """Retrieve a tracked commitment by its ID.

        SIMULATION ONLY.

        Args:
            commitment_id: The commitment identifier to look up.

        Returns:
            The Commitment object, or None if not registered.
        """
        return self._commitments.get(commitment_id)

    def all_commitments(self) -> list[Commitment]:
        """Return all registered commitments.

        SIMULATION ONLY.

        Returns:
            List of all Commitment objects currently tracked.
        """
        return list(self._commitments.values())

    def by_status(self, status: FulfillmentStatus) -> list[Commitment]:
        """Return all commitments with the given status.

        SIMULATION ONLY.

        Args:
            status: The FulfillmentStatus to filter on.

        Returns:
            List of Commitment objects in the specified state.
        """
        return [c for c in self._commitments.values() if c.status == status]

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    def check_status(
        self,
        commitment_id: str,
        follow_up_messages: list[Message],
    ) -> FulfillmentStatus:
        """Check and update the status of a commitment against follow-up messages.

        SIMULATION ONLY. Delegates to CommitmentExtractor.check_fulfillment to
        scan follow-up messages from the commitment's sender for fulfillment
        evidence. Updates the stored commitment status in place. All data SYNTHETIC.

        Args:
            commitment_id: Identifier of the commitment to check.
            follow_up_messages: Messages to scan for fulfillment evidence.

        Returns:
            The updated FulfillmentStatus. Returns ACTIVE if the commitment is
            not found in the registry.
        """
        commitment = self._commitments.get(commitment_id)
        if commitment is None:
            return FulfillmentStatus.ACTIVE

        if commitment.status != FulfillmentStatus.ACTIVE:
            return commitment.status

        new_status = self._extractor.check_fulfillment(commitment, follow_up_messages)
        if new_status != commitment.status:
            # Commitments are dataclass instances (not frozen); update status
            commitment.status = new_status
        return new_status

    def mark_fulfilled(self, commitment_id: str) -> bool:
        """Manually mark a commitment as fulfilled.

        SIMULATION ONLY. Directly sets status to FULFILLED regardless of
        current state. This simulates a manual override, as per the FIRE LINE
        constraint that trust/fulfillment changes are manual only in simulation.

        Args:
            commitment_id: Identifier of the commitment to mark fulfilled.

        Returns:
            True if the commitment was found and updated; False otherwise.
        """
        commitment = self._commitments.get(commitment_id)
        if commitment is None:
            return False
        commitment.status = FulfillmentStatus.FULFILLED
        return True

    def mark_expired(self, commitment_id: str) -> bool:
        """Manually mark a commitment as expired.

        SIMULATION ONLY. Directly sets status to EXPIRED. Models the case
        where a TTL elapses without fulfillment evidence being found.

        Args:
            commitment_id: Identifier of the commitment to mark expired.

        Returns:
            True if the commitment was found and updated; False otherwise.
        """
        commitment = self._commitments.get(commitment_id)
        if commitment is None:
            return False
        commitment.status = FulfillmentStatus.EXPIRED
        return True

    def mark_cancelled(self, commitment_id: str) -> bool:
        """Manually mark a commitment as cancelled.

        SIMULATION ONLY. Directly sets status to CANCELLED.

        Args:
            commitment_id: Identifier of the commitment to mark cancelled.

        Returns:
            True if the commitment was found and updated; False otherwise.
        """
        commitment = self._commitments.get(commitment_id)
        if commitment is None:
            return False
        commitment.status = FulfillmentStatus.CANCELLED
        return True

    def expire_overdue(self, current_timestamp: int, ttl: int) -> list[str]:
        """Expire all active commitments whose age exceeds the given TTL.

        SIMULATION ONLY. Scans all ACTIVE commitments and marks expired any
        whose (current_timestamp - timestamp) > ttl. Returns the list of
        expired commitment IDs. All data is SYNTHETIC.

        Args:
            current_timestamp: The current logical timestamp in the simulation.
            ttl: Maximum number of time units before an active commitment expires.

        Returns:
            List of commitment_ids that were transitioned to EXPIRED.
        """
        expired_ids: list[str] = []
        for commitment in self._commitments.values():
            if commitment.status == FulfillmentStatus.ACTIVE:
                age = current_timestamp - commitment.timestamp
                if age > ttl:
                    commitment.status = FulfillmentStatus.EXPIRED
                    expired_ids.append(commitment.commitment_id)
        return expired_ids

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def snapshot(self) -> TrackingSnapshot:
        """Return a summary snapshot of current tracker state.

        SIMULATION ONLY. Counts commitments in each status state and computes
        the fulfillment rate among resolved (non-active) commitments.

        Returns:
            TrackingSnapshot with counts and fulfillment_rate.
        """
        counts: dict[FulfillmentStatus, int] = {s: 0 for s in FulfillmentStatus}
        for commitment in self._commitments.values():
            counts[commitment.status] += 1

        resolved = counts[FulfillmentStatus.FULFILLED] + counts[FulfillmentStatus.EXPIRED]
        fulfillment_rate = (
            counts[FulfillmentStatus.FULFILLED] / resolved if resolved > 0 else 0.0
        )

        return TrackingSnapshot(
            total=len(self._commitments),
            active=counts[FulfillmentStatus.ACTIVE],
            fulfilled=counts[FulfillmentStatus.FULFILLED],
            expired=counts[FulfillmentStatus.EXPIRED],
            cancelled=counts[FulfillmentStatus.CANCELLED],
            fulfillment_rate=round(fulfillment_rate, 6),
        )

    def reset(self) -> None:
        """Clear all tracked commitments.

        SIMULATION ONLY. Returns the tracker to an empty state.
        """
        self._commitments = {}
