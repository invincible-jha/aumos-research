# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation

# @title Graduated Trust Convergence — Quick Start
# Run this cell-by-cell in Google Colab to explore the simulation.

# ── Cell 1: Install ────────────────────────────────────────────────────────────
# !pip install aumos-graduated-trust-convergence matplotlib numpy

# ── Cell 2: Imports ────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import NamedTuple

np.random.seed(42)


# ── Cell 3: Minimal inline simulation (no package required) ───────────────────

class TrustState(NamedTuple):
    agent_id: str
    current_level: int
    observation_count: int
    convergence_achieved: bool


def simulate_trust_convergence(
    num_agents: int,
    max_steps: int,
    noise_scale: float = 0.1,
) -> list[list[float]]:
    """Simulate graduated trust convergence over discrete time steps.

    Returns one trajectory per agent (list of trust levels, 0.0–5.0).
    """
    trajectories: list[list[float]] = []
    for agent_idx in range(num_agents):
        trust = float(np.random.randint(0, 3))
        trajectory = [trust]
        for _ in range(max_steps - 1):
            noise = np.random.normal(0.0, noise_scale)
            # Simplified convergence dynamics: trust drifts toward target
            target = 3.0 + agent_idx * 0.4
            delta = 0.3 * (target - trust) + noise
            trust = float(np.clip(trust + delta, 0.0, 5.0))
            trajectory.append(trust)
        trajectories.append(trajectory)
    return trajectories


# ── Cell 4: Run the simulation ─────────────────────────────────────────────────
NUM_AGENTS = 5
MAX_STEPS = 30

trajectories = simulate_trust_convergence(NUM_AGENTS, MAX_STEPS)

print("Graduated Trust Convergence Simulation")
print("=" * 40)
for agent_idx, traj in enumerate(trajectories):
    final_level = traj[-1]
    converged = abs(final_level - traj[-5]) < 0.15 if len(traj) >= 5 else False
    state = TrustState(
        agent_id=f"agent_{agent_idx}",
        current_level=int(final_level),
        observation_count=MAX_STEPS,
        convergence_achieved=converged,
    )
    print(f"  {state.agent_id}: level={final_level:.2f}  converged={state.convergence_achieved}")


# ── Cell 5: Visualisation ──────────────────────────────────────────────────────
steps = list(range(MAX_STEPS))
colors = plt.cm.viridis(np.linspace(0.2, 0.9, NUM_AGENTS))  # type: ignore[attr-defined]

fig, ax = plt.subplots(figsize=(10, 5))
for agent_idx, (traj, color) in enumerate(zip(trajectories, colors)):
    ax.plot(steps, traj, color=color, linewidth=1.8, label=f"Agent {agent_idx}")

ax.axhline(y=3.0, color="gray", linestyle="--", linewidth=1, alpha=0.6, label="Reference L3")
ax.set_xlabel("Observation Step")
ax.set_ylabel("Trust Level (0–5)")
ax.set_title("Graduated Trust Convergence — Synthetic Simulation")
ax.legend(loc="lower right", fontsize=8)
ax.set_ylim(-0.2, 5.5)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("graduated_trust_convergence.png", dpi=120)
plt.show()
print("Figure saved: graduated_trust_convergence.png")


# ── Next Steps ─────────────────────────────────────────────────────────────────
# - See packages/graduated-trust-convergence/README.md for full API documentation
# - Explore csa_mapping.py for CSA Agentic Trust Framework compliance mappings
# - Run the full test suite: pytest packages/graduated-trust-convergence/
