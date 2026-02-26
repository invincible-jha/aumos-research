# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Experiment 1 — Basic convergence of a compliant agent (Paper 13, Fig. 1).

NOTE: All data produced here is SYNTHETIC simulation output.
This experiment does NOT use or approximate production trust data.

Reproduces Figure 1 of Paper 13:
    "A single compliant agent progressing through trust levels under the
     baseline policy. The trajectory demonstrates monotone convergence to
     the asymptotic trust level within approximately 500 timesteps."

Usage
-----
    python experiments/exp1_basic_convergence.py [--save] [--output PATH]

Outputs
-------
    - Console metrics summary
    - Optional figure saved to results/figures/fig1_convergence.png
    - Optional JSON saved to results/precomputed/fig1_data.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running directly without installing the package
_pkg_root = Path(__file__).resolve().parent.parent / "src"
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from trust_convergence.agents import CompliantAgent
from trust_convergence.metrics import (
    convergence_bound,
    mean_trust_level,
    stability_index,
)
from trust_convergence.model import TrustProgressionModel
from trust_convergence.scenarios import SCENARIOS
from trust_convergence.visualization import plot_convergence

TIMESTEPS = 1000
SCENARIO_KEY = "baseline"
AGENT_QUALITY = 0.8
AGENT_NOISE = 0.05
AGENT_SEED = 42


def run_experiment(
    save_figure: bool = False,
    save_json: bool = False,
    output_dir: Path | None = None,
) -> dict[str, object]:
    """
    Execute Experiment 1 and return a summary dictionary.

    NOTE: Returns SYNTHETIC simulation metrics — NOT production data.

    Parameters
    ----------
    save_figure:
        Write the figure to ``results/figures/fig1_convergence.png``.
    save_json:
        Write trajectory data to ``results/precomputed/fig1_data.json``.
    output_dir:
        Base directory for output files. Defaults to the ``results/`` folder
        adjacent to this script.

    Returns
    -------
    dict
        Metrics summary with keys: scenario, agent, final_level,
        convergence_rate, stability, convergence_bound, mean_level.
    """
    config = SCENARIOS[SCENARIO_KEY]
    model = TrustProgressionModel(config)
    agent = CompliantAgent(quality=AGENT_QUALITY, noise_scale=AGENT_NOISE, seed=AGENT_SEED)

    result = model.simulate(agent, timesteps=TIMESTEPS)

    # Convergence bound: within 0.15 of final level
    target = result.final_level
    bound = convergence_bound(result.trajectory, target_level=target, tolerance=0.15)
    mean_level = mean_trust_level(result.trajectory, start=TIMESTEPS // 2)

    summary: dict[str, object] = {
        "experiment": "exp1_basic_convergence",
        "figure": "Fig. 1",
        "scenario": SCENARIO_KEY,
        "agent": "CompliantAgent",
        "agent_quality": AGENT_QUALITY,
        "timesteps": TIMESTEPS,
        "final_level": result.final_level,
        "convergence_rate": result.convergence_rate,
        "stability_index": result.stability,
        "convergence_bound": bound,
        "mean_level_second_half": mean_level,
        "config": {
            "num_levels": config.num_levels,
            "decay_rate": config.decay_rate,
            "promotion_threshold": config.promotion_threshold,
            "seed": config.seed,
        },
    }

    # --- Figure ---
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "results"

    fig_path = str(output_dir / "figures" / "fig1_convergence.png") if save_figure else None

    plot_convergence(
        result,
        title="Basic Trust Convergence — Compliant Agent (Paper 13, Fig. 1)",
        save_path=fig_path,
    )

    # --- JSON ---
    if save_json:
        json_path = output_dir / "precomputed" / "fig1_data.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        payload["summary"] = summary
        with json_path.open("w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"Saved precomputed data -> {json_path}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 1: basic convergence")
    parser.add_argument("--save", action="store_true", help="Save figure and JSON")
    parser.add_argument("--output", type=Path, default=None, help="Output base directory")
    args = parser.parse_args()

    summary = run_experiment(
        save_figure=args.save,
        save_json=args.save,
        output_dir=args.output,
    )

    print("\n=== Experiment 1: Basic Convergence ===")
    print(f"  Scenario:              {summary['scenario']}")
    print(f"  Agent:                 {summary['agent']}  (quality={summary['agent_quality']})")
    print(f"  Timesteps:             {summary['timesteps']}")
    print(f"  Final trust level:     {summary['final_level']:.4f}")
    print(f"  Convergence rate:      {summary['convergence_rate']:.6f}")
    print(f"  Stability index:       {summary['stability_index']:.6f}")
    print(f"  Convergence bound:     {summary['convergence_bound']}")
    print(f"  Mean level (2nd half): {summary['mean_level_second_half']:.4f}")


if __name__ == "__main__":
    main()
