# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""Experiment 2: Relevance Decay Retention.

SIMULATION ONLY — not production AMGP implementation.
Reproduces Figure 2 from Paper 5. Runs a RelevanceDecayPolicy simulation
with decay_rate=0.01, threshold=0.3, 500 synthetic records, seed=42.

Usage::

    python experiments/exp2_relevance_decay.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from governed_forgetting.scenarios import scenario_relevance_decay
from governed_forgetting.verifier import RetentionVerifier
from governed_forgetting.visualization import fig2_relevance_decay


def main() -> None:
    """Run Experiment 2 and emit metrics + figure.

    SIMULATION ONLY — not production AMGP implementation.
    """
    print("=" * 60)
    print("Experiment 2 — Relevance Decay Retention (seed=42)")
    print("SIMULATION ONLY — not production AMGP implementation.")
    print("=" * 60)

    bundle = scenario_relevance_decay(
        n_memories=500,
        decay_rate=0.01,
        threshold=0.3,
        timesteps=500,
        seed=42,
    )
    result = bundle.model.simulate(bundle.memory_stream, timesteps=bundle.timesteps)

    print(f"\nScenario      : {bundle.description}")
    print(f"Total records : {len(bundle.memory_stream)}")
    print(f"Retained      : {len(result.retained)}")
    print(f"Forgotten     : {len(result.forgotten)}")
    print(f"Retention rate: {result.retention_rate:.4f}")

    # Formal verification
    verifier = RetentionVerifier()
    policy = bundle.model.policies[0]
    stream = bundle.memory_stream

    completeness = verifier.verify_completeness(policy, stream)
    monotonic = verifier.verify_monotonic_forgetting(policy, stream, max_timestep=500)

    print("\n--- Verification ---")
    print(f"Completeness    : {'PASS' if completeness.holds else 'FAIL'} "
          f"({completeness.records_checked} checks)")
    print(f"Monotonic forget: {'PASS' if monotonic.holds else 'FAIL'} "
          f"({monotonic.records_checked} records)")

    if not monotonic.holds:
        for v in monotonic.violations[:5]:
            print(f"  VIOLATION: {v}")

    # Serialize history
    history_dicts = [
        {"timestep": s.timestep, "active": s.active, "forgotten": s.forgotten}
        for s in result.history
    ]
    out_path = os.path.join(
        os.path.dirname(__file__), "..", "results", "precomputed", "fig2_data.json"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "scenario": bundle.name,
                "seed": 42,
                "decay_rate": 0.01,
                "threshold": 0.3,
                "retention_rate": result.retention_rate,
                "history": history_dicts,
            },
            f,
            indent=2,
        )
    print(f"\nPrecomputed data saved to: {os.path.abspath(out_path)}")

    # Generate figure
    fig = fig2_relevance_decay(history_dicts, decay_rate=0.01, threshold=0.3)
    figures_dir = os.path.join(os.path.dirname(__file__), "..", "results", "figures")
    os.makedirs(figures_dir, exist_ok=True)
    fig_path = os.path.join(figures_dir, "fig2_relevance_decay.png")
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved to  : {os.path.abspath(fig_path)}")


if __name__ == "__main__":
    main()
