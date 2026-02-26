# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
delegation_trust — Research companion for Paper 18.

SIMULATION ONLY. This package implements a simplified multiplicative decay model
of trust propagation across multi-agent delegation chains. It does NOT contain
Paper 18's full theorem proofs, production delegation management algorithms,
adaptive trust progression, or behavioral scoring logic.

All delegation data is SYNTHETIC. All results are generated from seed=42
deterministic simulation.
"""

from delegation_trust.model import (
    AgentNode,
    DelegationEdge,
    DelegationTrustModel,
    ScenarioConfig,
    SimulationConfig,
    SimulationResult,
)
from delegation_trust.agents import (
    AgentPopulation,
    build_linear_chain,
    build_mesh_delegation,
    build_mixed_population,
    build_tree_delegation,
)
from delegation_trust.metrics import (
    DecayProfile,
    DepthAnalysis,
    PathReliability,
    TransitivityScore,
    decay_over_hops,
    delegation_depth_analysis,
    path_reliability,
    transitivity_score,
)

__version__ = "0.1.0"
__all__ = [
    # Model
    "DelegationTrustModel",
    "SimulationConfig",
    "SimulationResult",
    "DelegationEdge",
    "AgentNode",
    "ScenarioConfig",
    # Agents
    "AgentPopulation",
    "build_linear_chain",
    "build_tree_delegation",
    "build_mixed_population",
    "build_mesh_delegation",
    # Metrics
    "TransitivityScore",
    "DecayProfile",
    "DepthAnalysis",
    "PathReliability",
    "transitivity_score",
    "decay_over_hops",
    "delegation_depth_analysis",
    "path_reliability",
]
