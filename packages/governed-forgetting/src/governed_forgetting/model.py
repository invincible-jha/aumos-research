# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""MemoryRetentionModel — core simulation engine for governed-forgetting.

SIMULATION ONLY — not production AMGP implementation.
This module provides a simplified retention simulation for academic analysis.
No production algorithms, tuning parameters, or proprietary logic are included.
"""

from __future__ import annotations

import hashlib

import numpy as np

from governed_forgetting.policies import RetentionPolicy
from governed_forgetting.types import (
    MemoryRecord,
    RetentionResult,
    RetentionSnapshot,
    SimulationConfig,
)


class MemoryRetentionModel:
    """Simulate memory retention under various governance policies.

    SIMULATION ONLY — not the production AMGP implementation.
    Uses simplified retention dynamics for academic analysis.
    All memory records are synthetic; no real content is stored or processed.

    The model iterates through ``timesteps`` clock ticks. At each tick every
    active record is evaluated against all configured policies. A record is
    retained only when *all* policies return ``True``; otherwise it is moved
    to the forgotten set immediately. Once forgotten, a record is never
    reconsidered (monotonic forgetting).

    Args:
        config: A :class:`~governed_forgetting.types.SimulationConfig` containing
                the ordered list of policies, random seed, and timestep count.

    Example::

        from governed_forgetting.policies import TimeBasedPolicy
        from governed_forgetting.types import SimulationConfig
        from governed_forgetting.model import MemoryRetentionModel

        config = SimulationConfig(policies=[TimeBasedPolicy(ttl=100)])
        model = MemoryRetentionModel(config)
        stream = model.generate_synthetic_stream(n=200)
        result = model.simulate(stream)
        print(result.retention_rate)
    """

    def __init__(self, config: SimulationConfig) -> None:
        self.policies: list[RetentionPolicy] = config.policies
        self.seed: int = config.seed
        self.rng: np.random.RandomState = np.random.RandomState(config.seed)  # type: ignore[no-untyped-call]
        self._default_timesteps: int = config.timesteps

    # ------------------------------------------------------------------
    # Synthetic data generation
    # ------------------------------------------------------------------

    def generate_synthetic_stream(
        self,
        n: int,
        categories: list[str] | None = None,
        n_owners: int = 10,
        birth_spread: int | None = None,
    ) -> list[MemoryRecord]:
        """Generate a list of ``n`` synthetic MemoryRecord objects.

        SIMULATION ONLY — not production AMGP implementation.
        Records are created with deterministic pseudo-random attributes drawn
        from the model's seeded RNG so that results are reproducible given the
        same ``SimulationConfig.seed``.

        Args:
            n: Number of records to generate.
            categories: Optional list of category labels to sample from.
                        Defaults to ``["conversation", "preference", "fact", "event"]``.
            n_owners: Number of distinct consent_owner identifiers to spread
                      records across.
            birth_spread: Upper bound (exclusive) for the ``created_at`` timestep.
                          Defaults to ``self._default_timesteps // 2`` so that
                          most records are born before the halfway point.

        Returns:
            List of synthetic MemoryRecord instances.
        """
        if categories is None:
            categories = ["conversation", "preference", "fact", "event"]
        if birth_spread is None:
            birth_spread = max(1, self._default_timesteps // 2)

        records: list[MemoryRecord] = []
        for i in range(n):
            created_at = int(self.rng.randint(0, birth_spread))
            relevance = float(np.clip(self.rng.beta(2.0, 2.0), 0.01, 1.0))
            category = str(categories[int(self.rng.randint(0, len(categories)))])
            owner = f"user_{int(self.rng.randint(0, n_owners))}"
            # content_hash is a deterministic placeholder — no real content
            raw = f"{i}:{created_at}:{category}:{owner}:{self.seed}"
            content_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
            records.append(
                MemoryRecord(
                    record_id=f"rec_{i:05d}",
                    content_hash=content_hash,
                    created_at=created_at,
                    category=category,
                    relevance_score=relevance,
                    consent_owner=owner,
                )
            )
        return records

    # ------------------------------------------------------------------
    # Core simulation
    # ------------------------------------------------------------------

    def simulate(
        self,
        memory_stream: list[MemoryRecord],
        timesteps: int | None = None,
    ) -> RetentionResult:
        """Simulate retention decisions over the full timestep range.

        SIMULATION ONLY — not production AMGP implementation.
        At each timestep, every active record is tested against all policies.
        A record is forgotten as soon as *any* policy rejects it. Forgetting is
        monotonic: a forgotten record is never re-evaluated or resurrected.

        Args:
            memory_stream: The list of synthetic MemoryRecord objects to simulate.
            timesteps: Number of clock ticks to run. Defaults to
                       ``SimulationConfig.timesteps``.

        Returns:
            A :class:`~governed_forgetting.types.RetentionResult` containing the
            final retained set, the forgotten set, per-timestep history, and the
            aggregate retention rate.
        """
        if timesteps is None:
            timesteps = self._default_timesteps

        forgotten: list[MemoryRecord] = []
        history: list[RetentionSnapshot] = []
        active_memories: list[MemoryRecord] = list(memory_stream)

        for t in range(timesteps):
            still_active: list[MemoryRecord] = []
            newly_forgotten: list[MemoryRecord] = []

            for record in active_memories:
                if self._should_retain(record, t):
                    still_active.append(record)
                else:
                    newly_forgotten.append(record)

            active_memories = still_active
            forgotten.extend(newly_forgotten)
            history.append(
                RetentionSnapshot(
                    timestep=t,
                    active=len(active_memories),
                    forgotten=len(forgotten),
                )
            )

        retained = active_memories
        total = max(len(memory_stream), 1)
        return RetentionResult(
            retained=retained,
            forgotten=forgotten,
            history=history,
            retention_rate=len(retained) / total,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _should_retain(self, record: MemoryRecord, current_timestep: int) -> bool:
        """Return True only when ALL configured policies agree to retain.

        SIMULATION ONLY — not production AMGP implementation.

        Args:
            record: The MemoryRecord to evaluate.
            current_timestep: The current simulation clock value.

        Returns:
            True if all policies permit retention; False otherwise.
        """
        return all(
            policy.should_retain(record, current_timestep) for policy in self.policies
        )
