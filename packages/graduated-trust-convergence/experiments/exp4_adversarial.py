# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Experiment 4 — Trust dynamics under adversarial agent strategies (Paper 13, Fig. 4).

NOTE: All data produced here is SYNTHETIC simulation output.
This experiment does NOT use or approximate production trust data.
The adversarial patterns are mathematically constructed, not empirical.

Reproduces Figure 4 of Paper 13:
    "Comparison of four agent types under the adversarial scenario policy.
     The adversarial agent achieves periodic trust inflation while the
     degrading agent's trajectory diverges from the compliant baseline
     after approximately 300 timesteps."

Usage
-----
    python experiments/exp4_adversarial.py [--save] [--output PATH]

Outputs
-------
    - Console metrics table
    - Optional figure saved to results/figures/fig4_adversarial.png
    - Optional JSON saved to results/precomputed/fig4_data.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_pkg_root = Path(__file__).resolve().parent.parent / "src"
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from trust_convergence.agents import (
    AdversarialAgent,
    AgentBehavior,
    CompliantAgent,
    DegradingAgent,
    MixedAgent,
)
from trust_convergence.metrics import (
    convergence_bound,
    mean_trust_level,
    stability_index,
)
from trust_convergence.model import SimulationResult, TrustProgressionModel
from trust_convergence.scenarios import SCENARIOS
from trust_convergence.visualization import plot_adversarial

TIMESTEPS = 1000
SCENARIO_KEY = "adversarial"
AGENT_SEED = 42


def _build_agents(seed: int) -> dict[str, AgentBehavior]:
    """Construct the four agent variants used in this experiment."""
    return {
        "Compliant": CompliantAgent(quality=0.8, noise_scale=0.05, seed=seed),
        "Adversarial": AdversarialAgent(
            good_quality=0.9,
            bad_quality=0.05,
            good_phase_length=60,
            bad_phase_length=25,
            seed=seed,
        ),
        "Mixed": MixedAgent(alpha=3.0, beta_param=3.0, seed=seed),
        "Degrading": DegradingAgent(
            initial_quality=0.85,
            floor_quality=0.2,
            decay_rate=0.005,
            seed=seed,
        ),
    }


def run_experiment(
    save_figure: bool = False,
    save_json: bool = False,
    output_dir: Path | None = None,
) -> dict[str, object]:
    """
    Execute Experiment 4 and return a results dictionary.

    NOTE: Returns SYNTHETIC simulation metrics — NOT production data.

    Parameters
    ----------
    save_figure:
        Write the figure to ``results/figures/fig4_adversarial.png``.
    save_json:
        Write trajectory data to ``results/precomputed/fig4_data.json``.
    output_dir:
        Base directory for output files.

    Returns
    -------
    dict
        Per-agent metrics keyed by agent label.
    """
    config = SCENARIOS[SCENARIO_KEY]
    model = TrustProgressionModel(config)
    agents = _build_agents(seed=AGENT_SEED)

    results: dict[str, SimulationResult] = {}
    for label, agent in agents.items():
        results[label] = model.simulate(agent, timesteps=TIMESTEPS)

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "results"

    fig_path = (
        str(output_dir / "figures" / "fig4_adversarial.png")
        if save_figure
        else None
    )
    plot_adversarial(results, save_path=fig_path)

    summary: dict[str, object] = {
        "experiment": "exp4_adversarial",
        "figure": "Fig. 4",
        "scenario": SCENARIO_KEY,
        "timesteps": TIMESTEPS,
        "agents": {},
    }

    serialised_results: dict[str, dict[str, object]] = {}
    agent_summaries: dict[str, dict[str, object]] = {}

    for label, result in results.items():
        # Find convergence bound relative to the compliant agent's final level
        compliant_final = results["Compliant"].final_level
        bound = convergence_bound(result.trajectory, target_level=compliant_final, tolerance=0.2)
        tail_stability = stability_index(result.trajectory, window=200)

        agent_summaries[label] = {
            "final_level": result.final_level,
            "convergence_rate": result.convergence_rate,
            "stability_index": result.stability,
            "tail_stability_w200": tail_stability,
            "convergence_bound_vs_compliant": bound,
            "mean_level": mean_trust_level(result.trajectory),
            "mean_level_second_half": mean_trust_level(result.trajectory, start=TIMESTEPS // 2),
        }
        serialised_results[label] = result.to_dict()

    summary["agents"] = agent_summaries

    if save_json:
        json_path = output_dir / "precomputed" / "fig4_data.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"results": serialised_results, "summary": summary}
        with json_path.open("w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"Saved precomputed data -> {json_path}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 4: adversarial dynamics")
    parser.add_argument("--save", action="store_true", help="Save figure and JSON")
    parser.add_argument("--output", type=Path, default=None, help="Output base directory")
    args = parser.parse_args()

    summary = run_experiment(
        save_figure=args.save,
        save_json=args.save,
        output_dir=args.output,
    )

    print("\n=== Experiment 4: Adversarial Trust Dynamics ===")
    agents_data = summary.get("agents", {})
    assert isinstance(agents_data, dict)

    col_w = 14
    header = (
        f"{'Agent':<{col_w}} {'Final':>8} {'Conv.rate':>10} "
        f"{'Stability':>10} {'TailStab':>10} {'Mean(2H)':>10}"
    )
    print(header)
    print("-" * len(header))

    for label, metrics in agents_data.items():
        assert isinstance(metrics, dict)
        print(
            f"{label:<{col_w}} "
            f"{metrics['final_level']:>8.4f} "
            f"{metrics['convergence_rate']:>10.6f} "
            f"{metrics['stability_index']:>10.6f} "
            f"{metrics['tail_stability_w200']:>10.6f} "
            f"{metrics['mean_level_second_half']:>10.4f}"
        )


if __name__ == "__main__":
    main()
