# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Trust progression simulation model.

NOTE: This is a SIMULATION model for research reproduction.
It does NOT contain the production trust progression algorithm.
The simulation uses simplified linear dynamics for academic analysis only.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

from trust_convergence.agents import AgentBehavior
from trust_convergence.metrics import convergence_rate, stability_index


@dataclass(frozen=True)
class SimulationConfig:
    """
    Configuration for the trust progression simulation.

    All parameters here describe a SIMPLIFIED academic model, NOT production settings.

    Attributes
    ----------
    num_levels:
        Number of discrete trust levels (L0 through L_{n-1}). Default 6 gives
        levels L0–L5 as described in Paper 13, Section 3.1.
    decay_rate:
        Amount by which trust decays each timestep in the absence of positive
        actions. Models the idea that trust must be continuously reinforced.
    promotion_threshold:
        Scaling factor applied to the agent's raw action quality before it is
        added to the current trust value. Controls how quickly good behaviour
        translates to level advancement.
    seed:
        Random seed for the model's internal RNG. Use ``seed=42`` to reproduce
        the paper's exact trajectories.
    """

    num_levels: int = 6
    decay_rate: float = 0.01
    promotion_threshold: float = 0.1
    seed: int = 42


@dataclass
class SimulationResult:
    """
    Output of a single simulation run.

    NOTE: All fields are derived from SYNTHETIC agent behavior — NOT production data.

    Attributes
    ----------
    trajectory:
        Array of shape ``(timesteps,)`` holding the trust level at each step.
    convergence_rate:
        Scalar summary of how quickly the trajectory stabilises. See
        :func:`trust_convergence.metrics.convergence_rate`.
    final_level:
        Trust level recorded at the last timestep.
    stability:
        Variance-based stability index over the trajectory tail. See
        :func:`trust_convergence.metrics.stability_index`.
    config:
        The :class:`SimulationConfig` used to produce this result.
    agent_name:
        Human-readable label for the agent type used.
    """

    trajectory: npt.NDArray[np.float64]
    convergence_rate: float
    final_level: float
    stability: float
    config: SimulationConfig = field(default_factory=SimulationConfig)
    agent_name: str = "unknown"

    def to_dict(self) -> dict[str, object]:
        """
        Serialise the result to a JSON-compatible dictionary.

        Returns
        -------
        dict
            All fields with the trajectory represented as a list of floats.
        """
        return {
            "trajectory": self.trajectory.tolist(),
            "convergence_rate": self.convergence_rate,
            "final_level": self.final_level,
            "stability": self.stability,
            "agent_name": self.agent_name,
            "config": {
                "num_levels": self.config.num_levels,
                "decay_rate": self.config.decay_rate,
                "promotion_threshold": self.config.promotion_threshold,
                "seed": self.config.seed,
            },
        }


class TrustProgressionModel:
    """
    Simulate trust progression under various policies.

    NOTE: This is a SIMULATION model for research reproduction.
    It does NOT contain the production trust progression algorithm.
    The simulation uses simplified linear dynamics for academic analysis.

    The update rule at each timestep ``t`` is::

        level[t] = clip(
            level[t-1] + action_quality(t) * promotion_threshold - decay_rate,
            0,
            num_levels - 1,
        )

    This linear model is sufficient to reproduce the convergence properties
    analysed in Paper 13 without encoding any production system logic.

    Parameters
    ----------
    config:
        A :class:`SimulationConfig` describing the policy parameters.

    Examples
    --------
    >>> from trust_convergence.scenarios import SCENARIOS
    >>> from trust_convergence.agents import CompliantAgent
    >>> model = TrustProgressionModel(SCENARIOS["baseline"])
    >>> result = model.simulate(CompliantAgent(quality=0.8, seed=42), timesteps=500)
    >>> result.final_level > 0
    True
    """

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.num_levels: int = config.num_levels
        self.decay_rate: float = config.decay_rate
        self.promotion_threshold: float = config.promotion_threshold
        self.rng: np.random.RandomState = np.random.RandomState(config.seed)  # noqa: NPY002

    def simulate(
        self,
        agent_behavior: AgentBehavior,
        timesteps: int = 1000,
    ) -> SimulationResult:
        """
        Run a single simulation episode.

        NOTE: Uses SIMPLIFIED dynamics — NOT the production algorithm.

        The trajectory starts at trust level 0.0 and evolves according to
        the linear update rule described in the class docstring.

        Parameters
        ----------
        agent_behavior:
            A behaviour generator that produces a quality value in ``[0, 1]``
            for each timestep.
        timesteps:
            Number of steps to simulate. Paper 13 uses 1000 for all figures.

        Returns
        -------
        SimulationResult
            Trajectory and derived metrics for this episode.
        """
        trajectory: npt.NDArray[np.float64] = np.zeros(timesteps, dtype=np.float64)
        current_level: float = 0.0

        for t in range(timesteps):
            action_quality: float = agent_behavior.generate(t)
            current_level += action_quality * self.promotion_threshold
            current_level -= self.decay_rate
            current_level = float(
                np.clip(current_level, 0.0, float(self.num_levels - 1))
            )
            trajectory[t] = current_level

        return SimulationResult(
            trajectory=trajectory,
            convergence_rate=convergence_rate(trajectory),
            final_level=float(trajectory[-1]),
            stability=stability_index(trajectory),
            config=self.config,
            agent_name=type(agent_behavior).__name__,
        )

    def simulate_batch(
        self,
        agent_behavior: AgentBehavior,
        num_runs: int,
        timesteps: int = 1000,
    ) -> list[SimulationResult]:
        """
        Run multiple independent simulation episodes.

        NOTE: Uses SIMPLIFIED dynamics — NOT the production algorithm.
        All runs share the model's RNG state, so results are fully deterministic
        given the config seed.

        Parameters
        ----------
        agent_behavior:
            Behaviour generator. Its internal RNG is NOT reset between runs;
            pass a fresh instance per batch for full independence.
        num_runs:
            Number of independent episodes.
        timesteps:
            Steps per episode.

        Returns
        -------
        list[SimulationResult]
            One result per episode, in order.
        """
        return [self.simulate(agent_behavior, timesteps) for _ in range(num_runs)]
