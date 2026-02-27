# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation

# @title Delegation Trust Model — Quick Start
# Run this cell-by-cell in Google Colab to explore the simulation.

# ── Cell 1: Install ────────────────────────────────────────────────────────────
# !pip install aumos-delegation-trust-model matplotlib numpy

# ── Cell 2: Imports ────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from dataclasses import dataclass, field
from typing import NamedTuple

np.random.seed(42)


# ── Cell 3: Minimal inline simulation ─────────────────────────────────────────

@dataclass
class AgentNode:
    agent_id: str
    role: str
    assigned_trust: int          # 0–5 as assigned by orchestrator
    parent_id: str | None = None


class DelegationEdge(NamedTuple):
    from_agent: str
    to_agent: str
    task_description: str
    effective_trust: int          # min(parent trust, child assigned trust)


def build_delegation_chain(
    agents: list[AgentNode],
) -> dict[str, int]:
    """Compute effective trust for each agent by walking the delegation chain.

    Effective trust = minimum trust encountered from root to node.
    """
    id_to_node = {a.agent_id: a for a in agents}
    effective: dict[str, int] = {}

    def walk(agent_id: str) -> int:
        node = id_to_node[agent_id]
        if node.parent_id is None:
            effective[agent_id] = node.assigned_trust
            return node.assigned_trust
        parent_effective = walk(node.parent_id) if node.parent_id not in effective else effective[node.parent_id]
        computed = min(parent_effective, node.assigned_trust)
        effective[agent_id] = computed
        return computed

    for agent in agents:
        if agent.agent_id not in effective:
            walk(agent.agent_id)

    return effective


# ── Cell 4: Run the simulation ─────────────────────────────────────────────────
# Synthetic 4-agent crew: Manager -> Researcher -> Writer; Manager -> Reviewer
crew = [
    AgentNode("manager",    "Manager",    assigned_trust=4, parent_id=None),
    AgentNode("researcher", "Researcher", assigned_trust=3, parent_id="manager"),
    AgentNode("writer",     "Writer",     assigned_trust=2, parent_id="researcher"),
    AgentNode("reviewer",   "Reviewer",   assigned_trust=3, parent_id="manager"),
]

effective_trust = build_delegation_chain(crew)

print("Delegation Trust Model — Effective Trust Computation")
print("=" * 52)
for agent in crew:
    parent = agent.parent_id or "none"
    eff = effective_trust[agent.agent_id]
    print(f"  {agent.agent_id:<12} assigned={agent.assigned_trust}  "
          f"parent={parent:<12}  effective={eff}")


# ── Cell 5: Visualisation ──────────────────────────────────────────────────────
trust_colors = {0: "#B71C1C", 1: "#E53935", 2: "#FB8C00", 3: "#FDD835", 4: "#43A047", 5: "#1565C0"}
trust_palette = plt.cm.RdYlGn  # type: ignore[attr-defined]

agent_ids = [a.agent_id for a in crew]
assigned = [a.assigned_trust for a in crew]
effective = [effective_trust[a.agent_id] for a in crew]

x = np.arange(len(agent_ids))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 5))
bars1 = ax.bar(x - width / 2, assigned, width, label="Assigned Trust", color="#42A5F5", alpha=0.85)
bars2 = ax.bar(x + width / 2, effective, width, label="Effective Trust", color="#EF5350", alpha=0.85)
ax.set_xticks(x)
ax.set_xticklabels(agent_ids, fontsize=10)
ax.set_ylabel("Trust Level (0–5)")
ax.set_ylim(0, 6)
ax.set_title("Delegation Trust Model — Assigned vs Effective Trust\n(Synthetic crew example)")
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("delegation_trust_model.png", dpi=120)
plt.show()
print("Figure saved: delegation_trust_model.png")


# ── Next Steps ─────────────────────────────────────────────────────────────────
# - See packages/delegation-trust-model/README.md for full API documentation
# - Explore crewai_visualization.py for graph-based delegation visualisation
# - Explore max_depth_calculator.py for safe delegation depth analysis
# - Run the full test suite: pytest packages/delegation-trust-model/
