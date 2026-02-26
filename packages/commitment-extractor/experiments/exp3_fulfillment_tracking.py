# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
exp3_fulfillment_tracking.py — Fulfillment tracking lifecycle experiment.

SIMULATION ONLY. Demonstrates CommitmentTracker lifecycle management across
synthetic scenarios: extraction, registration, status checking, TTL expiry,
and manual fulfillment marking. All data is SYNTHETIC. Results reproduce
Figure 3 of the commitment-extractor companion paper.

Run:
    python experiments/exp3_fulfillment_tracking.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from commitment_extractor.model import CommitmentExtractor, FulfillmentStatus
from commitment_extractor.scenarios import (
    scenario_deadline_commitment,
    scenario_expired_commitment,
    scenario_fulfillment_tracking,
    scenario_mixed_types,
    scenario_no_commitments,
)
from commitment_extractor.tracker import CommitmentTracker


_TTL: int = 3  # Simulated TTL — commitments expire after 3 time units


def run_experiment() -> dict[str, object]:
    """Run Experiment 3: fulfillment tracking lifecycle simulation.

    SIMULATION ONLY. For each test scenario, extracts commitments, registers
    them with CommitmentTracker, runs status checks, and applies TTL expiry.
    All data is SYNTHETIC.

    Returns:
        Dictionary with per-scenario tracker snapshots and fulfillment rates.
    """
    print("=" * 62)
    print("Exp 3 — Fulfillment Tracking Lifecycle")
    print("SIMULATION ONLY — synthetic data, TTL-based expiry")
    print("=" * 62)

    extractor = CommitmentExtractor(model="rule-based")

    scenarios_with_followup = [
        scenario_fulfillment_tracking(),
        scenario_deadline_commitment(),
        scenario_mixed_types(),
        scenario_expired_commitment(),
        scenario_no_commitments(),
    ]

    scenario_results: list[dict[str, object]] = []
    all_fulfillment_rates: list[float] = []
    scenario_names: list[str] = []

    for scenario in scenarios_with_followup:
        print(f"\n  Scenario: {scenario.name!r}")
        tracker = CommitmentTracker()

        # Extract and register all commitments
        extracted = extractor.extract_from_conversation(scenario.messages)
        tracker.register_batch(extracted)
        print(f"    Extracted and registered: {len(extracted)} commitments")

        # Check fulfillment status using follow-up messages
        for commitment in extracted:
            # Use messages after the commitment's timestamp as follow-ups
            follow_up_messages = [
                msg for msg in scenario.messages
                if msg.timestamp > commitment.timestamp
            ]
            tracker.check_status(commitment.commitment_id, follow_up_messages)

        # Simulate TTL expiry at timestamp = max_timestamp + TTL
        max_timestamp = (
            max(msg.timestamp for msg in scenario.messages) if scenario.messages else 0
        )
        expired_ids = tracker.expire_overdue(
            current_timestamp=max_timestamp + _TTL + 1,
            ttl=_TTL,
        )
        print(f"    Expired after TTL={_TTL}: {len(expired_ids)} commitments")

        snapshot = tracker.snapshot()
        print(
            f"    Snapshot: total={snapshot.total} active={snapshot.active} "
            f"fulfilled={snapshot.fulfilled} expired={snapshot.expired} "
            f"fulfillment_rate={snapshot.fulfillment_rate:.4f}"
        )

        all_fulfillment_rates.append(snapshot.fulfillment_rate)
        scenario_names.append(scenario.name)

        scenario_results.append({
            "name": scenario.name,
            "extracted": len(extracted),
            "active": snapshot.active,
            "fulfilled": snapshot.fulfilled,
            "expired": snapshot.expired,
            "cancelled": snapshot.cancelled,
            "fulfillment_rate": snapshot.fulfillment_rate,
            "expired_by_ttl": len(expired_ids),
        })

    print(f"\n  Mean fulfillment rate across scenarios: "
          f"{sum(all_fulfillment_rates)/max(len(all_fulfillment_rates), 1):.4f}")

    return {
        "experiment": "exp3_fulfillment_tracking",
        "description": (
            "Commitment fulfillment tracking lifecycle across synthetic scenarios. "
            "SIMULATION ONLY — rule-based, TTL-based expiry, seed=42."
        ),
        "ttl": _TTL,
        "x": scenario_names,
        "x_label": "scenario",
        "y_label": "fulfillment_rate",
        "fulfillment_rates": all_fulfillment_rates,
        "per_scenario": scenario_results,
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
    print("SIMULATION ONLY — do not use for production commitment tracking.")


if __name__ == "__main__":
    main()
