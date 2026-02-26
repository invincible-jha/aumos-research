# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
visualization.py — Matplotlib figure generators for delegation trust analysis.

SIMULATION ONLY. All plots visualise SYNTHETIC data produced by
DelegationTrustModel and associated metric functions. These are NOT production
dashboards or real trust monitoring interfaces.
"""

from __future__ import annotations

import os
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from delegation_trust.metrics import DecayProfile, DepthAnalysis, PathReliability, TransitivityScore
from delegation_trust.model import SimulationResult

# Use non-interactive backend when running headless
if os.environ.get("MPLBACKEND") is None and not os.environ.get("DISPLAY"):
    matplotlib.use("Agg")


def _ensure_output_dir(save_path: Optional[str]) -> None:
    """Create parent directories for save_path if they do not exist."""
    if save_path is not None:
        parent = os.path.dirname(save_path)
        if parent:
            os.makedirs(parent, exist_ok=True)


def plot_trust_chain(
    result: SimulationResult,
    edge_trusts: list[float],
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot effective trust and per-hop edge trusts along a delegation chain.

    SIMULATION ONLY. Visualises how trust decays hop-by-hop along a delegation
    path, with the cumulative product (transitive trust) overlaid.

    Args:
        result: A SimulationResult produced by DelegationTrustModel.simulate_scenario.
        edge_trusts: List of pairwise trust levels for each hop in the path.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    hop_labels = [f"Hop {index + 1}" for index in range(len(edge_trusts))]
    cumulative: list[float] = []
    running = 1.0
    for trust in edge_trusts:
        running *= trust
        cumulative.append(running)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Left: per-hop edge trust levels
    axes[0].bar(hop_labels, edge_trusts, color="#2563eb", alpha=0.80, width=0.5)
    axes[0].axhline(y=1.0, color="#16a34a", linewidth=1.0, linestyle="--", label="Perfect trust")
    axes[0].set_ylim(0, 1.1)
    axes[0].set_xlabel("Delegation hop", fontsize=10)
    axes[0].set_ylabel("Pairwise edge trust", fontsize=10)
    axes[0].set_title(
        f"Per-hop edge trust — '{result.scenario_name}'\n[SIMULATION ONLY]",
        fontsize=10,
    )
    axes[0].legend(fontsize=9)
    axes[0].grid(True, axis="y", alpha=0.3)

    # Right: cumulative transitive trust
    x_positions = list(range(1, len(cumulative) + 1))
    axes[1].plot(
        x_positions,
        cumulative,
        color="#dc2626",
        linewidth=2.0,
        marker="o",
        markersize=6,
        label="Cumulative trust",
    )
    axes[1].axhline(y=result.terminal_trust, color="#f59e0b", linewidth=1.2,
                    linestyle=":", label=f"Terminal trust={result.terminal_trust:.4f}")
    axes[1].set_ylim(0, 1.1)
    axes[1].set_xlim(0.5, len(cumulative) + 0.5)
    axes[1].set_xlabel("Hop count (cumulative)", fontsize=10)
    axes[1].set_ylabel("Transitive trust", fontsize=10)
    axes[1].set_title(
        f"Cumulative transitive trust\n[SIMULATION ONLY]",
        fontsize=10,
    )
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)

    fig.suptitle(
        f"Delegation Trust Chain — path length {result.path_length} hops\n"
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


def plot_decay_profile(
    profile: DecayProfile,
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot the trust decay profile as a function of hop count.

    SIMULATION ONLY. Visualises mean_trust_per_hop and the theoretical
    multiplicative decay curve from DecayProfile.

    Args:
        profile: A DecayProfile produced by metrics.decay_over_hops.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        profile.hop_counts,
        profile.theoretical_decay,
        color="#2563eb",
        linewidth=2.0,
        marker="o",
        markersize=5,
        label=f"Theoretical decay (μ_edge={profile.mean_edge_trust:.3f})",
    )

    ax.set_xlabel("Chain length (hops)", fontsize=11)
    ax.set_ylabel("Effective transitive trust", fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.set_title(
        f"Trust Decay Profile — mean edge trust={profile.mean_edge_trust:.3f}\n"
        "[SIMULATION ONLY — synthetic data, seed=42]",
        fontsize=11,
    )
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.fill_between(
        profile.hop_counts,
        profile.theoretical_decay,
        0,
        alpha=0.10,
        color="#2563eb",
    )

    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    return fig


def plot_topology_comparison(
    scenario_names: list[str],
    terminal_trusts: list[float],
    path_lengths: list[int],
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot a side-by-side comparison of terminal trust across delegation topologies.

    SIMULATION ONLY. Visualises terminal trust (left) and path length (right)
    for multiple delegation scenarios.

    Args:
        scenario_names: Labels for each scenario.
        terminal_trusts: Effective terminal trust for each scenario.
        path_lengths: BFS path length for each scenario.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    x_positions = list(range(len(scenario_names)))
    colors = [
        "#16a34a" if trust >= 0.5 else ("#f59e0b" if trust >= 0.2 else "#dc2626")
        for trust in terminal_trusts
    ]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].bar(x_positions, terminal_trusts, color=colors, alpha=0.85, width=0.5)
    axes[0].set_xticks(x_positions)
    axes[0].set_xticklabels(scenario_names, fontsize=8, rotation=30, ha="right")
    axes[0].set_ylim(0, 1.1)
    axes[0].set_ylabel("Terminal trust", fontsize=10)
    axes[0].set_title("Terminal Transitive Trust by Topology\n[SIMULATION ONLY]", fontsize=10)
    axes[0].axhline(y=0.5, color="#6b7280", linewidth=1.0, linestyle="--",
                    label="0.5 threshold")
    axes[0].legend(fontsize=9)
    axes[0].grid(True, axis="y", alpha=0.3)

    axes[1].bar(x_positions, path_lengths, color="#6366f1", alpha=0.80, width=0.5)
    axes[1].set_xticks(x_positions)
    axes[1].set_xticklabels(scenario_names, fontsize=8, rotation=30, ha="right")
    axes[1].set_ylabel("Path length (hops)", fontsize=10)
    axes[1].set_title("Delegation Path Length by Topology\n[SIMULATION ONLY]", fontsize=10)
    axes[1].grid(True, axis="y", alpha=0.3)

    fig.suptitle(
        "Delegation Topology Comparison [SIMULATION ONLY — synthetic data, seed=42]",
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


def plot_adversarial_impact(
    chain_lengths: list[int],
    compliant_trusts: list[float],
    adversarial_trusts: list[float],
    save_path: Optional[str] = None,
    show: bool = False,
) -> matplotlib.figure.Figure:
    """Plot the impact of adversarial agents on terminal trust vs. chain length.

    SIMULATION ONLY. Compares terminal trust with and without an adversarial
    agent as a function of chain length.

    Args:
        chain_lengths: List of chain lengths evaluated.
        compliant_trusts: Terminal trust with all-compliant agents.
        adversarial_trusts: Terminal trust with one adversarial agent in chain.
        save_path: If provided, save the figure to this path (PNG).
        show: If True, call plt.show() after rendering.

    Returns:
        The matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        chain_lengths,
        compliant_trusts,
        color="#16a34a",
        linewidth=2.0,
        marker="o",
        markersize=5,
        label="All compliant",
    )
    ax.plot(
        chain_lengths,
        adversarial_trusts,
        color="#dc2626",
        linewidth=2.0,
        marker="s",
        markersize=5,
        label="One adversarial agent",
    )

    ax.fill_between(
        chain_lengths,
        compliant_trusts,
        adversarial_trusts,
        alpha=0.12,
        color="#f59e0b",
        label="Trust gap",
    )

    ax.set_xlabel("Chain length (number of agents)", fontsize=11)
    ax.set_ylabel("Terminal transitive trust", fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.set_title(
        "Adversarial Agent Impact on Transitive Trust\n"
        "[SIMULATION ONLY — synthetic data, seed=42]",
        fontsize=11,
    )
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    if save_path is not None:
        _ensure_output_dir(save_path)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    return fig
