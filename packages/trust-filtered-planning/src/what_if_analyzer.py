# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation
"""
what_if_analyzer.py — "What-if trust level" analyzer for trust-filtered planning.

Evaluates how the set of allowed plan actions and their aggregate cost changes
as the operational trust level varies from 0 to 5.

All action definitions, costs, and trust requirements are synthetic examples
for academic illustration only.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass, field


# ── Data models ────────────────────────────────────────────────────────────────

@dataclass
class PlanAction:
    """A single action in a plan with a minimum required trust level."""

    name: str
    required_trust: int    # 0–5: minimum trust needed to execute this action
    cost: float            # synthetic cost in arbitrary units
    description: str

    def __post_init__(self) -> None:
        if not 0 <= self.required_trust <= 5:
            raise ValueError(f"required_trust must be 0–5, got {self.required_trust}")
        if self.cost < 0:
            raise ValueError(f"cost must be non-negative, got {self.cost}")


@dataclass
class WhatIfResult:
    """Analysis result for a single trust level."""

    trust_level: int
    allowed_actions: list[PlanAction]
    denied_actions: list[PlanAction]
    total_cost: float
    coverage_ratio: float          # fraction of all actions that are allowed


# ── Analyzer ───────────────────────────────────────────────────────────────────

class WhatIfAnalyzer:
    """Analyse how trust level affects plan action availability and aggregate cost.

    Actions are allowed when their required_trust <= the current trust level.
    """

    def __init__(self) -> None:
        self._actions: list[PlanAction] = []

    def add_action(self, action: PlanAction) -> None:
        """Register a plan action for analysis."""
        self._actions.append(action)

    def analyze_at_level(self, trust_level: int) -> WhatIfResult:
        """Compute which actions are allowed and the total accessible cost at a trust level.

        Args:
            trust_level: The trust level to evaluate (0–5).

        Returns:
            A WhatIfResult describing accessible and denied actions.
        """
        if not 0 <= trust_level <= 5:
            raise ValueError(f"trust_level must be 0–5, got {trust_level}")

        allowed = [a for a in self._actions if a.required_trust <= trust_level]
        denied = [a for a in self._actions if a.required_trust > trust_level]
        total_cost = sum(a.cost for a in allowed)
        coverage = len(allowed) / len(self._actions) if self._actions else 0.0

        return WhatIfResult(
            trust_level=trust_level,
            allowed_actions=allowed,
            denied_actions=denied,
            total_cost=total_cost,
            coverage_ratio=coverage,
        )

    def analyze_all_levels(self) -> list[WhatIfResult]:
        """Return WhatIfResult for every trust level from 0 to 5."""
        return [self.analyze_at_level(level) for level in range(6)]

    def optimal_level(self, budget: float) -> int:
        """Find the lowest trust level at which all actions fit within the budget.

        Returns the minimum trust level where total_cost <= budget.
        Returns 5 if no level satisfies the constraint.
        """
        for result in self.analyze_all_levels():
            if result.total_cost <= budget:
                return result.trust_level
        return 5

    def plot_coverage(
        self,
        results: list[WhatIfResult],
        output_path: str = "what_if_coverage.png",
    ) -> None:
        """Render a bar chart showing action coverage and total cost by trust level."""
        levels = [r.trust_level for r in results]
        coverages = [r.coverage_ratio * 100 for r in results]
        costs = [r.total_cost for r in results]

        palette = plt.cm.RdYlGn(np.linspace(0.1, 0.9, len(levels)))  # type: ignore[attr-defined]

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))

        bars = axes[0].bar([f"L{l}" for l in levels], coverages, color=palette)
        axes[0].set_xlabel("Trust Level")
        axes[0].set_ylabel("Plan Coverage (%)")
        axes[0].set_title("Action Coverage by Trust Level")
        axes[0].set_ylim(0, 115)
        for bar, cov in zip(bars, coverages):
            axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                         f"{cov:.0f}%", ha="center", fontsize=9)
        axes[0].grid(axis="y", alpha=0.3)

        axes[1].plot([f"L{l}" for l in levels], costs, "o-", color="#1565C0",
                     linewidth=2, markersize=8)
        axes[1].fill_between(range(len(levels)), costs, alpha=0.15, color="#1565C0")
        axes[1].set_xlabel("Trust Level")
        axes[1].set_ylabel("Total Allowed Cost")
        axes[1].set_title("Cumulative Accessible Cost by Trust Level")
        axes[1].grid(alpha=0.3)

        plt.suptitle("What-If Trust Level Analyzer — Synthetic Simulation", fontsize=13)
        plt.tight_layout()
        plt.savefig(output_path, dpi=120)
        plt.show()

    def generate_report(self) -> str:
        """Produce a formatted comparison table across all trust levels."""
        results = self.analyze_all_levels()
        total_actions = len(self._actions)

        lines: list[str] = [
            "What-If Trust Level Analyzer — Report",
            "=" * 65,
            f"  Total actions in plan: {total_actions}",
            "",
            f"  {'Level':>6}  {'Allowed':>8}  {'Denied':>8}  {'Cost':>12}  {'Coverage':>10}",
            "  " + "-" * 52,
        ]

        for result in results:
            lines.append(
                f"  L{result.trust_level}     {len(result.allowed_actions):>8}  "
                f"{len(result.denied_actions):>8}  {result.total_cost:>12.2f}  "
                f"{result.coverage_ratio:>9.1%}"
            )

        lines.extend(["", "  Actions denied at each level:"])
        for result in results:
            if result.denied_actions:
                denied_names = ", ".join(a.name for a in result.denied_actions)
                lines.append(f"    L{result.trust_level}: {denied_names}")
            else:
                lines.append(f"    L{result.trust_level}: (none — all actions allowed)")

        return "\n".join(lines)


# ── Pre-built example action library ──────────────────────────────────────────

def build_example_actions() -> list[PlanAction]:
    """Return 10 synthetic actions with varying trust requirements and costs."""
    return [
        PlanAction("read_public_docs",    required_trust=0, cost=0.5,  description="Read public documentation"),
        PlanAction("web_search",          required_trust=1, cost=1.0,  description="Perform a web search"),
        PlanAction("draft_response",      required_trust=1, cost=2.0,  description="Draft a user-facing response"),
        PlanAction("read_internal_wiki",  required_trust=2, cost=3.0,  description="Access internal knowledge base"),
        PlanAction("write_to_database",   required_trust=3, cost=8.0,  description="Persist data to database"),
        PlanAction("send_email",          required_trust=3, cost=5.0,  description="Send email on user behalf"),
        PlanAction("call_external_api",   required_trust=3, cost=7.0,  description="Call a third-party API"),
        PlanAction("modify_code_repo",    required_trust=4, cost=15.0, description="Commit code changes"),
        PlanAction("provision_resources", required_trust=4, cost=20.0, description="Provision cloud resources"),
        PlanAction("grant_agent_access",  required_trust=5, cost=25.0, description="Grant access to another agent"),
    ]


# ── Example usage ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    analyzer = WhatIfAnalyzer()
    for action in build_example_actions():
        analyzer.add_action(action)

    print(analyzer.generate_report())
    print()
    optimal = analyzer.optimal_level(budget=20.0)
    print(f"Optimal trust level for budget=20.0: L{optimal}")

    results = analyzer.analyze_all_levels()
    analyzer.plot_coverage(results)
