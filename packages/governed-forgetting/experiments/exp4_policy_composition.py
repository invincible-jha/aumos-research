# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""Experiment 4: Composite Policy Comparison.

SIMULATION ONLY — not production AMGP implementation.
Reproduces Figure 4 from Paper 5. Runs three separate simulations and
overlays their retention curves:

  - Time-Based only (TTL=200)
  - Relevance Decay only (decay_rate=0.01, threshold=0.3)
  - Composite (Time + Decay + Consent, mode=all)

Demonstrates that policy composition accelerates forgetting relative to
any individual policy.

Usage::

    python experiments/exp4_policy_composition.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from governed_forgetting.policies import ConsentBasedPolicy
from governed_forgetting.scenarios import (
    scenario_composite_policy,
    scenario_relevance_decay,
    scenario_time_based,
)
from governed_forgetting.types import RetentionResult, RetentionSnapshot
from governed_forgetting.verifier import RetentionVerifier
from governed_forgetting.visualization import fig4_composite_policy


def _run_composite_with_revocations(bundle: object) -> RetentionResult:
    """Execute the composite simulation with mid-run consent revocations.

    SIMULATION ONLY — not production AMGP implementation.
    Applies revocations to the ConsentBasedPolicy's store at the specified
    timesteps before evaluating retention decisions for that tick.
    """
    from governed_forgetting.policies import CompositePolicy  # noqa: PLC0415

    composite = bundle.model.policies[0]  # type: ignore[attr-defined]
    assert isinstance(composite, CompositePolicy)

    # Locate the ConsentBasedPolicy inside the composite
    consent_policy: ConsentBasedPolicy | None = None
    for child in composite.policies:
        if isinstance(child, ConsentBasedPolicy):
            consent_policy = child
            break

    revocation_map: dict[int, list[str]] = {}
    for rev in bundle.consent_revocations:  # type: ignore[attr-defined]
        revocation_map.setdefault(rev.at_timestep, []).append(rev.owner)

    forgotten: list[object] = []
    history: list[RetentionSnapshot] = []
    active_memories = list(bundle.memory_stream)  # type: ignore[attr-defined]

    for t in range(bundle.timesteps):  # type: ignore[attr-defined]
        if consent_policy is not None and t in revocation_map:
            for owner in revocation_map[t]:
                consent_policy.revoke(owner)

        still_active = []
        newly_forgotten = []
        for record in active_memories:
            if composite.should_retain(record, t):
                still_active.append(record)
            else:
                newly_forgotten.append(record)

        active_memories = still_active
        forgotten.extend(newly_forgotten)
        history.append(
            RetentionSnapshot(
                timestep=t,
                active=len(active_memories),
                forgotten=len(forgotten),
            )
        )

    total = max(len(bundle.memory_stream), 1)  # type: ignore[attr-defined]
    return RetentionResult(
        retained=active_memories,  # type: ignore[arg-type]
        forgotten=forgotten,  # type: ignore[arg-type]
        history=history,
        retention_rate=len(active_memories) / total,
    )


def _history_to_dicts(result: RetentionResult) -> list[dict[str, int]]:
    return [
        {"timestep": s.timestep, "active": s.active, "forgotten": s.forgotten}
        for s in result.history
    ]


def main() -> None:
    """Run Experiment 4 and emit metrics + figure.

    SIMULATION ONLY — not production AMGP implementation.
    """
    print("=" * 60)
    print("Experiment 4 — Composite Policy Comparison (seed=42)")
    print("SIMULATION ONLY — not production AMGP implementation.")
    print("=" * 60)

    # --- Baseline 1: Time-Based (TTL=200) ---
    bundle_time = scenario_time_based(n_memories=500, ttl=200, timesteps=500, seed=42)
    result_time = bundle_time.model.simulate(bundle_time.memory_stream, timesteps=500)

    # --- Baseline 2: Relevance Decay ---
    bundle_decay = scenario_relevance_decay(
        n_memories=500, decay_rate=0.01, threshold=0.3, timesteps=500, seed=42
    )
    result_decay = bundle_decay.model.simulate(bundle_decay.memory_stream, timesteps=500)

    # --- Composite: Time + Decay + Consent ---
    bundle_comp = scenario_composite_policy(
        n_memories=500,
        ttl=200,
        decay_rate=0.01,
        threshold=0.3,
        n_owners=10,
        revocation_timesteps=[150, 300],
        timesteps=500,
        seed=42,
    )
    result_comp = _run_composite_with_revocations(bundle_comp)

    print("\n--- Results Summary ---")
    for label, result in [
        ("Time-Based", result_time),
        ("Relevance Decay", result_decay),
        ("Composite", result_comp),
    ]:
        print(
            f"{label:<20}: retained={len(result.retained):>4}  "
            f"forgotten={len(result.forgotten):>4}  "
            f"rate={result.retention_rate:.4f}"
        )

    # Verification on composite result
    verifier = RetentionVerifier()
    bounded = verifier.verify_bounded_retention(result_comp, max_retention=200)
    print(f"\nBounded retention (max=200): {'PASS' if bounded.holds else 'FAIL'} "
          f"({bounded.records_checked} records)")
    if not bounded.holds:
        for v in bounded.violations[:5]:
            print(f"  VIOLATION: {v}")

    # Serialize histories
    h_time = _history_to_dicts(result_time)
    h_decay = _history_to_dicts(result_decay)
    h_comp = _history_to_dicts(result_comp)

    out_path = os.path.join(
        os.path.dirname(__file__), "..", "results", "precomputed", "fig4_data.json"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "scenario": "composite_policy",
                "seed": 42,
                "retention_rate_time": result_time.retention_rate,
                "retention_rate_decay": result_decay.retention_rate,
                "retention_rate_composite": result_comp.retention_rate,
                "history_time": h_time,
                "history_decay": h_decay,
                "history_composite": h_comp,
            },
            f,
            indent=2,
        )
    print(f"\nPrecomputed data saved to: {os.path.abspath(out_path)}")

    # Generate figure
    fig = fig4_composite_policy(h_comp, h_time, h_decay)
    figures_dir = os.path.join(os.path.dirname(__file__), "..", "results", "figures")
    os.makedirs(figures_dir, exist_ok=True)
    fig_path = os.path.join(figures_dir, "fig4_composite_policy.png")
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved to  : {os.path.abspath(fig_path)}")


if __name__ == "__main__":
    main()
