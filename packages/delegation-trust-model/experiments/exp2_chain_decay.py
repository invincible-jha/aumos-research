# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp2_chain_decay.py — Trust decay over delegation hops experiment.

SIMULATION ONLY. Analyses how transitive trust decreases as a function of hop
count across agent types with different pairwise trust distributions. Compares
theoretical multiplicative decay against sampled chains. All data is SYNTHETIC.
Results reproduce Figure 2 of the companion paper.

Run:
    python experiments/exp2_chain_decay.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np

from delegation_trust.agents import build_linear_chain, _TRUST_PARAMS  # type: ignore[attr-defined]
from delegation_trust.metrics import decay_over_hops
from delegation_trust.model import DelegationTrustModel, SimulationConfig


# ---------------------------------------------------------------------------
# Experiment configuration — SIMULATION ONLY
# ---------------------------------------------------------------------------

SEED: int = 42
MAX_HOPS: int = 10
AGENT_TYPES_TO_COMPARE: list[str] = ["compliant", "mixed", "degrading", "strategic"]
SAMPLES_PER_HOP: int = 50  # synthetic chain samples per hop count


def _mean_edge_trust_for_type(agent_type: str) -> float:
    """Return the synthetic mean pairwise trust for a given agent type.

    SIMULATION ONLY. Uses the same distribution parameters as agents.py.
    """
    mean, _std = _TRUST_PARAMS.get(agent_type, (0.60, 0.15))
    return mean


def run_experiment() -> dict[str, object]:
    """Run Experiment 2: trust decay over delegation hops by agent type.

    SIMULATION ONLY. For each agent type, generates SAMPLES_PER_HOP synthetic
    chains at each hop count and measures the mean terminal trust. Compares
    sampled decay against the theoretical multiplicative curve. All data SYNTHETIC.

    Returns:
        Dictionary mapping agent type to sampled and theoretical decay curves.
    """
    print("=" * 62)
    print("Exp 2 — Trust Decay Over Delegation Hops")
    print("SIMULATION ONLY — synthetic data, seed=42")
    print("=" * 62)

    rng = np.random.RandomState(SEED)
    hop_counts = list(range(1, MAX_HOPS + 1))

    curves: dict[str, dict[str, list[float]]] = {}

    for agent_type in AGENT_TYPES_TO_COMPARE:
        sampled_means: list[float] = []
        theoretical: list[float] = []
        mean_edge = _mean_edge_trust_for_type(agent_type)

        print(f"\n  Agent type: {agent_type!r} | mean_edge_trust={mean_edge:.3f}")

        for hop_count in hop_counts:
            chain_length = hop_count + 1
            hop_samples: list[float] = []

            for sample_index in range(SAMPLES_PER_HOP):
                sample_seed = int(rng.randint(0, 2**31))
                sample_config = SimulationConfig(seed=sample_seed)
                population = build_linear_chain(
                    length=chain_length,
                    agent_type=agent_type,
                    config=sample_config,
                    task_scope="general",
                )

                model = DelegationTrustModel(sample_config)
                for agent in population.agents:
                    model.add_agent(agent)
                for edge in population.edges:
                    model.add_delegation(
                        delegator=edge.delegator,
                        delegatee=edge.delegatee,
                        trust_level=edge.trust_level,
                        task_scope=edge.task_scope,
                        edge_id=f"{agent_type}-s{sample_index}-{edge.edge_id}",
                    )

                trust = model.compute_transitive_trust(population.source, population.target)
                hop_samples.append(trust)

            sampled_mean = float(np.mean(hop_samples))
            theory_val = float(mean_edge ** hop_count)
            sampled_means.append(round(sampled_mean, 6))
            theoretical.append(round(theory_val, 6))

            print(
                f"    hops={hop_count} | sampled_mean={sampled_mean:.6f} "
                f"| theoretical={theory_val:.6f}"
            )

        curves[agent_type] = {
            "sampled_mean": sampled_means,
            "theoretical": theoretical,
            "mean_edge_trust": mean_edge,
        }

    return {
        "experiment": "exp2_chain_decay",
        "description": (
            "Trust decay over delegation hops by agent type. "
            "SIMULATION ONLY — synthetic data, seed=42."
        ),
        "x": hop_counts,
        "x_label": "hop_count",
        "y_label": "terminal_trust",
        "samples_per_hop": SAMPLES_PER_HOP,
        "curves": curves,
    }


def main() -> None:
    """Entry point for Experiment 2. SIMULATION ONLY."""
    results = run_experiment()

    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fig2_data.json")

    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(results, file_handle, indent=2)

    print(f"\nSaved results to: {output_path}")
    print("SIMULATION ONLY — do not use for production trust decisions.")


if __name__ == "__main__":
    main()
