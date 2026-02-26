# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp1_no_overspend.py — Figure 1: Enforcement prevents overspend.

SIMULATION ONLY. Generates 1000 random transactions against a single envelope
and demonstrates that:
  - With enforcement enabled: the no-overspend property always holds.
  - With enforcement disabled: overspend occurs and the property fails.

This script reproduces Figure 1 from Paper 22. All data is SYNTHETIC.
Results are deterministic with seed=42.
"""

from __future__ import annotations

import json
import os
import sys

# Allow running from the experiments/ directory or the package root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from economic_safety.model import (
    EconomicModel,
    SimulationConfig,
    SpendingAgent,
)
from economic_safety.verifier import EconomicSafetyVerifier
from economic_safety.visualization import plot_budget_trajectory

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "figures")


def run_with_enforcement(seed: int = 42, timesteps: int = 100) -> dict:  # type: ignore[type-arg]
    """Run the single-agent simulation with enforcement enabled.

    SIMULATION ONLY. All data is SYNTHETIC.

    Args:
        seed: RNG seed for reproducibility.
        timesteps: Number of simulation timesteps.

    Returns:
        Dictionary of result metrics and timeline data.
    """
    config = SimulationConfig(seed=seed, enforce_limits=True)
    model = EconomicModel(config)
    model.create_envelope("compute", limit=1000.0, period=timesteps)

    agents = [
        SpendingAgent(
            agent_id="agent-alpha",
            spending_rate=12.0,   # Would overspend without enforcement
            variance=2.0,
            category="compute",
        )
    ]

    result = model.simulate_spending(agents, timesteps=timesteps)

    verifier = EconomicSafetyVerifier()
    verification = verifier.verify_no_overspend(
        list(model.envelopes.values()), model.transactions
    )

    return {
        "mode": "enforced",
        "seed": seed,
        "timesteps": timesteps,
        "envelope_limit": result.envelope_limit,
        "total_spent": result.total_spent,
        "overspend_prevented": result.overspend_prevented,
        "balance_timeline": result.balance_timeline,
        "no_overspend_holds": verification.holds,
        "transactions_checked": verification.transactions_checked,
        "detail": verification.detail,
    }


def run_without_enforcement(seed: int = 42, timesteps: int = 100) -> dict:  # type: ignore[type-arg]
    """Run the single-agent simulation with enforcement disabled.

    SIMULATION ONLY. Demonstrates what happens without arithmetic enforcement —
    spending exceeds the limit. All data is SYNTHETIC.

    Args:
        seed: RNG seed for reproducibility.
        timesteps: Number of simulation timesteps.

    Returns:
        Dictionary of result metrics and timeline data.
    """
    config = SimulationConfig(seed=seed, enforce_limits=False)
    model = EconomicModel(config)
    model.create_envelope("compute", limit=1000.0, period=timesteps)

    agents = [
        SpendingAgent(
            agent_id="agent-alpha",
            spending_rate=12.0,
            variance=2.0,
            category="compute",
        )
    ]

    result = model.simulate_spending(agents, timesteps=timesteps)

    verifier = EconomicSafetyVerifier()
    verification = verifier.verify_no_overspend(
        list(model.envelopes.values()), model.transactions
    )

    return {
        "mode": "unenforced",
        "seed": seed,
        "timesteps": timesteps,
        "envelope_limit": result.envelope_limit,
        "total_spent": result.total_spent,
        "overspend_prevented": 0,
        "balance_timeline": result.balance_timeline,
        "no_overspend_holds": verification.holds,
        "transactions_checked": verification.transactions_checked,
        "detail": verification.detail,
    }


def main() -> None:
    """Run exp1 and save results to fig1_data.json and figures/fig1.png."""
    print("=" * 60)
    print("Experiment 1: No-Overspend Property")
    print("SIMULATION ONLY — all data is synthetic")
    print("=" * 60)

    enforced = run_with_enforcement(seed=42, timesteps=100)
    unenforced = run_without_enforcement(seed=42, timesteps=100)

    print(f"\n[Enforced]   holds={enforced['no_overspend_holds']}, "
          f"spent={enforced['total_spent']:.2f}, "
          f"blocked={enforced['overspend_prevented']}")
    print(f"             {enforced['detail']}")

    print(f"\n[Unenforced] holds={unenforced['no_overspend_holds']}, "
          f"spent={unenforced['total_spent']:.2f}")
    print(f"             {unenforced['detail']}")

    # Combine results for fig1_data.json
    fig1_data = {
        "experiment": "exp1_no_overspend",
        "paper": "Paper 22",
        "note": "SIMULATION ONLY — synthetic data, seed=42",
        "enforced": enforced,
        "unenforced": unenforced,
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, "fig1_data.json")
    with open(out_path, "w") as fh:
        json.dump(fig1_data, fh, indent=2)
    print(f"\nSaved: {out_path}")

    # Generate figure (enforced trajectory)
    from economic_safety.model import EconomicModel, SimulationConfig, SpendingAgent
    config = SimulationConfig(seed=42, enforce_limits=True)
    model = EconomicModel(config)
    model.create_envelope("compute", limit=1000.0, period=100)
    result = model.simulate_spending(
        [SpendingAgent("agent-alpha", 12.0, 2.0, "compute")], timesteps=100
    )

    fig_path = os.path.join(FIGURES_DIR, "fig1_budget_trajectory.png")
    plot_budget_trajectory(result, save_path=fig_path)
    print(f"Saved: {fig_path}")
    print("\nExperiment 1 complete.")


if __name__ == "__main__":
    main()
