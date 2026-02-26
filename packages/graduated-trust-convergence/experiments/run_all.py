# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
run_all.py — Execute all four experiments and save figures + precomputed JSON.

NOTE: All data generated here is SYNTHETIC simulation output.
This script does NOT access or produce production data of any kind.

Usage
-----
    python experiments/run_all.py [--output-dir PATH] [--no-figures] [--no-json]

Outputs (under results/ by default)
--------------------------------------
    results/figures/fig1_convergence.png
    results/figures/fig2_decay_comparison.png
    results/figures/fig3_multi_scope.png
    results/figures/fig4_adversarial.png
    results/precomputed/fig1_data.json
    results/precomputed/fig2_data.json
    results/precomputed/fig3_data.json
    results/precomputed/fig4_data.json
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_pkg_root = Path(__file__).resolve().parent.parent / "src"
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

# Import experiment runners after path is set
import exp1_basic_convergence
import exp2_decay_impact
import exp3_multi_scope
import exp4_adversarial


def run_all(
    output_dir: Path,
    save_figures: bool = True,
    save_json: bool = True,
) -> None:
    """
    Run all experiments sequentially and report timing.

    NOTE: Runs SYNTHETIC simulations — NOT production workloads.

    Parameters
    ----------
    output_dir:
        Root directory for all output artefacts.
    save_figures:
        Write PNG figures to ``output_dir/figures/``.
    save_json:
        Write JSON data to ``output_dir/precomputed/``.
    """
    experiments = [
        ("Experiment 1 — Basic Convergence (Fig. 1)", exp1_basic_convergence.run_experiment),
        ("Experiment 2 — Decay Impact (Fig. 2)",      exp2_decay_impact.run_experiment),
        ("Experiment 3 — Multi-Scope (Fig. 3)",       exp3_multi_scope.run_experiment),
        ("Experiment 4 — Adversarial (Fig. 4)",       exp4_adversarial.run_experiment),
    ]

    total_start = time.perf_counter()
    all_results: list[tuple[str, dict[str, object], float]] = []

    for name, runner in experiments:
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print("="*60)
        t0 = time.perf_counter()
        result = runner(
            save_figure=save_figures,
            save_json=save_json,
            output_dir=output_dir,
        )
        elapsed = time.perf_counter() - t0
        all_results.append((name, result, elapsed))
        print(f"  Completed in {elapsed:.3f}s")

    total_elapsed = time.perf_counter() - total_start

    print(f"\n{'='*60}")
    print("All experiments complete")
    print(f"{'='*60}")
    print(f"Total runtime: {total_elapsed:.3f}s")

    if save_figures:
        figures_dir = output_dir / "figures"
        print(f"\nFigures saved to: {figures_dir}")
        for fig_file in sorted(figures_dir.glob("*.png")):
            print(f"  {fig_file.name}")

    if save_json:
        precomputed_dir = output_dir / "precomputed"
        print(f"\nPrecomputed data saved to: {precomputed_dir}")
        for json_file in sorted(precomputed_dir.glob("*.json")):
            size_kb = json_file.stat().st_size / 1024
            print(f"  {json_file.name}  ({size_kb:.1f} KB)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run all Paper 13 experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "NOTE: All data is SYNTHETIC simulation output.\n"
            "This script does NOT access production systems or real data."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Root directory for figures and precomputed JSON. "
             "Defaults to <package_root>/results/",
    )
    parser.add_argument(
        "--no-figures",
        action="store_true",
        help="Skip figure generation (useful in headless environments)",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Skip saving precomputed JSON data",
    )
    args = parser.parse_args()

    if args.output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "results"
    else:
        output_dir = args.output_dir

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "figures").mkdir(exist_ok=True)
    (output_dir / "precomputed").mkdir(exist_ok=True)

    run_all(
        output_dir=output_dir,
        save_figures=not args.no_figures,
        save_json=not args.no_json,
    )


if __name__ == "__main__":
    main()
