# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Matplotlib figure generators for Paper 13 results.

NOTE: All figures generated here are based on SYNTHETIC simulation data.
They do NOT visualise real agent behavior or production trust levels.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

if TYPE_CHECKING:
    import matplotlib.figure

    from trust_convergence.model import SimulationResult

# ---------------------------------------------------------------------------
# Shared style constants
# ---------------------------------------------------------------------------

_PALETTE = [
    "#2563EB",  # blue
    "#DC2626",  # red
    "#16A34A",  # green
    "#CA8A04",  # amber
    "#7C3AED",  # violet
    "#0891B2",  # cyan
    "#EA580C",  # orange
]

_FIGURE_DPI = 150
_FONT_SIZE = 11


def _apply_base_style(ax: plt.Axes) -> None:
    """Apply consistent visual style to a single axes object."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=_FONT_SIZE - 1)
    ax.set_xlabel(ax.get_xlabel(), fontsize=_FONT_SIZE)
    ax.set_ylabel(ax.get_ylabel(), fontsize=_FONT_SIZE)
    ax.set_title(ax.get_title(), fontsize=_FONT_SIZE + 1, fontweight="bold")


def _save_or_show(
    fig: matplotlib.figure.Figure,
    save_path: str | None,
) -> None:
    """Save to file if ``save_path`` is given, otherwise show interactively."""
    if save_path is not None:
        output = Path(save_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=_FIGURE_DPI, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()


# ---------------------------------------------------------------------------
# Public figure functions
# ---------------------------------------------------------------------------


def plot_convergence(
    result: SimulationResult,
    title: str = "",
    save_path: str | None = None,
) -> matplotlib.figure.Figure:
    """
    Plot a single simulation trajectory with convergence annotation.

    NOTE: Visualises SYNTHETIC simulation data — NOT production trust levels.

    Produces a line plot of trust level over time. A horizontal dashed line
    marks the final level and an annotation reports the convergence rate and
    stability index.

    Parameters
    ----------
    result:
        A :class:`~trust_convergence.model.SimulationResult` from one simulation run.
    title:
        Optional figure title. Defaults to the agent name from the result.
    save_path:
        If provided, the figure is saved to this file path (PNG or PDF).
        The parent directory is created if it does not exist.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure object.
    """
    fig, ax = plt.subplots(figsize=(9, 4))

    timesteps = np.arange(len(result.trajectory))
    ax.plot(
        timesteps,
        result.trajectory,
        color=_PALETTE[0],
        linewidth=1.2,
        alpha=0.85,
        label="Trust level",
    )
    ax.axhline(
        result.final_level,
        color=_PALETTE[1],
        linestyle="--",
        linewidth=1.0,
        label=f"Final level ({result.final_level:.2f})",
    )

    # Level grid lines
    max_level = int(result.config.num_levels)
    for lvl in range(max_level):
        ax.axhline(lvl, color="gray", linewidth=0.4, alpha=0.4, linestyle=":")

    annotation = (
        f"Convergence rate: {result.convergence_rate:.4f}\n"
        f"Stability index:  {result.stability:.4f}"
    )
    ax.text(
        0.98,
        0.05,
        annotation,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=_FONT_SIZE - 2,
        family="monospace",
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.7},
    )

    ax.set_xlabel("Timestep")
    ax.set_ylabel("Trust level")
    ax.set_title(title or f"Trust trajectory — {result.agent_name}")
    ax.set_xlim(0, len(result.trajectory) - 1)
    ax.set_ylim(-0.1, max_level - 0.9)
    ax.legend(fontsize=_FONT_SIZE - 1, loc="upper left")
    _apply_base_style(ax)

    fig.tight_layout()
    _save_or_show(fig, save_path)
    return fig


def plot_decay_comparison(
    results: dict[str, SimulationResult],
    save_path: str | None = None,
) -> matplotlib.figure.Figure:
    """
    Compare trust trajectories under different decay / threshold settings.

    NOTE: Visualises SYNTHETIC simulation data — NOT production trust levels.

    Overlays all trajectories on a single axes, coloured by scenario name.
    A legend maps scenario names to line colours.

    Parameters
    ----------
    results:
        Mapping of scenario label to simulation result.
    save_path:
        Optional output file path.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure object.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    for idx, (label, result) in enumerate(results.items()):
        color = _PALETTE[idx % len(_PALETTE)]
        timesteps = np.arange(len(result.trajectory))
        ax.plot(
            timesteps,
            result.trajectory,
            color=color,
            linewidth=1.4,
            alpha=0.88,
            label=f"{label}  (rate={result.convergence_rate:.4f})",
        )

    num_levels = max(r.config.num_levels for r in results.values())
    for lvl in range(num_levels):
        ax.axhline(lvl, color="gray", linewidth=0.3, alpha=0.35, linestyle=":")

    ax.set_xlabel("Timestep")
    ax.set_ylabel("Trust level")
    ax.set_title("Decay and Threshold Impact on Trust Convergence (Paper 13, Fig. 2)")
    ax.legend(fontsize=_FONT_SIZE - 2, loc="lower right")
    _apply_base_style(ax)

    fig.tight_layout()
    _save_or_show(fig, save_path)
    return fig


def plot_multi_scope(
    results: dict[str, SimulationResult],
    save_path: str | None = None,
) -> matplotlib.figure.Figure:
    """
    Plot trajectories across multiple trust-scope (num_levels) configurations.

    NOTE: Visualises SYNTHETIC simulation data — NOT production trust levels.

    Renders each scenario in its own subplot, arranged in a single row.
    This mirrors the multi-panel layout used in Paper 13, Fig. 3.

    Parameters
    ----------
    results:
        Ordered mapping of panel label to simulation result.
    save_path:
        Optional output file path.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure object.
    """
    num_panels = len(results)
    fig, axes = plt.subplots(
        1, num_panels, figsize=(5 * num_panels, 4), sharey=False
    )
    if num_panels == 1:
        axes = [axes]

    for ax, (idx, (label, result)) in zip(
        axes, enumerate(results.items()), strict=True
    ):
        color = _PALETTE[idx % len(_PALETTE)]
        timesteps = np.arange(len(result.trajectory))
        ax.plot(
            timesteps,
            result.trajectory,
            color=color,
            linewidth=1.3,
            alpha=0.85,
        )
        ax.axhline(
            result.final_level,
            color="gray",
            linestyle="--",
            linewidth=0.8,
        )
        for lvl in range(result.config.num_levels):
            ax.axhline(lvl, color="gray", linewidth=0.3, alpha=0.3, linestyle=":")

        ax.set_xlabel("Timestep", fontsize=_FONT_SIZE - 1)
        ax.set_ylabel("Trust level", fontsize=_FONT_SIZE - 1)
        ax.set_title(label, fontsize=_FONT_SIZE, fontweight="bold")
        ax.set_ylim(-0.1, result.config.num_levels - 0.9)
        _apply_base_style(ax)

    fig.suptitle(
        "Multi-Scope Trust Convergence (Paper 13, Fig. 3)",
        fontsize=_FONT_SIZE + 2,
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()
    _save_or_show(fig, save_path)
    return fig


def plot_adversarial(
    results: dict[str, SimulationResult],
    save_path: str | None = None,
) -> matplotlib.figure.Figure:
    """
    Visualise trust evolution under adversarial agent strategies.

    NOTE: Visualises SYNTHETIC adversarial patterns — NOT real attack data.

    Shows two subplots: (1) raw trajectory overlay for all adversarial agent
    variants, and (2) a rolling-mean comparison to highlight the adversary's
    effect on trust dynamics.

    Parameters
    ----------
    results:
        Mapping of agent variant label to simulation result.
    save_path:
        Optional output file path.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure object.
    """
    fig, (ax_raw, ax_smooth) = plt.subplots(1, 2, figsize=(13, 5))

    window = 50

    for idx, (label, result) in enumerate(results.items()):
        color = _PALETTE[idx % len(_PALETTE)]
        timesteps = np.arange(len(result.trajectory))

        # Raw trajectory
        ax_raw.plot(
            timesteps,
            result.trajectory,
            color=color,
            linewidth=0.9,
            alpha=0.7,
            label=label,
        )

        # Rolling mean
        kernel = np.ones(window) / window
        smoothed = np.convolve(result.trajectory, kernel, mode="valid")
        ax_smooth.plot(
            np.arange(len(smoothed)) + window // 2,
            smoothed,
            color=color,
            linewidth=1.4,
            label=label,
        )

    for ax in (ax_raw, ax_smooth):
        num_levels = max(r.config.num_levels for r in results.values())
        for lvl in range(num_levels):
            ax.axhline(lvl, color="gray", linewidth=0.3, alpha=0.35, linestyle=":")
        ax.set_xlabel("Timestep")
        ax.set_ylabel("Trust level")
        ax.legend(fontsize=_FONT_SIZE - 2, loc="upper left")
        _apply_base_style(ax)

    ax_raw.set_title("Raw trajectories")
    ax_smooth.set_title(f"Rolling mean (w={window})")
    fig.suptitle(
        "Adversarial Agent Trust Dynamics (Paper 13, Fig. 4)",
        fontsize=_FONT_SIZE + 2,
        fontweight="bold",
    )
    fig.tight_layout()
    _save_or_show(fig, save_path)
    return fig


def plot_metrics_summary(
    results: dict[str, SimulationResult],
    save_path: str | None = None,
) -> matplotlib.figure.Figure:
    """
    Produce a bar chart comparing convergence rate and stability index across scenarios.

    NOTE: Visualises SYNTHETIC simulation metrics — NOT production measurements.

    Parameters
    ----------
    results:
        Mapping of scenario label to simulation result.
    save_path:
        Optional output file path.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure object.
    """
    labels = list(results.keys())
    convergence_rates = [r.convergence_rate for r in results.values()]
    stability_indices = [r.stability for r in results.values()]

    x = np.arange(len(labels))
    bar_width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - bar_width / 2, convergence_rates, bar_width, label="Convergence rate", color=_PALETTE[0])
    ax.bar(x + bar_width / 2, stability_indices, bar_width, label="Stability index", color=_PALETTE[1])

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=_FONT_SIZE - 1)
    ax.set_ylabel("Metric value")
    ax.set_title("Convergence Metrics by Scenario")
    ax.legend(fontsize=_FONT_SIZE - 1)
    _apply_base_style(ax)

    fig.tight_layout()
    _save_or_show(fig, save_path)
    return fig
