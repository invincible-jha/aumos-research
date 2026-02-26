# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""governed-forgetting — Research companion for Paper 5.

SIMULATION ONLY — not production AMGP implementation.
Provides simplified memory retention simulation and formal property
verification for academic analysis of governance policies.

Quick start::

    from governed_forgetting import (
        MemoryRetentionModel,
        SimulationConfig,
        TimeBasedPolicy,
        RetentionVerifier,
    )

    policy = TimeBasedPolicy(ttl=100)
    config = SimulationConfig(policies=[policy], seed=42)
    model = MemoryRetentionModel(config)
    stream = model.generate_synthetic_stream(n=500)
    result = model.simulate(stream)
    print(f"Retention rate: {result.retention_rate:.2%}")

    verifier = RetentionVerifier()
    check = verifier.verify_completeness(policy, stream)
    print(f"Completeness holds: {check.holds}")
"""

from governed_forgetting.model import MemoryRetentionModel
from governed_forgetting.policies import (
    CompositePolicy,
    CompositionMode,
    ConsentBasedPolicy,
    ConsentRevocation,
    RelevanceDecayPolicy,
    RetentionPolicy,
    TimeBasedPolicy,
)
from governed_forgetting.types import (
    MemoryRecord,
    RetentionResult,
    RetentionSnapshot,
    SimulationConfig,
    VerificationResult,
)
from governed_forgetting.verifier import RetentionVerifier

__all__ = [
    # model
    "MemoryRetentionModel",
    # policies
    "RetentionPolicy",
    "TimeBasedPolicy",
    "RelevanceDecayPolicy",
    "ConsentBasedPolicy",
    "CompositePolicy",
    "CompositionMode",
    "ConsentRevocation",
    # types
    "MemoryRecord",
    "RetentionResult",
    "RetentionSnapshot",
    "SimulationConfig",
    "VerificationResult",
    # verifier
    "RetentionVerifier",
]

__version__ = "0.1.0"
