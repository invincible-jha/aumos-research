# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation
"""
monotonic_proof.py — Monotonic restriction formal proof simulation.

Simulates and verifies that protocol compositions satisfy monotonic
non-increasing property constraints across trust, budget, consent, and
audit dimensions.

All proof verification is a simplified algorithmic simulation and does
not constitute a formal mathematical proof.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── Enumerations ───────────────────────────────────────────────────────────────

class MonotonicProperty(str, Enum):
    """Properties that must be monotonically non-increasing under composition."""

    TRUST_NON_INCREASING = "trust_non_increasing"
    BUDGET_NON_INCREASING = "budget_non_increasing"
    CONSENT_NON_RELAXING = "consent_non_relaxing"
    AUDIT_NON_REDUCIBLE = "audit_non_reducible"


# ── Data models ────────────────────────────────────────────────────────────────

@dataclass
class CompositionStep:
    """A single protocol application step in a composition sequence."""

    step_index: int
    protocol_applied: str
    property_values: dict[str, float] = field(default_factory=dict)

    def value_for(self, prop: MonotonicProperty) -> float:
        """Return the numeric value of a property at this step."""
        return self.property_values.get(prop.value, 0.0)


@dataclass
class ProofResult:
    """Result of verifying a monotonic property across a composition."""

    property: MonotonicProperty
    verified: bool
    violation_step: int | None
    explanation: str


# ── Proof engine ───────────────────────────────────────────────────────────────

class MonotonicProofEngine:
    """Verify monotonic non-increasing properties across protocol compositions.

    Usage:
        engine = MonotonicProofEngine()
        engine.add_step("scope_restrict", {
            "trust_non_increasing": 4.0,
            "budget_non_increasing": 0.8,
            "consent_non_relaxing": 0.9,
            "audit_non_reducible": 1.0,
        })
        results = engine.verify_all()
    """

    def __init__(self) -> None:
        self._steps: list[CompositionStep] = []

    def add_step(self, protocol: str, effects: dict[str, float]) -> None:
        """Add a protocol application step to the composition.

        Args:
            protocol: Human-readable name of the protocol being applied.
            effects: Mapping from MonotonicProperty.value string to numeric value.
                     All values must be non-negative.
        """
        step_index = len(self._steps)
        step = CompositionStep(
            step_index=step_index,
            protocol_applied=protocol,
            property_values=dict(effects),
        )
        self._steps.append(step)

    def verify_monotonicity(self, prop: MonotonicProperty) -> ProofResult:
        """Check whether a single property is monotonically non-increasing.

        A property is monotonically non-increasing if for every consecutive pair
        of steps (i, i+1): value[i+1] <= value[i].

        Returns a ProofResult indicating whether the property holds and, if not,
        at which step the first violation occurs.
        """
        if len(self._steps) < 2:
            return ProofResult(
                property=prop,
                verified=True,
                violation_step=None,
                explanation="Fewer than 2 steps — monotonicity is vacuously satisfied.",
            )

        for idx in range(1, len(self._steps)):
            prev_value = self._steps[idx - 1].value_for(prop)
            curr_value = self._steps[idx].value_for(prop)
            if curr_value > prev_value + 1e-9:
                return ProofResult(
                    property=prop,
                    verified=False,
                    violation_step=idx,
                    explanation=(
                        f"Monotonicity violated at step {idx} "
                        f"(protocol: '{self._steps[idx].protocol_applied}'): "
                        f"value increased from {prev_value:.4f} to {curr_value:.4f}."
                    ),
                )

        return ProofResult(
            property=prop,
            verified=True,
            violation_step=None,
            explanation=(
                f"Property '{prop.value}' is non-increasing across all "
                f"{len(self._steps)} composition steps."
            ),
        )

    def verify_all(self) -> dict[MonotonicProperty, ProofResult]:
        """Verify all four monotonic properties across the composition.

        Returns a mapping from each MonotonicProperty to its ProofResult.
        """
        return {prop: self.verify_monotonicity(prop) for prop in MonotonicProperty}

    def generate_proof_trace(self) -> str:
        """Produce a human-readable proof trace across all steps and properties.

        Includes per-step property values and a summary of verification outcomes.
        """
        if not self._steps:
            return "No composition steps recorded. Call add_step() first."

        lines: list[str] = [
            "Monotonic Proof Trace",
            "=" * 60,
            f"Total steps: {len(self._steps)}",
            "",
            "Step-by-step property values:",
            f"  {'Step':<6} {'Protocol':<22} {'Trust':>8} {'Budget':>8} {'Consent':>8} {'Audit':>8}",
            "  " + "-" * 60,
        ]

        for step in self._steps:
            trust = step.value_for(MonotonicProperty.TRUST_NON_INCREASING)
            budget = step.value_for(MonotonicProperty.BUDGET_NON_INCREASING)
            consent = step.value_for(MonotonicProperty.CONSENT_NON_RELAXING)
            audit = step.value_for(MonotonicProperty.AUDIT_NON_REDUCIBLE)
            lines.append(
                f"  {step.step_index:<6} {step.protocol_applied:<22} "
                f"{trust:>8.3f} {budget:>8.3f} {consent:>8.3f} {audit:>8.3f}"
            )

        lines.extend(["", "Verification results:", "-" * 40])
        for prop, result in self.verify_all().items():
            status = "VERIFIED" if result.verified else "VIOLATION"
            lines.append(f"  [{status}] {prop.value}")
            lines.append(f"           {result.explanation}")

        return "\n".join(lines)


# ── Example: 5-step composition maintaining all properties ────────────────────

def build_example_composition() -> MonotonicProofEngine:
    """Construct a 5-step composition that satisfies all monotonic properties.

    All values are synthetic and chosen to demonstrate the verification logic.
    """
    engine = MonotonicProofEngine()

    engine.add_step("initial_grant", {
        MonotonicProperty.TRUST_NON_INCREASING.value: 5.0,
        MonotonicProperty.BUDGET_NON_INCREASING.value: 1.0,
        MonotonicProperty.CONSENT_NON_RELAXING.value: 1.0,
        MonotonicProperty.AUDIT_NON_REDUCIBLE.value: 1.0,
    })
    engine.add_step("scope_restriction", {
        MonotonicProperty.TRUST_NON_INCREASING.value: 4.0,
        MonotonicProperty.BUDGET_NON_INCREASING.value: 0.85,
        MonotonicProperty.CONSENT_NON_RELAXING.value: 0.90,
        MonotonicProperty.AUDIT_NON_REDUCIBLE.value: 1.0,
    })
    engine.add_step("budget_cap", {
        MonotonicProperty.TRUST_NON_INCREASING.value: 4.0,
        MonotonicProperty.BUDGET_NON_INCREASING.value: 0.65,
        MonotonicProperty.CONSENT_NON_RELAXING.value: 0.90,
        MonotonicProperty.AUDIT_NON_REDUCIBLE.value: 1.0,
    })
    engine.add_step("consent_narrowing", {
        MonotonicProperty.TRUST_NON_INCREASING.value: 3.0,
        MonotonicProperty.BUDGET_NON_INCREASING.value: 0.65,
        MonotonicProperty.CONSENT_NON_RELAXING.value: 0.70,
        MonotonicProperty.AUDIT_NON_REDUCIBLE.value: 1.0,
    })
    engine.add_step("audit_tighten", {
        MonotonicProperty.TRUST_NON_INCREASING.value: 3.0,
        MonotonicProperty.BUDGET_NON_INCREASING.value: 0.50,
        MonotonicProperty.CONSENT_NON_RELAXING.value: 0.70,
        MonotonicProperty.AUDIT_NON_REDUCIBLE.value: 0.95,
    })

    return engine


# ── Example usage ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = build_example_composition()
    print(engine.generate_proof_trace())
