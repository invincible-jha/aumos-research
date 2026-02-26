# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
run_all.py — Run all commitment-extractor experiments and save results.

SIMULATION ONLY. Executes all four experiments in sequence, writing each
result to results/precomputed/fig{N}_data.json. All data is SYNTHETIC.

Run from the package root:
    python experiments/run_all.py
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

_EXPERIMENT_MODULES: list[tuple[str, str]] = [
    ("experiments.exp1_basic_extraction", "fig1_data.json"),
    ("experiments.exp2_classification_accuracy", "fig2_data.json"),
    ("experiments.exp3_fulfillment_tracking", "fig3_data.json"),
    ("experiments.exp4_conversation_analysis", "fig4_data.json"),
]


def main() -> None:
    """Run all experiments and persist results. SIMULATION ONLY."""
    print("=" * 62)
    print("commitment-extractor — Run All Experiments")
    print("SIMULATION ONLY — rule-based, synthetic data, seed=42")
    print("=" * 62)

    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "precomputed")
    os.makedirs(output_dir, exist_ok=True)

    total_start = time.time()
    summary: list[dict[str, object]] = []

    for module_path, output_filename in _EXPERIMENT_MODULES:
        print(f"\n{'─' * 62}")
        print(f"Running: {module_path}")
        print(f"{'─' * 62}")

        start = time.time()
        module = importlib.import_module(module_path)
        results = module.run_experiment()
        elapsed = time.time() - start

        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, "w", encoding="utf-8") as file_handle:
            json.dump(results, file_handle, indent=2)

        print(f"\n  Saved: {output_path} ({elapsed:.2f}s)")
        summary.append({
            "module": module_path,
            "output": output_filename,
            "elapsed_seconds": round(elapsed, 3),
            "status": "ok",
        })

    total_elapsed = time.time() - total_start

    print(f"\n{'=' * 62}")
    print("All experiments complete.")
    print(f"Total time: {total_elapsed:.2f}s")
    print("SIMULATION ONLY — all results are synthetic.")
    print(f"{'=' * 62}")

    for entry in summary:
        print(f"  {entry['output']}: {entry['elapsed_seconds']}s")


if __name__ == "__main__":
    main()
