# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""Retention policy types for governed-forgetting simulation.

SIMULATION ONLY — not production AMGP implementation.
All policies operate on synthetic MemoryRecord objects with no real content.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal

from governed_forgetting.types import MemoryRecord


class RetentionPolicy(ABC):
    """Abstract base class for memory retention policies.

    SIMULATION ONLY — not production AMGP implementation.
    Subclasses implement a single decision method that determines whether a
    synthetic MemoryRecord should be kept at a given simulation timestep.
    """

    @abstractmethod
    def should_retain(self, record: MemoryRecord, current_timestep: int) -> bool:
        """Return True if the record should remain in active memory.

        Args:
            record: The synthetic MemoryRecord under evaluation.
            current_timestep: The simulation clock tick (not wall-clock time).

        Returns:
            True to keep the record active, False to mark it forgotten.
        """
        ...

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class TimeBasedPolicy(RetentionPolicy):
    """Forget a memory after a fixed time-to-live window.

    SIMULATION ONLY — not production AMGP implementation.
    The age of a record is computed as ``current_timestep - record.created_at``.
    Once that age exceeds ``ttl``, the record is eligible for forgetting.

    Args:
        ttl: Number of simulation timesteps before a record is forgotten.
             Must be a positive integer.

    Raises:
        ValueError: If ``ttl`` is not a positive integer.

    Example::

        policy = TimeBasedPolicy(ttl=100)
        record = MemoryRecord(
            record_id="r1",
            content_hash="abc",
            created_at=0,
            category="conversation",
            relevance_score=0.9,
            consent_owner="user_1",
        )
        policy.should_retain(record, current_timestep=50)   # True
        policy.should_retain(record, current_timestep=100)  # False
    """

    def __init__(self, ttl: int) -> None:
        if ttl <= 0:
            raise ValueError(f"ttl must be a positive integer, got {ttl!r}")
        self.ttl = ttl

    def should_retain(self, record: MemoryRecord, current_timestep: int) -> bool:
        """Retain if the record is younger than ttl timesteps."""
        age = current_timestep - record.created_at
        return age < self.ttl

    def __repr__(self) -> str:
        return f"TimeBasedPolicy(ttl={self.ttl})"


class RelevanceDecayPolicy(RetentionPolicy):
    """Forget a memory when its decayed relevance score falls below a threshold.

    SIMULATION ONLY — not production AMGP implementation.
    Relevance decays exponentially from the record's initial ``relevance_score``
    using the formula::

        effective_score = relevance_score * exp(-decay_rate * age)

    When ``effective_score`` drops below ``threshold``, the record is forgotten.

    Args:
        decay_rate: Exponential decay constant (must be non-negative).
        threshold: Minimum effective relevance score to remain active (0–1).

    Raises:
        ValueError: If ``decay_rate`` is negative or ``threshold`` is outside [0, 1].

    Example::

        policy = RelevanceDecayPolicy(decay_rate=0.01, threshold=0.3)
        record = MemoryRecord(
            record_id="r1",
            content_hash="abc",
            created_at=0,
            category="fact",
            relevance_score=1.0,
            consent_owner="user_1",
        )
        policy.should_retain(record, current_timestep=10)   # True (score ~0.905)
        policy.should_retain(record, current_timestep=200)  # False (score ~0.135)
    """

    def __init__(self, decay_rate: float, threshold: float) -> None:
        if decay_rate < 0:
            raise ValueError(f"decay_rate must be non-negative, got {decay_rate!r}")
        if not (0.0 <= threshold <= 1.0):
            raise ValueError(f"threshold must be in [0, 1], got {threshold!r}")
        self.decay_rate = decay_rate
        self.threshold = threshold

    def effective_score(self, record: MemoryRecord, current_timestep: int) -> float:
        """Compute the decayed relevance score at the given timestep."""
        age = max(0, current_timestep - record.created_at)
        return record.relevance_score * math.exp(-self.decay_rate * age)

    def should_retain(self, record: MemoryRecord, current_timestep: int) -> bool:
        """Retain if the effective relevance score exceeds the threshold."""
        return self.effective_score(record, current_timestep) >= self.threshold

    def __repr__(self) -> str:
        return (
            f"RelevanceDecayPolicy("
            f"decay_rate={self.decay_rate}, threshold={self.threshold})"
        )


class ConsentBasedPolicy(RetentionPolicy):
    """Forget a memory when its owner revokes consent.

    SIMULATION ONLY — not production AMGP implementation.
    The policy checks a mutable consent store mapping ``consent_owner`` identifiers
    to booleans. When the value for an owner is ``False``, all records belonging
    to that owner are immediately eligible for forgetting.

    The consent store is mutable so that experiments can update it between
    simulation timesteps to model batch revocations.

    Args:
        consent_store: Mapping of owner identifier to consent status.
                       ``True`` means consent is active; ``False`` means revoked.

    Example::

        store: dict[str, bool] = {"user_1": True, "user_2": False}
        policy = ConsentBasedPolicy(consent_store=store)
        record = MemoryRecord(
            record_id="r1",
            content_hash="abc",
            created_at=0,
            category="preference",
            relevance_score=0.7,
            consent_owner="user_1",
        )
        policy.should_retain(record, current_timestep=50)  # True
        store["user_1"] = False
        policy.should_retain(record, current_timestep=51)  # False
    """

    def __init__(self, consent_store: dict[str, bool]) -> None:
        self.consent_store = consent_store

    def should_retain(self, record: MemoryRecord, current_timestep: int) -> bool:
        """Retain if the record owner still has active consent."""
        return self.consent_store.get(record.consent_owner, True)

    def revoke(self, owner: str) -> None:
        """Revoke consent for a given owner identifier.

        Args:
            owner: The consent_owner string to revoke.
        """
        self.consent_store[owner] = False

    def grant(self, owner: str) -> None:
        """Grant (or restore) consent for a given owner identifier.

        Args:
            owner: The consent_owner string to grant consent to.
        """
        self.consent_store[owner] = True

    def __repr__(self) -> str:
        active = sum(1 for v in self.consent_store.values() if v)
        total = len(self.consent_store)
        return f"ConsentBasedPolicy(active={active}/{total})"


CompositionMode = Literal["all", "any"]


@dataclass
class CompositePolicy(RetentionPolicy):
    """Compose multiple retention policies with AND or OR logic.

    SIMULATION ONLY — not production AMGP implementation.

    In ``"all"`` mode (AND): a record is retained only when *every* child policy
    returns True. This is the strictest composition — a single policy can force
    forgetting.

    In ``"any"`` mode (OR): a record is retained when *at least one* child policy
    returns True. This is the most permissive composition — forgetting only
    happens when all policies agree.

    Args:
        policies: Ordered list of RetentionPolicy instances to evaluate.
        mode: ``"all"`` for AND semantics (default), ``"any"`` for OR semantics.

    Raises:
        ValueError: If ``policies`` is empty or ``mode`` is not ``"all"``/``"any"``.

    Example::

        time_policy = TimeBasedPolicy(ttl=100)
        decay_policy = RelevanceDecayPolicy(decay_rate=0.01, threshold=0.3)
        composite = CompositePolicy(
            policies=[time_policy, decay_policy],
            mode="all",
        )
        # record is retained only when BOTH policies agree
    """

    policies: list[RetentionPolicy]
    mode: CompositionMode = "all"

    def __post_init__(self) -> None:
        if not self.policies:
            raise ValueError("CompositePolicy requires at least one child policy")
        if self.mode not in ("all", "any"):
            raise ValueError(f"mode must be 'all' or 'any', got {self.mode!r}")

    def should_retain(self, record: MemoryRecord, current_timestep: int) -> bool:
        """Apply composed logic across all child policies.

        Args:
            record: The synthetic MemoryRecord under evaluation.
            current_timestep: Current simulation timestep.

        Returns:
            True or False according to the composition mode.
        """
        decisions = (p.should_retain(record, current_timestep) for p in self.policies)
        if self.mode == "all":
            return all(decisions)
        return any(decisions)

    def __repr__(self) -> str:
        names = ", ".join(type(p).__name__ for p in self.policies)
        return f"CompositePolicy(mode={self.mode!r}, policies=[{names}])"


@dataclass(frozen=True)
class ConsentRevocation:
    """A consent revocation event in the simulation timeline.

    SIMULATION ONLY — not production AMGP implementation.

    Attributes:
        owner: The consent_owner identifier whose consent is revoked.
        at_timestep: The simulation timestep at which revocation takes effect.
    """

    owner: str
    at_timestep: int
