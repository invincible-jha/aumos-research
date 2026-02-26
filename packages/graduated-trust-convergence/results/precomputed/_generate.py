# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Utility script to regenerate all precomputed JSON files.

NOTE: Generates SYNTHETIC simulation data only — NOT production data.

Run from the package root:
    python results/precomputed/_generate.py

This will overwrite fig1_data.json through fig4_data.json with fresh
deterministic outputs (seed=42).  Run this script whenever the simulation
model is updated and the frozen reference data needs to be refreshed; bump
the package version at the same time.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_pkg_root = Path(__file__).resolve().parent.parent.parent / "src"
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from trust_convergence.agents import (
    AdversarialAgent,
    CompliantAgent,
    DegradingAgent,
    MixedAgent,
)
from trust_convergence.metrics import (
    area_under_trajectory,
    convergence_bound,
    mean_trust_level,
    stability_index,
)
from trust_convergence.model import TrustProgressionModel
from trust_convergence.scenarios import SCENARIOS

TIMESTEPS = 1000
OUT_DIR = Path(__file__).resolve().parent


def _write(path: Path, data: object) -> None:
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)
    size_kb = path.stat().st_size / 1024
    print(f"  Wrote {path.name}  ({size_kb:.1f} KB)")


def generate_fig1() -> None:
    """Generate fig1_data.json — basic convergence, compliant agent."""
    config = SCENARIOS["baseline"]
    model = TrustProgressionModel(config)
    agent = CompliantAgent(quality=0.8, noise_scale=0.05, seed=42)
    result = model.simulate(agent, timesteps=TIMESTEPS)

    bound = convergence_bound(result.trajectory, target_level=result.final_level, tolerance=0.15)
    payload = {
        **result.to_dict(),
        "summary": {
            "experiment": "exp1_basic_convergence",
            "figure": "Fig. 1",
            "scenario": "baseline",
            "agent": "CompliantAgent",
            "agent_quality": 0.8,
            "timesteps": TIMESTEPS,
            "final_level": result.final_level,
            "convergence_rate": result.convergence_rate,
            "stability_index": result.stability,
            "convergence_bound": bound,
            "mean_level_second_half": mean_trust_level(result.trajectory, start=500),
        },
    }
    _write(OUT_DIR / "fig1_data.json", payload)


def generate_fig2() -> None:
    """Generate fig2_data.json — decay and threshold impact."""
    scenarios = ["baseline", "high_decay", "low_threshold"]
    results = {}
    for key in scenarios:
        cfg = SCENARIOS[key]
        mdl = TrustProgressionModel(cfg)
        ag = CompliantAgent(quality=0.8, seed=42)
        results[key] = mdl.simulate(ag, timesteps=TIMESTEPS)

    payload = {
        "results": {k: v.to_dict() for k, v in results.items()},
        "summary": {
            "experiment": "exp2_decay_impact",
            "figure": "Fig. 2",
            "timesteps": TIMESTEPS,
            "scenarios": {
                k: {
                    "final_level": v.final_level,
                    "convergence_rate": v.convergence_rate,
                    "stability_index": v.stability,
                    "mean_level_second_half": mean_trust_level(v.trajectory, start=500),
                    "config": {
                        "decay_rate": v.config.decay_rate,
                        "promotion_threshold": v.config.promotion_threshold,
                    },
                }
                for k, v in results.items()
            },
        },
    }
    _write(OUT_DIR / "fig2_data.json", payload)


def generate_fig3() -> None:
    """Generate fig3_data.json — multi-scope convergence."""
    panels = [
        ("lenient\n(CompliantAgent)", "lenient", CompliantAgent(quality=0.8, seed=42)),
        ("baseline\n(MixedAgent)", "baseline", MixedAgent(alpha=4.0, beta_param=2.0, seed=42)),
        ("strict\n(MixedAgent)", "strict", MixedAgent(alpha=4.0, beta_param=2.0, seed=42)),
        ("wide_scale\n(CompliantAgent)", "wide_scale", CompliantAgent(quality=0.8, seed=42)),
    ]
    results = {}
    for label, sc_key, ag in panels:
        cfg = SCENARIOS[sc_key]
        mdl = TrustProgressionModel(cfg)
        results[label] = mdl.simulate(ag, timesteps=TIMESTEPS)

    payload = {
        "results": {k: v.to_dict() for k, v in results.items()},
        "summary": {
            "experiment": "exp3_multi_scope",
            "figure": "Fig. 3",
            "timesteps": TIMESTEPS,
            "panels": {
                k: {
                    "final_level": v.final_level,
                    "convergence_rate": v.convergence_rate,
                    "stability_index": v.stability,
                    "mean_level": mean_trust_level(v.trajectory),
                    "area_under_curve": area_under_trajectory(v.trajectory),
                    "num_levels": v.config.num_levels,
                }
                for k, v in results.items()
            },
        },
    }
    _write(OUT_DIR / "fig3_data.json", payload)


def generate_fig4() -> None:
    """Generate fig4_data.json — adversarial agent dynamics."""
    config = SCENARIOS["adversarial"]
    model = TrustProgressionModel(config)
    agents = {
        "Compliant": CompliantAgent(quality=0.8, noise_scale=0.05, seed=42),
        "Adversarial": AdversarialAgent(
            good_quality=0.9,
            bad_quality=0.05,
            good_phase_length=60,
            bad_phase_length=25,
            seed=42,
        ),
        "Mixed": MixedAgent(alpha=3.0, beta_param=3.0, seed=42),
        "Degrading": DegradingAgent(
            initial_quality=0.85,
            floor_quality=0.2,
            decay_rate=0.005,
            seed=42,
        ),
    }
    results = {label: model.simulate(ag, timesteps=TIMESTEPS) for label, ag in agents.items()}
    compliant_final = results["Compliant"].final_level

    payload = {
        "results": {k: v.to_dict() for k, v in results.items()},
        "summary": {
            "experiment": "exp4_adversarial",
            "figure": "Fig. 4",
            "scenario": "adversarial",
            "timesteps": TIMESTEPS,
            "agents": {
                label: {
                    "final_level": r.final_level,
                    "convergence_rate": r.convergence_rate,
                    "stability_index": r.stability,
                    "tail_stability_w200": stability_index(r.trajectory, window=200),
                    "convergence_bound_vs_compliant": convergence_bound(
                        r.trajectory, target_level=compliant_final, tolerance=0.2
                    ),
                    "mean_level": mean_trust_level(r.trajectory),
                    "mean_level_second_half": mean_trust_level(r.trajectory, start=500),
                }
                for label, r in results.items()
            },
        },
    }
    _write(OUT_DIR / "fig4_data.json", payload)


def main() -> None:
    print("Regenerating precomputed JSON data (seed=42)...")
    print("NOTE: All data is SYNTHETIC — NOT production data.\n")
    generate_fig1()
    generate_fig2()
    generate_fig3()
    generate_fig4()
    print("\nDone. All four precomputed files updated.")


if __name__ == "__main__":
    main()
