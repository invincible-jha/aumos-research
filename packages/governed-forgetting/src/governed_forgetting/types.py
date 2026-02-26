# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""Core data types for the governed-forgetting simulation.

SIMULATION ONLY — not production AMGP implementation.
All MemoryRecord instances use synthetic content hashes; no real agent
memory content is stored or transmitted in this package.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MemoryRecord:
    """An immutable, synthetic memory record for simulation purposes.

    SIMULATION ONLY — not production AMGP implementation.
    Actual content is never stored; only a ``content_hash`` placeholder is kept
    to represent a distinct memory item without revealing any real information.

    Attributes:
        record_id: Unique identifier for this record within a simulation run.
        content_hash: Opaque placeholder representing hashed content (no real data).
        created_at: Simulation timestep at which the record was created.
        category: Semantic category label, e.g. ``"conversation"``, ``"fact"``.
        relevance_score: Initial relevance in [0, 1]. May decay over time
                         depending on the active policy.
        consent_owner: Identifier of the simulated owner whose consent governs
                       this record's retention.
    """

    record_id: str
    content_hash: str
    created_at: int
    category: str
    relevance_score: float
    consent_owner: str


@dataclass(frozen=True)
class RetentionSnapshot:
    """A point-in-time observation of the simulation state.

    SIMULATION ONLY — not production AMGP implementation.

    Attributes:
        timestep: The simulation clock value at the time of this snapshot.
        active: Number of records still held in active memory.
        forgotten: Cumulative number of records that have been forgotten so far.
    """

    timestep: int
    active: int
    forgotten: int


@dataclass(frozen=True)
class RetentionResult:
    """Aggregate outcome of a complete simulation run.

    SIMULATION ONLY — not production AMGP implementation.

    Attributes:
        retained: All MemoryRecord objects still active at the end of the run.
        forgotten: All MemoryRecord objects that were forgotten during the run.
        history: Ordered list of RetentionSnapshot objects, one per timestep.
        retention_rate: Fraction of the original stream that remains retained
                        at the end, in [0, 1].
    """

    retained: list[MemoryRecord]
    forgotten: list[MemoryRecord]
    history: list[RetentionSnapshot]
    retention_rate: float


@dataclass(frozen=True)
class VerificationResult:
    """Outcome of a formal property verification check.

    SIMULATION ONLY — not production AMGP implementation.

    Attributes:
        holds: True when the checked property was satisfied for all examined records.
        violations: Human-readable descriptions of any property violations found.
        records_checked: Total number of records (or events) evaluated.
    """

    holds: bool
    violations: list[str] = field(default_factory=list)
    records_checked: int = 0


@dataclass
class SimulationConfig:
    """Configuration object for a MemoryRetentionModel run.

    SIMULATION ONLY — not production AMGP implementation.

    Attributes:
        policies: List of RetentionPolicy instances to apply at each timestep.
                  Policies are evaluated sequentially; a record is forgotten when
                  *any* policy returns False (i.e., AND of all retentions).
        seed: Random seed for reproducible synthetic data generation.
        timesteps: Number of simulation clock ticks to run.

    Note:
        The ``policies`` field accepts any objects with a ``should_retain`` method.
        The ``RetentionPolicy`` type annotation uses ``Any`` to avoid a circular
        import at module load time; the runtime type is enforced by the model.
    """

    policies: list[Any]
    seed: int = 42
    timesteps: int = 500
