# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation

# @title Commitment Extractor — Quick Start
# Run this cell-by-cell in Google Colab to explore the simulation.

# ── Cell 1: Install ────────────────────────────────────────────────────────────
# !pip install aumos-commitment-extractor matplotlib numpy

# ── Cell 2: Imports ────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import NamedTuple
from enum import Enum

np.random.seed(42)


# ── Cell 3: Minimal inline simulation ─────────────────────────────────────────

class CommitmentStatus(str, Enum):
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    VIOLATED = "violated"
    EXPIRED = "expired"


@dataclass
class ExtractedCommitment:
    commitment_id: str
    agent_id: str
    description: str
    status: CommitmentStatus


class ExtractionResult(NamedTuple):
    total_extracted: int
    fulfilled: int
    violated: int
    active: int
    fulfillment_rate: float


# Synthetic commitment patterns for illustration
SYNTHETIC_TEMPLATES: list[str] = [
    "Agent will respond within time window",
    "Agent will not exceed allocated resource budget",
    "Agent will log all external API calls",
    "Agent will request user approval for high-impact actions",
    "Agent will preserve data minimisation constraints",
    "Agent will escalate unresolved ambiguities",
    "Agent will not retain session data beyond task scope",
    "Agent will cite sources for all factual claims",
]


def extract_commitments(
    agent_id: str,
    num_commitments: int,
) -> list[ExtractedCommitment]:
    """Simulate commitment extraction from a synthetic agent conversation log.

    Returns a list of extracted commitments with randomly assigned statuses.
    All data is synthetic.
    """
    statuses = np.random.choice(
        [CommitmentStatus.FULFILLED, CommitmentStatus.VIOLATED,
         CommitmentStatus.ACTIVE, CommitmentStatus.EXPIRED],
        size=num_commitments,
        p=[0.55, 0.15, 0.20, 0.10],
    )
    templates = np.random.choice(SYNTHETIC_TEMPLATES, size=num_commitments, replace=True)
    return [
        ExtractedCommitment(
            commitment_id=f"c_{i:03d}",
            agent_id=agent_id,
            description=str(templates[i]),
            status=CommitmentStatus(statuses[i]),
        )
        for i in range(num_commitments)
    ]


def summarise(commitments: list[ExtractedCommitment]) -> ExtractionResult:
    total = len(commitments)
    fulfilled = sum(1 for c in commitments if c.status == CommitmentStatus.FULFILLED)
    violated = sum(1 for c in commitments if c.status == CommitmentStatus.VIOLATED)
    active = sum(1 for c in commitments if c.status == CommitmentStatus.ACTIVE)
    rate = fulfilled / total if total > 0 else 0.0
    return ExtractionResult(total, fulfilled, violated, active, rate)


# ── Cell 4: Run the simulation ─────────────────────────────────────────────────
agents = ["agent_alpha", "agent_beta", "agent_gamma"]
num_per_agent = [12, 8, 15]

all_summaries: dict[str, ExtractionResult] = {}
for agent_id, count in zip(agents, num_per_agent):
    commitments = extract_commitments(agent_id, count)
    summary = summarise(commitments)
    all_summaries[agent_id] = summary

print("Commitment Extractor — Extraction Summary")
print("=" * 52)
print(f"  {'Agent':<16} {'Total':>6} {'Fulfilled':>10} {'Violated':>9} {'Rate':>7}")
print("  " + "-" * 50)
for agent_id, summary in all_summaries.items():
    print(f"  {agent_id:<16} {summary.total_extracted:>6} {summary.fulfilled:>10} "
          f"{summary.violated:>9} {summary.fulfillment_rate:>6.1%}")


# ── Cell 5: Visualisation ──────────────────────────────────────────────────────
x = np.arange(len(agents))
width = 0.25
fulfilled_vals = [all_summaries[a].fulfilled for a in agents]
violated_vals = [all_summaries[a].violated for a in agents]
active_vals = [all_summaries[a].active for a in agents]

fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(x - width, fulfilled_vals, width, label="Fulfilled", color="#43A047")
ax.bar(x,          violated_vals, width, label="Violated",  color="#E53935")
ax.bar(x + width,  active_vals,   width, label="Active",    color="#1E88E5")
ax.set_xticks(x)
ax.set_xticklabels(agents, fontsize=10)
ax.set_ylabel("Commitment Count")
ax.set_title("Commitment Extractor — Status by Agent\n(Synthetic data)")
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("commitment_extractor.png", dpi=120)
plt.show()
print("Figure saved: commitment_extractor.png")


# ── Next Steps ─────────────────────────────────────────────────────────────────
# - See packages/commitment-extractor/README.md for full API documentation
# - Explore sla_enforcement.py for agent SLA enforcement from extracted commitments
# - Explore commitment_dashboard.py for a full dashboard data model
# - Run the full test suite: pytest packages/commitment-extractor/
