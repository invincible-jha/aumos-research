# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Experiment 3 — Multi-scope convergence across policy configurations (Paper 13, Fig. 3).

NOTE: All data produced here is SYNTHETIC simulation output.
This experiment does NOT use or approximate production trust data.

Reproduces Figure 3 of Paper 13:
    "Side-by-side comparison of trust trajectories under lenient, baseline,
     strict, and wide-scale policies. Stricter policies produce lower
     asymptotic levels; wider level ranges show proportionally similar
     convergence behaviour."

Usage
-----
    python experiments/exp3_multi_scope.py [--save] [--output PATH]

Outputs
-------
    - Console metrics table
    - Optional figure saved to results/figures/fig3_multi_scope.png
    - Optional JSON saved to results/precomputed/fig3_data.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_pkg_root = Path(__file__).resolve().parent.parent / "src"
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from trust_convergence.agents import CompliantAgent, MixedAgent
from trust_convergence.metrics import area_under_trajectory, mean_trust_level
from trust_convergence.model import SimulationResult, TrustProgressionModel
from trust_convergence.scenarios import SCENARIOS
from trust_convergence.visualization import plot_multi_scope

TIMESTEPS = 1000
# Each panel uses a different (scenario, agent) pair for variety
PANELS: list[tuple[str, str]] = [
    ("lenient", "CompliantAgent"),
    ("baseline", "MixedAgent"),
    ("strict", "MixedAgent"),
    ("wide_scale", "CompliantAgent"),
]
AGENT_SEED = 42


def _build_agent(agent_name: str, seed: int = 42) -> CompliantAgent | MixedAgent:
    """Construct an agent by name for this experiment."""
    if agent_name == "CompliantAgent":
        return CompliantAgent(quality=0.8, seed=seed)
    if agent_name == "MixedAgent":
        return MixedAgent(alpha=4.0, beta_param=2.0, seed=seed)
    raise ValueError(f"Unknown agent name: {agent_name!r}")


def run_experiment(
    save_figure: bool = False,
    save_json: bool = False,
    output_dir: Path | None = None,
) -> dict[str, object]:
    """
    Execute Experiment 3 and return a results dictionary.

    NOTE: Returns SYNTHETIC simulation metrics — NOT production data.

    Parameters
    ----------
    save_figure:
        Write the figure to ``results/figures/fig3_multi_scope.png``.
    save_json:
        Write trajectory data to ``results/precomputed/fig3_data.json``.
    output_dir:
        Base directory for output files.

    Returns
    -------
    dict
        Per-panel metrics keyed by panel label.
    """
    results: dict[str, SimulationResult] = {}

    for scenario_key, agent_name in PANELS:
        config = SCENARIOS[scenario_key]
        model = TrustProgressionModel(config)
        agent = _build_agent(agent_name, seed=AGENT_SEED)
        panel_label = f"{scenario_key}\n({agent_name})"
        results[panel_label] = model.simulate(agent, timesteps=TIMESTEPS)

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "results"

    fig_path = (
        str(output_dir / "figures" / "fig3_multi_scope.png")
        if save_figure
        else None
    )
    plot_multi_scope(results, save_path=fig_path)

    summary: dict[str, object] = {
        "experiment": "exp3_multi_scope",
        "figure": "Fig. 3",
        "timesteps": TIMESTEPS,
        "panels": {},
    }

    serialised_results: dict[str, dict[str, object]] = {}
    panel_summaries: dict[str, dict[str, object]] = {}

    for label, result in results.items():
        panel_summaries[label] = {
            "scenario": label,
            "final_level": result.final_level,
            "convergence_rate": result.convergence_rate,
            "stability_index": result.stability,
            "mean_level": mean_trust_level(result.trajectory),
            "area_under_curve": area_under_trajectory(result.trajectory),
            "num_levels": result.config.num_levels,
        }
        serialised_results[label] = result.to_dict()

    summary["panels"] = panel_summaries

    if save_json:
        json_path = output_dir / "precomputed" / "fig3_data.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"results": serialised_results, "summary": summary}
        with json_path.open("w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"Saved precomputed data -> {json_path}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 3: multi-scope")
    parser.add_argument("--save", action="store_true", help="Save figure and JSON")
    parser.add_argument("--output", type=Path, default=None, help="Output base directory")
    args = parser.parse_args()

    summary = run_experiment(
        save_figure=args.save,
        save_json=args.save,
        output_dir=args.output,
    )

    print("\n=== Experiment 3: Multi-Scope Convergence ===")
    panels = summary.get("panels", {})
    assert isinstance(panels, dict)
    for label, metrics in panels.items():
        assert isinstance(metrics, dict)
        clean_label = label.replace("\n", " ")
        print(
            f"  [{clean_label}]"
            f"  levels={metrics['num_levels']}"
            f"  final={metrics['final_level']:.3f}"
            f"  rate={metrics['convergence_rate']:.5f}"
            f"  auc={metrics['area_under_curve']:.3f}"
        )


if __name__ == "__main__":
    main()
