# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
composition_verifier — Research companion for Papers 9/25.

RESEARCH TOOL — not production orchestration.

This package implements bounded model checking for formal properties of
composed governance protocol state machines. All state machines are
synthetic and intentionally simplified (3–5 states per protocol).

Quick start
-----------
    >>> from composition_verifier.scenarios import standard_composition
    >>> from composition_verifier.verifier import ProtocolCompositionVerifier
    >>> protocols = standard_composition()
    >>> verifier = ProtocolCompositionVerifier()
    >>> result = verifier.verify_deadlock_freedom(protocols)
    >>> result.holds
    True

See Also
--------
- :mod:`composition_verifier.model`       — State, Transition, ProtocolModel
- :mod:`composition_verifier.composer`    — ProtocolComposer
- :mod:`composition_verifier.properties`  — PropertySpec catalogue
- :mod:`composition_verifier.verifier`    — ProtocolCompositionVerifier
- :mod:`composition_verifier.scenarios`   — Predefined synthetic protocols
- :mod:`composition_verifier.visualization` — Matplotlib figure helpers
"""

from composition_verifier.composer import ComposedDecision, ComposerError, ProtocolComposer
from composition_verifier.model import (
    ComposedState,
    ProtocolDecision,
    ProtocolModel,
    ProtocolModelError,
    State,
    Transition,
    VerificationResult,
)
from composition_verifier.properties import (
    DEADLOCK_FREEDOM,
    MONOTONIC_RESTRICTION,
    PropertyKind,
    PropertySpec,
    priority_ordering_spec,
)
from composition_verifier.scenarios import (
    ALL_ACTIONS,
    build_aeap,
    build_asp,
    build_atp,
    build_broken_deadlock_protocol,
    standard_composition,
)
from composition_verifier.verifier import ProtocolCompositionVerifier, VerifierError

__version__: str = "0.1.0"
__all__: list[str] = [
    # model
    "State",
    "Transition",
    "ProtocolDecision",
    "ComposedState",
    "VerificationResult",
    "ProtocolModel",
    "ProtocolModelError",
    # composer
    "ComposedDecision",
    "ComposerError",
    "ProtocolComposer",
    # properties
    "PropertyKind",
    "PropertySpec",
    "MONOTONIC_RESTRICTION",
    "DEADLOCK_FREEDOM",
    "priority_ordering_spec",
    # verifier
    "ProtocolCompositionVerifier",
    "VerifierError",
    # scenarios
    "ALL_ACTIONS",
    "build_atp",
    "build_asp",
    "build_aeap",
    "build_broken_deadlock_protocol",
    "standard_composition",
    # version
    "__version__",
]
