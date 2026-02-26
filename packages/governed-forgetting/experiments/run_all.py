# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""Run all four governed-forgetting experiments in sequence.

SIMULATION ONLY — not production AMGP implementation.
Executes Experiments 1–4 and writes all precomputed results and figures
under ``results/``.

Usage::

    python experiments/run_all.py

    # Skip figure rendering (headless environments without a display)
    python experiments/run_all.py --no-figures
"""

from __future__ import annotations

import argparse
import importlib
import sys
import time
import traceback
from pathlib import Path

# Ensure src/ is on the path so the package is importable without installation
_src = Path(__file__).parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

EXPERIMENTS: list[str] = [
    "exp1_time_based_retention",
    "exp2_relevance_decay",
    "exp3_consent_revocation",
    "exp4_policy_composition",
]


def run_experiment(module_name: str) -> bool:
    """Import and execute a single experiment module's ``main()`` function.

    SIMULATION ONLY — not production AMGP implementation.

    Args:
        module_name: Bare module name (without the ``experiments.`` prefix).

    Returns:
        True on success, False on failure.
    """
    # Add the experiments directory to the path so direct imports work
    experiments_dir = str(Path(__file__).parent)
    if experiments_dir not in sys.path:
        sys.path.insert(0, experiments_dir)

    try:
        module = importlib.import_module(module_name)
        module.main()  # type: ignore[attr-defined]
        return True
    except Exception:
        traceback.print_exc()
        return False


def main() -> None:
    """Entry point — run all experiments and report a summary.

    SIMULATION ONLY — not production AMGP implementation.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run all governed-forgetting experiments (SIMULATION ONLY — "
            "not production AMGP implementation)."
        )
    )
    parser.add_argument(
        "--no-figures",
        action="store_true",
        help="Skip matplotlib figure generation (useful for headless environments).",
    )
    args = parser.parse_args()

    if args.no_figures:
        import matplotlib  # noqa: PLC0415
        matplotlib.use("Agg")  # non-interactive backend

    print("\n" + "=" * 70)
    print(" governed-forgetting — Run All Experiments")
    print(" SIMULATION ONLY — not production AMGP implementation.")
    print("=" * 70 + "\n")

    results: dict[str, bool] = {}
    total_start = time.monotonic()

    for exp_name in EXPERIMENTS:
        print(f"\n{'=' * 70}")
        print(f"  Running: {exp_name}")
        print(f"{'=' * 70}")
        start = time.monotonic()
        success = run_experiment(exp_name)
        elapsed = time.monotonic() - start
        results[exp_name] = success
        status = "PASSED" if success else "FAILED"
        print(f"\n[{status}] {exp_name} ({elapsed:.2f}s)")

    total_elapsed = time.monotonic() - total_start

    print("\n" + "=" * 70)
    print(" Summary")
    print("=" * 70)
    for exp_name, success in results.items():
        icon = "OK  " if success else "FAIL"
        print(f"  {icon}  {exp_name}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n  {passed}/{total} experiments passed in {total_elapsed:.2f}s")
    print("=" * 70 + "\n")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
