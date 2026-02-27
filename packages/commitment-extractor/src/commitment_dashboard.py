# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation
"""
commitment_dashboard.py — Commitment tracking dashboard data model.

Provides an in-memory dashboard for tracking agent commitments across
their full lifecycle: creation, fulfilment, violation, expiry, and withdrawal.

All data is synthetic and stored in-memory only. No persistence is provided.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ── Enumerations ───────────────────────────────────────────────────────────────

class CommitmentStatus(str, Enum):
    """Lifecycle states for a tracked agent commitment."""

    ACTIVE = "active"
    FULFILLED = "fulfilled"
    VIOLATED = "violated"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


# ── Data models ────────────────────────────────────────────────────────────────

@dataclass
class Commitment:
    """A single tracked agent commitment."""

    id: str
    agent_id: str
    description: str
    status: CommitmentStatus
    created_at: str              # ISO 8601 datetime string
    deadline: str | None = None  # ISO 8601 date string, or None if open-ended
    evidence: list[str] = field(default_factory=list)

    def is_terminal(self) -> bool:
        """Return True if this commitment has reached a terminal state."""
        return self.status in (
            CommitmentStatus.FULFILLED,
            CommitmentStatus.VIOLATED,
            CommitmentStatus.EXPIRED,
            CommitmentStatus.WITHDRAWN,
        )


@dataclass
class DashboardMetrics:
    """Aggregate metrics for a set of commitments."""

    total: int
    active: int
    fulfilled: int
    violated: int
    expired: int
    fulfillment_rate: float       # fulfilled / (fulfilled + violated), or 1.0 if none resolved

    def to_dict(self) -> dict[str, float | int]:
        return {
            "total": self.total,
            "active": self.active,
            "fulfilled": self.fulfilled,
            "violated": self.violated,
            "expired": self.expired,
            "fulfillment_rate": round(self.fulfillment_rate, 4),
        }


# ── Dashboard ──────────────────────────────────────────────────────────────────

class CommitmentDashboard:
    """In-memory commitment tracking dashboard.

    Stores commitments indexed by ID and provides aggregate metrics
    per agent and across all agents.
    """

    def __init__(self) -> None:
        self._commitments: dict[str, Commitment] = {}

    # ── Mutation methods ───────────────────────────────────────────────────────

    def add_commitment(
        self,
        agent_id: str,
        description: str,
        deadline: str | None = None,
    ) -> str:
        """Create and register a new ACTIVE commitment.

        Args:
            agent_id: Identifier of the agent making the commitment.
            description: Natural-language description of the commitment.
            deadline: Optional ISO 8601 date string for the commitment deadline.

        Returns:
            The unique commitment ID (UUID4 string).
        """
        commitment_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        commitment = Commitment(
            id=commitment_id,
            agent_id=agent_id,
            description=description,
            status=CommitmentStatus.ACTIVE,
            created_at=now,
            deadline=deadline,
        )
        self._commitments[commitment_id] = commitment
        return commitment_id

    def update_status(
        self,
        commitment_id: str,
        status: CommitmentStatus,
        evidence: list[str] | None = None,
    ) -> None:
        """Update the status of an existing commitment.

        Args:
            commitment_id: The UUID of the commitment to update.
            status: New lifecycle status.
            evidence: Optional list of evidence strings to append.

        Raises:
            KeyError: If no commitment with the given ID exists.
            ValueError: If the commitment is already in a terminal state.
        """
        if commitment_id not in self._commitments:
            raise KeyError(f"Commitment '{commitment_id}' not found.")

        commitment = self._commitments[commitment_id]
        if commitment.is_terminal():
            raise ValueError(
                f"Commitment '{commitment_id}' is already in terminal state "
                f"'{commitment.status.value}' and cannot be updated."
            )

        commitment.status = status
        if evidence:
            commitment.evidence.extend(evidence)

    # ── Query methods ──────────────────────────────────────────────────────────

    def _commitments_for(self, agent_id: str) -> list[Commitment]:
        return [c for c in self._commitments.values() if c.agent_id == agent_id]

    def _compute_metrics(self, commitments: list[Commitment]) -> DashboardMetrics:
        total = len(commitments)
        active = sum(1 for c in commitments if c.status == CommitmentStatus.ACTIVE)
        fulfilled = sum(1 for c in commitments if c.status == CommitmentStatus.FULFILLED)
        violated = sum(1 for c in commitments if c.status == CommitmentStatus.VIOLATED)
        expired = sum(1 for c in commitments if c.status == CommitmentStatus.EXPIRED)
        resolved = fulfilled + violated
        rate = fulfilled / resolved if resolved > 0 else 1.0
        return DashboardMetrics(
            total=total,
            active=active,
            fulfilled=fulfilled,
            violated=violated,
            expired=expired,
            fulfillment_rate=rate,
        )

    def metrics_for(self, agent_id: str) -> DashboardMetrics:
        """Return aggregate metrics for a single agent's commitments."""
        return self._compute_metrics(self._commitments_for(agent_id))

    def overall_metrics(self) -> DashboardMetrics:
        """Return aggregate metrics across all agents."""
        return self._compute_metrics(list(self._commitments.values()))

    def agents_by_reliability(self) -> list[tuple[str, float]]:
        """Return agents sorted descending by their commitment fulfilment rate.

        Returns:
            List of (agent_id, fulfillment_rate) tuples, best first.
        """
        agent_ids = {c.agent_id for c in self._commitments.values()}
        rated = [
            (agent_id, self.metrics_for(agent_id).fulfillment_rate)
            for agent_id in agent_ids
        ]
        return sorted(rated, key=lambda pair: pair[1], reverse=True)

    def export_json(self) -> str:
        """Serialise the full dashboard state to a JSON string.

        Includes all commitments and overall metrics.
        """
        payload: dict[str, object] = {
            "exported_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "overall_metrics": self.overall_metrics().to_dict(),
            "commitments": [
                {
                    "id": c.id,
                    "agent_id": c.agent_id,
                    "description": c.description,
                    "status": c.status.value,
                    "created_at": c.created_at,
                    "deadline": c.deadline,
                    "evidence": c.evidence,
                }
                for c in self._commitments.values()
            ],
        }
        return json.dumps(payload, indent=2)


# ── Example usage ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    dashboard = CommitmentDashboard()

    # Synthetic commitments for three agents
    agents = {
        "agent_alpha": [
            ("Will respond within allocated time window", "2026-03-01"),
            ("Will not exceed allocated resource budget", None),
            ("Will log all external API calls", None),
        ],
        "agent_beta": [
            ("Will request approval for high-impact actions", "2026-02-28"),
            ("Will preserve data minimisation constraints", None),
        ],
        "agent_gamma": [
            ("Will escalate unresolved ambiguities", "2026-03-15"),
            ("Will cite sources for factual claims", None),
            ("Will retain data only within task scope", None),
        ],
    }

    commitment_ids: dict[str, list[str]] = {}
    for agent_id, commitments in agents.items():
        commitment_ids[agent_id] = []
        for description, deadline in commitments:
            cid = dashboard.add_commitment(agent_id, description, deadline)
            commitment_ids[agent_id].append(cid)

    # Simulate lifecycle updates
    dashboard.update_status(commitment_ids["agent_alpha"][0], CommitmentStatus.FULFILLED,
                            evidence=["response_time=2.3s"])
    dashboard.update_status(commitment_ids["agent_alpha"][1], CommitmentStatus.VIOLATED,
                            evidence=["budget_usage=0.97"])
    dashboard.update_status(commitment_ids["agent_beta"][0], CommitmentStatus.FULFILLED,
                            evidence=["approval_obtained=true"])
    dashboard.update_status(commitment_ids["agent_gamma"][0], CommitmentStatus.EXPIRED)

    # Report
    print("Commitment Dashboard — Overall Metrics")
    print("=" * 44)
    overall = dashboard.overall_metrics()
    print(f"  Total:          {overall.total}")
    print(f"  Active:         {overall.active}")
    print(f"  Fulfilled:      {overall.fulfilled}")
    print(f"  Violated:       {overall.violated}")
    print(f"  Expired:        {overall.expired}")
    print(f"  Fulfilment rate: {overall.fulfillment_rate:.1%}")

    print("\nAgents by reliability:")
    for agent_id, rate in dashboard.agents_by_reliability():
        print(f"  {agent_id:<16} {rate:.1%}")

    print("\nJSON export (truncated):")
    print(dashboard.export_json()[:400] + "\n  ...")
