# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp3_concurrent_spending.py — Figure 3: Concurrent agent spending safety.

SIMULATION ONLY. Simulates 5 agents racing to spend from a shared envelope
and compares the safe (enforced) and unsafe (unenforced) implementations.

Demonstrates that:
  - Without enforcement: concurrent overspend events are common.
  - With enforcement: the no-overspend property holds even under concurrency.

Reproduces Figure 3 from Paper 22. All data is SYNTHETIC. seed=42.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from economic_safety.model import (
    Envelope,
    SpendingAgent,
)
from economic_safety.verifier import EconomicSafetyVerifier
from economic_safety.visualization import plot_concurrent_spending

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "figures")

ENVELOPE_LIMIT = 1000.0
NUM_AGENTS = 5
TIMESTEPS = 100
SEED = 42


def build_agents(num_agents: int) -> list[SpendingAgent]:
    """Build a list of synthetic spending agents for the concurrency test.

    SIMULATION ONLY. Each agent has a spending_rate of 2.5 and variance 0.8,
    giving a combined expected spend of 12.5 per timestep across 5 agents —
    which exceeds the per-step budget of 10.0 (limit=1000 / 100 steps).

    Args:
        num_agents: Number of agents to create.

    Returns:
        List of SpendingAgent instances.
    """
    return [
        SpendingAgent(
            agent_id=f"concurrent-agent-{index + 1:02d}",
            spending_rate=2.5,
            variance=0.8,
            category="compute",
        )
        for index in range(num_agents)
    ]


def run_safe_concurrent(seed: int = SEED) -> dict:  # type: ignore[type-arg]
    """Run the concurrent spending simulation with enforcement enabled.

    SIMULATION ONLY. Each agent's spend is checked against the running
    balance before being applied. All data is SYNTHETIC.

    Args:
        seed: RNG seed for reproducibility.

    Returns:
        Dictionary of ConcurrencyResult metrics and serialisable timeline.
    """
    agents = build_agents(NUM_AGENTS)
    envelope = Envelope(
        category="compute",
        limit=ENVELOPE_LIMIT,
        spent=0.0,
        committed=0.0,
        period_steps=TIMESTEPS,
    )

    verifier = EconomicSafetyVerifier()
    result = verifier.simulate_concurrent_spending(
        envelope=envelope,
        agents=agents,
        timesteps=TIMESTEPS,
        seed=seed,
        enforce=True,
    )

    return {
        "mode": "enforced",
        "seed": seed,
        "num_agents": NUM_AGENTS,
        "envelope_limit": result.envelope_limit,
        "total_spent": result.total_spent,
        "safe": result.safe,
        "overspend_events": result.overspend_events,
        "timeline": result.timeline,
        "final_balance": result.timeline[-1] if result.timeline else None,
    }


def run_unsafe_concurrent(seed: int = SEED) -> dict:  # type: ignore[type-arg]
    """Run the concurrent spending simulation with enforcement disabled.

    SIMULATION ONLY. All agent spends are applied without checking the
    balance, demonstrating unsafe concurrent access. All data is SYNTHETIC.

    Args:
        seed: RNG seed for reproducibility.

    Returns:
        Dictionary of ConcurrencyResult metrics and serialisable timeline.
    """
    agents = build_agents(NUM_AGENTS)
    envelope = Envelope(
        category="compute",
        limit=ENVELOPE_LIMIT,
        spent=0.0,
        committed=0.0,
        period_steps=TIMESTEPS,
    )

    verifier = EconomicSafetyVerifier()
    result = verifier.simulate_concurrent_spending(
        envelope=envelope,
        agents=agents,
        timesteps=TIMESTEPS,
        seed=seed,
        enforce=False,
    )

    return {
        "mode": "unenforced",
        "seed": seed,
        "num_agents": NUM_AGENTS,
        "envelope_limit": result.envelope_limit,
        "total_spent": result.total_spent,
        "safe": result.safe,
        "overspend_events": result.overspend_events,
        "timeline": result.timeline,
        "final_balance": result.timeline[-1] if result.timeline else None,
    }


def main() -> None:
    """Run exp3 and save results to fig3_data.json and figures/fig3_*.png."""
    print("=" * 60)
    print("Experiment 3: Concurrent Spending Safety")
    print("SIMULATION ONLY — all data is synthetic")
    print("=" * 60)

    safe_run = run_safe_concurrent(seed=SEED)
    unsafe_run = run_unsafe_concurrent(seed=SEED)

    print(f"\n[Enforced]   safe={safe_run['safe']}, "
          f"spent={safe_run['total_spent']:.2f}, "
          f"overspend_events={safe_run['overspend_events']}, "
          f"final_balance={safe_run['final_balance']:.2f}")

    print(f"[Unenforced] safe={unsafe_run['safe']}, "
          f"spent={unsafe_run['total_spent']:.2f}, "
          f"overspend_events={unsafe_run['overspend_events']}, "
          f"final_balance={unsafe_run['final_balance']:.2f}")

    fig3_data = {
        "experiment": "exp3_concurrent_spending",
        "paper": "Paper 22",
        "note": "SIMULATION ONLY — synthetic data, seed=42",
        "num_agents": NUM_AGENTS,
        "timesteps": TIMESTEPS,
        "enforced": safe_run,
        "unenforced": unsafe_run,
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, "fig3_data.json")
    with open(out_path, "w") as fh:
        json.dump(fig3_data, fh, indent=2)
    print(f"\nSaved: {out_path}")

    # Figures
    os.makedirs(FIGURES_DIR, exist_ok=True)

    agents = build_agents(NUM_AGENTS)
    envelope = Envelope(
        category="compute",
        limit=ENVELOPE_LIMIT,
        spent=0.0,
        committed=0.0,
        period_steps=TIMESTEPS,
    )
    verifier = EconomicSafetyVerifier()

    safe_result = verifier.simulate_concurrent_spending(
        envelope=envelope, agents=agents, timesteps=TIMESTEPS, seed=SEED, enforce=True
    )
    safe_fig_path = os.path.join(FIGURES_DIR, "fig3_concurrent_safe.png")
    plot_concurrent_spending(
        safe_result, label="Enforced (safe)", save_path=safe_fig_path
    )
    print(f"Saved: {safe_fig_path}")

    # Reset envelope for unsafe run
    envelope_unsafe = Envelope(
        category="compute",
        limit=ENVELOPE_LIMIT,
        spent=0.0,
        committed=0.0,
        period_steps=TIMESTEPS,
    )
    unsafe_result = verifier.simulate_concurrent_spending(
        envelope=envelope_unsafe,
        agents=agents,
        timesteps=TIMESTEPS,
        seed=SEED,
        enforce=False,
    )
    unsafe_fig_path = os.path.join(FIGURES_DIR, "fig3_concurrent_unsafe.png")
    plot_concurrent_spending(
        unsafe_result, label="Unenforced (unsafe)", save_path=unsafe_fig_path
    )
    print(f"Saved: {unsafe_fig_path}")
    print("\nExperiment 3 complete.")


if __name__ == "__main__":
    main()
