# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation
"""
sla_enforcement.py — Agent SLA enforcement from extracted commitments.

Provides data models and an enforcer for checking agent operational metrics
against Service Level Agreement rules extracted from agent commitments.

All thresholds and metrics in this module are synthetic examples for
academic simulation. They do not represent production SLA requirements.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


# ── Data models ────────────────────────────────────────────────────────────────

@dataclass
class SLARule:
    """A single measurable SLA constraint."""

    metric: str                  # e.g. "response_time_seconds"
    threshold: float             # upper bound that must not be exceeded
    unit: str                    # e.g. "seconds", "ratio", "fraction"
    violation_action: str        # e.g. "alert", "suspend", "log"

    def is_violated(self, actual_value: float) -> bool:
        """Return True if the actual value exceeds the rule's threshold."""
        return actual_value > self.threshold


@dataclass
class AgentSLA:
    """An SLA document binding an agent to a set of measurable rules."""

    agent_id: str
    rules: list[SLARule]
    effective_from: str          # ISO 8601 date string
    effective_until: str         # ISO 8601 date string


@dataclass
class SLAViolation:
    """A recorded SLA violation event."""

    rule: SLARule
    actual_value: float
    timestamp: str               # ISO 8601 datetime string
    severity: str                # "low" | "medium" | "high" | "critical"

    @classmethod
    def compute_severity(cls, rule: SLARule, actual_value: float) -> str:
        """Derive violation severity from how far actual_value exceeds threshold.

        Returns one of: "low", "medium", "high", "critical".
        Severity bands are illustrative and synthetic.
        """
        ratio = actual_value / rule.threshold if rule.threshold > 0 else float("inf")
        if ratio < 1.2:
            return "low"
        elif ratio < 2.0:
            return "medium"
        elif ratio < 5.0:
            return "high"
        else:
            return "critical"


# ── Enforcer ───────────────────────────────────────────────────────────────────

class SLAEnforcer:
    """Check agent metrics against registered SLAs and track violations.

    Maintains an in-memory store of SLAs and violations.
    Thread-safety is not guaranteed; use a single-threaded simulation context.
    """

    def __init__(self) -> None:
        self._slas: dict[str, AgentSLA] = {}
        self._violations: dict[str, list[SLAViolation]] = {}
        self._check_counts: dict[str, int] = {}

    def register_sla(self, sla: AgentSLA) -> None:
        """Register an SLA for an agent, replacing any existing SLA."""
        self._slas[sla.agent_id] = sla
        if sla.agent_id not in self._violations:
            self._violations[sla.agent_id] = []
        self._check_counts.setdefault(sla.agent_id, 0)

    def check_metric(
        self,
        agent_id: str,
        metric: str,
        value: float,
    ) -> SLAViolation | None:
        """Check a single metric value against the agent's SLA rules.

        Increments the total check count. Returns a SLAViolation if the
        relevant rule is breached, otherwise returns None.
        """
        if agent_id not in self._slas:
            return None

        sla = self._slas[agent_id]
        self._check_counts[agent_id] = self._check_counts.get(agent_id, 0) + 1

        matching_rules = [r for r in sla.rules if r.metric == metric]
        if not matching_rules:
            return None

        rule = matching_rules[0]
        if not rule.is_violated(value):
            return None

        timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        severity = SLAViolation.compute_severity(rule, value)
        violation = SLAViolation(
            rule=rule,
            actual_value=value,
            timestamp=timestamp,
            severity=severity,
        )
        self._violations[agent_id].append(violation)
        return violation

    def violations_for(self, agent_id: str) -> list[SLAViolation]:
        """Return all recorded violations for the given agent."""
        return list(self._violations.get(agent_id, []))

    def compliance_rate(self, agent_id: str) -> float:
        """Compute the fraction of metric checks that did not produce a violation.

        Returns a value in [0.0, 1.0]. Returns 1.0 if no checks have been made.
        """
        total_checks = self._check_counts.get(agent_id, 0)
        if total_checks == 0:
            return 1.0
        violation_count = len(self._violations.get(agent_id, []))
        return max(0.0, 1.0 - violation_count / total_checks)

    def generate_report(self, agent_id: str) -> str:
        """Produce a formatted SLA compliance report for an agent."""
        if agent_id not in self._slas:
            return f"No SLA registered for agent '{agent_id}'."

        sla = self._slas[agent_id]
        violations = self.violations_for(agent_id)
        total_checks = self._check_counts.get(agent_id, 0)
        rate = self.compliance_rate(agent_id)

        lines: list[str] = [
            f"SLA Compliance Report — {agent_id}",
            "=" * 50,
            f"  SLA effective : {sla.effective_from} to {sla.effective_until}",
            f"  Rules defined : {len(sla.rules)}",
            f"  Total checks  : {total_checks}",
            f"  Violations    : {len(violations)}",
            f"  Compliance    : {rate:.1%}",
            "",
            "  SLA Rules:",
        ]
        for rule in sla.rules:
            lines.append(
                f"    {rule.metric:<30} <= {rule.threshold} {rule.unit:<12} action={rule.violation_action}"
            )

        if violations:
            lines.extend(["", "  Violations:"])
            for violation in violations:
                lines.append(
                    f"    [{violation.severity.upper():<8}] {violation.rule.metric:<30} "
                    f"actual={violation.actual_value:.4f}  at {violation.timestamp}"
                )
        else:
            lines.append("\n  No violations recorded.")

        return "\n".join(lines)


# ── Example SLA ────────────────────────────────────────────────────────────────

def build_example_sla(agent_id: str = "agent_alpha") -> AgentSLA:
    """Construct a synthetic example SLA for demonstration.

    Thresholds are illustrative synthetic values, not production requirements.
    """
    return AgentSLA(
        agent_id=agent_id,
        rules=[
            SLARule(
                metric="response_time_seconds",
                threshold=5.0,
                unit="seconds",
                violation_action="alert",
            ),
            SLARule(
                metric="error_rate",
                threshold=0.05,
                unit="ratio",
                violation_action="log",
            ),
            SLARule(
                metric="budget_usage_fraction",
                threshold=0.90,
                unit="fraction",
                violation_action="suspend",
            ),
        ],
        effective_from="2026-01-01",
        effective_until="2026-12-31",
    )


# ── Example usage ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import random
    random.seed(42)

    enforcer = SLAEnforcer()
    sla = build_example_sla("agent_alpha")
    enforcer.register_sla(sla)

    # Simulate a series of synthetic metric observations
    synthetic_observations: list[tuple[str, float]] = [
        ("response_time_seconds", 3.1),
        ("response_time_seconds", 6.8),     # violation
        ("error_rate", 0.02),
        ("error_rate", 0.12),               # violation
        ("budget_usage_fraction", 0.75),
        ("budget_usage_fraction", 0.95),    # violation
        ("response_time_seconds", 4.5),
        ("error_rate", 0.01),
    ]

    for metric, value in synthetic_observations:
        violation = enforcer.check_metric("agent_alpha", metric, value)
        if violation:
            print(f"  VIOLATION: {metric}={value}  severity={violation.severity}")

    print()
    print(enforcer.generate_report("agent_alpha"))
