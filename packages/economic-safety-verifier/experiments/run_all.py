# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
run_all.py — Run all Paper 22 experiments and generate all figures.

SIMULATION ONLY. Executes exp1, exp2, and exp3 in sequence, writing all
pre-computed JSON data to results/precomputed/ and all figures to
results/figures/.

Usage::

    python experiments/run_all.py

All results are SYNTHETIC and deterministic with seed=42.
"""

from __future__ import annotations

import importlib
import os
import sys
import time

# Ensure the package source is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

EXPERIMENTS = [
    ("exp1_no_overspend", "Exp 1: No-Overspend Property (Fig 1)"),
    ("exp2_commitment_safety", "Exp 2: Commitment Safety (Fig 2)"),
    ("exp3_concurrent_spending", "Exp 3: Concurrent Spending (Fig 3)"),
]


def run_all() -> None:
    """Execute all experiments sequentially.

    SIMULATION ONLY. All data is SYNTHETIC. All results use seed=42.
    """
    print("=" * 65)
    print("AumOS Research — Economic Safety Verifier")
    print("Paper 22 — All Experiments")
    print("SIMULATION ONLY — all data is synthetic, seed=42")
    print("=" * 65)

    experiments_dir = os.path.dirname(__file__)
    total_start = time.perf_counter()
    results: list[tuple[str, bool, float]] = []

    for module_name, description in EXPERIMENTS:
        print(f"\n--- {description} ---")
        start = time.perf_counter()
        success = False
        try:
            # Import and run the experiment module's main()
            spec = importlib.util.spec_from_file_location(  # type: ignore[attr-defined]
                module_name,
                os.path.join(experiments_dir, f"{module_name}.py"),
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load {module_name}")
            module = importlib.util.module_from_spec(spec)  # type: ignore[attr-defined]
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            module.main()
            success = True
        except Exception as exc:
            print(f"ERROR in {module_name}: {exc}")
        elapsed = time.perf_counter() - start
        results.append((module_name, success, elapsed))

    total_elapsed = time.perf_counter() - total_start

    print("\n" + "=" * 65)
    print("Summary")
    print("=" * 65)
    for module_name, success, elapsed in results:
        status = "OK" if success else "FAILED"
        print(f"  {status:6s}  {module_name:<35s}  {elapsed:.2f}s")

    print(f"\nTotal: {total_elapsed:.2f}s")
    print("\nPre-computed data: results/precomputed/fig{{1,2,3}}_data.json")
    print("Figures:           results/figures/")
    print("\nNOTE: All results are SIMULATION ONLY — synthetic data.")


if __name__ == "__main__":
    run_all()
