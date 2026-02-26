# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""Matplotlib figure generators for governed-forgetting simulation results.

SIMULATION ONLY — not production AMGP implementation.
All figures are generated from synthetic data. No real agent memory content
is represented or implied by these visualizations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    import matplotlib.figure

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_STYLE_DEFAULTS: dict[str, Any] = {
    "figure.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.35,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "legend.fontsize": 9,
    "font.family": "sans-serif",
}


def _apply_style(ax: Any) -> None:
    """Apply minimal styling to an Axes object."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.35)


# ---------------------------------------------------------------------------
# Figure 1 — Time-Based Retention Curve
# ---------------------------------------------------------------------------

def fig1_time_based_retention(
    history_data: list[dict[str, int]],
    ttl: int = 100,
    title: str = "Figure 1 — Time-Based Retention (Synthetic)",
) -> "matplotlib.figure.Figure":
    """Generate the retention curve for the time-based scenario.

    SIMULATION ONLY — not production AMGP implementation.
    Plots active and cumulative-forgotten memory counts over simulation time.

    Args:
        history_data: List of dicts with keys ``"timestep"``, ``"active"``,
                      ``"forgotten"`` — typically loaded from ``fig1_data.json``.
        ttl: The TTL value used in the simulation (shown as a reference line).
        title: Figure title string.

    Returns:
        A ``matplotlib.figure.Figure`` instance.
    """
    import matplotlib.pyplot as plt  # noqa: PLC0415

    timesteps = [d["timestep"] for d in history_data]
    active = [d["active"] for d in history_data]
    forgotten = [d["forgotten"] for d in history_data]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    fig.suptitle(title, y=1.01, fontsize=13)

    # Left: active memory count
    ax0 = axes[0]
    ax0.plot(timesteps, active, color="#2563EB", linewidth=1.8, label="Active")
    ax0.set_xlabel("Simulation Timestep")
    ax0.set_ylabel("Active Memory Records")
    ax0.set_title("Active Memories Over Time")
    _apply_style(ax0)

    # Right: cumulative forgotten
    ax1 = axes[1]
    ax1.plot(timesteps, forgotten, color="#DC2626", linewidth=1.8, label="Forgotten (cumulative)")
    ax1.set_xlabel("Simulation Timestep")
    ax1.set_ylabel("Cumulative Forgotten Records")
    ax1.set_title("Cumulative Forgotten Records")
    _apply_style(ax1)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figure 2 — Relevance Decay Retention Curve
# ---------------------------------------------------------------------------

def fig2_relevance_decay(
    history_data: list[dict[str, int]],
    decay_rate: float = 0.01,
    threshold: float = 0.3,
    title: str = "Figure 2 — Relevance Decay Retention (Synthetic)",
) -> "matplotlib.figure.Figure":
    """Generate the retention curve for the relevance-decay scenario.

    SIMULATION ONLY — not production AMGP implementation.
    Plots active memory count alongside the theoretical effective-score
    curve for a median-relevance record (score=0.5) to illustrate the
    decay dynamics.

    Args:
        history_data: List of dicts with keys ``"timestep"``, ``"active"``,
                      ``"forgotten"``.
        decay_rate: Decay constant used in the simulation.
        threshold: Relevance threshold used in the simulation.
        title: Figure title string.

    Returns:
        A ``matplotlib.figure.Figure`` instance.
    """
    import matplotlib.pyplot as plt  # noqa: PLC0415

    timesteps = [d["timestep"] for d in history_data]
    active = [d["active"] for d in history_data]

    # Theoretical decay curve for a record with relevance_score=0.5
    t_arr = np.linspace(0, max(timesteps), 300)
    theoretical_score = 0.5 * np.exp(-decay_rate * t_arr)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    fig.suptitle(title, y=1.01, fontsize=13)

    ax0 = axes[0]
    ax0.plot(timesteps, active, color="#059669", linewidth=1.8, label="Active")
    ax0.set_xlabel("Simulation Timestep")
    ax0.set_ylabel("Active Memory Records")
    ax0.set_title("Active Memories Over Time")
    _apply_style(ax0)

    ax1 = axes[1]
    ax1.plot(t_arr, theoretical_score, color="#7C3AED", linewidth=1.8, label="Effective score (initial=0.5)")
    ax1.axhline(threshold, color="#DC2626", linestyle="--", linewidth=1.2, label=f"Threshold={threshold}")
    ax1.set_xlabel("Age (timesteps since creation)")
    ax1.set_ylabel("Effective Relevance Score")
    ax1.set_title("Theoretical Relevance Decay")
    ax1.legend()
    _apply_style(ax1)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figure 3 — Consent Revocation Staircase
# ---------------------------------------------------------------------------

def fig3_consent_revocation(
    history_data: list[dict[str, int]],
    revocation_timesteps: list[int] | None = None,
    title: str = "Figure 3 — Consent Revocation (Synthetic)",
) -> "matplotlib.figure.Figure":
    """Generate the retention staircase for the consent-revocation scenario.

    SIMULATION ONLY — not production AMGP implementation.
    Plots active memory count with vertical markers at the scheduled batch
    revocation timesteps to illustrate the staircase drop pattern.

    Args:
        history_data: List of dicts with keys ``"timestep"``, ``"active"``,
                      ``"forgotten"``.
        revocation_timesteps: Timesteps at which revocations were scheduled.
                              Defaults to ``[100, 200, 300]``.
        title: Figure title string.

    Returns:
        A ``matplotlib.figure.Figure`` instance.
    """
    import matplotlib.pyplot as plt  # noqa: PLC0415

    if revocation_timesteps is None:
        revocation_timesteps = [100, 200, 300]

    timesteps = [d["timestep"] for d in history_data]
    active = [d["active"] for d in history_data]
    forgotten = [d["forgotten"] for d in history_data]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.suptitle(title, y=1.01, fontsize=13)

    ax.plot(timesteps, active, color="#2563EB", linewidth=1.8, label="Active")
    ax.plot(timesteps, forgotten, color="#DC2626", linewidth=1.2,
            linestyle="--", label="Forgotten (cumulative)")

    for t in revocation_timesteps:
        ax.axvline(t, color="#F59E0B", linestyle=":", linewidth=1.5,
                   label=f"Revocation t={t}" if t == revocation_timesteps[0] else None)

    ax.set_xlabel("Simulation Timestep")
    ax.set_ylabel("Memory Record Count")
    ax.set_title("Active vs. Forgotten — Consent Batch Revocations")
    ax.legend()
    _apply_style(ax)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figure 4 — Composite Policy Comparison
# ---------------------------------------------------------------------------

def fig4_composite_policy(
    history_data_composite: list[dict[str, int]],
    history_data_time: list[dict[str, int]],
    history_data_decay: list[dict[str, int]],
    title: str = "Figure 4 — Composite Policy vs. Individual Policies (Synthetic)",
) -> "matplotlib.figure.Figure":
    """Generate the composite-vs-individual policy comparison figure.

    SIMULATION ONLY — not production AMGP implementation.
    Overlays the active-memory curves from the composite policy against the
    two individual baseline policies (time-based and relevance-decay) to
    show the accelerated forgetting from policy composition.

    Args:
        history_data_composite: History from the composite scenario.
        history_data_time: History from the time-based scenario.
        history_data_decay: History from the relevance-decay scenario.
        title: Figure title string.

    Returns:
        A ``matplotlib.figure.Figure`` instance.
    """
    import matplotlib.pyplot as plt  # noqa: PLC0415

    def _extract(data: list[dict[str, int]]) -> tuple[list[int], list[int]]:
        return [d["timestep"] for d in data], [d["active"] for d in data]

    t_comp, a_comp = _extract(history_data_composite)
    t_time, a_time = _extract(history_data_time)
    t_dec, a_dec = _extract(history_data_decay)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.suptitle(title, y=1.01, fontsize=13)

    ax.plot(t_time, a_time, color="#2563EB", linewidth=1.5, linestyle="-",
            label="Time-Based (baseline)")
    ax.plot(t_dec, a_dec, color="#059669", linewidth=1.5, linestyle="-",
            label="Relevance Decay (baseline)")
    ax.plot(t_comp, a_comp, color="#DC2626", linewidth=2.0, linestyle="-",
            label="Composite (Time + Decay + Consent)")

    ax.set_xlabel("Simulation Timestep")
    ax.set_ylabel("Active Memory Records")
    ax.set_title("Retention Rate: Composite Policy vs. Individual Policies")
    ax.legend()
    _apply_style(ax)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Convenience dispatcher
# ---------------------------------------------------------------------------

def render_all_figures(
    fig_data: dict[str, list[dict[str, int]]],
    output_dir: str | None = None,
) -> dict[str, "matplotlib.figure.Figure"]:
    """Render all four paper figures from pre-computed data.

    SIMULATION ONLY — not production AMGP implementation.
    Loads data for all four figures and returns a dict of Figure objects.
    If ``output_dir`` is provided, figures are saved as PNG files.

    Args:
        fig_data: Dict with keys ``"fig1"``, ``"fig2"``, ``"fig3"``,
                  ``"fig4_composite"``, ``"fig4_time"``, ``"fig4_decay"``.
        output_dir: Optional directory path for saving PNG files.

    Returns:
        Dict mapping figure key to matplotlib Figure instance.
    """
    import matplotlib.pyplot as plt  # noqa: PLC0415

    figures: dict[str, matplotlib.figure.Figure] = {}

    if "fig1" in fig_data:
        figures["fig1"] = fig1_time_based_retention(fig_data["fig1"])
    if "fig2" in fig_data:
        figures["fig2"] = fig2_relevance_decay(fig_data["fig2"])
    if "fig3" in fig_data:
        figures["fig3"] = fig3_consent_revocation(fig_data["fig3"])
    if all(k in fig_data for k in ("fig4_composite", "fig4_time", "fig4_decay")):
        figures["fig4"] = fig4_composite_policy(
            fig_data["fig4_composite"],
            fig_data["fig4_time"],
            fig_data["fig4_decay"],
        )

    if output_dir is not None:
        import os  # noqa: PLC0415
        os.makedirs(output_dir, exist_ok=True)
        for key, fig in figures.items():
            path = os.path.join(output_dir, f"{key}.png")
            fig.savefig(path, dpi=150, bbox_inches="tight")
            print(f"Saved {path}")

    plt.close("all")
    return figures
