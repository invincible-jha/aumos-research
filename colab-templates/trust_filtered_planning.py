# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation

# @title Trust-Filtered Planning — Quick Start
# Run this cell-by-cell in Google Colab to explore the simulation.

# ── Cell 1: Install ────────────────────────────────────────────────────────────
# !pip install aumos-trust-filtered-planning matplotlib numpy

# ── Cell 2: Imports ────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import NamedTuple

np.random.seed(42)


# ── Cell 3: Minimal inline simulation ─────────────────────────────────────────

@dataclass
class PlanAction:
    name: str
    required_trust: int    # 0–5
    cost: float
    description: str


class FilterResult(NamedTuple):
    trust_level: int
    allowed_count: int
    denied_count: int
    total_allowed_cost: float
    coverage_ratio: float


def filter_plan(
    actions: list[PlanAction],
    trust_level: int,
) -> FilterResult:
    """Filter a plan's actions based on the current trust level.

    Actions with required_trust > trust_level are denied.
    """
    allowed = [a for a in actions if a.required_trust <= trust_level]
    denied = [a for a in actions if a.required_trust > trust_level]
    total_cost = sum(a.cost for a in allowed)
    coverage = len(allowed) / len(actions) if actions else 0.0
    return FilterResult(trust_level, len(allowed), len(denied), total_cost, coverage)


# Synthetic action library
SYNTHETIC_ACTIONS: list[PlanAction] = [
    PlanAction("read_public_docs",      required_trust=0, cost=0.5,  description="Read public documentation"),
    PlanAction("web_search",            required_trust=1, cost=1.0,  description="Perform web search"),
    PlanAction("draft_response",        required_trust=1, cost=2.0,  description="Draft a user-facing response"),
    PlanAction("read_internal_wiki",    required_trust=2, cost=3.0,  description="Access internal knowledge base"),
    PlanAction("write_to_database",     required_trust=3, cost=8.0,  description="Persist data to database"),
    PlanAction("send_email",            required_trust=3, cost=5.0,  description="Send email on user's behalf"),
    PlanAction("call_external_api",     required_trust=3, cost=7.0,  description="Call a third-party API"),
    PlanAction("modify_code_repo",      required_trust=4, cost=15.0, description="Commit code changes"),
    PlanAction("provision_resources",   required_trust=4, cost=20.0, description="Provision cloud resources"),
    PlanAction("grant_user_access",     required_trust=5, cost=25.0, description="Grant access to another agent"),
]


# ── Cell 4: Run the simulation ─────────────────────────────────────────────────
results: list[FilterResult] = [filter_plan(SYNTHETIC_ACTIONS, level) for level in range(6)]

print("Trust-Filtered Planning — Coverage by Trust Level")
print("=" * 55)
print(f"  {'Level':>6} {'Allowed':>8} {'Denied':>8} {'Cost ($)':>10} {'Coverage':>10}")
print("  " + "-" * 48)
for result in results:
    print(f"  L{result.trust_level}     {result.allowed_count:>7} {result.denied_count:>8} "
          f"  {result.total_allowed_cost:>8.1f}   {result.coverage_ratio:>8.1%}")


# ── Cell 5: Visualisation ──────────────────────────────────────────────────────
levels = [r.trust_level for r in results]
coverages = [r.coverage_ratio * 100 for r in results]
costs = [r.total_allowed_cost for r in results]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

bar_colors = plt.cm.RdYlGn(np.linspace(0.1, 0.9, len(levels)))  # type: ignore[attr-defined]
axes[0].bar([f"L{l}" for l in levels], coverages, color=bar_colors)
axes[0].set_xlabel("Trust Level")
axes[0].set_ylabel("Plan Coverage (%)")
axes[0].set_title("Action Coverage by Trust Level")
axes[0].set_ylim(0, 110)
for i, (level, cov) in enumerate(zip(levels, coverages)):
    axes[0].text(i, cov + 2, f"{cov:.0f}%", ha="center", fontsize=9)
axes[0].grid(axis="y", alpha=0.3)

axes[1].plot([f"L{l}" for l in levels], costs, "o-", color="#1565C0", linewidth=2)
axes[1].fill_between(range(len(levels)), costs, alpha=0.15, color="#1565C0")
axes[1].set_xlabel("Trust Level")
axes[1].set_ylabel("Total Allowed Cost ($)")
axes[1].set_title("Cumulative Accessible Cost by Trust Level")
axes[1].grid(alpha=0.3)

plt.suptitle("Trust-Filtered Planning — Synthetic Simulation", fontsize=13)
plt.tight_layout()
plt.savefig("trust_filtered_planning.png", dpi=120)
plt.show()
print("Figure saved: trust_filtered_planning.png")


# ── Next Steps ─────────────────────────────────────────────────────────────────
# - See packages/trust-filtered-planning/README.md for full API documentation
# - Explore what_if_analyzer.py for comprehensive what-if trust level analysis
# - Explore regulatory_constraints.py for EU AI Act / NIST / ISO 42001 constraint modelling
# - Run the full test suite: pytest packages/trust-filtered-planning/
