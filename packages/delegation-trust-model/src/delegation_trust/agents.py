# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
agents.py — Synthetic multi-agent scenario builders for delegation trust simulation.

SIMULATION ONLY. This module generates synthetic agent populations and delegation
graph topologies for use in academic experiments. All agents and trust values are
SYNTHETIC. Agent types (Compliant/Adversarial/Mixed/Degrading/Strategic) determine
how pairwise trust levels are sampled from configurable distributions.

No real agent identities, delegation records, or behavioral data are used.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from delegation_trust.model import AgentNode, DelegationEdge, SimulationConfig


# ---------------------------------------------------------------------------
# Trust level samplers per agent type
# ---------------------------------------------------------------------------

#: Trust level sampling parameters by agent type.
#: Each entry is (mean, std_dev) for a truncated Normal(mean, std) in [0, 1].
#: These are SYNTHETIC parameters for simulation — not production thresholds.
_TRUST_PARAMS: dict[str, tuple[float, float]] = {
    "compliant": (0.88, 0.06),    # High trust, low variance
    "adversarial": (0.25, 0.10),  # Low trust, moderate variance
    "mixed": (0.60, 0.15),        # Moderate trust, higher variance
    "degrading": (0.70, 0.08),    # Starts moderate, degrades over hops
    "strategic": (0.75, 0.12),    # Selectively high trust on key paths
}


def _sample_trust(
    agent_type: str,
    rng: np.random.RandomState,
    hop_index: int = 0,
) -> float:
    """Sample a pairwise trust level for an agent of the given type.

    SIMULATION ONLY. Uses truncated Normal sampling from type-specific
    parameters. No production algorithm or behavioral scoring is used.

    Args:
        agent_type: One of the VALID_TYPES from AgentNode.
        rng: Random number generator for reproducibility.
        hop_index: For "degrading" agents, trust decreases by 0.05 per hop
            (floored at 0.1). Ignored for other types.

    Returns:
        Pairwise trust level in [0.0, 1.0].
    """
    mean, std = _TRUST_PARAMS.get(agent_type, (0.60, 0.15))

    if agent_type == "degrading":
        mean = max(0.10, mean - 0.05 * hop_index)

    raw = float(rng.normal(mean, std))
    return float(np.clip(raw, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Scenario population builders
# ---------------------------------------------------------------------------


@dataclass
class AgentPopulation:
    """A synthetic collection of agents and delegation edges for a scenario.

    SIMULATION ONLY. Encapsulates agents and edges ready to be loaded into
    DelegationTrustModel for a simulation run.

    Attributes:
        agents: List of AgentNode instances.
        edges: List of DelegationEdge instances forming the delegation graph.
        source: Recommended source agent for transitive trust queries.
        target: Recommended target agent for transitive trust queries.
        description: Human-readable description of the population.
    """

    agents: list[AgentNode]
    edges: list[DelegationEdge]
    source: str
    target: str
    description: str


def build_linear_chain(
    length: int,
    agent_type: str = "compliant",
    config: SimulationConfig = SimulationConfig(),
    task_scope: str = "general",
) -> AgentPopulation:
    """Build a linear delegation chain of the specified length.

    SIMULATION ONLY. Creates a straight-line delegation graph:
    agent-0 -> agent-1 -> ... -> agent-{length-1}

    All trust levels are sampled from the distribution for the given agent_type.
    This is SYNTHETIC data — not a real delegation hierarchy.

    Args:
        length: Number of agents in the chain (minimum 2).
        agent_type: Type applied to all non-root agents.
        config: Simulation config supplying the RNG seed.
        task_scope: Task scope label for all delegation edges.

    Returns:
        AgentPopulation with the constructed chain.

    Raises:
        ValueError: If length < 2.
    """
    if length < 2:
        raise ValueError(f"Chain length must be >= 2; got {length}")

    rng = np.random.RandomState(config.seed)
    agents: list[AgentNode] = []
    edges: list[DelegationEdge] = []

    for index in range(length):
        node_type = "compliant" if index == 0 else agent_type
        agents.append(
            AgentNode(
                agent_id=f"agent-{index}",
                agent_type=node_type,
                label=f"A{index}",
            )
        )

    for index in range(length - 1):
        trust = _sample_trust(agents[index + 1].agent_type, rng, hop_index=index)
        edges.append(
            DelegationEdge(
                edge_id=f"edge-{index}-{index + 1}",
                delegator=f"agent-{index}",
                delegatee=f"agent-{index + 1}",
                trust_level=trust,
                task_scope=task_scope,
            )
        )

    return AgentPopulation(
        agents=agents,
        edges=edges,
        source="agent-0",
        target=f"agent-{length - 1}",
        description=(
            f"Linear chain of {length} agents, all type='{agent_type}'. "
            f"SIMULATION ONLY — synthetic data."
        ),
    )


def build_tree_delegation(
    depth: int,
    branching_factor: int = 2,
    agent_type: str = "compliant",
    config: SimulationConfig = SimulationConfig(),
    task_scope: str = "general",
) -> AgentPopulation:
    """Build a tree delegation graph with the given depth and branching factor.

    SIMULATION ONLY. Creates a balanced tree where each non-leaf agent
    delegates to branching_factor children. Source is the root; target is
    the leftmost leaf at maximum depth. All trust values are SYNTHETIC.

    Args:
        depth: Tree depth (root is depth 0; leaves are depth `depth`).
        branching_factor: Number of children per non-leaf agent.
        agent_type: Agent type for all non-root nodes.
        config: Simulation config supplying the RNG seed.
        task_scope: Task scope label for all delegation edges.

    Returns:
        AgentPopulation with the constructed tree.

    Raises:
        ValueError: If depth < 1 or branching_factor < 2.
    """
    if depth < 1:
        raise ValueError(f"depth must be >= 1; got {depth}")
    if branching_factor < 2:
        raise ValueError(f"branching_factor must be >= 2; got {branching_factor}")

    rng = np.random.RandomState(config.seed)
    agents: list[AgentNode] = []
    edges: list[DelegationEdge] = []

    counter = 0

    def make_subtree(parent_id: str, current_depth: int, hop_index: int) -> None:
        nonlocal counter
        if current_depth >= depth:
            return
        for _ in range(branching_factor):
            child_id = f"agent-{counter}"
            counter += 1
            agents.append(
                AgentNode(
                    agent_id=child_id,
                    agent_type=agent_type,
                    label=child_id,
                )
            )
            trust = _sample_trust(agent_type, rng, hop_index=hop_index)
            edges.append(
                DelegationEdge(
                    edge_id=f"edge-{parent_id}-{child_id}",
                    delegator=parent_id,
                    delegatee=child_id,
                    trust_level=trust,
                    task_scope=task_scope,
                )
            )
            make_subtree(child_id, current_depth + 1, hop_index + 1)

    root_id = "agent-0"
    counter = 1
    agents.append(AgentNode(agent_id=root_id, agent_type="compliant", label="root"))
    make_subtree(root_id, 0, 0)

    # Target: leftmost leaf agent at maximum depth
    target_id = agents[-1].agent_id

    return AgentPopulation(
        agents=agents,
        edges=edges,
        source=root_id,
        target=target_id,
        description=(
            f"Tree: depth={depth}, branching={branching_factor}, "
            f"type='{agent_type}'. SIMULATION ONLY — synthetic data."
        ),
    )


def build_mixed_population(
    chain_length: int,
    adversarial_positions: list[int],
    config: SimulationConfig = SimulationConfig(),
    task_scope: str = "general",
) -> AgentPopulation:
    """Build a linear chain with adversarial agents at specified positions.

    SIMULATION ONLY. Inserts adversarial agents (low trust level) at the
    given chain positions to demonstrate how a single bad actor degrades
    overall transitive trust. All data is SYNTHETIC.

    Args:
        chain_length: Total number of agents in the chain.
        adversarial_positions: Zero-indexed positions to assign "adversarial" type.
        config: Simulation config supplying the RNG seed.
        task_scope: Task scope label for all edges.

    Returns:
        AgentPopulation with mixed compliant/adversarial agents.

    Raises:
        ValueError: If any position is out of range [0, chain_length).
    """
    for position in adversarial_positions:
        if not (0 <= position < chain_length):
            raise ValueError(
                f"adversarial_positions entry {position} out of range "
                f"[0, {chain_length})"
            )

    rng = np.random.RandomState(config.seed)
    agents: list[AgentNode] = []
    edges: list[DelegationEdge] = []
    adversarial_set = set(adversarial_positions)

    for index in range(chain_length):
        agent_type = "adversarial" if index in adversarial_set else "compliant"
        agents.append(
            AgentNode(
                agent_id=f"agent-{index}",
                agent_type=agent_type,
                label=f"A{index}({'adv' if agent_type == 'adversarial' else 'ok'})",
            )
        )

    for index in range(chain_length - 1):
        trust = _sample_trust(agents[index + 1].agent_type, rng, hop_index=index)
        edges.append(
            DelegationEdge(
                edge_id=f"edge-{index}-{index + 1}",
                delegator=f"agent-{index}",
                delegatee=f"agent-{index + 1}",
                trust_level=trust,
                task_scope=task_scope,
            )
        )

    return AgentPopulation(
        agents=agents,
        edges=edges,
        source="agent-0",
        target=f"agent-{chain_length - 1}",
        description=(
            f"Mixed chain length={chain_length}, adversarial at {adversarial_positions}. "
            "SIMULATION ONLY — synthetic data."
        ),
    )


def build_mesh_delegation(
    size: int,
    config: SimulationConfig = SimulationConfig(),
    task_scope: str = "general",
) -> AgentPopulation:
    """Build a fully-connected mesh delegation graph among N agents.

    SIMULATION ONLY. Creates directed edges from every agent to every other
    agent, simulating a peer delegation mesh. Source is agent-0; target is
    agent-{size-1}. All trust values are SYNTHETIC.

    Args:
        size: Number of agents in the mesh (minimum 3).
        config: Simulation config supplying the RNG seed.
        task_scope: Task scope label for all edges.

    Returns:
        AgentPopulation with mesh topology.

    Raises:
        ValueError: If size < 3.
    """
    if size < 3:
        raise ValueError(f"Mesh size must be >= 3; got {size}")

    rng = np.random.RandomState(config.seed)
    agents: list[AgentNode] = [
        AgentNode(agent_id=f"agent-{index}", agent_type="compliant", label=f"M{index}")
        for index in range(size)
    ]
    edges: list[DelegationEdge] = []

    for from_index in range(size):
        for to_index in range(size):
            if from_index == to_index:
                continue
            trust = _sample_trust("compliant", rng)
            edges.append(
                DelegationEdge(
                    edge_id=f"edge-{from_index}-{to_index}",
                    delegator=f"agent-{from_index}",
                    delegatee=f"agent-{to_index}",
                    trust_level=trust,
                    task_scope=task_scope,
                )
            )

    return AgentPopulation(
        agents=agents,
        edges=edges,
        source="agent-0",
        target=f"agent-{size - 1}",
        description=(
            f"Fully-connected mesh of {size} agents. "
            "SIMULATION ONLY — synthetic data."
        ),
    )
