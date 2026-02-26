# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Synthetic agent behavior generators.

NOTE: These classes generate SYNTHETIC action quality values for simulation only.
They do NOT model real agent behavior, production systems, or empirical data.
All outputs are mathematically constructed to exercise the simulation dynamics
described in Paper 13.
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod


class AgentBehavior(ABC):
    """
    Abstract base class for synthetic agent behavior generators.

    NOTE: SIMULATION use only — NOT a representation of real agent behavior.

    Each concrete subclass encodes a stylised behavioral pattern sufficient
    to demonstrate a specific convergence property analysed in Paper 13.
    Action quality values are bounded to ``[0, 1]``.
    """

    @abstractmethod
    def generate(self, timestep: int) -> float:
        """
        Generate an action quality value for the given timestep.

        Parameters
        ----------
        timestep:
            Current simulation timestep (0-indexed).

        Returns
        -------
        float
            A quality value in ``[0, 1]`` where 1.0 is the highest possible
            quality and 0.0 represents a completely unhelpful or harmful action.
        """

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class CompliantAgent(AgentBehavior):
    """
    Agent that consistently produces high-quality actions with minor noise.

    NOTE: SYNTHETIC behavior — NOT a real agent or production model.

    Models an agent that has already been calibrated to produce reliable,
    high-quality outputs. A small Gaussian noise term prevents the trajectory
    from being perfectly deterministic, which is more realistic than a pure
    constant-quality agent.

    Parameters
    ----------
    quality:
        Mean action quality, in ``[0, 1]``. Default ``0.8``.
    noise_scale:
        Standard deviation of zero-mean Gaussian noise added each step.
        Default ``0.05``.
    seed:
        Random seed for reproducibility.

    Examples
    --------
    >>> agent = CompliantAgent(quality=0.9, noise_scale=0.02, seed=42)
    >>> 0.0 <= agent.generate(0) <= 1.0
    True
    """

    def __init__(
        self,
        quality: float = 0.8,
        noise_scale: float = 0.05,
        seed: int = 0,
    ) -> None:
        import numpy as np  # local import keeps top-level import-free

        self.quality = quality
        self.noise_scale = noise_scale
        self._rng = np.random.RandomState(seed)  # noqa: NPY002

    def generate(self, timestep: int) -> float:  # noqa: ARG002
        """
        Return quality with small Gaussian noise, clamped to ``[0, 1]``.

        NOTE: SYNTHETIC — not derived from empirical data.
        """
        import numpy as np

        raw = self.quality + self._rng.normal(0.0, self.noise_scale)
        return float(np.clip(raw, 0.0, 1.0))


class AdversarialAgent(AgentBehavior):
    """
    Agent that alternates between high-quality and low-quality actions.

    NOTE: SYNTHETIC behavior — NOT a real adversarial agent.

    Models a strategically adversarial actor that performs well for
    ``good_phase_length`` steps to accumulate trust, then performs poorly
    for ``bad_phase_length`` steps, cycling repeatedly. This pattern
    exercises the trust system's resistance to manipulation.

    Parameters
    ----------
    good_quality:
        Action quality during the cooperative phase. Default ``0.9``.
    bad_quality:
        Action quality during the adversarial phase. Default ``0.05``.
    good_phase_length:
        Duration of the cooperative phase in timesteps. Default ``50``.
    bad_phase_length:
        Duration of the adversarial phase in timesteps. Default ``20``.
    seed:
        Random seed. The noise term uses this seed.
    noise_scale:
        Small noise added to each quality value to avoid exact periodicity.

    Examples
    --------
    >>> agent = AdversarialAgent(good_phase_length=10, bad_phase_length=5)
    >>> # First 10 steps should be high quality
    >>> all(agent.generate(t) > 0.5 for t in range(10))
    True
    """

    def __init__(
        self,
        good_quality: float = 0.9,
        bad_quality: float = 0.05,
        good_phase_length: int = 50,
        bad_phase_length: int = 20,
        noise_scale: float = 0.03,
        seed: int = 0,
    ) -> None:
        import numpy as np

        self.good_quality = good_quality
        self.bad_quality = bad_quality
        self.good_phase_length = good_phase_length
        self.bad_phase_length = bad_phase_length
        self.noise_scale = noise_scale
        self._rng = np.random.RandomState(seed)  # noqa: NPY002
        self._cycle_length = good_phase_length + bad_phase_length

    def generate(self, timestep: int) -> float:
        """
        Return quality based on which phase of the cycle the timestep falls in.

        NOTE: SYNTHETIC adversarial pattern — NOT empirical data.
        """
        import numpy as np

        phase_position = timestep % self._cycle_length
        base_quality = (
            self.good_quality
            if phase_position < self.good_phase_length
            else self.bad_quality
        )
        noisy = base_quality + self._rng.normal(0.0, self.noise_scale)
        return float(np.clip(noisy, 0.0, 1.0))


class MixedAgent(AgentBehavior):
    """
    Agent with probabilistic behavior quality drawn from a Beta distribution.

    NOTE: SYNTHETIC behavior — NOT a model of real agent uncertainty.

    At each timestep, action quality is sampled independently from a
    Beta(alpha, beta) distribution. The Beta distribution is parameterised so
    that ``mean = alpha / (alpha + beta)``, giving fine control over the
    expected quality and its variance.

    Parameters
    ----------
    alpha:
        Beta distribution shape parameter controlling the upper tail.
        Higher values push the mean toward 1. Default ``4.0``.
    beta_param:
        Beta distribution shape parameter controlling the lower tail.
        Higher values push the mean toward 0. Default ``2.0``.
    seed:
        Random seed for reproducibility.

    Examples
    --------
    >>> agent = MixedAgent(alpha=4.0, beta_param=2.0, seed=42)
    >>> 0.0 <= agent.generate(0) <= 1.0
    True
    """

    def __init__(
        self,
        alpha: float = 4.0,
        beta_param: float = 2.0,
        seed: int = 0,
    ) -> None:
        import numpy as np

        self.alpha = alpha
        self.beta_param = beta_param
        self._rng = np.random.RandomState(seed)  # noqa: NPY002

    def generate(self, timestep: int) -> float:  # noqa: ARG002
        """
        Sample quality from the Beta distribution.

        NOTE: SYNTHETIC stochastic behavior — NOT empirical data.
        """
        return float(self._rng.beta(self.alpha, self.beta_param))


class DegradingAgent(AgentBehavior):
    """
    Agent whose action quality decreases monotonically over time.

    NOTE: SYNTHETIC degradation curve — NOT a real model of agent drift.

    Models capability drift or motivation decay: the agent starts at
    ``initial_quality`` and decays exponentially toward ``floor_quality``
    with rate constant ``decay_rate``. The formula is::

        quality(t) = floor + (initial - floor) * exp(-decay_rate * t)

    This produces a smooth, monotonically decreasing trajectory that
    eventually stabilises near ``floor_quality``.

    Parameters
    ----------
    initial_quality:
        Quality at timestep 0. Default ``0.85``.
    floor_quality:
        Asymptotic minimum quality as ``t -> inf``. Default ``0.2``.
    decay_rate:
        Rate of exponential decay. Larger values mean faster degradation.
        Default ``0.005``.
    noise_scale:
        Standard deviation of noise added at each step. Default ``0.02``.
    seed:
        Random seed.

    Examples
    --------
    >>> agent = DegradingAgent(initial_quality=0.9, floor_quality=0.1, decay_rate=0.01)
    >>> agent.generate(0) > agent.generate(500)
    True
    """

    def __init__(
        self,
        initial_quality: float = 0.85,
        floor_quality: float = 0.2,
        decay_rate: float = 0.005,
        noise_scale: float = 0.02,
        seed: int = 0,
    ) -> None:
        import numpy as np

        self.initial_quality = initial_quality
        self.floor_quality = floor_quality
        self.decay_rate = decay_rate
        self.noise_scale = noise_scale
        self._rng = np.random.RandomState(seed)  # noqa: NPY002

    def generate(self, timestep: int) -> float:
        """
        Return exponentially decaying quality with noise.

        NOTE: SYNTHETIC degradation model — NOT empirical data.
        """
        import numpy as np

        base = self.floor_quality + (
            self.initial_quality - self.floor_quality
        ) * math.exp(-self.decay_rate * timestep)
        noisy = base + self._rng.normal(0.0, self.noise_scale)
        return float(np.clip(noisy, 0.0, 1.0))


class PeriodicAgent(AgentBehavior):
    """
    Agent whose quality oscillates sinusoidally around a mean.

    NOTE: SYNTHETIC periodic behavior — NOT a real behavioral pattern.

    Useful for studying how the trust model responds to regular, predictable
    fluctuations in action quality. The quality at timestep ``t`` is::

        quality(t) = mean + amplitude * sin(2*pi*t / period)

    clamped to ``[0, 1]``.

    Parameters
    ----------
    mean_quality:
        Centre of the oscillation. Default ``0.6``.
    amplitude:
        Peak deviation from the mean. Default ``0.3``.
    period:
        Oscillation period in timesteps. Default ``100``.

    Examples
    --------
    >>> agent = PeriodicAgent(mean_quality=0.5, amplitude=0.4, period=200)
    >>> 0.0 <= agent.generate(0) <= 1.0
    True
    """

    def __init__(
        self,
        mean_quality: float = 0.6,
        amplitude: float = 0.3,
        period: float = 100.0,
    ) -> None:
        import numpy as np

        self.mean_quality = mean_quality
        self.amplitude = amplitude
        self.period = period
        self._np = np  # kept for clip

    def generate(self, timestep: int) -> float:
        """
        Return sinusoidally varying quality clamped to ``[0, 1]``.

        NOTE: SYNTHETIC oscillation — NOT empirical data.
        """
        raw = self.mean_quality + self.amplitude * math.sin(
            2.0 * math.pi * timestep / self.period
        )
        return float(self._np.clip(raw, 0.0, 1.0))
