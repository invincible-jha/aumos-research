# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation

# @title Protocol Composition Verifier — Quick Start
# Run this cell-by-cell in Google Colab to explore the simulation.

# ── Cell 1: Install ────────────────────────────────────────────────────────────
# !pip install aumos-protocol-composition-verifier matplotlib numpy

# ── Cell 2: Imports ────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from dataclasses import dataclass
from typing import NamedTuple

np.random.seed(42)


# ── Cell 3: Minimal inline simulation ─────────────────────────────────────────

@dataclass
class ProtocolEffect:
    name: str
    trust_delta: float       # change applied to trust property
    budget_delta: float      # change applied to budget property
    consent_delta: float     # change applied to consent scope


class StepRecord(NamedTuple):
    step_index: int
    protocol: str
    trust_value: float
    budget_value: float
    consent_value: float


def simulate_composition(
    protocols: list[ProtocolEffect],
    initial_trust: float = 5.0,
    initial_budget: float = 1.0,
    initial_consent: float = 1.0,
) -> list[StepRecord]:
    """Simulate protocol composition and record property values at each step.

    All property values should be non-increasing for monotonicity to hold.
    """
    records: list[StepRecord] = []
    trust = initial_trust
    budget = initial_budget
    consent = initial_consent

    for step_index, protocol in enumerate(protocols):
        trust = max(0.0, trust + protocol.trust_delta)
        budget = max(0.0, budget + protocol.budget_delta)
        consent = max(0.0, consent + protocol.consent_delta)
        records.append(StepRecord(step_index, protocol.name, trust, budget, consent))

    return records


def verify_monotonicity(records: list[StepRecord], property_name: str) -> tuple[bool, int | None]:
    """Verify a property is non-increasing across composition steps.

    Returns (is_monotone, first_violation_step_index | None).
    """
    values = [getattr(r, property_name) for r in records]
    for idx in range(1, len(values)):
        if values[idx] > values[idx - 1] + 1e-9:
            return False, idx
    return True, None


# ── Cell 4: Run the simulation ─────────────────────────────────────────────────
example_protocols = [
    ProtocolEffect("scope_restriction", trust_delta=-0.5, budget_delta=-0.1, consent_delta=-0.2),
    ProtocolEffect("budget_cap",        trust_delta=0.0,  budget_delta=-0.2, consent_delta=0.0),
    ProtocolEffect("consent_narrowing", trust_delta=-0.3, budget_delta=0.0,  consent_delta=-0.15),
    ProtocolEffect("audit_tighten",     trust_delta=-0.2, budget_delta=-0.05, consent_delta=-0.05),
    ProtocolEffect("final_approval",    trust_delta=-0.1, budget_delta=-0.1, consent_delta=-0.1),
]

records = simulate_composition(example_protocols)

print("Protocol Composition Verifier — Monotonicity Check")
print("=" * 50)
for prop in ("trust_value", "budget_value", "consent_value"):
    is_mono, violation = verify_monotonicity(records, prop)
    status = "PASS" if is_mono else f"FAIL at step {violation}"
    print(f"  {prop:<18}: {status}")

print("\nComposition trace:")
for r in records:
    print(f"  Step {r.step_index}: {r.protocol:<20} trust={r.trust_value:.2f}  "
          f"budget={r.budget_value:.2f}  consent={r.consent_value:.2f}")


# ── Cell 5: Visualisation ──────────────────────────────────────────────────────
steps = [r.step_index for r in records]
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(steps, [r.trust_value for r in records], "o-", color="#1565C0", label="Trust (0–5)")
ax.plot(steps, [r.budget_value * 5 for r in records], "s--", color="#2E7D32", label="Budget × 5")
ax.plot(steps, [r.consent_value * 5 for r in records], "^:", color="#C62828", label="Consent × 5")
ax.set_xticks(steps)
ax.set_xticklabels([r.protocol for r in records], rotation=20, ha="right", fontsize=8)
ax.set_ylabel("Property Value")
ax.set_title("Protocol Composition — Monotonic Property Verification")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("protocol_composition.png", dpi=120)
plt.show()
print("Figure saved: protocol_composition.png")


# ── Next Steps ─────────────────────────────────────────────────────────────────
# - See packages/protocol-composition-verifier/README.md for full API documentation
# - Explore monotonic_proof.py for formal proof simulation with ProofResult objects
# - Run the full test suite: pytest packages/protocol-composition-verifier/
