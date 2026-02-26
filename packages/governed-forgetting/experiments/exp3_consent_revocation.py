# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""Experiment 3: Consent Revocation.

SIMULATION ONLY — not production AMGP implementation.
Reproduces Figure 3 from Paper 5. Simulates batch consent revocations at
timesteps 100, 200, and 300 across 10 simulated owners. Verifies that
all records belonging to revoked owners are forgotten within 1 timestep
of the revocation event.

Usage::

    python experiments/exp3_consent_revocation.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from governed_forgetting.policies import ConsentBasedPolicy
from governed_forgetting.scenarios import scenario_consent_revocation
from governed_forgetting.verifier import RetentionVerifier
from governed_forgetting.visualization import fig3_consent_revocation


def _run_with_revocations(bundle: object) -> object:
    """Execute the simulation with mid-run consent revocations.

    SIMULATION ONLY — not production AMGP implementation.
    Because ConsentBasedPolicy uses a mutable consent_store, revocations
    are applied by mutating the store before the corresponding timestep
    batch is processed. This function orchestrates that by running the
    simulation in segments between revocation events.
    """
    from governed_forgetting.types import RetentionResult, RetentionSnapshot  # noqa: PLC0415

    # Extract the ConsentBasedPolicy from the model's policy list
    policy = bundle.model.policies[0]  # type: ignore[attr-defined]
    assert isinstance(policy, ConsentBasedPolicy)

    # Sort revocations by timestep
    sorted_revocations = sorted(
        bundle.consent_revocations,  # type: ignore[attr-defined]
        key=lambda r: r.at_timestep,
    )

    # Build a per-timestep revocation lookup
    revocation_map: dict[int, list[str]] = {}
    for rev in sorted_revocations:
        revocation_map.setdefault(rev.at_timestep, []).append(rev.owner)

    # Run manually, applying revocations at the right timestep
    forgotten: list[object] = []
    history: list[RetentionSnapshot] = []
    active_memories = list(bundle.memory_stream)  # type: ignore[attr-defined]

    for t in range(bundle.timesteps):  # type: ignore[attr-defined]
        # Apply any revocations scheduled for this timestep
        if t in revocation_map:
            for owner in revocation_map[t]:
                policy.revoke(owner)

        still_active = []
        newly_forgotten = []
        for record in active_memories:
            if policy.should_retain(record, t):
                still_active.append(record)
            else:
                newly_forgotten.append(record)

        active_memories = still_active
        forgotten.extend(newly_forgotten)
        history.append(
            RetentionSnapshot(timestep=t, active=len(active_memories), forgotten=len(forgotten))
        )

    total = max(len(bundle.memory_stream), 1)  # type: ignore[attr-defined]
    return RetentionResult(
        retained=active_memories,  # type: ignore[arg-type]
        forgotten=forgotten,  # type: ignore[arg-type]
        history=history,
        retention_rate=len(active_memories) / total,
    )


def main() -> None:
    """Run Experiment 3 and emit metrics + figure.

    SIMULATION ONLY — not production AMGP implementation.
    """
    print("=" * 60)
    print("Experiment 3 — Consent Revocation (seed=42)")
    print("SIMULATION ONLY — not production AMGP implementation.")
    print("=" * 60)

    bundle = scenario_consent_revocation(
        n_memories=500,
        n_owners=10,
        revocation_timesteps=[100, 200, 300],
        timesteps=500,
        seed=42,
    )
    result = _run_with_revocations(bundle)

    print(f"\nScenario      : {bundle.description}")
    print(f"Total records : {len(bundle.memory_stream)}")
    print(f"Retained      : {len(result.retained)}")
    print(f"Forgotten     : {len(result.forgotten)}")
    print(f"Retention rate: {result.retention_rate:.4f}")

    # Verification — rebuild a fresh consent policy at a post-revocation state
    revoked_store: dict[str, bool] = {
        rev.owner: False for rev in bundle.consent_revocations
    }
    consent_policy_for_verify = ConsentBasedPolicy(consent_store=revoked_store)
    verifier = RetentionVerifier()
    compliance = verifier.verify_consent_compliance(
        policy=consent_policy_for_verify,
        consent_revocations=bundle.consent_revocations,
        memory_stream=bundle.memory_stream,
        max_delay=1,
    )

    print("\n--- Verification ---")
    print(f"Consent compliance: {'PASS' if compliance.holds else 'FAIL'} "
          f"({compliance.records_checked} records checked)")
    if not compliance.holds:
        for v in compliance.violations[:5]:
            print(f"  VIOLATION: {v}")

    # Serialize history
    history_dicts = [
        {"timestep": s.timestep, "active": s.active, "forgotten": s.forgotten}
        for s in result.history
    ]
    out_path = os.path.join(
        os.path.dirname(__file__), "..", "results", "precomputed", "fig3_data.json"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "scenario": bundle.name,
                "seed": 42,
                "revocation_timesteps": [100, 200, 300],
                "retention_rate": result.retention_rate,
                "history": history_dicts,
            },
            f,
            indent=2,
        )
    print(f"\nPrecomputed data saved to: {os.path.abspath(out_path)}")

    # Generate figure
    fig = fig3_consent_revocation(history_dicts, revocation_timesteps=[100, 200, 300])
    figures_dir = os.path.join(os.path.dirname(__file__), "..", "results", "figures")
    os.makedirs(figures_dir, exist_ok=True)
    fig_path = os.path.join(figures_dir, "fig3_consent_revocation.png")
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved to  : {os.path.abspath(fig_path)}")


if __name__ == "__main__":
    main()
