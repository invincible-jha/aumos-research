# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
visualization.py — Commitment lifecycle visualisations with matplotlib.

SIMULATION ONLY. All plots visualise SYNTHETIC data produced by CommitmentExtractor,
CommitmentTracker, and evaluation functions. These are NOT production dashboards
or real commitment monitoring interfaces.
"""

from __future__ import annotations

import os
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from commitment_extractor.evaluation import ExtractionMetrics, TypeBreakdown
from commitment_extractor.model import CommitmentType, FulfillmentStatus
from commitment_extractor.tracker import TrackingSnapshot

# Use non-interactive backend when running headless
if os.environ.get("MPLBACKEND") is None and not os.environ.get("DISPLAY"):
    matplotlib.use("Agg")

_STATUS_COLORS: dict[FulfillmentStatus, str] = {
    FulfillmentStatus.ACTIVE: "#6366f1",
    FulfillmentStatus.FULFILLED: "#16a34a",
    FulfillmentStatus.EXPIRED: "#f59e0b",
    FulfillmentStatus.CANCELLED: "#6b7280",
}

_TYPE_COLORS: dict[CommitmentType, str] = {
    CommitmentType.PROMISE: "#2563eb",
    CommitmentType.OBLIGATION: "#dc2626",
    CommitmentType.DEADLINE: "#f59e0b",
    CommitmentType.CONDITIONAL: "#7c3aed",
    CommitmentType.OFFER: "#16a34a",
}


def _ensure_output_dir(save_path: Optional[str]) -> None:
    """Create parent directories for save_path if they do not exist."""
    if save_path is not None:
        parent = os.path.dirname(save_path)
        if parent:
            os.makedirs(parent, exist_ok=True)


def plot_type_distribution(
    type_counts: dict[CommitmentType, int],
    title: str = "Commitment Type Distribution",
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot a bar chart of commitment counts by type.

    SIMULATION ONLY. Visualises the distribution of extracted commitment types
    from a synthetic conversation dataset.

    Args:
        type_counts: Dict mapping CommitmentType to count.
        title: Plot title string.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    labels = [t.value for t in CommitmentType]
    counts = [type_counts.get(t, 0) for t in CommitmentType]
    colors = [_TYPE_COLORS[t] for t in CommitmentType]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(labels, counts, color=colors, alpha=0.85, width=0.5)
    ax.set_xlabel("Commitment type", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title(f"{title}\n[SIMULATION ONLY — synthetic data, seed=42]", fontsize=11)
    ax.grid(True, axis="y", alpha=0.3)

    for index, count in enumerate(counts):
        if count > 0:
            ax.text(index, count + 0.1, str(count), ha="center", fontsize=9)

    fig.tight_layout()
    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_lifecycle_snapshot(
    snapshot: TrackingSnapshot,
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot a pie chart of commitment lifecycle states from a TrackingSnapshot.

    SIMULATION ONLY. Visualises the distribution of ACTIVE, FULFILLED, EXPIRED,
    and CANCELLED commitments at a point in the synthetic simulation.

    Args:
        snapshot: A TrackingSnapshot from CommitmentTracker.snapshot().
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    status_values = [
        (FulfillmentStatus.ACTIVE, snapshot.active),
        (FulfillmentStatus.FULFILLED, snapshot.fulfilled),
        (FulfillmentStatus.EXPIRED, snapshot.expired),
        (FulfillmentStatus.CANCELLED, snapshot.cancelled),
    ]
    labels = [s.value for s, _ in status_values if _ > 0]
    counts = [count for _, count in status_values if count > 0]
    colors = [_STATUS_COLORS[s] for s, count in status_values if count > 0]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    if counts:
        axes[0].pie(
            counts,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            textprops={"fontsize": 9},
        )
    axes[0].set_title(
        f"Commitment Lifecycle States (n={snapshot.total})\n[SIMULATION ONLY]",
        fontsize=10,
    )

    # Bar chart of fulfillment rate
    axes[1].bar(
        ["Fulfillment\nRate"],
        [snapshot.fulfillment_rate],
        color="#16a34a",
        alpha=0.85,
        width=0.3,
    )
    axes[1].set_ylim(0, 1.1)
    axes[1].set_ylabel("Rate", fontsize=11)
    axes[1].set_title(
        f"Fulfillment Rate = {snapshot.fulfillment_rate:.3f}\n[SIMULATION ONLY]",
        fontsize=10,
    )
    axes[1].grid(True, axis="y", alpha=0.3)
    axes[1].axhline(y=0.8, color="#f59e0b", linestyle="--", linewidth=1.0,
                    label="0.8 reference line")
    axes[1].legend(fontsize=9)

    fig.suptitle(
        "Commitment Lifecycle Summary [SIMULATION ONLY — synthetic data, seed=42]",
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


def plot_precision_recall_by_scenario(
    metrics: list[ExtractionMetrics],
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot precision, recall, and F1 scores across multiple scenarios.

    SIMULATION ONLY. Visualises extraction quality metrics per synthetic scenario.

    Args:
        metrics: List of ExtractionMetrics, one per synthetic scenario.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    names = [m.scenario_name for m in metrics]
    precisions = [m.precision for m in metrics]
    recalls = [m.recall for m in metrics]
    f1_scores = [m.f1_score for m in metrics]

    x_positions = np.arange(len(names))
    bar_width = 0.25

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(x_positions - bar_width, precisions, width=bar_width,
           label="Precision", color="#2563eb", alpha=0.85)
    ax.bar(x_positions, recalls, width=bar_width,
           label="Recall", color="#16a34a", alpha=0.85)
    ax.bar(x_positions + bar_width, f1_scores, width=bar_width,
           label="F1", color="#dc2626", alpha=0.85)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title(
        "Extraction Precision / Recall / F1 by Scenario\n"
        "[SIMULATION ONLY — synthetic data, seed=42]",
        fontsize=11,
    )
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_type_precision_recall(
    breakdowns: list[TypeBreakdown],
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot per-type precision and recall as a grouped bar chart.

    SIMULATION ONLY. Visualises how accurately the extractor identifies each
    CommitmentType across the evaluation dataset.

    Args:
        breakdowns: List of TypeBreakdown objects from evaluation.per_type_breakdown.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    type_names = [b.commitment_type.value for b in breakdowns]
    precisions = [b.precision for b in breakdowns]
    recalls = [b.recall for b in breakdowns]

    x_positions = np.arange(len(type_names))
    bar_width = 0.35

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(x_positions - bar_width / 2, precisions, width=bar_width,
           label="Precision", color="#2563eb", alpha=0.85)
    ax.bar(x_positions + bar_width / 2, recalls, width=bar_width,
           label="Recall", color="#16a34a", alpha=0.85)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(type_names, fontsize=10)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title(
        "Per-Type Precision and Recall\n[SIMULATION ONLY — synthetic data, seed=42]",
        fontsize=11,
    )
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig
