# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp4_network_topology.py — Different network topologies experiment.

SIMULATION ONLY. Compares transitive trust, path length, and transitivity
metrics across three synthetic delegation network topologies: linear chain,
binary tree, and fully-connected mesh. All data is SYNTHETIC. Results
reproduce Figure 4 of the companion paper.

Run:
    python experiments/exp4_network_topology.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from delegation_trust.agents import (
    build_linear_chain,
    build_mesh_delegation,
    build_tree_delegation,
)
from delegation_trust.metrics import transitivity_score, delegation_depth_analysis
from delegation_trust.model import DelegationTrustModel, SimulationConfig
from delegation_trust.visualization import plot_topology_comparison


# ---------------------------------------------------------------------------
# Experiment configuration — SIMULATION ONLY
# ---------------------------------------------------------------------------

SEED: int = 42

# Topology specifications: (name, builder_kwargs) — SIMULATION ONLY
_TOPOLOGY_SPECS: list[dict[str, object]] = [
    {
        "name": "linear_4",
        "label": "Linear (4 agents)",
        "type": "linear",
        "length": 4,
    },
    {
        "name": "linear_8",
        "label": "Linear (8 agents)",
        "type": "linear",
        "length": 8,
    },
    {
        "name": "tree_d2_b2",
        "label": "Tree (depth=2, branch=2)",
        "type": "tree",
        "depth": 2,
        "branching_factor": 2,
    },
    {
        "name": "tree_d3_b2",
        "label": "Tree (depth=3, branch=2)",
        "type": "tree",
        "depth": 3,
        "branching_factor": 2,
    },
    {
        "name": "mesh_5",
        "label": "Mesh (5 agents)",
        "type": "mesh",
        "size": 5,
    },
    {
        "name": "mesh_7",
        "label": "Mesh (7 agents)",
        "type": "mesh",
        "size": 7,
    },
]


def _build_model_for_spec(
    spec: dict[str, object],
    config: SimulationConfig,
) -> tuple[DelegationTrustModel, str, str]:
    """Build a DelegationTrustModel for a given topology spec.

    SIMULATION ONLY. Returns (model, source_id, target_id).
    """
    topology_type = str(spec["type"])
    model = DelegationTrustModel(config)

    if topology_type == "linear":
        population = build_linear_chain(
            length=int(spec["length"]),  # type: ignore[arg-type]
            agent_type="compliant",
            config=config,
            task_scope="general",
        )
    elif topology_type == "tree":
        population = build_tree_delegation(
            depth=int(spec["depth"]),  # type: ignore[arg-type]
            branching_factor=int(spec["branching_factor"]),  # type: ignore[arg-type]
            agent_type="compliant",
            config=config,
            task_scope="general",
        )
    elif topology_type == "mesh":
        population = build_mesh_delegation(
            size=int(spec["size"]),  # type: ignore[arg-type]
            config=config,
            task_scope="general",
        )
    else:
        raise ValueError(f"Unknown topology type: {topology_type!r}")

    for agent in population.agents:
        model.add_agent(agent)
    for edge in population.edges:
        model.add_delegation(
            delegator=edge.delegator,
            delegatee=edge.delegatee,
            trust_level=edge.trust_level,
            task_scope=edge.task_scope,
            edge_id=edge.edge_id,
        )

    return model, population.source, population.target


def run_experiment() -> dict[str, object]:
    """Run Experiment 4: network topology comparison.

    SIMULATION ONLY. Evaluates six delegation graph topologies, measuring:
    - Terminal transitive trust from source to target (BFS path)
    - BFS path length in hops
    - Mean transitive trust across all reachable agent pairs

    All graph structures and trust values are SYNTHETIC.

    Returns:
        Dictionary with per-topology results and aggregate comparison arrays.
    """
    print("=" * 62)
    print("Exp 4 — Network Topology Comparison")
    print("SIMULATION ONLY — synthetic data, seed=42")
    print("=" * 62)

    config = SimulationConfig(seed=SEED)

    topology_results: list[dict[str, object]] = []
    scenario_labels: list[str] = []
    terminal_trusts: list[float] = []
    path_lengths: list[int] = []
    mean_pair_trusts: list[float] = []

    for spec in _TOPOLOGY_SPECS:
        name = str(spec["name"])
        label = str(spec["label"])
        print(f"\n  Topology: {label}")

        model, source, target = _build_model_for_spec(spec, config)

        terminal = model.compute_transitive_trust(source, target)
        found_path = model._find_shortest_path(source, target)
        path_len = len(found_path) - 1 if found_path else 0

        # Transitivity across all pairs
        ts = transitivity_score(model)
        depth_analysis = delegation_depth_analysis(model, source)

        print(f"    terminal_trust={terminal:.6f} | path_length={path_len}")
        print(f"    mean_pair_trust={ts.mean_trust:.6f} | reachable_pairs={ts.reachable_pairs}")
        print(f"    max_depth_from_source={depth_analysis.max_depth}")

        result_entry: dict[str, object] = {
            "name": name,
            "label": label,
            "terminal_trust": round(terminal, 6),
            "path_length": path_len,
            "mean_pair_trust": round(ts.mean_trust, 6),
            "std_pair_trust": round(ts.std_trust, 6),
            "reachable_pairs": ts.reachable_pairs,
            "total_pairs": ts.total_pairs,
            "max_depth": depth_analysis.max_depth,
        }
        topology_results.append(result_entry)
        scenario_labels.append(label)
        terminal_trusts.append(round(terminal, 6))
        path_lengths.append(path_len)
        mean_pair_trusts.append(round(ts.mean_trust, 6))

    # Generate figure
    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "figures")
    os.makedirs(output_dir, exist_ok=True)

    fig = plot_topology_comparison(
        scenario_names=scenario_labels,
        terminal_trusts=terminal_trusts,
        path_lengths=path_lengths,
        save_path=os.path.join(output_dir, "fig4_topology_comparison.png"),
        show=False,
    )
    fig.clf()

    print("\n  Aggregate comparison (sorted by terminal trust):")
    ranked = sorted(topology_results, key=lambda entry: entry["terminal_trust"], reverse=True)  # type: ignore[return-value]
    for entry in ranked:
        print(
            f"    {entry['name']}: terminal={entry['terminal_trust']:.6f} "
            f"hops={entry['path_length']} mean_pair={entry['mean_pair_trust']:.6f}"
        )

    return {
        "experiment": "exp4_network_topology",
        "description": (
            "Network topology comparison: linear, tree, mesh. "
            "SIMULATION ONLY — synthetic data, seed=42."
        ),
        "scenario_labels": scenario_labels,
        "terminal_trusts": terminal_trusts,
        "path_lengths": path_lengths,
        "mean_pair_trusts": mean_pair_trusts,
        "topology_results": topology_results,
    }


def main() -> None:
    """Entry point for Experiment 4. SIMULATION ONLY."""
    results = run_experiment()

    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fig4_data.json")

    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(results, file_handle, indent=2)

    print(f"\nSaved results to: {output_path}")
    print("SIMULATION ONLY — do not use for production trust decisions.")


if __name__ == "__main__":
    main()
