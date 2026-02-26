# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Visualization utilities for protocol composition analysis.

RESEARCH TOOL — not production orchestration.
Produces static matplotlib figures for the state space, verification
outcomes, and priority heatmaps described in Papers 9/25.

All figures are deterministic given fixed inputs and match the style
of the precomputed figures in results/precomputed/.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

# Lazy import guard — matplotlib is an optional dependency during CI
try:
    import matplotlib
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    import numpy as np

    matplotlib.use("Agg")  # Non-interactive backend safe for headless environments
    _MATPLOTLIB_AVAILABLE = True
except ImportError:  # pragma: no cover
    _MATPLOTLIB_AVAILABLE = False

if TYPE_CHECKING:
    from composition_verifier.composer import ProtocolComposer
    from composition_verifier.model import ProtocolModel, VerificationResult


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _require_matplotlib(function_name: str) -> None:
    """Raise ImportError with a clear message if matplotlib is absent."""
    if not _MATPLOTLIB_AVAILABLE:
        raise ImportError(
            f"visualization.{function_name} requires matplotlib and numpy. "
            "Install them with: pip install matplotlib numpy"
        )


def _save_or_show(figure: Any, save_path: str | None) -> None:
    """Save figure to ``save_path`` or display interactively.

    RESEARCH TOOL — not production orchestration.

    Args:
        figure: A matplotlib Figure object.
        save_path: If provided, saves to this path. If None, calls plt.show().
    """
    if save_path:
        figure.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Figure saved to %s", save_path)
    else:
        plt.show()
    plt.close(figure)


# ---------------------------------------------------------------------------
# Public visualization functions
# ---------------------------------------------------------------------------

def plot_state_space(
    composer: "ProtocolComposer",
    save_path: str | None = None,
    max_states: int = 200,
) -> None:
    """Plot a grid view of the reachable composed state space.

    RESEARCH TOOL — not production orchestration.

    For each reachable composed state, a row is plotted showing the
    per-protocol state names and the path length (number of actions)
    needed to reach that state from the initial configuration.

    Args:
        composer: A :class:`ProtocolComposer` to enumerate.
        save_path: If provided, the figure is saved here (PNG/PDF/SVG).
            If None, the figure is shown interactively.
        max_states: Maximum number of states to enumerate and display.
            Defaults to 200.

    Example:
        >>> from composition_verifier.scenarios import standard_composition
        >>> from composition_verifier.composer import ProtocolComposer
        >>> composer = ProtocolComposer(standard_composition())
        >>> plot_state_space(composer, save_path="/tmp/state_space.png")
    """
    _require_matplotlib("plot_state_space")

    reachable = composer.enumerate_states(max_states=max_states)
    protocol_names = composer.protocol_names
    num_states = len(reachable)
    num_protocols = len(protocol_names)

    fig, axes = plt.subplots(
        1, 2,
        figsize=(max(10, num_protocols * 2.5), max(6, num_states * 0.35 + 2)),
        gridspec_kw={"width_ratios": [3, 1]},
    )

    # Left panel: state grid
    ax_grid = axes[0]
    ax_grid.set_title(
        f"Reachable Composed State Space\n"
        f"({num_states} states, {num_protocols} protocols)",
        fontsize=11, pad=10,
    )

    # Build a 2D colour matrix: rows = states, cols = protocols
    # Colour encodes a simple hash of the state name for visual distinction
    all_state_names_per_protocol: list[list[str]] = [
        [] for _ in protocol_names
    ]
    for composed_state in reachable:
        for col_idx, name in enumerate(protocol_names):
            all_state_names_per_protocol[col_idx].append(
                composed_state.states.get(name, "?")
            )

    # Assign integer codes to state names for colouring
    unique_labels: list[str] = sorted(
        {
            state_name
            for col in all_state_names_per_protocol
            for state_name in col
        }
    )
    label_to_code = {label: idx for idx, label in enumerate(unique_labels)}
    colour_matrix = np.array(
        [
            [label_to_code.get(s, 0) for s in col]
            for col in all_state_names_per_protocol
        ],
        dtype=float,
    ).T  # shape: (num_states, num_protocols)

    im = ax_grid.imshow(
        colour_matrix,
        aspect="auto",
        cmap="tab20",
        interpolation="nearest",
        vmin=0,
        vmax=max(len(unique_labels) - 1, 1),
    )
    ax_grid.set_xticks(range(num_protocols))
    ax_grid.set_xticklabels(protocol_names, rotation=30, ha="right", fontsize=9)
    ax_grid.set_ylabel("State index (BFS order)", fontsize=9)
    ax_grid.set_xlabel("Protocol", fontsize=9)

    # Annotate cells with state name abbreviation
    for row_idx in range(min(num_states, 50)):  # annotate at most 50 rows
        for col_idx in range(num_protocols):
            label = all_state_names_per_protocol[col_idx][row_idx]
            ax_grid.text(
                col_idx, row_idx, label[:3],
                ha="center", va="center", fontsize=6, color="white",
                fontweight="bold",
            )

    # Right panel: BFS depth histogram
    ax_hist = axes[1]
    depths = [len(composed_state.actions) for composed_state in reachable]
    ax_hist.barh(range(num_states), depths, color="#4C72B0", alpha=0.75)
    ax_hist.set_xlabel("BFS depth", fontsize=9)
    ax_hist.set_title("Action depth", fontsize=10)
    ax_hist.set_yticks([])
    ax_hist.invert_yaxis()

    # Legend for state colours
    legend_patches = [
        mpatches.Patch(
            facecolor=plt.cm.tab20(label_to_code[lbl] / max(len(unique_labels) - 1, 1)),  # type: ignore[attr-defined]
            label=lbl,
        )
        for lbl in unique_labels
    ]
    fig.legend(
        handles=legend_patches,
        loc="lower center",
        ncol=min(len(unique_labels), 6),
        fontsize=8,
        title="State names",
        framealpha=0.9,
    )

    fig.suptitle("Protocol Composition Verifier — State Space", fontsize=13, y=1.01)
    fig.tight_layout()
    _save_or_show(fig, save_path)


def plot_verification_result(
    result: "VerificationResult",
    save_path: str | None = None,
) -> None:
    """Plot a summary card for a single verification result.

    RESEARCH TOOL — not production orchestration.

    Displays the property name, verdict (HOLDS / VIOLATED), number of
    states checked, and — when the property is violated — the
    counterexample path and the implicated protocol.

    Args:
        result: A :class:`VerificationResult` from the verifier.
        save_path: If provided, the figure is saved here.

    Example:
        >>> plot_verification_result(result, save_path="/tmp/result.png")
    """
    _require_matplotlib("plot_verification_result")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")

    verdict_color = "#2ca02c" if result.holds else "#d62728"
    verdict_text = "HOLDS" if result.holds else "VIOLATED"

    # Title block
    ax.text(
        0.5, 0.92,
        f"Property: {result.property_name.replace('_', ' ').title()}",
        ha="center", va="top", fontsize=14, fontweight="bold",
        transform=ax.transAxes,
    )

    # Verdict badge
    ax.text(
        0.5, 0.72,
        verdict_text,
        ha="center", va="top", fontsize=28, fontweight="bold",
        color=verdict_color, transform=ax.transAxes,
    )

    # States checked
    ax.text(
        0.5, 0.52,
        f"States checked: {result.states_checked:,}",
        ha="center", va="top", fontsize=12, color="#333333",
        transform=ax.transAxes,
    )

    # Counterexample details (if any)
    if result.counterexample is not None:
        path_str = " → ".join(result.counterexample.actions) or "(initial state)"
        joint_str = ", ".join(
            f"{k}={v}" for k, v in result.counterexample.states.items()
        )
        details = f"Path: {path_str}\nJoint state: {joint_str}"
        if result.violating_protocol:
            details += f"\nViolating protocol: {result.violating_protocol}"
        ax.text(
            0.5, 0.35,
            details,
            ha="center", va="top", fontsize=9, color="#555555",
            transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#fff3cd", alpha=0.8),
        )

    ax.set_facecolor("#f8f9fa")
    fig.patch.set_facecolor("#f8f9fa")
    fig.suptitle(
        "Protocol Composition Verifier — Verification Result",
        fontsize=11, color="#555555",
    )
    fig.tight_layout()
    _save_or_show(fig, save_path)


def plot_priority_heatmap(
    protocols: list["ProtocolModel"],
    priority: list[str],
    save_path: str | None = None,
) -> None:
    """Plot a heatmap showing per-state permission profiles for each protocol.

    RESEARCH TOOL — not production orchestration.

    For each protocol in ``protocols`` and each of its states, a row in
    the heatmap shows which actions are permitted (green) or denied (red).
    The protocols are displayed in priority order (highest priority at top).

    Args:
        protocols: The list of :class:`ProtocolModel` instances to visualise.
        priority: Protocol names ordered from highest to lowest priority.
        save_path: If provided, the figure is saved here.

    Example:
        >>> from composition_verifier.scenarios import standard_composition
        >>> protocols = standard_composition()
        >>> plot_priority_heatmap(
        ...     protocols, ["ASP", "ATP", "AEAP"],
        ...     save_path="/tmp/priority_heatmap.png",
        ... )
    """
    _require_matplotlib("plot_priority_heatmap")

    # Collect all unique actions
    all_actions = sorted({action for p in protocols for action in p.all_actions()})
    protocol_map = {p.name: p for p in protocols}

    # Order protocols by priority (unknown protocols go last)
    ordered_names = [name for name in priority if name in protocol_map]
    remaining = [p.name for p in protocols if p.name not in ordered_names]
    ordered_names += remaining

    # Build rows: one row per (protocol, state) pair
    row_labels: list[str] = []
    row_data: list[list[float]] = []
    priority_dividers: list[int] = []  # row indices where protocol changes

    current_row = 0
    for protocol_name in ordered_names:
        protocol = protocol_map[protocol_name]
        priority_dividers.append(current_row)
        for state_name in protocol.state_names():
            row_labels.append(f"{protocol_name} / {state_name}")
            protocol.current_state = state_name
            row: list[float] = []
            for action in all_actions:
                decision = protocol.decide(action)
                row.append(1.0 if decision.permitted else 0.0)
            row_data.append(row)
            current_row += 1
        protocol.reset()

    matrix = np.array(row_data)
    num_rows, num_cols = matrix.shape

    fig, ax = plt.subplots(figsize=(max(8, num_cols * 1.2), max(5, num_rows * 0.5 + 2)))

    cmap = matplotlib.colors.ListedColormap(["#d62728", "#2ca02c"])  # type: ignore[attr-defined]
    ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1, interpolation="nearest")

    # Action labels (x-axis)
    ax.set_xticks(range(num_cols))
    ax.set_xticklabels(all_actions, rotation=30, ha="right", fontsize=10)
    ax.set_xlabel("Action", fontsize=10, labelpad=8)

    # State labels (y-axis)
    ax.set_yticks(range(num_rows))
    ax.set_yticklabels(row_labels, fontsize=8)

    # Cell annotations
    for row_idx in range(num_rows):
        for col_idx in range(num_cols):
            value = matrix[row_idx, col_idx]
            text = "Y" if value == 1.0 else "N"
            ax.text(
                col_idx, row_idx, text,
                ha="center", va="center", fontsize=8,
                color="white", fontweight="bold",
            )

    # Horizontal dividers between protocols
    for divider_row in priority_dividers[1:]:
        ax.axhline(divider_row - 0.5, color="white", linewidth=2.5)

    # Priority rank annotations on left margin
    for rank_idx, protocol_name in enumerate(ordered_names):
        divider_row = priority_dividers[rank_idx]
        protocol = protocol_map[protocol_name]
        mid_row = divider_row + len(protocol.state_names()) / 2 - 0.5
        ax.text(
            -0.7, mid_row,
            f"P{rank_idx + 1}",
            ha="right", va="center", fontsize=9,
            color="#555555", fontweight="bold",
            transform=ax.get_yaxis_transform(),
        )

    # Legend
    legend_handles = [
        mpatches.Patch(facecolor="#2ca02c", label="Permitted"),
        mpatches.Patch(facecolor="#d62728", label="Denied"),
    ]
    ax.legend(
        handles=legend_handles, loc="upper right",
        bbox_to_anchor=(1.0, -0.12), ncol=2, fontsize=9, framealpha=0.9,
    )

    ax.set_title(
        f"Permission Profile Heatmap — Priority Order: {' > '.join(priority)}\n"
        f"(RESEARCH TOOL — not production orchestration)",
        fontsize=11, pad=12,
    )
    fig.tight_layout()
    _save_or_show(fig, save_path)


def plot_composition_summary(
    results: dict[str, "VerificationResult"],
    save_path: str | None = None,
) -> None:
    """Plot a bar chart summarising multiple verification results.

    RESEARCH TOOL — not production orchestration.

    Useful for displaying the output of
    :meth:`ProtocolCompositionVerifier.verify_all` at a glance.

    Args:
        results: Dict mapping property name to :class:`VerificationResult`.
        save_path: If provided, the figure is saved here.

    Example:
        >>> plot_composition_summary(
        ...     verifier.verify_all(protocols, priority=["ASP", "ATP", "AEAP"]),
        ...     save_path="/tmp/summary.png",
        ... )
    """
    _require_matplotlib("plot_composition_summary")

    property_names = list(results.keys())
    verdicts = [results[name].holds for name in property_names]
    states_checked = [results[name].states_checked for name in property_names]
    colours = ["#2ca02c" if holds else "#d62728" for holds in verdicts]
    labels = [
        name.replace("_", "\n").title() for name in property_names
    ]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    # Left: verdict bars
    ax_left = axes[0]
    bars = ax_left.bar(range(len(property_names)), [1] * len(property_names),
                       color=colours, alpha=0.85, width=0.5)
    ax_left.set_xticks(range(len(property_names)))
    ax_left.set_xticklabels(labels, fontsize=10)
    ax_left.set_yticks([])
    ax_left.set_title("Verification Verdicts", fontsize=11)
    for idx, (holds, bar) in enumerate(zip(verdicts, bars)):
        ax_left.text(
            bar.get_x() + bar.get_width() / 2,
            0.5,
            "HOLDS" if holds else "VIOLATED",
            ha="center", va="center", fontsize=11, fontweight="bold",
            color="white",
        )
    ax_left.set_ylim(0, 1.4)

    # Right: states checked
    ax_right = axes[1]
    ax_right.barh(range(len(property_names)), states_checked,
                  color="#4C72B0", alpha=0.8)
    ax_right.set_yticks(range(len(property_names)))
    ax_right.set_yticklabels(labels, fontsize=10)
    ax_right.set_xlabel("Composed states checked", fontsize=9)
    ax_right.set_title("Verification Coverage", fontsize=11)
    for idx, count in enumerate(states_checked):
        ax_right.text(
            count + max(states_checked) * 0.01, idx,
            str(count), va="center", fontsize=9,
        )

    fig.suptitle(
        "Protocol Composition Verifier — Experiment Summary\n"
        "(RESEARCH TOOL — not production orchestration)",
        fontsize=12,
    )
    fig.tight_layout()
    _save_or_show(fig, save_path)
