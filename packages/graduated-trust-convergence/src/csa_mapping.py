# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation
"""
csa_mapping.py — CSA Agentic AI Trust Framework mapping for graduated trust levels.

Maps Cloud Security Alliance (CSA) agentic AI trust categories to the
graduated-trust-convergence framework's discrete trust levels (0–5).

All mappings are simplified approximations for academic simulation purposes.
They do not constitute legal or compliance advice.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from textwrap import dedent


class CSACategory(str, Enum):
    """Top-level CSA Agentic AI Trust Framework categories."""

    IDENTITY = "identity"
    AUTHORIZATION = "authorization"
    DATA_PROTECTION = "data_protection"
    MONITORING = "monitoring"
    INCIDENT_RESPONSE = "incident_response"


@dataclass
class CSATrustMapping:
    """A single CSA control mapped to a graduated trust level."""

    csa_category: CSACategory
    trust_level: int                    # 0–5: level at which this control is satisfied
    description: str
    controls: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0 <= self.trust_level <= 5:
            raise ValueError(f"trust_level must be 0–5, got {self.trust_level}")


# ── Built-in mapping library ───────────────────────────────────────────────────
# 19 mappings spanning all 5 CSA categories across trust levels 0–5.
_BUILT_IN_MAPPINGS: list[CSATrustMapping] = [

    # ── IDENTITY ────────────────────────────────────────────────────────────────
    CSATrustMapping(
        csa_category=CSACategory.IDENTITY,
        trust_level=1,
        description="Basic agent identity assertion — agent presents a stable identifier.",
        controls=["IAM-01: Agent identifier registration", "IAM-02: Session token issuance"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.IDENTITY,
        trust_level=2,
        description="Verified agent identity — identifier is attested by an orchestrator.",
        controls=["IAM-03: Orchestrator attestation", "IAM-04: Identity binding to task scope"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.IDENTITY,
        trust_level=3,
        description="Continuous identity verification — identity re-verified per task boundary.",
        controls=["IAM-05: Per-task identity refresh", "IAM-06: Revocation list consultation"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.IDENTITY,
        trust_level=4,
        description="Cryptographic identity assurance — agent signs all actions with key pair.",
        controls=["IAM-07: Action signing with agent key", "IAM-08: Key rotation policy"],
    ),

    # ── AUTHORIZATION ───────────────────────────────────────────────────────────
    CSATrustMapping(
        csa_category=CSACategory.AUTHORIZATION,
        trust_level=0,
        description="No authorisation — agent operates in fully sandboxed read-only mode.",
        controls=["AZ-00: Sandbox isolation", "AZ-01: Read-only filesystem scope"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.AUTHORIZATION,
        trust_level=1,
        description="Minimal authorisation — agent may query pre-approved public data sources.",
        controls=["AZ-02: Allowlist-based data access", "AZ-03: Explicit scope declaration"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.AUTHORIZATION,
        trust_level=2,
        description="Task-scoped authorisation — permissions bound to declared task objectives.",
        controls=["AZ-04: Task-scoped capability tokens", "AZ-05: Capability expiry enforcement"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.AUTHORIZATION,
        trust_level=3,
        description="Delegated authorisation — agent may sub-delegate within granted scope.",
        controls=["AZ-06: Sub-delegation controls", "AZ-07: Delegation chain length limit"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.AUTHORIZATION,
        trust_level=5,
        description="Full orchestrator authorisation — agent acts as trusted orchestrator.",
        controls=["AZ-08: Orchestrator role assignment", "AZ-09: Cross-system policy enforcement"],
    ),

    # ── DATA PROTECTION ─────────────────────────────────────────────────────────
    CSATrustMapping(
        csa_category=CSACategory.DATA_PROTECTION,
        trust_level=1,
        description="Data minimisation — agent requests only data fields required for task.",
        controls=["DP-01: Field-level access filtering", "DP-02: PII tagging required"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.DATA_PROTECTION,
        trust_level=2,
        description="Retention controls — agent subject to defined data retention windows.",
        controls=["DP-03: Retention policy binding", "DP-04: Erasure-on-completion default"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.DATA_PROTECTION,
        trust_level=3,
        description="Encryption in transit — all agent data exchanges are TLS-encrypted.",
        controls=["DP-05: TLS 1.3+ enforcement", "DP-06: Certificate pinning for APIs"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.DATA_PROTECTION,
        trust_level=4,
        description="Encryption at rest — agent-generated artefacts stored encrypted.",
        controls=["DP-07: AES-256 storage encryption", "DP-08: Key management policy"],
    ),

    # ── MONITORING ──────────────────────────────────────────────────────────────
    CSATrustMapping(
        csa_category=CSACategory.MONITORING,
        trust_level=1,
        description="Action logging — all agent tool calls logged to an append-only store.",
        controls=["MON-01: Append-only audit log", "MON-02: Log completeness validation"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.MONITORING,
        trust_level=2,
        description="Anomaly flagging — unusual action patterns trigger human review queue.",
        controls=["MON-03: Threshold-based flagging", "MON-04: Human review workflow"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.MONITORING,
        trust_level=3,
        description="Real-time monitoring — monitoring pipeline operates in-band with agent.",
        controls=["MON-05: In-band monitoring hooks", "MON-06: SLA for alert latency"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.MONITORING,
        trust_level=4,
        description="Continuous compliance monitoring — regulatory constraints checked per action.",
        controls=["MON-07: Per-action compliance gate", "MON-08: Regulatory rule engine"],
    ),

    # ── INCIDENT RESPONSE ───────────────────────────────────────────────────────
    CSATrustMapping(
        csa_category=CSACategory.INCIDENT_RESPONSE,
        trust_level=2,
        description="Kill-switch capability — orchestrator can halt agent mid-task.",
        controls=["IR-01: Graceful task termination", "IR-02: State preservation on halt"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.INCIDENT_RESPONSE,
        trust_level=3,
        description="Incident notification — security team notified of policy violations.",
        controls=["IR-03: Violation notification channel", "IR-04: Escalation time window"],
    ),
    CSATrustMapping(
        csa_category=CSACategory.INCIDENT_RESPONSE,
        trust_level=4,
        description="Forensic audit trail — full replay capability for post-incident review.",
        controls=["IR-05: Action replay capability", "IR-06: Evidence preservation policy"],
    ),
]


class CSAComplianceChecker:
    """Check CSA Agentic Trust Framework compliance for graduated trust levels.

    Uses a fixed set of pre-built CSA control mappings. Each mapping specifies
    the minimum trust level at which a CSA control is considered satisfied.
    """

    def __init__(self, mappings: list[CSATrustMapping] | None = None) -> None:
        """Initialise with the built-in mappings or a custom list."""
        self._mappings: list[CSATrustMapping] = mappings if mappings is not None else _BUILT_IN_MAPPINGS

    def map_trust_level(self, level: int) -> list[CSATrustMapping]:
        """Return all CSA controls satisfied at or below the given trust level.

        A control is satisfied at level `l` if the mapping's trust_level <= l.
        """
        if not 0 <= level <= 5:
            raise ValueError(f"trust_level must be 0–5, got {level}")
        return [m for m in self._mappings if m.trust_level <= level]

    def gaps_at_level(self, level: int) -> list[CSATrustMapping]:
        """Return all CSA controls not yet satisfied at the given trust level.

        A control is unsatisfied if the mapping's trust_level > level.
        """
        if not 0 <= level <= 5:
            raise ValueError(f"trust_level must be 0–5, got {level}")
        return [m for m in self._mappings if m.trust_level > level]

    def generate_report(self, levels: list[int]) -> str:
        """Generate a formatted compliance gap report for multiple trust levels.

        Returns a plain-text report suitable for printing or inclusion in docs.
        """
        lines: list[str] = [
            "CSA Agentic Trust Framework — Compliance Gap Report",
            "=" * 56,
            "NOTE: Simplified simulation mappings — not legal/compliance advice.",
            "",
        ]

        for level in sorted(set(levels)):
            satisfied = self.map_trust_level(level)
            gaps = self.gaps_at_level(level)
            lines.append(f"Trust Level {level}")
            lines.append(f"  Satisfied controls : {len(satisfied)}/{len(self._mappings)}")
            lines.append(f"  Outstanding gaps   : {len(gaps)}")

            if gaps:
                lines.append("  Gap details:")
                for gap in gaps:
                    lines.append(f"    [{gap.csa_category.value.upper()}] L{gap.trust_level} — {gap.description}")
            else:
                lines.append("  All controls satisfied at this level.")
            lines.append("")

        return "\n".join(lines)


# ── Example usage ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    checker = CSAComplianceChecker()
    report = checker.generate_report(levels=[0, 2, 3, 5])
    print(report)
