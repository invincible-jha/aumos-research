# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp1_basic_delegation.py — Basic delegation chain trust propagation experiment.

SIMULATION ONLY. Demonstrates how multiplicative trust decay propagates along
linear delegation chains of varying lengths with all-compliant agent populations.
All data is SYNTHETIC. Results reproduce Figure 1 of the companion paper.

Run:
    python experiments/exp1_basic_delegation.py
"""

from __future__ import annotations

import json
import os
import sys

# Allow running from the package root without installing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np

from delegation_trust.agents import build_linear_chain
from delegation_trust.model import DelegationTrustModel, SimulationConfig
from delegation_trust.metrics import decay_over_hops, path_reliability


# ---------------------------------------------------------------------------
# Experiment configuration — SIMULATION ONLY
# ---------------------------------------------------------------------------

SEED: int = 42
CHAIN_LENGTHS: list[int] = [2, 3, 4, 5, 6, 7, 8, 9, 10]
EDGE_TRUST_LEVELS: list[float] = [0.70, 0.80, 0.85, 0.90, 0.95]


def run_experiment() -> dict[str, object]:
    """Run Experiment 1: basic delegation chain trust propagation.

    SIMULATION ONLY. Sweeps chain length and fixed edge-trust values,
    computing the theoretical and simulated transitive trust at each hop count.
    All agent populations and trust values are SYNTHETIC.

    Returns:
        Dictionary with x (chain lengths), y curves per trust level,
        and per-hop decay profiles.
    """
    print("=" * 62)
    print("Exp 1 — Basic Delegation Chain Trust Propagation")
    print("SIMULATION ONLY — synthetic data, seed=42")
    print("=" * 62)

    config = SimulationConfig(seed=SEED)
    results_by_trust: dict[str, list[float]] = {}

    for edge_trust in EDGE_TRUST_LEVELS:
        terminal_trusts: list[float] = []
        label = f"edge_trust={edge_trust:.2f}"

        for chain_length in CHAIN_LENGTHS:
            # Build a compliant chain with uniform edge trust
            population = build_linear_chain(
                length=chain_length,
                agent_type="compliant",
                config=config,
                task_scope="compute",
            )
            model = DelegationTrustModel(config)
            for agent in population.agents:
                model.add_agent(agent)

            # Override all edge trusts to the fixed value for this sweep
            for index in range(chain_length - 1):
                model.add_delegation(
                    delegator=f"agent-{index}",
                    delegatee=f"agent-{index + 1}",
                    trust_level=edge_trust,
                    task_scope="compute",
                    edge_id=f"exp1-edge-{index}",
                )

            effective = model.compute_transitive_trust("agent-0", f"agent-{chain_length - 1}")
            terminal_trusts.append(round(effective, 6))

            hops = chain_length - 1
            print(
                f"  {label} | chain_length={chain_length} | hops={hops} "
                f"| terminal_trust={effective:.6f}"
            )

        results_by_trust[label] = terminal_trusts

    # Also compute the decay profile for the mean edge trust (0.85)
    rng = np.random.RandomState(SEED)
    synthetic_edges_trusts = [float(rng.uniform(0.80, 0.90)) for _ in range(10)]

    from delegation_trust.model import DelegationEdge
    synthetic_edges = [
        DelegationEdge(
            edge_id=f"synthetic-{index}",
            delegator=f"agent-{index}",
            delegatee=f"agent-{index + 1}",
            trust_level=t,
            task_scope="compute",
        )
        for index, t in enumerate(synthetic_edges_trusts)
    ]
    decay_profile = decay_over_hops(synthetic_edges, max_hops=len(CHAIN_LENGTHS))

    print("\nDecay profile (theoretical, mean_edge_trust=0.85 approx):")
    for hops, theory in zip(decay_profile.hop_counts, decay_profile.theoretical_decay):
        print(f"  hops={hops} | theory={theory:.6f}")

    return {
        "experiment": "exp1_basic_delegation",
        "description": (
            "Basic delegation chain trust propagation. "
            "SIMULATION ONLY — synthetic data, seed=42."
        ),
        "x": CHAIN_LENGTHS,
        "x_label": "chain_length",
        "y_label": "terminal_trust",
        "curves": results_by_trust,
        "decay_profile": {
            "hop_counts": decay_profile.hop_counts,
            "theoretical": decay_profile.theoretical_decay,
            "mean_edge_trust": decay_profile.mean_edge_trust,
        },
    }


def main() -> None:
    """Entry point for Experiment 1. SIMULATION ONLY."""
    results = run_experiment()

    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fig1_data.json")

    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(results, file_handle, indent=2)

    print(f"\nSaved results to: {output_path}")
    print("SIMULATION ONLY — do not use for production trust decisions.")


if __name__ == "__main__":
    main()
