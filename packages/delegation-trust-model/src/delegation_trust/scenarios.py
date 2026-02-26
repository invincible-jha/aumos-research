# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
scenarios.py — Predefined delegation trust scenarios for Paper 18 experiments.

SIMULATION ONLY. All scenario parameters are chosen to reproduce the paper's
figures from SYNTHETIC data. None of these configurations reflect real agent
delegation hierarchies or production trust policies.
"""

from __future__ import annotations

from delegation_trust.model import AgentNode, DelegationEdge, ScenarioConfig


def _make_linear(
    agent_types: list[str],
    trust_levels: list[float],
    name: str,
    description: str,
    task_scope: str = "general",
    seed: int = 42,
) -> ScenarioConfig:
    """Build a ScenarioConfig for a linear chain delegation graph."""
    agents = [
        AgentNode(
            agent_id=f"agent-{index}",
            agent_type=agent_type,
            label=f"A{index}",
        )
        for index, agent_type in enumerate(agent_types)
    ]
    edges = [
        DelegationEdge(
            edge_id=f"edge-{index}-{index + 1}",
            delegator=f"agent-{index}",
            delegatee=f"agent-{index + 1}",
            trust_level=trust_level,
            task_scope=task_scope,
        )
        for index, trust_level in enumerate(trust_levels)
    ]
    return ScenarioConfig(
        name=name,
        description=description,
        agents=agents,
        edges=edges,
        source="agent-0",
        target=f"agent-{len(agents) - 1}",
        seed=seed,
    )


SCENARIOS: dict[str, ScenarioConfig] = {
    # ------------------------------------------------------------------
    # linear_chain_3hop
    # Three-agent linear chain, all compliant, high trust edges.
    # Expected terminal trust ≈ 0.9^3 = 0.729
    # ------------------------------------------------------------------
    "linear_chain_3hop": _make_linear(
        agent_types=["compliant", "compliant", "compliant"],
        trust_levels=[0.90, 0.90],
        name="linear_chain_3hop",
        description=(
            "2 delegation hops, all compliant agents, trust_level=0.90 per edge. "
            "Expected terminal_trust ≈ 0.81. SIMULATION ONLY."
        ),
    ),
    # ------------------------------------------------------------------
    # linear_chain_5hop
    # Five-agent chain, all compliant, moderate trust.
    # Expected terminal trust ≈ 0.85^4 = 0.522
    # ------------------------------------------------------------------
    "linear_chain_5hop": _make_linear(
        agent_types=["compliant", "compliant", "compliant", "compliant", "compliant"],
        trust_levels=[0.85, 0.85, 0.85, 0.85],
        name="linear_chain_5hop",
        description=(
            "4 delegation hops, all compliant agents, trust_level=0.85 per edge. "
            "Expected terminal_trust ≈ 0.522. SIMULATION ONLY."
        ),
    ),
    # ------------------------------------------------------------------
    # linear_chain_8hop
    # Eight-agent chain, all compliant, moderate trust.
    # Expected terminal trust ≈ 0.85^7 = 0.321
    # ------------------------------------------------------------------
    "linear_chain_8hop": _make_linear(
        agent_types=["compliant"] * 8,
        trust_levels=[0.85] * 7,
        name="linear_chain_8hop",
        description=(
            "7 delegation hops, all compliant agents, trust_level=0.85 per edge. "
            "Expected terminal_trust ≈ 0.321. SIMULATION ONLY."
        ),
    ),
    # ------------------------------------------------------------------
    # adversarial_midchain
    # Five-agent chain with one adversarial agent in the middle.
    # The adversarial edge has low trust (0.20), degrading overall trust.
    # ------------------------------------------------------------------
    "adversarial_midchain": _make_linear(
        agent_types=["compliant", "compliant", "adversarial", "compliant", "compliant"],
        trust_levels=[0.90, 0.90, 0.20, 0.90],
        name="adversarial_midchain",
        description=(
            "5-agent chain with adversarial agent at position 2 (trust=0.20). "
            "Expected terminal_trust ≈ 0.9*0.9*0.20*0.9 ≈ 0.146. SIMULATION ONLY."
        ),
    ),
    # ------------------------------------------------------------------
    # adversarial_tail
    # Five-agent chain with adversarial agent at the last position.
    # Demonstrates that even the final hop degrades overall trust.
    # ------------------------------------------------------------------
    "adversarial_tail": _make_linear(
        agent_types=["compliant", "compliant", "compliant", "compliant", "adversarial"],
        trust_levels=[0.90, 0.90, 0.90, 0.20],
        name="adversarial_tail",
        description=(
            "5-agent chain with adversarial agent at tail (trust=0.20). "
            "Expected terminal_trust ≈ 0.9^3*0.20 ≈ 0.146. SIMULATION ONLY."
        ),
    ),
    # ------------------------------------------------------------------
    # degrading_chain
    # Five-agent chain with monotonically decreasing trust per hop.
    # Models an authority cascade that loses fidelity at each delegation.
    # ------------------------------------------------------------------
    "degrading_chain": _make_linear(
        agent_types=["compliant", "degrading", "degrading", "degrading", "degrading"],
        trust_levels=[0.90, 0.80, 0.70, 0.60],
        name="degrading_chain",
        description=(
            "5-agent chain with monotonically decreasing trust per hop: "
            "0.90, 0.80, 0.70, 0.60. Expected terminal_trust ≈ 0.302. SIMULATION ONLY."
        ),
    ),
    # ------------------------------------------------------------------
    # high_trust_long_chain
    # Ten-agent chain with high trust per edge.
    # Tests that high-trust delegations can maintain reasonable terminal trust
    # even over many hops.
    # ------------------------------------------------------------------
    "high_trust_long_chain": _make_linear(
        agent_types=["compliant"] * 10,
        trust_levels=[0.95] * 9,
        name="high_trust_long_chain",
        description=(
            "9 delegation hops, all compliant, trust_level=0.95 per edge. "
            "Expected terminal_trust ≈ 0.95^9 ≈ 0.630. SIMULATION ONLY."
        ),
    ),
    # ------------------------------------------------------------------
    # mixed_strategic
    # Six-agent chain mixing compliant and strategic agents.
    # Strategic agents have moderate-high trust, creating a non-uniform profile.
    # ------------------------------------------------------------------
    "mixed_strategic": _make_linear(
        agent_types=["compliant", "strategic", "compliant", "strategic", "compliant", "compliant"],
        trust_levels=[0.88, 0.75, 0.88, 0.75, 0.88],
        name="mixed_strategic",
        description=(
            "6-agent chain alternating compliant (0.88) and strategic (0.75) edges. "
            "Expected terminal_trust ≈ 0.88^3 * 0.75^2 ≈ 0.406. SIMULATION ONLY."
        ),
    ),
}
