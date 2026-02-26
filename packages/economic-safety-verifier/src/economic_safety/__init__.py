# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
economic_safety — Research companion for Paper 22.

SIMULATION ONLY. This package implements simplified arithmetic verification
of economic safety properties for agent spending envelopes. It does NOT
contain Paper 22's 25 theorem proofs, production AEAP algorithms, or any
real agent spending data.

All spending data is SYNTHETIC. All results are generated from seed=42
deterministic simulation.
"""

from economic_safety.model import (
    EconomicModel,
    SimulationConfig,
    SpendingResult,
)
from economic_safety.properties import EconomicProperties
from economic_safety.verifier import EconomicSafetyVerifier
from economic_safety.model import (
    Envelope,
    Transaction,
    Commitment,
    SpendingAgent,
    VerificationResult,
    ConcurrencyResult,
)

__version__ = "0.1.0"
__all__ = [
    "EconomicModel",
    "SimulationConfig",
    "SpendingResult",
    "EconomicProperties",
    "EconomicSafetyVerifier",
    "Envelope",
    "Transaction",
    "Commitment",
    "SpendingAgent",
    "VerificationResult",
    "ConcurrencyResult",
]
