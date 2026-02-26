# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
visualization.py — Plan quality vs trust level charts.

SIMULATION ONLY. All plots visualise SYNTHETIC planning data produced by
TrustFilteredPlanner, SimplePlanner, and PlanEvaluator. These are NOT
production planning dashboards or real agent monitoring interfaces.
"""

from __future__ import annotations

import os
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from trust_planning.evaluator import PlanQualityMetrics, TrustComparisonRow
from trust_planning.model import Plan

if os.environ.get("MPLBACKEND") is None and not os.environ.get("DISPLAY"):
    matplotlib.use("Agg")

_TRUST_COLORS: list[str] = [
    "#dc2626",  # 0 — red (lowest trust)
    "#f59e0b",  # 1 — amber
    "#eab308",  # 2 — yellow
    "#16a34a",  # 3 — green
    "#2563eb",  # 4 — blue
    "#7c3aed",  # 5 — purple (highest)
]


def _ensure_output_dir(save_path: Optional[str]) -> None:
    """Create parent directories for save_path if they do not exist."""
    if save_path is not None:
        parent = os.path.dirname(save_path)
        if parent:
            os.makedirs(parent, exist_ok=True)


def plot_plan_length_by_trust(
    plans: list[Plan],
    goal_id: str,
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot plan step count and total cost vs trust level.

    SIMULATION ONLY. Visualises how plan quality (length, cost) varies as
    trust level changes for a single planning goal.

    Args:
        plans: List of Plan objects, one per trust level (0–5).
        goal_id: Goal identifier for the plot title.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    trust_levels = [plan.trust_level for plan in plans]
    step_counts = [plan.length if plan.reachable else float("nan") for plan in plans]
    total_costs = [plan.total_cost if plan.reachable else float("nan") for plan in plans]
    reachable_flags = [plan.reachable for plan in plans]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    bar_colors = [
        _TRUST_COLORS[level] if reachable_flags[index] else "#9ca3af"
        for index, level in enumerate(trust_levels)
    ]

    axes[0].bar(trust_levels, step_counts, color=bar_colors, alpha=0.85, width=0.6)
    axes[0].set_xlabel("Trust level", fontsize=11)
    axes[0].set_ylabel("Plan step count", fontsize=11)
    axes[0].set_xticks(trust_levels)
    axes[0].set_title(
        f"Plan Length by Trust Level — goal={goal_id!r}\n[SIMULATION ONLY]",
        fontsize=10,
    )
    axes[0].grid(True, axis="y", alpha=0.3)

    valid_trusts = [level for level, plan in zip(trust_levels, plans) if plan.reachable]
    valid_costs = [plan.total_cost for plan in plans if plan.reachable]

    axes[1].plot(
        valid_trusts,
        valid_costs,
        color="#2563eb",
        linewidth=2.0,
        marker="o",
        markersize=7,
        label="Plan cost",
    )
    axes[1].set_xlabel("Trust level", fontsize=11)
    axes[1].set_ylabel("Total plan cost", fontsize=11)
    axes[1].set_xticks(trust_levels)
    axes[1].set_title(
        f"Plan Cost by Trust Level — goal={goal_id!r}\n[SIMULATION ONLY]",
        fontsize=10,
    )
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)

    fig.suptitle(
        f"Trust-Filtered Planning Quality — {goal_id!r}\n"
        "[SIMULATION ONLY — synthetic data, seed=42]",
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_action_space_size(
    trust_levels: list[int],
    action_counts: list[int],
    total_actions: int,
    domain_name: str,
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot available action count vs trust level.

    SIMULATION ONLY. Visualises how the available action space grows with
    trust level in a synthetic planning domain.

    Args:
        trust_levels: List of trust levels evaluated.
        action_counts: Number of available actions at each trust level.
        total_actions: Total number of actions in the domain.
        domain_name: Domain name for the plot title.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    fractions = [count / max(total_actions, 1) for count in action_counts]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    colors = [_TRUST_COLORS[level] for level in trust_levels]
    axes[0].bar(trust_levels, action_counts, color=colors, alpha=0.85, width=0.6)
    axes[0].axhline(y=total_actions, color="#6b7280", linestyle="--", linewidth=1.0,
                    label=f"Total actions ({total_actions})")
    axes[0].set_xlabel("Trust level", fontsize=11)
    axes[0].set_ylabel("Available actions", fontsize=11)
    axes[0].set_xticks(trust_levels)
    axes[0].set_title(
        f"Action Space Size by Trust Level — {domain_name!r}\n[SIMULATION ONLY]",
        fontsize=10,
    )
    axes[0].legend(fontsize=9)
    axes[0].grid(True, axis="y", alpha=0.3)

    axes[1].plot(
        trust_levels,
        fractions,
        color="#7c3aed",
        linewidth=2.0,
        marker="s",
        markersize=7,
    )
    axes[1].set_xlabel("Trust level", fontsize=11)
    axes[1].set_ylabel("Fraction of action space", fontsize=11)
    axes[1].set_ylim(0, 1.1)
    axes[1].set_xticks(trust_levels)
    axes[1].set_title(
        f"Fraction of Action Space Available\n[SIMULATION ONLY]",
        fontsize=10,
    )
    axes[1].grid(True, alpha=0.3)

    fig.suptitle(
        f"Action Space Analysis — {domain_name!r}\n"
        "[SIMULATION ONLY — synthetic data, seed=42]",
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_quality_degradation(
    trust_levels: list[int],
    degradation_rates: list[float],
    reachable_flags: list[bool],
    domain_name: str,
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot plan quality degradation rate as trust level decreases.

    SIMULATION ONLY. Visualises the cost increase relative to the baseline
    optimal plan as trust level falls below maximum. Unreachable plans are
    indicated with a distinct marker.

    Args:
        trust_levels: List of trust levels (ascending order).
        degradation_rates: Fractional cost increase relative to baseline.
            float('inf') for unreachable plans.
        reachable_flags: True if the goal was reachable at each trust level.
        domain_name: Domain name for the plot title.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    finite_rates = [
        rate if rate != float("inf") else float("nan")
        for rate in degradation_rates
    ]

    fig, ax = plt.subplots(figsize=(10, 5))

    reachable_x = [t for t, r in zip(trust_levels, reachable_flags) if r]
    reachable_y = [
        rate for rate, r in zip(finite_rates, reachable_flags)
        if r and not (isinstance(rate, float) and rate != rate)
    ]

    if reachable_x:
        ax.plot(
            reachable_x,
            reachable_y,
            color="#dc2626",
            linewidth=2.0,
            marker="o",
            markersize=7,
            label="Reachable (cost degradation)",
        )

    unreachable_x = [t for t, r in zip(trust_levels, reachable_flags) if not r]
    if unreachable_x:
        ax.scatter(
            unreachable_x,
            [0.0] * len(unreachable_x),
            color="#6b7280",
            marker="X",
            s=100,
            label="Unreachable",
            zorder=5,
        )

    ax.set_xlabel("Trust level", fontsize=11)
    ax.set_ylabel("Cost degradation rate (relative to optimal)", fontsize=11)
    ax.set_xticks(trust_levels)
    ax.set_title(
        f"Plan Quality Degradation by Trust Level — {domain_name!r}\n"
        "[SIMULATION ONLY — synthetic data, seed=42]",
        fontsize=11,
    )
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color="#16a34a", linewidth=1.0, linestyle="--", label="Optimal baseline")
    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_domain_comparison(
    domain_names: list[str],
    min_trust_for_reachability: list[int],
    optimal_costs: list[int],
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Compare minimum required trust and optimal cost across planning domains.

    SIMULATION ONLY. Shows which trust level first makes each domain's goal
    reachable, and what the optimal (trust=5) plan cost is per domain.

    Args:
        domain_names: Labels for each domain.
        min_trust_for_reachability: Minimum trust level at which goal is first reachable.
        optimal_costs: Plan cost at trust level 5 for each domain.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    x_positions = np.arange(len(domain_names))
    bar_width = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    colors_min_trust = [_TRUST_COLORS[level] for level in min_trust_for_reachability]
    axes[0].bar(x_positions, min_trust_for_reachability, color=colors_min_trust,
                alpha=0.85, width=0.5)
    axes[0].set_xticks(x_positions)
    axes[0].set_xticklabels(domain_names, rotation=20, ha="right", fontsize=9)
    axes[0].set_ylabel("Min trust for reachability", fontsize=11)
    axes[0].set_ylim(0, 6)
    axes[0].set_title(
        "Min Trust Level for Goal Reachability\n[SIMULATION ONLY]",
        fontsize=10,
    )
    axes[0].grid(True, axis="y", alpha=0.3)

    axes[1].bar(x_positions, optimal_costs, color="#2563eb", alpha=0.85, width=0.5)
    axes[1].set_xticks(x_positions)
    axes[1].set_xticklabels(domain_names, rotation=20, ha="right", fontsize=9)
    axes[1].set_ylabel("Optimal plan cost (trust=5)", fontsize=11)
    axes[1].set_title(
        "Optimal Plan Cost by Domain\n[SIMULATION ONLY]",
        fontsize=10,
    )
    axes[1].grid(True, axis="y", alpha=0.3)

    fig.suptitle(
        "Planning Domain Comparison [SIMULATION ONLY — synthetic data, seed=42]",
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig
