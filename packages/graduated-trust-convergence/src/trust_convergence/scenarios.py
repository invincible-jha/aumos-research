# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Predefined simulation scenarios from Paper 13.

NOTE: These configurations describe SIMPLIFIED academic simulation parameters.
They do NOT represent production system settings, thresholds, or policies.

All scenarios use ``seed=42`` for deterministic reproduction of the paper's figures.
"""
from __future__ import annotations

from trust_convergence.model import SimulationConfig

# ---------------------------------------------------------------------------
# Canonical scenarios referenced in Paper 13
# ---------------------------------------------------------------------------

SCENARIOS: dict[str, SimulationConfig] = {
    #
    # Baseline — Fig. 1
    # Standard six-level system with moderate decay and promotion threshold.
    # Serves as the reference point for all other comparisons.
    #
    "baseline": SimulationConfig(
        num_levels=6,
        decay_rate=0.01,
        promotion_threshold=0.1,
        seed=42,
    ),
    #
    # High decay — Fig. 2
    # Decay rate 5× the baseline. Trust erodes quickly without sustained
    # high-quality actions. Expected to show slower convergence and a lower
    # asymptotic level for agents with intermittent quality.
    #
    "high_decay": SimulationConfig(
        num_levels=6,
        decay_rate=0.05,
        promotion_threshold=0.1,
        seed=42,
    ),
    #
    # Low threshold — Fig. 2 (second panel)
    # Promotion threshold halved relative to baseline. A given action quality
    # produces a smaller trust increment, requiring sustained performance for
    # level advancement.
    #
    "low_threshold": SimulationConfig(
        num_levels=6,
        decay_rate=0.01,
        promotion_threshold=0.05,
        seed=42,
    ),
    #
    # Adversarial — Fig. 4
    # Slightly elevated decay (2×) combined with the adversarial agent type
    # in exp4_adversarial.py. Tests whether the linear model detects gaming.
    #
    "adversarial": SimulationConfig(
        num_levels=6,
        decay_rate=0.02,
        promotion_threshold=0.1,
        seed=42,
    ),
    #
    # Wide scale — Fig. 3 (multi-scope panel)
    # Ten-level variant to study convergence properties in a wider trust range.
    # Paper 13, Section 4.3 discusses generalisation beyond six levels.
    #
    "wide_scale": SimulationConfig(
        num_levels=10,
        decay_rate=0.01,
        promotion_threshold=0.08,
        seed=42,
    ),
    #
    # Strict — Fig. 3 (strict panel)
    # High decay combined with a high promotion threshold creates a "strict"
    # system where only the best-performing agents reach the upper levels.
    #
    "strict": SimulationConfig(
        num_levels=6,
        decay_rate=0.04,
        promotion_threshold=0.15,
        seed=42,
    ),
    #
    # Lenient — Fig. 3 (lenient panel)
    # Low decay and low promotion threshold: trust accumulates quickly and
    # rarely erodes. Used to demonstrate the upper bound on convergence speed.
    #
    "lenient": SimulationConfig(
        num_levels=6,
        decay_rate=0.005,
        promotion_threshold=0.06,
        seed=42,
    ),
}


def get_scenario(name: str) -> SimulationConfig:
    """
    Retrieve a named scenario configuration.

    NOTE: Returns SIMULATION configuration — NOT production system settings.

    Parameters
    ----------
    name:
        Key into :data:`SCENARIOS`. Case-sensitive.

    Returns
    -------
    SimulationConfig
        The frozen configuration for the named scenario.

    Raises
    ------
    KeyError
        If ``name`` is not a recognised scenario key.

    Examples
    --------
    >>> cfg = get_scenario("baseline")
    >>> cfg.num_levels
    6
    >>> cfg.decay_rate
    0.01
    """
    if name not in SCENARIOS:
        available = ", ".join(sorted(SCENARIOS))
        raise KeyError(
            f"Unknown scenario {name!r}. Available scenarios: {available}"
        )
    return SCENARIOS[name]


def list_scenarios() -> list[str]:
    """
    Return a sorted list of all available scenario names.

    Returns
    -------
    list[str]
        Scenario names that can be passed to :func:`get_scenario`.
    """
    return sorted(SCENARIOS)
