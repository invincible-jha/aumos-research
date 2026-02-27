# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation
"""
crewai_visualization.py — Trust delegation visualization for multi-agent frameworks.

Provides a graph-based model of agent delegation hierarchies, computing
effective trust levels and rendering Matplotlib or Mermaid diagrams.

Intended as a research companion for the delegation-trust-model package.
Not affiliated with or endorsed by the CrewAI project.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from dataclasses import dataclass, field


# ── Data models ────────────────────────────────────────────────────────────────

@dataclass
class DelegationNode:
    """An agent node in the delegation graph."""

    agent_id: str
    role: str
    trust_level: int              # 0–5 as assigned by the orchestrator
    parent_id: str | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.trust_level <= 5:
            raise ValueError(f"trust_level must be 0–5, got {self.trust_level}")


@dataclass
class DelegationEdge:
    """A directed delegation edge between two agents."""

    from_agent: str
    to_agent: str
    task_description: str
    delegated_trust: int          # effective trust on this edge = min(parent, child)


# ── Trust colour palette (L0=red … L5=blue) ───────────────────────────────────
_TRUST_COLORS: dict[int, str] = {
    0: "#B71C1C",
    1: "#E53935",
    2: "#FB8C00",
    3: "#FDD835",
    4: "#43A047",
    5: "#1565C0",
}


def _trust_color(level: int) -> str:
    return _TRUST_COLORS.get(max(0, min(5, level)), "#9E9E9E")


# ── Graph class ────────────────────────────────────────────────────────────────

class DelegationGraph:
    """A directed graph representing agent delegation with trust propagation.

    Trust propagates downward using a monotonic non-increasing rule:
    the effective trust at any node is the minimum of all trust values
    from the root to that node.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, DelegationNode] = {}
        self._edges: list[DelegationEdge] = []
        self._effective_trust_cache: dict[str, int] = {}

    def add_agent(self, agent_id: str, role: str, trust_level: int) -> None:
        """Register an agent in the delegation graph."""
        node = DelegationNode(agent_id=agent_id, role=role, trust_level=trust_level)
        self._nodes[agent_id] = node
        self._effective_trust_cache.clear()

    def add_delegation(self, from_id: str, to_id: str, task: str) -> None:
        """Add a delegation edge from one agent to another.

        Sets to_id's parent_id to from_id (the delegating agent).
        Effective trust = min(parent effective trust, child assigned trust).
        """
        if from_id not in self._nodes:
            raise KeyError(f"Agent '{from_id}' not registered. Call add_agent() first.")
        if to_id not in self._nodes:
            raise KeyError(f"Agent '{to_id}' not registered. Call add_agent() first.")

        self._nodes[to_id].parent_id = from_id
        delegated = min(self.effective_trust(from_id), self._nodes[to_id].trust_level)
        edge = DelegationEdge(
            from_agent=from_id,
            to_agent=to_id,
            task_description=task,
            delegated_trust=delegated,
        )
        # Replace any existing edge between the same pair
        self._edges = [e for e in self._edges if not (e.from_agent == from_id and e.to_agent == to_id)]
        self._edges.append(edge)
        self._effective_trust_cache.clear()

    def effective_trust(self, agent_id: str) -> int:
        """Compute effective trust for an agent by walking the delegation chain.

        Effective trust = min(trust values from root to this node).
        Cached after first computation.
        """
        if agent_id in self._effective_trust_cache:
            return self._effective_trust_cache[agent_id]

        if agent_id not in self._nodes:
            raise KeyError(f"Agent '{agent_id}' not found in graph.")

        node = self._nodes[agent_id]
        if node.parent_id is None:
            result = node.trust_level
        else:
            result = min(self.effective_trust(node.parent_id), node.trust_level)

        self._effective_trust_cache[agent_id] = result
        return result

    def visualize(self, output_path: str = "delegation_graph.png") -> None:
        """Render the delegation graph as a Matplotlib figure.

        Nodes are coloured by effective trust level.
        Edges show delegated trust values.
        """
        agent_ids = list(self._nodes.keys())
        num_agents = len(agent_ids)
        if num_agents == 0:
            return

        # Compute simple layered layout based on delegation depth
        depth_map: dict[str, int] = {}

        def compute_depth(aid: str) -> int:
            if aid in depth_map:
                return depth_map[aid]
            parent = self._nodes[aid].parent_id
            d = 0 if parent is None else compute_depth(parent) + 1
            depth_map[aid] = d
            return d

        for aid in agent_ids:
            compute_depth(aid)

        max_depth = max(depth_map.values()) if depth_map else 0
        positions: dict[str, tuple[float, float]] = {}
        depth_counts: dict[int, int] = {}
        depth_current: dict[int, int] = {}

        for aid in agent_ids:
            d = depth_map[aid]
            depth_counts[d] = depth_counts.get(d, 0) + 1

        for aid in agent_ids:
            d = depth_map[aid]
            depth_current[d] = depth_current.get(d, 0)
            count = depth_counts[d]
            x = (depth_current[d] - (count - 1) / 2.0) * 2.5
            y = float(-d * 2.0)
            positions[aid] = (x, y)
            depth_current[d] += 1

        fig, ax = plt.subplots(figsize=(max(8, num_agents * 2), max(5, (max_depth + 1) * 2.5)))
        ax.set_aspect("equal")
        ax.axis("off")

        # Draw edges
        for edge in self._edges:
            x0, y0 = positions[edge.from_agent]
            x1, y1 = positions[edge.to_agent]
            ax.annotate(
                "",
                xy=(x1, y1 + 0.45),
                xytext=(x0, y0 - 0.45),
                arrowprops=dict(arrowstyle="->", color="#555555", lw=1.5),
            )
            mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
            ax.text(mid_x + 0.1, mid_y, f"L{edge.delegated_trust}",
                    fontsize=8, color="#333333", ha="left")

        # Draw nodes
        for aid, node in self._nodes.items():
            x, y = positions[aid]
            eff = self.effective_trust(aid)
            color = _trust_color(eff)
            circle = plt.Circle((x, y), 0.42, color=color, zorder=3)
            ax.add_patch(circle)
            ax.text(x, y + 0.06, aid, ha="center", va="center", fontsize=8,
                    fontweight="bold", color="white", zorder=4)
            ax.text(x, y - 0.18, node.role, ha="center", va="center", fontsize=6.5,
                    color="white", zorder=4)
            ax.text(x, y - 0.55, f"eff L{eff}", ha="center", va="center", fontsize=7.5,
                    color="#222222")

        # Legend
        legend_patches = [
            mpatches.Patch(color=_trust_color(level), label=f"Trust L{level}")
            for level in range(6)
        ]
        ax.legend(handles=legend_patches, loc="upper right", fontsize=8, framealpha=0.9)
        ax.set_title("Agent Delegation Graph — Effective Trust (Synthetic Example)", pad=14)

        plt.tight_layout()
        plt.savefig(output_path, dpi=120)
        plt.show()

    def to_mermaid(self) -> str:
        """Export the delegation graph as a Mermaid diagram string.

        Can be pasted into any Mermaid-compatible renderer.
        """
        lines: list[str] = ["graph TD"]
        for node in self._nodes.values():
            eff = self.effective_trust(node.agent_id)
            label = f"{node.agent_id}[{node.role} — L{eff} eff]"
            lines.append(f"  {label}")
        for edge in self._edges:
            lines.append(
                f"  {edge.from_agent} -->|L{edge.delegated_trust}: {edge.task_description}| {edge.to_agent}"
            )
        return "\n".join(lines)


# ── Pre-built example: 4-agent CrewAI-style crew ──────────────────────────────

def build_example_crew() -> DelegationGraph:
    """Build a synthetic 4-agent crew for illustration.

    Topology: Manager (L4) -> Researcher (L3), Manager -> Reviewer (L3),
              Researcher -> Writer (L2).
    """
    graph = DelegationGraph()
    graph.add_agent("manager",    "Manager",    trust_level=4)
    graph.add_agent("researcher", "Researcher", trust_level=3)
    graph.add_agent("writer",     "Writer",     trust_level=2)
    graph.add_agent("reviewer",   "Reviewer",   trust_level=3)

    graph.add_delegation("manager",    "researcher", "conduct literature review")
    graph.add_delegation("researcher", "writer",     "draft findings report")
    graph.add_delegation("manager",    "reviewer",   "quality-check report")

    return graph


# ── Example usage ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    crew = build_example_crew()

    print("Delegation Trust Graph — Effective Trust")
    print("=" * 44)
    for agent_id, node in crew._nodes.items():
        eff = crew.effective_trust(agent_id)
        print(f"  {agent_id:<12} role={node.role:<14} assigned=L{node.trust_level}  effective=L{eff}")

    print("\nMermaid Diagram:")
    print(crew.to_mermaid())

    crew.visualize("delegation_graph_example.png")
