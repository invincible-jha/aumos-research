# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp3_adversarial_delegation.py — Adversarial agents in delegation chains.

SIMULATION ONLY. Measures how a single adversarial agent placed at different
positions along a delegation chain degrades the overall transitive trust.
Adversarial agents have low pairwise trust levels. All data is SYNTHETIC.
Results reproduce Figure 3 of the companion paper.

Run:
    python experiments/exp3_adversarial_delegation.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np

from delegation_trust.agents import build_mixed_population
from delegation_trust.model import DelegationEdge, DelegationTrustModel, SimulationConfig


# ---------------------------------------------------------------------------
# Experiment configuration — SIMULATION ONLY
# ---------------------------------------------------------------------------

SEED: int = 42
CHAIN_LENGTHS: list[int] = [3, 5, 7, 9]
ADVERSARIAL_TRUST: float = 0.20
COMPLIANT_TRUST: float = 0.90


def _build_uniform_model(
    chain_length: int,
    trust_level: float,
    config: SimulationConfig,
) -> DelegationTrustModel:
    """Build a uniform-trust chain model.

    SIMULATION ONLY. Creates a linear chain model with a fixed pairwise trust
    level on every edge. All data is SYNTHETIC.
    """
    model = DelegationTrustModel(config)
    for index in range(chain_length):
        from delegation_trust.model import AgentNode
        model.add_agent(AgentNode(
            agent_id=f"agent-{index}",
            agent_type="compliant",
            label=f"A{index}",
        ))

    for index in range(chain_length - 1):
        model.add_delegation(
            delegator=f"agent-{index}",
            delegatee=f"agent-{index + 1}",
            trust_level=trust_level,
            task_scope="general",
            edge_id=f"baseline-{index}",
        )
    return model


def run_experiment() -> dict[str, object]:
    """Run Experiment 3: adversarial agents in delegation chains.

    SIMULATION ONLY. For each chain length, measures terminal trust when:
    - All agents are compliant (baseline)
    - One adversarial agent occupies each position along the chain

    Reports trust degradation by adversarial position. All data SYNTHETIC.

    Returns:
        Dictionary with chain lengths, baseline trusts, and per-position
        adversarial trust arrays.
    """
    print("=" * 62)
    print("Exp 3 — Adversarial Agents in Delegation Chains")
    print("SIMULATION ONLY — synthetic data, seed=42")
    print("=" * 62)

    config = SimulationConfig(seed=SEED)

    baseline_trusts: list[float] = []
    # adversarial_results[chain_len] = list of (position, trust)
    adversarial_by_length: dict[int, dict[str, list[object]]] = {}

    for chain_length in CHAIN_LENGTHS:
        print(f"\n  Chain length: {chain_length}")

        # Baseline: all compliant
        baseline_model = _build_uniform_model(chain_length, COMPLIANT_TRUST, config)
        baseline_trust = baseline_model.compute_transitive_trust(
            "agent-0", f"agent-{chain_length - 1}"
        )
        baseline_trusts.append(round(baseline_trust, 6))
        print(f"    Baseline (all compliant): terminal_trust={baseline_trust:.6f}")

        positions: list[int] = []
        adv_trusts: list[float] = []

        # Place adversarial agent at each non-root, non-leaf position (1..chain-2)
        # and also at position chain-1 (tail)
        for adv_pos in range(1, chain_length):
            population = build_mixed_population(
                chain_length=chain_length,
                adversarial_positions=[adv_pos],
                config=config,
                task_scope="general",
            )

            # Rebuild model with fixed trust values instead of sampled
            model = DelegationTrustModel(config)
            for agent in population.agents:
                model.add_agent(agent)

            for index in range(chain_length - 1):
                # The edge incoming to the adversarial agent has low trust
                is_adv_edge = (index + 1) == adv_pos
                edge_trust = ADVERSARIAL_TRUST if is_adv_edge else COMPLIANT_TRUST
                model.add_delegation(
                    delegator=f"agent-{index}",
                    delegatee=f"agent-{index + 1}",
                    trust_level=edge_trust,
                    task_scope="general",
                    edge_id=f"adv-pos{adv_pos}-edge-{index}",
                )

            adv_trust = model.compute_transitive_trust(
                "agent-0", f"agent-{chain_length - 1}"
            )
            positions.append(adv_pos)
            adv_trusts.append(round(adv_trust, 6))

            degradation = baseline_trust - adv_trust
            print(
                f"    adv_position={adv_pos} | terminal_trust={adv_trust:.6f} "
                f"| degradation={degradation:.6f}"
            )

        adversarial_by_length[chain_length] = {
            "positions": positions,
            "terminal_trusts": adv_trusts,
            "baseline_trust": round(baseline_trust, 6),
        }

    # Aggregate: for every chain length, compare baseline vs best/worst adversarial case
    print("\n  Summary: best and worst adversarial positions")
    for chain_length in CHAIN_LENGTHS:
        entry = adversarial_by_length[chain_length]
        trusts = entry["terminal_trusts"]
        positions = entry["positions"]
        if trusts:
            worst_idx = int(np.argmin(trusts))
            best_idx = int(np.argmax(trusts))
            print(
                f"    chain={chain_length}: worst_pos={positions[worst_idx]} "
                f"trust={trusts[worst_idx]:.6f} | "
                f"best_pos={positions[best_idx]} trust={trusts[best_idx]:.6f}"
            )

    return {
        "experiment": "exp3_adversarial_delegation",
        "description": (
            "Adversarial agent impact by chain position. "
            "SIMULATION ONLY — synthetic data, seed=42."
        ),
        "chain_lengths": CHAIN_LENGTHS,
        "baseline_trusts": baseline_trusts,
        "compliant_trust": COMPLIANT_TRUST,
        "adversarial_trust": ADVERSARIAL_TRUST,
        "adversarial_by_length": {
            str(k): v for k, v in adversarial_by_length.items()
        },
    }


def main() -> None:
    """Entry point for Experiment 3. SIMULATION ONLY."""
    results = run_experiment()

    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fig3_data.json")

    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(results, file_handle, indent=2)

    print(f"\nSaved results to: {output_path}")
    print("SIMULATION ONLY — do not use for production trust decisions.")


if __name__ == "__main__":
    main()
