# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation

# @title Economic Safety Verifier — Quick Start
# Run this cell-by-cell in Google Colab to explore the simulation.

# ── Cell 1: Install ────────────────────────────────────────────────────────────
# !pip install aumos-economic-safety-verifier matplotlib numpy

# ── Cell 2: Imports ────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import NamedTuple

np.random.seed(42)


# ── Cell 3: Minimal inline simulation ─────────────────────────────────────────

@dataclass
class SpendingRecord:
    step: int
    amount: float
    governed: bool
    cumulative: float


class SafetyVerdict(NamedTuple):
    governed_total: float
    ungoverned_total: float
    savings: float
    governed_violations: int
    ungoverned_violations: int


def simulate_economic_spending(
    num_steps: int,
    governed: bool,
    daily_ceiling: float = 100.0,
) -> list[SpendingRecord]:
    """Simulate economic spending with or without governance guardrails.

    Governed mode enforces a daily ceiling; ungoverned mode does not.
    All amounts are synthetic and for illustration only.
    """
    records: list[SpendingRecord] = []
    cumulative = 0.0
    for step in range(num_steps):
        raw_spend = float(np.random.exponential(scale=60.0))
        if governed:
            spend = min(raw_spend, daily_ceiling)
        else:
            spend = raw_spend
        cumulative += spend
        records.append(SpendingRecord(step, spend, governed, cumulative))
    return records


def compute_verdict(
    governed_records: list[SpendingRecord],
    ungoverned_records: list[SpendingRecord],
    ceiling: float = 100.0,
) -> SafetyVerdict:
    """Compare governed vs ungoverned outcomes."""
    gov_total = governed_records[-1].cumulative
    ungov_total = ungoverned_records[-1].cumulative
    gov_viol = sum(1 for r in governed_records if r.amount > ceiling)
    ungov_viol = sum(1 for r in ungoverned_records if r.amount > ceiling)
    return SafetyVerdict(gov_total, ungov_total, ungov_total - gov_total, gov_viol, ungov_viol)


# ── Cell 4: Run the simulation ─────────────────────────────────────────────────
NUM_STEPS = 60

governed_records = simulate_economic_spending(NUM_STEPS, governed=True)
ungoverned_records = simulate_economic_spending(NUM_STEPS, governed=False)
verdict = compute_verdict(governed_records, ungoverned_records)

print("Economic Safety Verifier — Spending Simulation")
print("=" * 50)
print(f"  Governed total:        ${verdict.governed_total:,.2f}")
print(f"  Ungoverned total:      ${verdict.ungoverned_total:,.2f}")
print(f"  Savings from gov.:     ${verdict.savings:,.2f}")
print(f"  Governed violations:   {verdict.governed_violations}")
print(f"  Ungoverned violations: {verdict.ungoverned_violations}")


# ── Cell 5: Visualisation ──────────────────────────────────────────────────────
steps = list(range(NUM_STEPS))
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].plot(steps, [r.cumulative for r in governed_records], color="#2E7D32", label="Governed")
axes[0].plot(steps, [r.cumulative for r in ungoverned_records], color="#C62828", linestyle="--",
             label="Ungoverned")
axes[0].set_xlabel("Day")
axes[0].set_ylabel("Cumulative Spend ($)")
axes[0].set_title("Cumulative Spending Trajectories")
axes[0].legend()
axes[0].grid(alpha=0.3)

bar_labels = ["Governed", "Ungoverned"]
bar_vals = [verdict.governed_total, verdict.ungoverned_total]
bar_colors = ["#2E7D32", "#C62828"]
axes[1].bar(bar_labels, bar_vals, color=bar_colors, width=0.5)
axes[1].set_ylabel("Total Spend ($)")
axes[1].set_title(f"Total Spend Comparison\nSavings: ${verdict.savings:,.0f}")
axes[1].grid(axis="y", alpha=0.3)

plt.suptitle("Economic Safety Verifier — Synthetic Simulation", fontsize=13)
plt.tight_layout()
plt.savefig("economic_safety_verifier.png", dpi=120)
plt.show()
print("Figure saved: economic_safety_verifier.png")


# ── Next Steps ─────────────────────────────────────────────────────────────────
# - See packages/economic-safety-verifier/README.md for full API documentation
# - Explore cost_ungoverned.py for Monte Carlo cost-of-ungoverned-AI simulations
# - Run the full test suite: pytest packages/economic-safety-verifier/
