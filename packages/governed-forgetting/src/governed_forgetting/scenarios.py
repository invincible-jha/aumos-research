# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""Predefined simulation scenarios matching Paper 5 figures.

SIMULATION ONLY — not production AMGP implementation.
Each scenario function returns a fully configured MemoryRetentionModel
and a synthetic memory stream, ready to pass to ``model.simulate()``.
Seeds are fixed to 42 for all scenarios to ensure reproducibility.
"""

from __future__ import annotations

from dataclasses import dataclass

from governed_forgetting.model import MemoryRetentionModel
from governed_forgetting.policies import (
    CompositePolicy,
    ConsentBasedPolicy,
    ConsentRevocation,
    RelevanceDecayPolicy,
    TimeBasedPolicy,
)
from governed_forgetting.types import MemoryRecord, SimulationConfig


@dataclass
class ScenarioBundle:
    """All components needed to execute a single scenario.

    SIMULATION ONLY — not production AMGP implementation.

    Attributes:
        name: Short identifier used in figure titles and file names.
        description: One-sentence description of what the scenario demonstrates.
        model: Configured MemoryRetentionModel ready for ``simulate()``.
        memory_stream: Synthetic records to feed into ``model.simulate()``.
        consent_revocations: Any scheduled revocation events (may be empty).
        timesteps: Recommended number of simulation ticks.
    """

    name: str
    description: str
    model: MemoryRetentionModel
    memory_stream: list[MemoryRecord]
    consent_revocations: list[ConsentRevocation]
    timesteps: int


# ---------------------------------------------------------------------------
# Scenario 1 — Time-Based Retention (Figure 1)
# ---------------------------------------------------------------------------

def scenario_time_based(
    n_memories: int = 500,
    ttl: int = 100,
    timesteps: int = 500,
    seed: int = 42,
) -> ScenarioBundle:
    """Build the time-based retention scenario (Paper 5, Figure 1).

    SIMULATION ONLY — not production AMGP implementation.
    Each record is forgotten exactly once its age exceeds ``ttl`` simulation
    timesteps. With ``ttl=100`` and ``timesteps=500``, the retention curve
    should fall to zero before t=300 (all records born before t=200 age out).

    Args:
        n_memories: Number of synthetic records to generate.
        ttl: Time-to-live in simulation timesteps.
        timesteps: Total simulation duration.
        seed: Random seed for reproducibility.

    Returns:
        A ScenarioBundle ready for ``model.simulate()``.
    """
    policy = TimeBasedPolicy(ttl=ttl)
    config = SimulationConfig(policies=[policy], seed=seed, timesteps=timesteps)
    model = MemoryRetentionModel(config)
    stream = model.generate_synthetic_stream(n=n_memories)
    return ScenarioBundle(
        name="time_based_retention",
        description=f"Time-based forgetting: TTL={ttl}, {n_memories} synthetic records.",
        model=model,
        memory_stream=stream,
        consent_revocations=[],
        timesteps=timesteps,
    )


# ---------------------------------------------------------------------------
# Scenario 2 — Relevance Decay (Figure 2)
# ---------------------------------------------------------------------------

def scenario_relevance_decay(
    n_memories: int = 500,
    decay_rate: float = 0.01,
    threshold: float = 0.3,
    timesteps: int = 500,
    seed: int = 42,
) -> ScenarioBundle:
    """Build the relevance-decay retention scenario (Paper 5, Figure 2).

    SIMULATION ONLY — not production AMGP implementation.
    Records decay exponentially from their initial relevance score. Records
    with low initial relevance are forgotten early; high-relevance records
    persist longer. At ``decay_rate=0.01`` a record starting at 1.0 reaches
    the ``threshold=0.3`` at approximately t=120 after creation.

    Args:
        n_memories: Number of synthetic records to generate.
        decay_rate: Exponential decay constant (non-negative float).
        threshold: Minimum effective relevance to remain active.
        timesteps: Total simulation duration.
        seed: Random seed for reproducibility.

    Returns:
        A ScenarioBundle ready for ``model.simulate()``.
    """
    policy = RelevanceDecayPolicy(decay_rate=decay_rate, threshold=threshold)
    config = SimulationConfig(policies=[policy], seed=seed, timesteps=timesteps)
    model = MemoryRetentionModel(config)
    stream = model.generate_synthetic_stream(n=n_memories)
    return ScenarioBundle(
        name="relevance_decay",
        description=(
            f"Relevance-decay forgetting: decay_rate={decay_rate}, "
            f"threshold={threshold}, {n_memories} synthetic records."
        ),
        model=model,
        memory_stream=stream,
        consent_revocations=[],
        timesteps=timesteps,
    )


# ---------------------------------------------------------------------------
# Scenario 3 — Consent Revocation (Figure 3)
# ---------------------------------------------------------------------------

def scenario_consent_revocation(
    n_memories: int = 500,
    n_owners: int = 10,
    revocation_timesteps: list[int] | None = None,
    timesteps: int = 500,
    seed: int = 42,
) -> ScenarioBundle:
    """Build the consent-revocation scenario (Paper 5, Figure 3).

    SIMULATION ONLY — not production AMGP implementation.
    Consent is revoked in three batches at t=100, t=200, and t=300, covering
    roughly one third of all simulated owners per batch. This produces a
    staircase drop in the active-memory curve.

    The ConsentBasedPolicy's internal store is mutated by the returned
    ScenarioBundle; experiments must update the store before each timestep
    batch using the ``consent_revocations`` list.

    Args:
        n_memories: Number of synthetic records to generate.
        n_owners: Number of distinct consent owner identifiers.
        revocation_timesteps: Timesteps at which to schedule batch revocations.
                              Defaults to ``[100, 200, 300]``.
        timesteps: Total simulation duration.
        seed: Random seed for reproducibility.

    Returns:
        A ScenarioBundle containing scheduled ConsentRevocation events.
    """
    if revocation_timesteps is None:
        revocation_timesteps = [100, 200, 300]

    # Build the initial consent store — all owners start with active consent
    consent_store: dict[str, bool] = {
        f"user_{i}": True for i in range(n_owners)
    }
    policy = ConsentBasedPolicy(consent_store=consent_store)
    config = SimulationConfig(policies=[policy], seed=seed, timesteps=timesteps)
    model = MemoryRetentionModel(config)
    stream = model.generate_synthetic_stream(n=n_memories, n_owners=n_owners)

    # Spread owners across the three revocation batches
    owners = list(consent_store.keys())
    revocations: list[ConsentRevocation] = []
    batch_size = max(1, n_owners // len(revocation_timesteps))
    for batch_index, t in enumerate(revocation_timesteps):
        start = batch_index * batch_size
        end = start + batch_size if batch_index < len(revocation_timesteps) - 1 else n_owners
        for owner in owners[start:end]:
            revocations.append(ConsentRevocation(owner=owner, at_timestep=t))

    return ScenarioBundle(
        name="consent_revocation",
        description=(
            f"Consent-based forgetting: batch revocations at "
            f"t={revocation_timesteps}, {n_memories} synthetic records."
        ),
        model=model,
        memory_stream=stream,
        consent_revocations=revocations,
        timesteps=timesteps,
    )


# ---------------------------------------------------------------------------
# Scenario 4 — Composite Policy (Figure 4)
# ---------------------------------------------------------------------------

def scenario_composite_policy(
    n_memories: int = 500,
    ttl: int = 200,
    decay_rate: float = 0.01,
    threshold: float = 0.3,
    n_owners: int = 10,
    revocation_timesteps: list[int] | None = None,
    timesteps: int = 500,
    seed: int = 42,
) -> ScenarioBundle:
    """Build the composite-policy scenario (Paper 5, Figure 4).

    SIMULATION ONLY — not production AMGP implementation.
    Combines TimeBasedPolicy, RelevanceDecayPolicy, and ConsentBasedPolicy
    using AND semantics (``mode="all"``). A record is forgotten as soon as
    *any* policy rejects it. This scenario demonstrates how layering policies
    accelerates the overall forgetting rate compared to any single policy alone.

    Args:
        n_memories: Number of synthetic records to generate.
        ttl: Time-to-live for the TimeBasedPolicy component.
        decay_rate: Decay constant for the RelevanceDecayPolicy component.
        threshold: Relevance threshold for the RelevanceDecayPolicy component.
        n_owners: Number of distinct consent owner identifiers.
        revocation_timesteps: Timesteps at which to schedule batch revocations.
                              Defaults to ``[150, 300]``.
        timesteps: Total simulation duration.
        seed: Random seed for reproducibility.

    Returns:
        A ScenarioBundle containing the composite policy and scheduled revocations.
    """
    if revocation_timesteps is None:
        revocation_timesteps = [150, 300]

    consent_store: dict[str, bool] = {
        f"user_{i}": True for i in range(n_owners)
    }
    time_policy = TimeBasedPolicy(ttl=ttl)
    decay_policy = RelevanceDecayPolicy(decay_rate=decay_rate, threshold=threshold)
    consent_policy = ConsentBasedPolicy(consent_store=consent_store)

    composite = CompositePolicy(
        policies=[time_policy, decay_policy, consent_policy],
        mode="all",
    )
    config = SimulationConfig(policies=[composite], seed=seed, timesteps=timesteps)
    model = MemoryRetentionModel(config)
    stream = model.generate_synthetic_stream(n=n_memories, n_owners=n_owners)

    owners = list(consent_store.keys())
    revocations: list[ConsentRevocation] = []
    batch_size = max(1, n_owners // len(revocation_timesteps))
    for batch_index, t in enumerate(revocation_timesteps):
        start = batch_index * batch_size
        end = start + batch_size if batch_index < len(revocation_timesteps) - 1 else n_owners
        for owner in owners[start:end]:
            revocations.append(ConsentRevocation(owner=owner, at_timestep=t))

    return ScenarioBundle(
        name="composite_policy",
        description=(
            f"Composite forgetting (Time + Decay + Consent, mode=all): "
            f"ttl={ttl}, decay_rate={decay_rate}, threshold={threshold}, "
            f"{n_memories} synthetic records."
        ),
        model=model,
        memory_stream=stream,
        consent_revocations=revocations,
        timesteps=timesteps,
    )


# ---------------------------------------------------------------------------
# Convenience registry
# ---------------------------------------------------------------------------

ALL_SCENARIOS: dict[str, str] = {
    "time_based_retention": "scenario_time_based",
    "relevance_decay": "scenario_relevance_decay",
    "consent_revocation": "scenario_consent_revocation",
    "composite_policy": "scenario_composite_policy",
}
"""Mapping of scenario name to the corresponding factory function name."""
