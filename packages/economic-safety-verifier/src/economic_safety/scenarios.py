# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
scenarios.py — Predefined spending scenarios for Paper 22 experiments.

SIMULATION ONLY. All scenario parameters are chosen to reproduce the paper's
figures from SYNTHETIC data. None of these configurations reflect real agent
spending behaviour or production AEAP budget policies.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from economic_safety.model import SpendingAgent


@dataclass(frozen=True)
class ScenarioConfig:
    """Configuration for a predefined experiment scenario.

    SIMULATION ONLY. Bundles envelope parameters and agent definitions
    for a single experiment run.

    Attributes:
        name: Short identifier matching the SCENARIOS dict key.
        description: Human-readable description of what this scenario tests.
        category: Envelope category label.
        envelope_limit: Budget limit for the envelope.
        agents: List of synthetic spending agents.
        timesteps: Number of simulation timesteps to run.
        seed: RNG seed for deterministic reproduction.
        commitment_amounts: Optional list of commitment amounts to create
            before running the spending simulation.
        commitment_duration: Timesteps for which each commitment remains
            active before expiry (used when commitment_amounts is set).
    """

    name: str
    description: str
    category: str
    envelope_limit: float
    agents: list[SpendingAgent]
    timesteps: int = 100
    seed: int = 42
    commitment_amounts: list[float] = field(default_factory=list)
    commitment_duration: int = 50


SCENARIOS: dict[str, ScenarioConfig] = {
    # ------------------------------------------------------------------
    # safe_single_agent
    # One well-behaved agent spending ~60% of budget per period.
    # Expected outcome: no_overspend holds, balance stays positive.
    # ------------------------------------------------------------------
    "safe_single_agent": ScenarioConfig(
        name="safe_single_agent",
        description=(
            "Single agent with spending_rate=6.0 and variance=1.0 against a "
            "limit=1000 envelope over 100 timesteps. Expected total spend ~600, "
            "well within budget. SIMULATION ONLY."
        ),
        category="compute",
        envelope_limit=1000.0,
        agents=[
            SpendingAgent(
                agent_id="agent-alpha",
                spending_rate=6.0,
                variance=1.0,
                category="compute",
            )
        ],
        timesteps=100,
        seed=42,
    ),
    # ------------------------------------------------------------------
    # near_limit
    # Single agent spending near 95% of the budget limit.
    # Demonstrates the verifier operating close to the boundary.
    # ------------------------------------------------------------------
    "near_limit": ScenarioConfig(
        name="near_limit",
        description=(
            "Single agent with spending_rate=9.5 and variance=0.2 against a "
            "limit=1000 envelope over 100 timesteps. Expected spend ~950, "
            "near the limit but within it. SIMULATION ONLY."
        ),
        category="storage",
        envelope_limit=1000.0,
        agents=[
            SpendingAgent(
                agent_id="agent-beta",
                spending_rate=9.5,
                variance=0.2,
                category="storage",
            )
        ],
        timesteps=100,
        seed=42,
    ),
    # ------------------------------------------------------------------
    # multi_agent_safe
    # Three agents sharing a budget; combined rate << limit.
    # Tests that concurrent agents can coexist safely within budget.
    # ------------------------------------------------------------------
    "multi_agent_safe": ScenarioConfig(
        name="multi_agent_safe",
        description=(
            "Three agents (rates 2.0, 1.5, 1.0) sharing a compute envelope "
            "with limit=1000 over 100 timesteps. Combined rate ~4.5/step, "
            "total ~450, well within budget. SIMULATION ONLY."
        ),
        category="compute",
        envelope_limit=1000.0,
        agents=[
            SpendingAgent(
                agent_id="agent-c1",
                spending_rate=2.0,
                variance=0.3,
                category="compute",
            ),
            SpendingAgent(
                agent_id="agent-c2",
                spending_rate=1.5,
                variance=0.3,
                category="compute",
            ),
            SpendingAgent(
                agent_id="agent-c3",
                spending_rate=1.0,
                variance=0.2,
                category="compute",
            ),
        ],
        timesteps=100,
        seed=42,
    ),
    # ------------------------------------------------------------------
    # multi_agent_unsafe
    # Three agents whose combined rate exceeds the limit without enforcement.
    # Demonstrates the necessity of enforcement: without it these agents
    # would overspend; with enforcement the verifier blocks overspend.
    # ------------------------------------------------------------------
    "multi_agent_unsafe": ScenarioConfig(
        name="multi_agent_unsafe",
        description=(
            "Three agents (rates 4.0, 4.0, 4.0) sharing a compute envelope "
            "with limit=1000 over 100 timesteps. Combined rate 12/step means "
            "~1200 total attempted; enforcement blocks overspend. SIMULATION ONLY."
        ),
        category="compute",
        envelope_limit=1000.0,
        agents=[
            SpendingAgent(
                agent_id="agent-d1",
                spending_rate=4.0,
                variance=0.5,
                category="compute",
            ),
            SpendingAgent(
                agent_id="agent-d2",
                spending_rate=4.0,
                variance=0.5,
                category="compute",
            ),
            SpendingAgent(
                agent_id="agent-d3",
                spending_rate=4.0,
                variance=0.5,
                category="compute",
            ),
        ],
        timesteps=100,
        seed=42,
    ),
    # ------------------------------------------------------------------
    # commitment_heavy
    # Large upfront commitments that consume most of the available balance,
    # leaving little room for actual spending transactions.
    # ------------------------------------------------------------------
    "commitment_heavy": ScenarioConfig(
        name="commitment_heavy",
        description=(
            "Single agent against a limit=1000 envelope with 700 units "
            "pre-committed. Available balance is 300; agent spending_rate=2.5 "
            "so ~250 actual spend expected. Tests commitment_bounded property. "
            "SIMULATION ONLY."
        ),
        category="network",
        envelope_limit=1000.0,
        agents=[
            SpendingAgent(
                agent_id="agent-e1",
                spending_rate=2.5,
                variance=0.4,
                category="network",
            )
        ],
        timesteps=100,
        seed=42,
        commitment_amounts=[350.0, 350.0],
        commitment_duration=100,
    ),
    # ------------------------------------------------------------------
    # burst_spending
    # An agent that alternates between low and high spend per step,
    # simulating bursty workloads. Tests that no_overspend holds under
    # irregular spending patterns with enforcement active.
    # ------------------------------------------------------------------
    "burst_spending": ScenarioConfig(
        name="burst_spending",
        description=(
            "Single agent with high variance (spending_rate=5.0, variance=4.0) "
            "against a limit=1000 envelope over 100 timesteps. Bursty draws; "
            "enforcement clamps overspend. SIMULATION ONLY."
        ),
        category="compute",
        envelope_limit=1000.0,
        agents=[
            SpendingAgent(
                agent_id="agent-f1",
                spending_rate=5.0,
                variance=4.0,
                category="compute",
            )
        ],
        timesteps=100,
        seed=42,
    ),
}
