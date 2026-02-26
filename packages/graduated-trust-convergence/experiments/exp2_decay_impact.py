# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Experiment 2 — Impact of decay rate and promotion threshold (Paper 13, Fig. 2).

NOTE: All data produced here is SYNTHETIC simulation output.
This experiment does NOT use or approximate production trust data.

Reproduces Figure 2 of Paper 13:
    "Overlaid trajectories for the baseline, high-decay, and low-threshold
     scenarios demonstrate that increased decay substantially reduces the
     asymptotic trust level while a reduced threshold slows progression."

Usage
-----
    python experiments/exp2_decay_impact.py [--save] [--output PATH]

Outputs
-------
    - Console metrics table
    - Optional figure saved to results/figures/fig2_decay_comparison.png
    - Optional JSON saved to results/precomputed/fig2_data.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_pkg_root = Path(__file__).resolve().parent.parent / "src"
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from trust_convergence.agents import CompliantAgent
from trust_convergence.metrics import mean_trust_level
from trust_convergence.model import TrustProgressionModel
from trust_convergence.scenarios import SCENARIOS
from trust_convergence.visualization import plot_decay_comparison

TIMESTEPS = 1000
SCENARIO_KEYS = ["baseline", "high_decay", "low_threshold"]
AGENT_QUALITY = 0.8
AGENT_SEED = 42


def run_experiment(
    save_figure: bool = False,
    save_json: bool = False,
    output_dir: Path | None = None,
) -> dict[str, object]:
    """
    Execute Experiment 2 and return a results dictionary.

    NOTE: Returns SYNTHETIC simulation metrics — NOT production data.

    Parameters
    ----------
    save_figure:
        Write the figure to ``results/figures/fig2_decay_comparison.png``.
    save_json:
        Write trajectory data to ``results/precomputed/fig2_data.json``.
    output_dir:
        Base directory for output files.

    Returns
    -------
    dict
        Per-scenario metrics keyed by scenario name.
    """
    from trust_convergence.model import SimulationResult

    results: dict[str, SimulationResult] = {}

    for key in SCENARIO_KEYS:
        config = SCENARIOS[key]
        model = TrustProgressionModel(config)
        # Fresh agent per scenario so RNG is independent
        agent = CompliantAgent(quality=AGENT_QUALITY, seed=AGENT_SEED)
        results[key] = model.simulate(agent, timesteps=TIMESTEPS)

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "results"

    fig_path = (
        str(output_dir / "figures" / "fig2_decay_comparison.png")
        if save_figure
        else None
    )
    plot_decay_comparison(results, save_path=fig_path)

    summary: dict[str, object] = {
        "experiment": "exp2_decay_impact",
        "figure": "Fig. 2",
        "timesteps": TIMESTEPS,
        "scenarios": {},
    }

    serialised_results: dict[str, dict[str, object]] = {}
    for key, result in results.items():
        scenario_summary = {
            "final_level": result.final_level,
            "convergence_rate": result.convergence_rate,
            "stability_index": result.stability,
            "mean_level_second_half": mean_trust_level(result.trajectory, start=TIMESTEPS // 2),
            "config": {
                "decay_rate": result.config.decay_rate,
                "promotion_threshold": result.config.promotion_threshold,
            },
        }
        summary["scenarios"] = {**summary.get("scenarios", {}), key: scenario_summary}  # type: ignore[arg-type]
        serialised_results[key] = result.to_dict()

    if save_json:
        json_path = output_dir / "precomputed" / "fig2_data.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"results": serialised_results, "summary": summary}
        with json_path.open("w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"Saved precomputed data -> {json_path}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 2: decay impact")
    parser.add_argument("--save", action="store_true", help="Save figure and JSON")
    parser.add_argument("--output", type=Path, default=None, help="Output base directory")
    args = parser.parse_args()

    summary = run_experiment(
        save_figure=args.save,
        save_json=args.save,
        output_dir=args.output,
    )

    print("\n=== Experiment 2: Decay and Threshold Impact ===")
    col_width = 18
    header = f"{'Scenario':<{col_width}} {'Final level':>12} {'Conv. rate':>12} {'Stability':>12} {'Mean (2H)':>12}"
    print(header)
    print("-" * len(header))
    scenarios_data = summary.get("scenarios", {})
    assert isinstance(scenarios_data, dict)
    for key, metrics in scenarios_data.items():
        assert isinstance(metrics, dict)
        print(
            f"{key:<{col_width}} "
            f"{metrics['final_level']:>12.4f} "
            f"{metrics['convergence_rate']:>12.6f} "
            f"{metrics['stability_index']:>12.6f} "
            f"{metrics['mean_level_second_half']:>12.4f}"
        )


if __name__ == "__main__":
    main()
