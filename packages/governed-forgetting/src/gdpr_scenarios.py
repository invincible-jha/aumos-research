# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation
"""
gdpr_scenarios.py — GDPR right-to-erasure test scenarios for governed forgetting.

Provides pre-built synthetic scenarios covering Article 17 (right to erasure),
Article 6 (lawfulness of processing), and related GDPR provisions.

All scenarios use synthetic data and simplified regulatory logic.
This module does not provide legal advice.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


# ── Data models ────────────────────────────────────────────────────────────────

@dataclass
class GDPRScenario:
    """A single GDPR right-to-erasure test scenario."""

    name: str
    description: str
    data_categories: list[str]
    retention_days: int
    erasure_required: bool
    legal_basis: str


@dataclass
class ScenarioResult:
    """Outcome of running a forgetting policy against a GDPR scenario."""

    scenario_name: str
    data_retained: list[str]
    data_erased: list[str]
    compliant: bool
    violations: list[str] = field(default_factory=list)


# ── Forgetting policy protocol ─────────────────────────────────────────────────

class ForgettingPolicy(Protocol):
    """Protocol for objects that can decide whether to erase a data category."""

    def should_erase(self, data_category: str, retention_days: int, erasure_requested: bool) -> bool:
        """Return True if this data category should be erased under this policy."""
        ...


@dataclass
class SimpleForgettingPolicy:
    """A simplified forgetting policy for simulation.

    Erases data when:
    - erasure explicitly requested, OR
    - retention window has elapsed (age_days > max_retention_days)
    """

    max_retention_days: int
    honour_requests: bool = True
    simulated_age_days: int = 200      # synthetic age used when evaluating retention

    def should_erase(
        self,
        data_category: str,
        retention_days: int,
        erasure_requested: bool,
    ) -> bool:
        if erasure_requested and self.honour_requests:
            return True
        return self.simulated_age_days > retention_days


# ── Pre-built scenarios ────────────────────────────────────────────────────────

def _build_scenarios() -> list[GDPRScenario]:
    """Construct the 10 pre-built GDPR right-to-erasure scenarios."""
    return [
        GDPRScenario(
            name="explicit_consent_withdrawal",
            description="User withdraws previously granted consent for marketing profiling.",
            data_categories=["marketing_profile", "browsing_history", "email_preferences"],
            retention_days=0,
            erasure_required=True,
            legal_basis="consent",
        ),
        GDPRScenario(
            name="legitimate_interest_expiry",
            description="Retention under legitimate interest has expired after the balancing test.",
            data_categories=["purchase_history", "product_recommendations"],
            retention_days=180,
            erasure_required=True,
            legal_basis="legitimate_interest",
        ),
        GDPRScenario(
            name="child_data_erasure",
            description="Data of a minor collected without valid parental consent.",
            data_categories=["child_profile", "location_data", "device_identifiers"],
            retention_days=0,
            erasure_required=True,
            legal_basis="consent",
        ),
        GDPRScenario(
            name="health_data_request",
            description="Special category health data subject requests erasure after treatment.",
            data_categories=["medical_records", "prescription_history", "appointment_notes"],
            retention_days=3650,          # medical records often held 10 years
            erasure_required=False,       # legal obligation override applies
            legal_basis="legal_obligation",
        ),
        GDPRScenario(
            name="employee_data_post_termination",
            description="Ex-employee requests erasure of HR data after employment ended.",
            data_categories=["performance_reviews", "payroll_records", "disciplinary_notes"],
            retention_days=2555,          # 7-year statutory retention
            erasure_required=False,
            legal_basis="legal_obligation",
        ),
        GDPRScenario(
            name="marketing_data_no_longer_needed",
            description="Marketing campaign data no longer necessary for the original purpose.",
            data_categories=["campaign_responses", "click_data", "ab_test_cohort"],
            retention_days=90,
            erasure_required=True,
            legal_basis="legitimate_interest",
        ),
        GDPRScenario(
            name="contract_completion",
            description="Customer data retained solely for contract performance; contract now complete.",
            data_categories=["order_details", "delivery_address", "payment_reference"],
            retention_days=365,
            erasure_required=True,
            legal_basis="contract",
        ),
        GDPRScenario(
            name="legal_obligation_override",
            description="Subject requests erasure but data must be retained for tax authority.",
            data_categories=["invoice_records", "vat_data", "transaction_logs"],
            retention_days=2555,
            erasure_required=False,
            legal_basis="legal_obligation",
        ),
        GDPRScenario(
            name="cross_border_transfer",
            description="Data transferred under SCCs; subject requests erasure post-transfer.",
            data_categories=["cross_border_user_profile", "consent_records"],
            retention_days=730,
            erasure_required=True,
            legal_basis="consent",
        ),
        GDPRScenario(
            name="automated_decision_making",
            description="Subject objects to automated credit-scoring decision under Art. 22.",
            data_categories=["credit_score_inputs", "decision_rationale", "model_output"],
            retention_days=365,
            erasure_required=True,
            legal_basis="legitimate_interest",
        ),
    ]


BUILT_IN_SCENARIOS: list[GDPRScenario] = _build_scenarios()


# ── Runner ─────────────────────────────────────────────────────────────────────

class GDPRScenarioRunner:
    """Run GDPR right-to-erasure scenarios against a forgetting policy.

    Evaluates whether the policy produces outcomes that are consistent with
    GDPR Article 17 obligations as represented in the scenario metadata.
    All evaluation logic is a simplified simulation — not legal determination.
    """

    def __init__(self, scenarios: list[GDPRScenario] | None = None) -> None:
        self._scenarios: list[GDPRScenario] = scenarios if scenarios is not None else BUILT_IN_SCENARIOS
        self._results: list[ScenarioResult] = []

    def run_scenario(
        self,
        scenario: GDPRScenario,
        forgetting_policy: ForgettingPolicy,
    ) -> ScenarioResult:
        """Simulate a forgetting policy against a single GDPR scenario.

        Checks each data category and compares the policy's erasure decision
        against the scenario's ground-truth erasure_required flag.
        """
        data_retained: list[str] = []
        data_erased: list[str] = []
        violations: list[str] = []

        for category in scenario.data_categories:
            will_erase = forgetting_policy.should_erase(
                data_category=category,
                retention_days=scenario.retention_days,
                erasure_requested=scenario.erasure_required,
            )
            if will_erase:
                data_erased.append(category)
            else:
                data_retained.append(category)

        # Compliance check: erasure_required means ALL categories must be erased
        if scenario.erasure_required and data_retained:
            for retained_cat in data_retained:
                violations.append(
                    f"Data category '{retained_cat}' retained despite erasure requirement "
                    f"(legal_basis: {scenario.legal_basis})"
                )
        # Legal hold check: if erasure NOT required, erasing is a violation
        if not scenario.erasure_required and data_erased:
            for erased_cat in data_erased:
                violations.append(
                    f"Data category '{erased_cat}' erased despite legal retention obligation "
                    f"(legal_basis: {scenario.legal_basis})"
                )

        result = ScenarioResult(
            scenario_name=scenario.name,
            data_retained=data_retained,
            data_erased=data_erased,
            compliant=len(violations) == 0,
            violations=violations,
        )
        return result

    def run_all(self, forgetting_policy: ForgettingPolicy | None = None) -> list[ScenarioResult]:
        """Run all built-in scenarios against the given policy.

        If no policy is supplied, uses SimpleForgettingPolicy with defaults.
        """
        policy: ForgettingPolicy = forgetting_policy if forgetting_policy is not None else SimpleForgettingPolicy(
            max_retention_days=180,
        )
        self._results = [self.run_scenario(scenario, policy) for scenario in self._scenarios]
        return self._results

    def compliance_summary(self) -> str:
        """Return a formatted compliance summary across all run scenarios."""
        if not self._results:
            return "No scenarios have been run yet. Call run_all() first."

        compliant_count = sum(1 for r in self._results if r.compliant)
        total = len(self._results)

        lines: list[str] = [
            "GDPR Right-to-Erasure — Scenario Compliance Summary",
            "=" * 56,
            f"Scenarios run : {total}",
            f"Compliant     : {compliant_count}/{total}",
            f"Non-compliant : {total - compliant_count}/{total}",
            "",
        ]

        for result in self._results:
            status = "PASS" if result.compliant else "FAIL"
            lines.append(f"  [{status}] {result.scenario_name}")
            if result.violations:
                for violation in result.violations:
                    lines.append(f"         Violation: {violation}")

        return "\n".join(lines)


# ── Example usage ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    policy = SimpleForgettingPolicy(max_retention_days=180, honour_requests=True, simulated_age_days=200)
    runner = GDPRScenarioRunner()
    runner.run_all(forgetting_policy=policy)
    print(runner.compliance_summary())
