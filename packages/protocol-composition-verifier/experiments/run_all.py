# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
run_all.py — Execute all three experiments and write a JSON summary.

RESEARCH TOOL — not production orchestration.
Runs Experiments 1–3 sequentially and saves a machine-readable summary
of all results to ``results/precomputed/run_all_summary.json``.

Usage::

    python experiments/run_all.py

Or from the package root::

    python -m experiments.run_all

All experiments are deterministic — given the same code version they will
always produce the same numeric results.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Allow running as a script without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import exp1_monotonic_restriction
import exp2_deadlock_freedom
import exp3_priority_ordering
from composition_verifier.model import VerificationResult


def _serialise_result(result: VerificationResult) -> dict[str, object]:
    """Convert a VerificationResult to a JSON-serialisable dict.

    RESEARCH TOOL — not production orchestration.
    """
    counterexample: dict[str, object] | None = None
    if result.counterexample is not None:
        counterexample = {
            "states": result.counterexample.states,
            "actions": result.counterexample.actions,
        }
    return {
        "holds": result.holds,
        "property_name": result.property_name,
        "states_checked": result.states_checked,
        "counterexample": counterexample,
        "violating_protocol": result.violating_protocol,
    }


def main() -> None:
    """Run all experiments, print a summary, and write JSON output.

    RESEARCH TOOL — not production orchestration.
    """
    print("=" * 64)
    print("  Protocol Composition Verifier — Full Experiment Run")
    print("  RESEARCH TOOL — not production orchestration")
    print("=" * 64)

    start = time.perf_counter()

    print("\n--- Experiment 1: Monotonic Restriction ---")
    results_exp1 = exp1_monotonic_restriction.run()

    print("\n--- Experiment 2: Deadlock Freedom ---")
    results_exp2 = exp2_deadlock_freedom.run()

    print("\n--- Experiment 3: Priority Ordering ---")
    results_exp3 = exp3_priority_ordering.run()

    elapsed = time.perf_counter() - start

    # ------------------------------------------------------------------
    # Aggregate summary
    # ------------------------------------------------------------------
    summary: dict[str, object] = {
        "package": "protocol-composition-verifier",
        "version": "0.1.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": round(elapsed, 3),
        "note": (
            "RESEARCH TOOL — not production orchestration. "
            "All state machines are synthetic."
        ),
        "exp1": {
            "two_protocol": _serialise_result(
                results_exp1["two_protocol"]  # type: ignore[arg-type]
            ),
            "three_protocol": _serialise_result(
                results_exp1["three_protocol"]  # type: ignore[arg-type]
            ),
            "initial_permitted_two": results_exp1["initial_permitted_two"],
            "initial_permitted_three": results_exp1["initial_permitted_three"],
            "most_permissive_name": results_exp1["most_permissive_name"],
            "most_permissive_count": results_exp1["most_permissive_count"],
        },
        "exp2": {
            "standard": _serialise_result(
                results_exp2["standard"]  # type: ignore[arg-type]
            ),
            "broken": _serialise_result(
                results_exp2["broken"]  # type: ignore[arg-type]
            ),
        },
        "exp3": {
            "priority_result": _serialise_result(
                results_exp3["priority_result"]  # type: ignore[arg-type]
            ),
            "dominance_summary": results_exp3["dominance_summary"],
            "total_joint_states": results_exp3["total_joint_states"],
        },
    }

    # ------------------------------------------------------------------
    # Final console summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 64)
    print("  SUMMARY")
    print("=" * 64)

    all_results = [
        ("EXP1 monotonic_restriction (2-proto)",
         results_exp1["two_protocol"]),
        ("EXP1 monotonic_restriction (3-proto)",
         results_exp1["three_protocol"]),
        ("EXP2 deadlock_freedom (standard)",
         results_exp2["standard"]),
        ("EXP2 deadlock_freedom (broken) [expect VIOLATED]",
         results_exp2["broken"]),
        ("EXP3 priority_ordering",
         results_exp3["priority_result"]),
    ]

    for label, result in all_results:
        verdict = "HOLDS   " if result.holds else "VIOLATED"  # type: ignore[union-attr]
        states = result.states_checked  # type: ignore[union-attr]
        print(f"  {verdict}  {label} ({states} states checked)")

    print(f"\n  Total elapsed: {elapsed:.3f}s")
    print("=" * 64)

    # ------------------------------------------------------------------
    # Write JSON output
    # ------------------------------------------------------------------
    output_dir = Path(__file__).parent.parent / "results" / "precomputed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "run_all_summary.json"

    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(summary, file_handle, indent=2)

    print(f"\n  JSON summary written to: {output_path}")


if __name__ == "__main__":
    main()
