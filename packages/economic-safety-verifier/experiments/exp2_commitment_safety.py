# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp2_commitment_safety.py — Figure 2: Commitment + spent bounded by limit.

SIMULATION ONLY. Demonstrates that when commitments are created before spending,
the sum of committed + spent never exceeds the envelope limit, and that the
waterfall of reservations correctly reduces available balance.

Reproduces Figure 2 from Paper 22. All data is SYNTHETIC. seed=42.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from economic_safety.model import (
    Commitment,
    EconomicModel,
    SimulationConfig,
    SpendingAgent,
)
from economic_safety.verifier import EconomicSafetyVerifier
from economic_safety.visualization import (
    plot_budget_trajectory,
    plot_commitment_waterfall,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "figures")


def run_commitment_scenario(seed: int = 42) -> dict:  # type: ignore[type-arg]
    """Run the commitment-heavy scenario and verify commitment_bounded.

    SIMULATION ONLY. Two large commitments are created against the envelope
    before any spending occurs. The verifier checks that committed + spent
    never exceeds the limit. All data is SYNTHETIC.

    Args:
        seed: RNG seed for reproducibility.

    Returns:
        Dictionary of scenario metrics and serialisable timeline data.
    """
    config = SimulationConfig(seed=seed, enforce_limits=True)
    model = EconomicModel(config)
    envelope_limit = 1000.0
    model.create_envelope("network", limit=envelope_limit, period=100)

    # Create two pre-commitments consuming 700 total
    commitment_a = Commitment(
        commitment_id="commit-a1",
        category="network",
        amount=350.0,
        agent_id="system",
        created_at=0,
        expires_at=100,
    )
    commitment_b = Commitment(
        commitment_id="commit-b1",
        category="network",
        amount=350.0,
        agent_id="system",
        created_at=0,
        expires_at=100,
    )

    accepted_a = model.create_commitment(commitment_a)
    accepted_b = model.create_commitment(commitment_b)

    total_committed = (
        commitment_a.amount * int(accepted_a) +
        commitment_b.amount * int(accepted_b)
    )

    # Agent spending against reduced available balance (~300 units)
    agents = [
        SpendingAgent(
            agent_id="agent-e1",
            spending_rate=2.5,
            variance=0.4,
            category="network",
        )
    ]

    result = model.simulate_spending(agents, timesteps=100)

    verifier = EconomicSafetyVerifier()
    commitment_result = verifier.verify_commitment_bounded(
        list(model.envelopes.values()), model.commitments
    )
    no_overspend_result = verifier.verify_no_overspend(
        list(model.envelopes.values()), model.transactions
    )
    non_negative_result = verifier.verify_non_negative_balance(
        list(model.envelopes.values())
    )

    envelope_snapshot = model.envelopes["network"]

    return {
        "seed": seed,
        "envelope_limit": envelope_limit,
        "commitment_amounts": [commitment_a.amount, commitment_b.amount],
        "commitments_accepted": [accepted_a, accepted_b],
        "total_committed": total_committed,
        "total_spent": result.total_spent,
        "available_after_simulation": envelope_snapshot.available,
        "balance_timeline": result.balance_timeline,
        "commitment_bounded_holds": commitment_result.holds,
        "no_overspend_holds": no_overspend_result.holds,
        "non_negative_balance_holds": non_negative_result.holds,
        "commitment_bounded_detail": commitment_result.detail,
        "no_overspend_detail": no_overspend_result.detail,
    }


def run_commitment_violation_demo(seed: int = 42) -> dict:  # type: ignore[type-arg]
    """Attempt to create commitments that exceed the envelope limit.

    SIMULATION ONLY. Creates commitments totalling more than the limit to
    show that enforcement correctly rejects the final commitment. All data
    is SYNTHETIC.

    Args:
        seed: RNG seed for reproducibility.

    Returns:
        Dictionary describing which commitments were accepted and rejected.
    """
    config = SimulationConfig(seed=seed, enforce_limits=True)
    model = EconomicModel(config)
    model.create_envelope("network", limit=1000.0, period=100)

    # Attempt commitments totalling 1100 > limit of 1000
    commitments = [
        Commitment("c-x1", "network", 500.0, "system", 0, 100),
        Commitment("c-x2", "network", 400.0, "system", 0, 100),
        Commitment("c-x3", "network", 200.0, "system", 0, 100),  # should fail
    ]

    outcomes = []
    for commitment in commitments:
        accepted = model.create_commitment(commitment)
        outcomes.append({"commitment_id": commitment.commitment_id,
                         "amount": commitment.amount,
                         "accepted": accepted})

    verifier = EconomicSafetyVerifier()
    result = verifier.verify_commitment_bounded(
        list(model.envelopes.values()), model.commitments
    )

    return {
        "commitment_outcomes": outcomes,
        "commitment_bounded_holds": result.holds,
        "detail": result.detail,
    }


def main() -> None:
    """Run exp2 and save results to fig2_data.json and figures/fig2_*.png."""
    print("=" * 60)
    print("Experiment 2: Commitment Safety")
    print("SIMULATION ONLY — all data is synthetic")
    print("=" * 60)

    scenario = run_commitment_scenario(seed=42)
    violation_demo = run_commitment_violation_demo(seed=42)

    print(f"\n[Scenario]  committed={scenario['total_committed']:.1f}, "
          f"spent={scenario['total_spent']:.2f}, "
          f"available={scenario['available_after_simulation']:.2f}")
    print(f"            commitment_bounded={scenario['commitment_bounded_holds']}")
    print(f"            no_overspend={scenario['no_overspend_holds']}")
    print(f"            non_negative={scenario['non_negative_balance_holds']}")
    print(f"            {scenario['commitment_bounded_detail']}")

    print(f"\n[Violation] outcomes={violation_demo['commitment_outcomes']}")
    print(f"            bounded_holds={violation_demo['commitment_bounded_holds']}")

    fig2_data = {
        "experiment": "exp2_commitment_safety",
        "paper": "Paper 22",
        "note": "SIMULATION ONLY — synthetic data, seed=42",
        "scenario": scenario,
        "violation_demo": violation_demo,
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, "fig2_data.json")
    with open(out_path, "w") as fh:
        json.dump(fig2_data, fh, indent=2)
    print(f"\nSaved: {out_path}")

    # Figures
    os.makedirs(FIGURES_DIR, exist_ok=True)

    # Rebuild model for figures
    config = SimulationConfig(seed=42, enforce_limits=True)
    model = EconomicModel(config)
    model.create_envelope("network", limit=1000.0, period=100)
    model.create_commitment(
        Commitment("commit-a1", "network", 350.0, "system", 0, 100)
    )
    model.create_commitment(
        Commitment("commit-b1", "network", 350.0, "system", 0, 100)
    )
    agents = [SpendingAgent("agent-e1", 2.5, 0.4, "network")]
    result = model.simulate_spending(agents, timesteps=100)

    fig_path = os.path.join(FIGURES_DIR, "fig2_budget_trajectory.png")
    plot_budget_trajectory(result, save_path=fig_path)
    print(f"Saved: {fig_path}")

    waterfall_path = os.path.join(FIGURES_DIR, "fig2_commitment_waterfall.png")
    plot_commitment_waterfall(
        model.envelopes["network"],
        model.commitments,
        save_path=waterfall_path,
    )
    print(f"Saved: {waterfall_path}")
    print("\nExperiment 2 complete.")


if __name__ == "__main__":
    main()
