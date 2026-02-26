# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
model.py — DelegationTrustModel and core dataclasses for delegation chain simulation.

SIMULATION ONLY. This module implements a simplified multiplicative decay model of
trust propagation across multi-agent delegation chains. It does NOT contain production
delegation management algorithms, Paper 18's full theorem proofs, adaptive trust
progression, or behavioral scoring. All data produced is SYNTHETIC.

Trust propagation uses MULTIPLICATIVE DECAY ONLY: the effective trust from source
to target along a delegation path is the product of all pairwise edge trust levels.
This is a simplification for academic analysis, not the production algorithm.
"""

from __future__ import annotations

import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Core dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DelegationEdge:
    """A single delegation relationship between two agents.

    SIMULATION ONLY. Represents a static trust level on a delegation link —
    not a production trust record. Trust levels are set at creation and never
    automatically updated based on observed behavior.

    Attributes:
        edge_id: Unique identifier for this delegation edge.
        delegator: Identifier of the agent granting authority.
        delegatee: Identifier of the agent receiving authority.
        trust_level: Pairwise trust level (0.0–1.0). Used as the decay
            multiplier in transitive trust computation.
        task_scope: Label describing what task domain is delegated.
    """

    edge_id: str
    delegator: str
    delegatee: str
    trust_level: float
    task_scope: str

    def __post_init__(self) -> None:
        if not (0.0 <= self.trust_level <= 1.0):
            raise ValueError(
                f"trust_level must be in [0.0, 1.0]; got {self.trust_level}"
            )


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration for the DelegationTrustModel simulation.

    SIMULATION ONLY.

    Attributes:
        seed: RNG seed for deterministic reproducibility (default 42).
        max_path_length: Maximum BFS depth when searching delegation paths.
    """

    seed: int = 42
    max_path_length: int = 10


@dataclass
class SimulationResult:
    """Aggregate result of a delegation trust simulation run.

    SIMULATION ONLY. Produced by DelegationTrustModel.simulate_scenario — not
    by any production system.

    Attributes:
        scenario_name: Name of the scenario that produced this result.
        source: Source agent identifier.
        target: Target agent identifier.
        terminal_trust: Effective transitive trust from source to target.
        path: Ordered list of agent identifiers from source to target.
        path_length: Number of delegation hops in the path.
        decay_per_hop: Geometric mean trust decay per delegation hop.
        path_found: True when a delegation path exists from source to target.
        detail: Human-readable summary of the simulation outcome.
    """

    scenario_name: str
    source: str
    target: str
    terminal_trust: float
    path: list[str]
    path_length: int
    decay_per_hop: float
    path_found: bool
    detail: str = ""


@dataclass(frozen=True)
class AgentNode:
    """A synthetic agent node in the delegation graph.

    SIMULATION ONLY. Encapsulates agent identity and type for graph construction.
    Agent types affect how trust levels are assigned in scenario generation.

    Attributes:
        agent_id: Unique agent identifier.
        agent_type: One of "compliant", "adversarial", "mixed", "degrading",
            "strategic". Affects generated trust levels in synthetic scenarios.
        label: Optional display label for visualization.
    """

    agent_id: str
    agent_type: str
    label: str = ""

    VALID_TYPES: frozenset[str] = frozenset(
        {"compliant", "adversarial", "mixed", "degrading", "strategic"}
    )

    def __post_init__(self) -> None:
        if self.agent_type not in self.VALID_TYPES:
            raise ValueError(
                f"agent_type must be one of {self.VALID_TYPES}; got '{self.agent_type}'"
            )


@dataclass(frozen=True)
class ScenarioConfig:
    """Configuration for a predefined delegation trust scenario.

    SIMULATION ONLY. Bundles graph topology parameters and agent definitions.

    Attributes:
        name: Short identifier matching the SCENARIOS dict key.
        description: Human-readable description of what this scenario tests.
        agents: Ordered list of agent nodes forming the delegation graph.
        edges: Delegation edges defining the graph topology.
        source: Source agent for transitive trust queries.
        target: Target agent for transitive trust queries.
        seed: RNG seed for deterministic reproduction.
    """

    name: str
    description: str
    agents: list[AgentNode]
    edges: list[DelegationEdge]
    source: str
    target: str
    seed: int = 42


# ---------------------------------------------------------------------------
# DelegationTrustModel
# ---------------------------------------------------------------------------


class DelegationTrustModel:
    """Simulate trust propagation across agent delegation chains.

    SIMULATION ONLY — does not contain production delegation management
    algorithms or Paper 18's full theorem proofs. Uses simplified multiplicative
    decay for academic analysis. All produced delegation data is SYNTHETIC.

    The model maintains a directed graph of delegation edges. Trust propagates
    from source to target along the shortest BFS path. Effective trust is the
    product of all pairwise edge trust levels along the path (multiplicative
    decay). No adaptive trust progression or behavioral scoring is implemented.

    Example::

        config = SimulationConfig(seed=42)
        model = DelegationTrustModel(config)
        model.add_delegation("root", "agent-a", trust_level=0.9, task_scope="compute")
        model.add_delegation("agent-a", "agent-b", trust_level=0.8, task_scope="compute")
        effective = model.compute_transitive_trust("root", "agent-b")
        print(effective)  # 0.72
    """

    def __init__(self, config: SimulationConfig) -> None:
        """Initialise the model with the given configuration.

        SIMULATION ONLY.

        Args:
            config: Simulation parameters including seed and max path length.
        """
        self.config = config
        self.rng = np.random.RandomState(config.seed)
        self._edges: list[DelegationEdge] = []
        # Adjacency list: delegator -> list of (delegatee, edge)
        self._graph: dict[str, list[tuple[str, DelegationEdge]]] = {}
        self._agents: dict[str, AgentNode] = {}

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def add_agent(self, node: AgentNode) -> None:
        """Register an agent node in the delegation graph.

        SIMULATION ONLY.

        Args:
            node: The agent node to register.
        """
        self._agents[node.agent_id] = node
        if node.agent_id not in self._graph:
            self._graph[node.agent_id] = []

    def add_delegation(
        self,
        delegator: str,
        delegatee: str,
        trust_level: float,
        task_scope: str,
        edge_id: Optional[str] = None,
    ) -> DelegationEdge:
        """Add a directed delegation edge from delegator to delegatee.

        SIMULATION ONLY. Trust levels are static — no automatic update based
        on observed agent behavior.

        Args:
            delegator: Agent granting authority.
            delegatee: Agent receiving authority.
            trust_level: Pairwise trust level in [0.0, 1.0].
            task_scope: Label for the delegated task domain.
            edge_id: Optional explicit edge identifier; auto-generated if None.

        Returns:
            The created DelegationEdge.

        Raises:
            ValueError: If trust_level is outside [0.0, 1.0].
        """
        resolved_id = edge_id if edge_id is not None else str(uuid.uuid4())
        edge = DelegationEdge(
            edge_id=resolved_id,
            delegator=delegator,
            delegatee=delegatee,
            trust_level=trust_level,
            task_scope=task_scope,
        )

        self._edges.append(edge)
        if delegator not in self._graph:
            self._graph[delegator] = []
        if delegatee not in self._graph:
            self._graph[delegatee] = []
        self._graph[delegator].append((delegatee, edge))

        return edge

    # ------------------------------------------------------------------
    # Path finding
    # ------------------------------------------------------------------

    def _find_shortest_path(
        self, source: str, target: str
    ) -> Optional[list[str]]:
        """Find the shortest delegation path from source to target using BFS.

        SIMULATION ONLY. Returns the first path found by BFS over the
        delegation graph — not a production graph traversal algorithm.

        Args:
            source: Starting agent identifier.
            target: Destination agent identifier.

        Returns:
            Ordered list of agent identifiers from source to target, or None
            if no path exists within max_path_length hops.
        """
        if source == target:
            return [source]

        visited: set[str] = {source}
        queue: deque[list[str]] = deque([[source]])

        while queue:
            current_path = queue.popleft()
            current_node = current_path[-1]

            if len(current_path) > self.config.max_path_length:
                continue

            for neighbor, _edge in self._graph.get(current_node, []):
                if neighbor == target:
                    return current_path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(current_path + [neighbor])

        return None

    # ------------------------------------------------------------------
    # Trust computation
    # ------------------------------------------------------------------

    def compute_transitive_trust(self, source: str, target: str) -> float:
        """Compute effective transitive trust from source to target.

        SIMULATION ONLY. Uses multiplicative decay along the shortest BFS path:
        effective_trust = product of all edge trust_levels along the path.
        This is a simplified academic model — NOT the production trust algorithm.

        Args:
            source: Source agent identifier.
            target: Target agent identifier.

        Returns:
            Effective trust in [0.0, 1.0]. Returns 0.0 when no path exists.
            Returns 1.0 when source == target (self-delegation).

        Raises:
            KeyError: If source is not registered in the graph.
        """
        if source not in self._graph:
            raise KeyError(f"Source agent '{source}' not found in delegation graph")

        if source == target:
            return 1.0

        path = self._find_shortest_path(source, target)
        if path is None:
            return 0.0

        # Multiply all edge trust_levels along the path
        effective_trust = 1.0
        for index in range(len(path) - 1):
            from_agent = path[index]
            to_agent = path[index + 1]
            # Find the edge connecting these two agents
            edge_trust = self._get_edge_trust(from_agent, to_agent)
            effective_trust *= edge_trust

        return effective_trust

    def _get_edge_trust(self, from_agent: str, to_agent: str) -> float:
        """Retrieve trust level for a direct delegation edge.

        SIMULATION ONLY.

        Args:
            from_agent: Delegator agent identifier.
            to_agent: Delegatee agent identifier.

        Returns:
            Edge trust level, or 0.0 if edge does not exist.
        """
        for neighbor, edge in self._graph.get(from_agent, []):
            if neighbor == to_agent:
                return edge.trust_level
        return 0.0

    # ------------------------------------------------------------------
    # Scenario simulation
    # ------------------------------------------------------------------

    def simulate_scenario(self, scenario: ScenarioConfig) -> SimulationResult:
        """Run a full delegation trust scenario simulation.

        SIMULATION ONLY. Constructs the delegation graph from the scenario
        configuration, then computes transitive trust from source to target.
        All data is SYNTHETIC.

        Args:
            scenario: The scenario configuration to simulate.

        Returns:
            SimulationResult with terminal trust, path details, and metrics.
        """
        # Register all agents and edges from the scenario
        for agent in scenario.agents:
            self.add_agent(agent)
        for edge in scenario.edges:
            # Add edge without re-registering if already present
            if edge not in self._edges:
                self._edges.append(edge)
                if edge.delegator not in self._graph:
                    self._graph[edge.delegator] = []
                if edge.delegatee not in self._graph:
                    self._graph[edge.delegatee] = []
                self._graph[edge.delegator].append((edge.delegatee, edge))

        path = self._find_shortest_path(scenario.source, scenario.target)
        path_found = path is not None

        if path is None:
            return SimulationResult(
                scenario_name=scenario.name,
                source=scenario.source,
                target=scenario.target,
                terminal_trust=0.0,
                path=[],
                path_length=0,
                decay_per_hop=0.0,
                path_found=False,
                detail=(
                    f"No delegation path found from '{scenario.source}' "
                    f"to '{scenario.target}'. SIMULATION ONLY."
                ),
            )

        terminal_trust = self.compute_transitive_trust(scenario.source, scenario.target)
        hop_count = len(path) - 1
        decay_per_hop = (
            float(np.power(terminal_trust, 1.0 / hop_count))
            if hop_count > 0
            else 1.0
        )

        return SimulationResult(
            scenario_name=scenario.name,
            source=scenario.source,
            target=scenario.target,
            terminal_trust=terminal_trust,
            path=path,
            path_length=hop_count,
            decay_per_hop=decay_per_hop,
            path_found=path_found,
            detail=(
                f"Scenario '{scenario.name}': path length {hop_count} hop(s), "
                f"terminal_trust={terminal_trust:.6f}, "
                f"decay_per_hop={decay_per_hop:.6f}. SIMULATION ONLY."
            ),
        )

    def reset(self) -> None:
        """Reset the model to an empty state.

        SIMULATION ONLY. Clears all registered agents, edges, and graph state.
        The RNG is NOT reset — call __init__ again for full reset with new seed.
        """
        self._edges = []
        self._graph = {}
        self._agents = {}
