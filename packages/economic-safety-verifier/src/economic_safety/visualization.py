# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
visualization.py — Matplotlib figure generators for spending envelope analysis.

SIMULATION ONLY. All plots visualise SYNTHETIC data produced by EconomicModel
and EconomicSafetyVerifier. These are NOT production dashboards or real
financial reports.
"""

from __future__ import annotations

import os
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from economic_safety.model import (
    Commitment,
    ConcurrencyResult,
    Envelope,
    SpendingResult,
)

# Use a non-interactive backend when running headless (e.g. in CI)
if os.environ.get("MPLBACKEND") is None and not os.environ.get("DISPLAY"):
    matplotlib.use("Agg")


def _ensure_output_dir(save_path: Optional[str]) -> None:
    """Create parent directories for save_path if they do not exist."""
    if save_path is not None:
        parent = os.path.dirname(save_path)
        if parent:
            os.makedirs(parent, exist_ok=True)


def plot_budget_trajectory(
    result: SpendingResult,
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot the remaining budget balance over simulation timesteps.

    SIMULATION ONLY. Visualises the balance_timeline from a SpendingResult,
    with the zero-balance line and the total spend annotated.

    Args:
        result: A SpendingResult produced by EconomicModel.simulate_spending.
        save_path: If provided, save the figure to this path (PNG). Parent
            directories are created automatically.
        show: If True, call plt.show() after rendering. Defaults to False.

    Returns:
        The matplotlib Figure object.
    """
    timesteps = list(range(len(result.balance_timeline)))
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        timesteps,
        result.balance_timeline,
        color="#2563eb",
        linewidth=1.8,
        label="Remaining balance",
    )
    ax.axhline(y=0.0, color="#dc2626", linewidth=1.2, linestyle="--", label="Zero balance")
    ax.axhline(
        y=result.envelope_limit,
        color="#16a34a",
        linewidth=1.2,
        linestyle=":",
        label=f"Envelope limit ({result.envelope_limit:.0f})",
    )

    ax.fill_between(
        timesteps,
        result.balance_timeline,
        0,
        where=[b >= 0 for b in result.balance_timeline],
        alpha=0.12,
        color="#2563eb",
    )

    ax.set_xlabel("Timestep", fontsize=11)
    ax.set_ylabel("Remaining balance", fontsize=11)
    ax.set_title(
        f"Budget Trajectory — category='{result.category}' "
        f"(total spent={result.total_spent:.2f})\n"
        "[SIMULATION ONLY — synthetic data]",
        fontsize=11,
    )
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, max(timesteps) if timesteps else 1)

    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    return fig


def plot_commitment_waterfall(
    envelope: Envelope,
    commitments: list[Commitment],
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot a waterfall chart showing how commitments reduce the available balance.

    SIMULATION ONLY. Visualises the envelope's limit, spent amount, each
    commitment's reserved amount, and the remaining available balance.

    Args:
        envelope: The envelope snapshot with current spent and committed values.
        commitments: Active commitments against envelope.category.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    relevant = [c for c in commitments if c.category == envelope.category]

    labels = ["Limit"]
    values = [envelope.limit]
    colors = ["#16a34a"]

    if envelope.spent > 0:
        labels.append("Spent")
        values.append(-envelope.spent)
        colors.append("#dc2626")

    for index, commitment in enumerate(relevant):
        labels.append(f"Commit {index + 1}\n({commitment.commitment_id[:8]}…)")
        values.append(-commitment.amount)
        colors.append("#f59e0b")

    available = envelope.available
    labels.append("Available")
    values.append(available)
    colors.append("#2563eb")

    # Compute waterfall running totals
    running = [0.0]
    cumulative = 0.0
    bar_heights = []
    bar_bottoms = []
    for val in values:
        if val >= 0:
            bar_bottoms.append(cumulative)
            bar_heights.append(val)
            cumulative += val
        else:
            cumulative += val
            bar_bottoms.append(cumulative)
            bar_heights.append(abs(val))
        running.append(cumulative)

    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 1.4), 6))
    x_positions = list(range(len(labels)))

    for x_pos, height, bottom, color, label in zip(
        x_positions, bar_heights, bar_bottoms, colors, labels
    ):
        ax.bar(x_pos, height, bottom=bottom, color=color, alpha=0.85, width=0.6)
        ax.text(
            x_pos,
            bottom + height / 2,
            f"{height:.1f}",
            ha="center",
            va="center",
            fontsize=8,
            color="white",
            fontweight="bold",
        )

    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Amount", fontsize=11)
    ax.set_title(
        f"Commitment Waterfall — category='{envelope.category}' "
        f"(limit={envelope.limit:.0f})\n"
        "[SIMULATION ONLY — synthetic data]",
        fontsize=11,
    )
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_ylim(0, envelope.limit * 1.1)

    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    return fig


def plot_concurrent_spending(
    result: ConcurrencyResult,
    label: str = "",
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot the balance timeline from a concurrent spending simulation.

    SIMULATION ONLY. Visualises the per-timestep remaining balance from
    a ConcurrencyResult, shading overspend regions in red and safe regions
    in blue.

    Args:
        result: A ConcurrencyResult produced by EconomicSafetyVerifier.
        label: Optional label suffix for the figure title.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    timesteps = list(range(len(result.timeline)))
    fig, ax = plt.subplots(figsize=(10, 5))

    line_color = "#16a34a" if result.safe else "#dc2626"
    status_label = "SAFE" if result.safe else f"UNSAFE ({result.overspend_events} overspend event(s))"

    ax.plot(
        timesteps,
        result.timeline,
        color=line_color,
        linewidth=1.8,
        label=f"Balance ({status_label})",
    )
    ax.axhline(y=0.0, color="#6b7280", linewidth=1.0, linestyle="--", label="Zero balance")
    ax.axhline(
        y=result.envelope_limit,
        color="#2563eb",
        linewidth=1.2,
        linestyle=":",
        label=f"Envelope limit ({result.envelope_limit:.0f})",
    )

    # Shade overspend zones (balance < 0)
    overspend_mask = [b < 0 for b in result.timeline]
    if any(overspend_mask):
        ax.fill_between(
            timesteps,
            result.timeline,
            0,
            where=overspend_mask,
            alpha=0.20,
            color="#dc2626",
            label="Overspend zone",
        )

    # Shade safe zone
    safe_mask = [b >= 0 for b in result.timeline]
    if any(safe_mask):
        ax.fill_between(
            timesteps,
            result.timeline,
            0,
            where=safe_mask,
            alpha=0.10,
            color="#16a34a",
        )

    title_suffix = f" — {label}" if label else ""
    ax.set_xlabel("Timestep", fontsize=11)
    ax.set_ylabel("Remaining balance", fontsize=11)
    ax.set_title(
        f"Concurrent Spending Simulation{title_suffix}\n"
        f"total_spent={result.total_spent:.2f}, limit={result.envelope_limit:.0f} "
        "[SIMULATION ONLY — synthetic data]",
        fontsize=11,
    )
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, max(timesteps) if timesteps else 1)

    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    return fig


def plot_verification_summary(
    property_names: list[str],
    holds_flags: list[bool],
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot a bar chart summarising verification results across properties.

    SIMULATION ONLY. Provides a quick visual summary of which safety properties
    hold and which are violated across a verification run.

    Args:
        property_names: List of property name strings.
        holds_flags: Corresponding list of bool results (True = holds).
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    colors = ["#16a34a" if h else "#dc2626" for h in holds_flags]
    y_values = [1.0 if h else 0.0 for h in holds_flags]

    fig, ax = plt.subplots(figsize=(max(6, len(property_names) * 2), 4))
    x_positions = list(range(len(property_names)))

    ax.bar(x_positions, y_values, color=colors, alpha=0.85, width=0.5)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(property_names, fontsize=10)
    ax.set_yticks([0.0, 1.0])
    ax.set_yticklabels(["FAILS", "HOLDS"], fontsize=10)
    ax.set_ylim(-0.1, 1.3)
    ax.set_title(
        "Verification Summary [SIMULATION ONLY — synthetic data]",
        fontsize=11,
    )

    for x_pos, holds in zip(x_positions, holds_flags):
        ax.text(
            x_pos,
            1.05 if holds else 0.05,
            "HOLDS" if holds else "FAILS",
            ha="center",
            fontsize=9,
            color="#16a34a" if holds else "#dc2626",
            fontweight="bold",
        )

    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    return fig
