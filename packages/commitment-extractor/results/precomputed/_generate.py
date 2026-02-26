# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
_generate.py — Regenerate all precomputed figure data files for commitment-extractor.

SIMULATION ONLY. Run this script to rebuild fig1_data.json through
fig4_data.json from the experiment modules. All data is SYNTHETIC.
Requires the commitment_extractor package to be installed or the src/ directory
to be on PYTHONPATH.

Run from the package root:
    python results/precomputed/_generate.py
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_PACKAGE_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_SRC_DIR = os.path.join(_PACKAGE_ROOT, "src")

if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
if _PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, _PACKAGE_ROOT)

_EXPERIMENTS: list[tuple[str, str]] = [
    ("experiments.exp1_basic_extraction", "fig1_data.json"),
    ("experiments.exp2_classification_accuracy", "fig2_data.json"),
    ("experiments.exp3_fulfillment_tracking", "fig3_data.json"),
    ("experiments.exp4_conversation_analysis", "fig4_data.json"),
]


def main() -> None:
    """Regenerate all precomputed data files. SIMULATION ONLY."""
    print("=" * 62)
    print("commitment-extractor — Regenerate Precomputed Data")
    print("SIMULATION ONLY — rule-based, synthetic data, seed=42")
    print("=" * 62)

    total_start = time.time()

    for module_path, filename in _EXPERIMENTS:
        output_path = os.path.join(_HERE, filename)
        print(f"\nRunning {module_path} ...")
        start = time.time()

        module = importlib.import_module(module_path)
        results = module.run_experiment()
        elapsed = time.time() - start

        with open(output_path, "w", encoding="utf-8") as file_handle:
            json.dump(results, file_handle, indent=2)

        print(f"  Wrote {output_path} ({elapsed:.2f}s)")

    total_elapsed = time.time() - total_start
    print(f"\nAll files regenerated in {total_elapsed:.2f}s.")
    print("SIMULATION ONLY — seed=42, all results are synthetic.")


if __name__ == "__main__":
    main()
