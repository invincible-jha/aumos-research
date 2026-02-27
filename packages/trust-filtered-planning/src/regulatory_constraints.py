# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation
"""
regulatory_constraints.py — Regulatory constraint modeling for trust-filtered planning.

Models simplified regulatory requirements from EU AI Act, NIST AI RMF,
ISO 42001, SOC 2, and GDPR Article 22, mapping each requirement to a
minimum trust level that must be satisfied.

All regulatory mappings are intentionally simplified for academic simulation.
They do not constitute legal advice and should not be used for compliance
determination in real systems.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ── Enumerations ───────────────────────────────────────────────────────────────

class Regulation(str, Enum):
    """Supported regulatory frameworks."""

    EU_AI_ACT = "eu_ai_act"
    NIST_AI_RMF = "nist_ai_rmf"
    ISO_42001 = "iso_42001"
    SOC2 = "soc2"
    GDPR_ART22 = "gdpr_art22"


# ── Data models ────────────────────────────────────────────────────────────────

@dataclass
class RegulatoryConstraint:
    """A single regulatory requirement mapped to a minimum trust level."""

    regulation: Regulation
    requirement: str             # short identifier, e.g. "human_oversight"
    min_trust_level: int         # 0–5: trust level needed to satisfy this requirement
    mandatory: bool              # if True, non-compliance blocks deployment
    description: str

    def __post_init__(self) -> None:
        if not 0 <= self.min_trust_level <= 5:
            raise ValueError(f"min_trust_level must be 0–5, got {self.min_trust_level}")


@dataclass
class RegulatoryProfile:
    """A named collection of regulatory constraints."""

    name: str
    constraints: list[RegulatoryConstraint]

    def mandatory_constraints(self) -> list[RegulatoryConstraint]:
        return [c for c in self.constraints if c.mandatory]

    def optional_constraints(self) -> list[RegulatoryConstraint]:
        return [c for c in self.constraints if not c.mandatory]


@dataclass
class ComplianceResult:
    """Result of checking a trust level against a regulatory profile."""

    profile_name: str
    trust_level: int
    satisfied: list[RegulatoryConstraint]
    unsatisfied: list[RegulatoryConstraint]
    mandatory_gaps: list[RegulatoryConstraint]
    compliant: bool              # True only if all mandatory constraints satisfied


# ── Pre-built profiles ────────────────────────────────────────────────────────

def _eu_ai_act_profile() -> RegulatoryProfile:
    """Simplified EU AI Act high-risk AI system requirements."""
    return RegulatoryProfile(
        name="EU AI Act (High-Risk)",
        constraints=[
            RegulatoryConstraint(
                regulation=Regulation.EU_AI_ACT,
                requirement="human_oversight",
                min_trust_level=3,
                mandatory=True,
                description="Art. 14: High-risk AI systems must allow effective human oversight.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.EU_AI_ACT,
                requirement="transparency_logging",
                min_trust_level=2,
                mandatory=True,
                description="Art. 13: Systems must be transparent and logs kept for audit.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.EU_AI_ACT,
                requirement="accuracy_robustness",
                min_trust_level=2,
                mandatory=True,
                description="Art. 15: Systems must meet accuracy, robustness, and cybersecurity standards.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.EU_AI_ACT,
                requirement="data_governance",
                min_trust_level=3,
                mandatory=True,
                description="Art. 10: Training data must meet quality criteria and be governed.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.EU_AI_ACT,
                requirement="conformity_assessment",
                min_trust_level=4,
                mandatory=True,
                description="Art. 43: Conformity assessment before deployment.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.EU_AI_ACT,
                requirement="post_market_monitoring",
                min_trust_level=3,
                mandatory=False,
                description="Art. 72: Post-market monitoring system recommended.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.EU_AI_ACT,
                requirement="incident_reporting",
                min_trust_level=2,
                mandatory=False,
                description="Art. 73: Serious incident reporting to national authority.",
            ),
        ],
    )


def _nist_ai_rmf_profile() -> RegulatoryProfile:
    """Simplified NIST AI Risk Management Framework requirements."""
    return RegulatoryProfile(
        name="NIST AI RMF 1.0",
        constraints=[
            RegulatoryConstraint(
                regulation=Regulation.NIST_AI_RMF,
                requirement="govern_accountability",
                min_trust_level=2,
                mandatory=True,
                description="GOVERN 1.1: Roles and responsibilities for AI risk are established.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.NIST_AI_RMF,
                requirement="map_context",
                min_trust_level=1,
                mandatory=True,
                description="MAP 1.1: Context is established to understand AI risks.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.NIST_AI_RMF,
                requirement="measure_bias",
                min_trust_level=2,
                mandatory=True,
                description="MEASURE 2.5: Bias and fairness metrics are evaluated.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.NIST_AI_RMF,
                requirement="manage_incidents",
                min_trust_level=3,
                mandatory=True,
                description="MANAGE 3.1: Responses to identified AI risks are prepared.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.NIST_AI_RMF,
                requirement="continuous_monitoring",
                min_trust_level=3,
                mandatory=False,
                description="MANAGE 4.1: Deployed systems are monitored for risk emergence.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.NIST_AI_RMF,
                requirement="explainability",
                min_trust_level=2,
                mandatory=False,
                description="MAP 5.1: Explainability approaches are used to characterise decisions.",
            ),
        ],
    )


def _iso_42001_profile() -> RegulatoryProfile:
    """Simplified ISO/IEC 42001 AI management system requirements."""
    return RegulatoryProfile(
        name="ISO/IEC 42001:2023",
        constraints=[
            RegulatoryConstraint(
                regulation=Regulation.ISO_42001,
                requirement="ai_policy",
                min_trust_level=1,
                mandatory=True,
                description="Cl. 5.2: Organisation establishes an AI policy.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.ISO_42001,
                requirement="risk_assessment",
                min_trust_level=2,
                mandatory=True,
                description="Cl. 6.1: AI risk assessment process is defined and applied.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.ISO_42001,
                requirement="impact_assessment",
                min_trust_level=3,
                mandatory=True,
                description="Cl. 8.4: AI impact assessment is conducted prior to deployment.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.ISO_42001,
                requirement="supplier_controls",
                min_trust_level=3,
                mandatory=True,
                description="Cl. 8.6: Controls over AI suppliers and third-party systems.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.ISO_42001,
                requirement="performance_evaluation",
                min_trust_level=2,
                mandatory=True,
                description="Cl. 9.1: Performance evaluation of the AI management system.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.ISO_42001,
                requirement="continual_improvement",
                min_trust_level=2,
                mandatory=False,
                description="Cl. 10.1: Non-conformity corrective actions are tracked.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.ISO_42001,
                requirement="competence",
                min_trust_level=1,
                mandatory=False,
                description="Cl. 7.2: Personnel involved in AI have appropriate competence.",
            ),
            RegulatoryConstraint(
                regulation=Regulation.ISO_42001,
                requirement="documentation_control",
                min_trust_level=1,
                mandatory=True,
                description="Cl. 7.5: AI management system documentation is controlled.",
            ),
        ],
    )


# ── Constraint engine ──────────────────────────────────────────────────────────

class RegulatoryConstraintEngine:
    """Evaluate trust-level compliance against regulatory profiles.

    Bundles pre-built profiles for EU AI Act, NIST AI RMF, and ISO 42001.
    Custom profiles can be passed directly to the check methods.

    NOTE: All regulatory mappings are simplified for simulation.
    This engine does not provide legal or compliance advice.
    """

    def __init__(self) -> None:
        self._built_in_profiles: dict[str, RegulatoryProfile] = {
            "eu_ai_act": _eu_ai_act_profile(),
            "nist_ai_rmf": _nist_ai_rmf_profile(),
            "iso_42001": _iso_42001_profile(),
        }

    @property
    def built_in_profiles(self) -> dict[str, RegulatoryProfile]:
        return dict(self._built_in_profiles)

    def check_compliance(
        self,
        trust_level: int,
        profile: RegulatoryProfile,
    ) -> ComplianceResult:
        """Check whether a trust level satisfies all constraints in a profile.

        Args:
            trust_level: Current operational trust level (0–5).
            profile: The regulatory profile to check against.

        Returns:
            A ComplianceResult detailing satisfied, unsatisfied, and gap constraints.
        """
        if not 0 <= trust_level <= 5:
            raise ValueError(f"trust_level must be 0–5, got {trust_level}")

        satisfied = [c for c in profile.constraints if c.min_trust_level <= trust_level]
        unsatisfied = [c for c in profile.constraints if c.min_trust_level > trust_level]
        mandatory_gaps = [c for c in unsatisfied if c.mandatory]
        compliant = len(mandatory_gaps) == 0

        return ComplianceResult(
            profile_name=profile.name,
            trust_level=trust_level,
            satisfied=satisfied,
            unsatisfied=unsatisfied,
            mandatory_gaps=mandatory_gaps,
            compliant=compliant,
        )

    def minimum_trust_for(self, profile: RegulatoryProfile) -> int:
        """Return the minimum trust level that satisfies all mandatory constraints.

        Scans trust levels 0 to 5 and returns the first level at which all
        mandatory constraints are met.
        """
        for level in range(6):
            result = self.check_compliance(level, profile)
            if result.compliant:
                return level
        return 5

    def gap_analysis(
        self,
        trust_level: int,
        profile: RegulatoryProfile,
    ) -> list[RegulatoryConstraint]:
        """Return constraints not satisfied at the given trust level.

        Includes both mandatory and optional unsatisfied constraints.
        """
        result = self.check_compliance(trust_level, profile)
        return result.unsatisfied

    def compare_profiles(self, profiles: list[RegulatoryProfile]) -> str:
        """Produce a side-by-side comparison table of compliance across trust levels.

        Shows the minimum trust level required and mandatory constraint count
        for each profile.
        """
        lines: list[str] = [
            "Regulatory Profile Comparison",
            "=" * 70,
            "NOTE: Simplified simulation mappings — not legal/compliance advice.",
            "",
            f"  {'Profile':<28} {'Min Trust':>10} {'Mandatory':>10} {'Optional':>10}",
            "  " + "-" * 62,
        ]

        for profile in profiles:
            min_trust = self.minimum_trust_for(profile)
            mandatory_count = len(profile.mandatory_constraints())
            optional_count = len(profile.optional_constraints())
            lines.append(
                f"  {profile.name:<28} {'L' + str(min_trust):>10} "
                f"{mandatory_count:>10} {optional_count:>10}"
            )

        lines.extend(["", "  Compliance status by trust level:"])
        lines.append(
            f"  {'Level':<8} " + "  ".join(f"{p.name[:18]:<20}" for p in profiles)
        )
        lines.append("  " + "-" * (10 + 22 * len(profiles)))

        for level in range(6):
            row = f"  L{level}      "
            for profile in profiles:
                result = self.check_compliance(level, profile)
                status = "PASS" if result.compliant else f"FAIL ({len(result.mandatory_gaps)} gap)"
                row += f"  {status:<20}"
            lines.append(row)

        return "\n".join(lines)


# ── Example usage ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = RegulatoryConstraintEngine()
    profiles = list(engine.built_in_profiles.values())

    print(engine.compare_profiles(profiles))
    print()

    # Detailed check for a single profile at trust level 3
    result = engine.check_compliance(trust_level=3, profile=profiles[0])
    print(f"EU AI Act @ L3 — compliant: {result.compliant}")
    if result.mandatory_gaps:
        print("  Mandatory gaps:")
        for gap in result.mandatory_gaps:
            print(f"    [{gap.requirement}] requires L{gap.min_trust_level}: {gap.description}")
