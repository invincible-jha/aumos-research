# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
properties.py — Economic safety property definitions.

SIMULATION ONLY. This module defines simplified arithmetic safety properties
for agent spending envelope systems. These are NOT the 25 formal theorems from
Paper 22. They are simplified corollaries used to verify simulation outputs
and reproduce paper figures. No formal proof machinery is implemented here.
"""

from __future__ import annotations

from economic_safety.model import Commitment, Envelope, Transaction


class EconomicProperties:
    """Arithmetic safety predicates for spending envelope verification.

    SIMULATION ONLY. Each static method is an arithmetic check over
    synthetic simulation data — not a formal theorem proof. Paper 22's
    25 theorems are proprietary and are NOT implemented here.

    All methods are pure functions that accept snapshot data and return
    a boolean indicating whether the property holds for that snapshot.

    Example::

        from economic_safety.model import Envelope, Transaction
        from economic_safety.properties import EconomicProperties

        envelope = Envelope(category="compute", limit=1000.0, spent=850.0)
        txs = [Transaction("t1", "compute", 850.0, "agent-1", 10)]
        print(EconomicProperties.no_overspend(envelope, txs))  # True
    """

    @staticmethod
    def no_overspend(
        envelope: Envelope, transactions: list[Transaction]
    ) -> bool:
        """Verify that cumulative spending never exceeds the envelope limit.

        SIMULATION ONLY. Property P1 (simplified): for all prefixes of the
        transaction sequence, the running sum of amounts for this category
        does not exceed envelope.limit.

        Args:
            envelope: The envelope snapshot to check against.
            transactions: All transactions charged to envelope.category.

        Returns:
            True when cumulative spend at every transaction prefix is within
            the envelope limit. False as soon as any prefix violates it.
        """
        relevant = [t for t in transactions if t.category == envelope.category]
        cumulative = 0.0
        for tx in relevant:
            cumulative += tx.amount
            if cumulative > envelope.limit + 1e-9:
                return False
        return True

    @staticmethod
    def commitment_bounded(
        envelope: Envelope, commitments: list[Commitment]
    ) -> bool:
        """Verify that committed + spent never exceeds the envelope limit.

        SIMULATION ONLY. Property P2 (simplified): the sum of all active
        commitment amounts plus envelope.spent does not exceed envelope.limit.

        Args:
            envelope: The envelope snapshot carrying the current spent value.
            commitments: All active commitments against envelope.category.

        Returns:
            True when spent + total_committed <= limit. False otherwise.
        """
        relevant = [c for c in commitments if c.category == envelope.category]
        total_committed = sum(c.amount for c in relevant)
        return (envelope.spent + total_committed) <= envelope.limit + 1e-9

    @staticmethod
    def non_negative_balance(envelope: Envelope) -> bool:
        """Verify that the remaining balance of the envelope is non-negative.

        SIMULATION ONLY. Property P3 (simplified): envelope.limit - envelope.spent
        - envelope.committed >= 0.

        Args:
            envelope: The envelope snapshot to check.

        Returns:
            True when the available balance is >= 0. False otherwise.
        """
        return envelope.available >= -1e-9

    @staticmethod
    def no_overspend_prefix(
        envelope: Envelope, transactions: list[Transaction]
    ) -> tuple[bool, int]:
        """Return the index of the first violating transaction, if any.

        SIMULATION ONLY. Variant of no_overspend that identifies the specific
        transaction at which the property first fails, useful for counterexample
        extraction.

        Args:
            envelope: The envelope snapshot to check against.
            transactions: All transactions charged to envelope.category.

        Returns:
            A tuple (holds, violation_index) where holds is True when no
            violation is found (violation_index will be -1), and False with
            the zero-based index of the first violating transaction otherwise.
        """
        relevant = [t for t in transactions if t.category == envelope.category]
        cumulative = 0.0
        for index, tx in enumerate(relevant):
            cumulative += tx.amount
            if cumulative > envelope.limit + 1e-9:
                return False, index
        return True, -1

    @staticmethod
    def period_budget_reset(
        balance_at_period_end: float,
        balance_at_period_start: float,
        envelope_limit: float,
    ) -> bool:
        """Verify that a period reset restores the balance to the full limit.

        SIMULATION ONLY. Property P4 (simplified): after a period boundary
        reset, the available balance equals envelope.limit.

        Args:
            balance_at_period_end: Available balance just before reset.
            balance_at_period_start: Available balance just after reset.
            envelope_limit: The envelope's full limit.

        Returns:
            True when balance_at_period_start is approximately equal to
            envelope_limit, indicating a full reset occurred.
        """
        return abs(balance_at_period_start - envelope_limit) < 1e-9
