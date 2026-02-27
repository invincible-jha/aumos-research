# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation

# @title Governed Forgetting — Quick Start
# Run this cell-by-cell in Google Colab to explore the simulation.

# ── Cell 1: Install ────────────────────────────────────────────────────────────
# !pip install aumos-governed-forgetting matplotlib numpy

# ── Cell 2: Imports ────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import NamedTuple

np.random.seed(42)


# ── Cell 3: Minimal inline simulation ─────────────────────────────────────────

@dataclass
class MemoryRecord:
    record_id: str
    data_category: str
    age_days: int
    erasure_requested: bool
    legal_hold: bool


@dataclass
class ForgettingPolicy:
    max_retention_days: int
    honour_erasure_requests: bool
    legal_hold_override: bool


class ForgetResult(NamedTuple):
    record_id: str
    action: str       # "retained" | "erased" | "held"
    reason: str


def apply_forgetting_policy(
    records: list[MemoryRecord],
    policy: ForgettingPolicy,
) -> list[ForgetResult]:
    """Apply a governed forgetting policy to a list of memory records.

    Returns one ForgetResult per record describing the action taken.
    """
    results: list[ForgetResult] = []
    for record in records:
        if record.legal_hold and policy.legal_hold_override:
            results.append(ForgetResult(record.record_id, "held", "legal_hold_active"))
        elif record.erasure_requested and policy.honour_erasure_requests:
            results.append(ForgetResult(record.record_id, "erased", "erasure_request_honoured"))
        elif record.age_days > policy.max_retention_days:
            results.append(ForgetResult(record.record_id, "erased", "retention_limit_exceeded"))
        else:
            results.append(ForgetResult(record.record_id, "retained", "within_policy"))
    return results


# ── Cell 4: Run the simulation ─────────────────────────────────────────────────
synthetic_records = [
    MemoryRecord(f"rec_{i:03d}", np.random.choice(["pii", "health", "marketing", "contract"]),
                 int(np.random.randint(1, 400)), bool(np.random.rand() < 0.3),
                 bool(np.random.rand() < 0.1))
    for i in range(30)
]

policy = ForgettingPolicy(max_retention_days=180, honour_erasure_requests=True, legal_hold_override=True)
results = apply_forgetting_policy(synthetic_records, policy)

action_counts = {"retained": 0, "erased": 0, "held": 0}
for result in results:
    action_counts[result.action] += 1

print("Governed Forgetting Simulation")
print("=" * 40)
print(f"  Total records:   {len(results)}")
print(f"  Retained:        {action_counts['retained']}")
print(f"  Erased:          {action_counts['erased']}")
print(f"  Legal hold:      {action_counts['held']}")
print(f"  Erasure rate:    {action_counts['erased'] / len(results):.1%}")


# ── Cell 5: Visualisation ──────────────────────────────────────────────────────
labels = list(action_counts.keys())
sizes = list(action_counts.values())
palette = ["#4CAF50", "#F44336", "#FF9800"]

fig, axes = plt.subplots(1, 2, figsize=(11, 5))

axes[0].pie(sizes, labels=labels, colors=palette, autopct="%1.0f%%", startangle=90)
axes[0].set_title("Record Disposition Distribution")

ages = [r.age_days for r in synthetic_records]
actions = [res.action for res in results]
color_map = {"retained": "#4CAF50", "erased": "#F44336", "held": "#FF9800"}
dot_colors = [color_map[a] for a in actions]
axes[1].scatter(ages, range(len(ages)), c=dot_colors, alpha=0.7, s=40)
axes[1].axvline(x=policy.max_retention_days, color="navy", linestyle="--", label="Retention limit")
axes[1].set_xlabel("Record Age (days)")
axes[1].set_title("Records by Age and Disposition")
axes[1].legend()

plt.suptitle("Governed Forgetting — Synthetic Simulation", fontsize=13)
plt.tight_layout()
plt.savefig("governed_forgetting.png", dpi=120)
plt.show()
print("Figure saved: governed_forgetting.png")


# ── Next Steps ─────────────────────────────────────────────────────────────────
# - See packages/governed-forgetting/README.md for full API documentation
# - Explore gdpr_scenarios.py for pre-built GDPR right-to-erasure test scenarios
# - Run the full test suite: pytest packages/governed-forgetting/
