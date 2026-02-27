# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation
"""
max_depth_calculator.py — Maximum safe delegation depth calculator.

Computes the maximum delegation depth that preserves a minimum operational
trust level, given a root trust value and a per-level trust decay.

Decay model: trust_at_depth(d) = max(0, root_trust - d * decay_per_level)

All values are synthetic and for academic illustration only.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass


# ── Data models ────────────────────────────────────────────────────────────────

@dataclass
class DepthConstraint:
    """Configuration for a delegation depth calculation."""

    max_depth: int
    min_trust_at_leaf: int
    trust_decay_per_level: int

    def __post_init__(self) -> None:
        if self.max_depth < 0:
            raise ValueError("max_depth must be non-negative")
        if not 0 <= self.min_trust_at_leaf <= 5:
            raise ValueError("min_trust_at_leaf must be 0–5")
        if self.trust_decay_per_level < 0:
            raise ValueError("trust_decay_per_level must be non-negative")


# ── Calculator ─────────────────────────────────────────────────────────────────

class DepthCalculator:
    """Calculate maximum safe delegation depth under a linear trust decay model.

    The trust decay model is intentionally simplified for academic illustration.
    Real delegation systems may use non-linear, context-dependent decay.
    """

    ABSOLUTE_MAX_SEARCH_DEPTH: int = 50     # upper bound for depth search

    def trust_at_depth(
        self,
        root_trust: int,
        depth: int,
        decay: int,
    ) -> int:
        """Compute trust level at a given delegation depth.

        Trust at depth d = max(0, root_trust - d * decay).

        Args:
            root_trust: Trust level at depth 0 (0–5).
            depth: Delegation depth to evaluate.
            decay: Trust units lost per delegation level.

        Returns:
            Trust level at the given depth, clamped to [0, 5].
        """
        if root_trust < 0 or root_trust > 5:
            raise ValueError(f"root_trust must be 0–5, got {root_trust}")
        if depth < 0:
            raise ValueError(f"depth must be non-negative, got {depth}")
        if decay < 0:
            raise ValueError(f"decay must be non-negative, got {decay}")
        return max(0, root_trust - depth * decay)

    def calculate_max_depth(
        self,
        root_trust: int,
        min_leaf_trust: int,
        decay: int,
    ) -> int:
        """Return the maximum delegation depth before trust drops below min_leaf_trust.

        Searches depth from 0 upward and stops at the last depth where
        trust_at_depth >= min_leaf_trust.

        Returns 0 if root_trust is already below min_leaf_trust.
        """
        if root_trust < min_leaf_trust:
            return 0
        if decay == 0:
            return self.ABSOLUTE_MAX_SEARCH_DEPTH

        max_depth = 0
        for depth in range(self.ABSOLUTE_MAX_SEARCH_DEPTH + 1):
            if self.trust_at_depth(root_trust, depth, decay) >= min_leaf_trust:
                max_depth = depth
            else:
                break
        return max_depth

    def generate_depth_table(
        self,
        root_trust: int,
        decay: int,
    ) -> list[tuple[int, int]]:
        """Generate a table of (depth, trust_value) pairs from depth 0 to zero-trust.

        Stops when trust reaches 0 or ABSOLUTE_MAX_SEARCH_DEPTH, whichever comes first.

        Returns:
            List of (depth, trust) tuples.
        """
        rows: list[tuple[int, int]] = []
        for depth in range(self.ABSOLUTE_MAX_SEARCH_DEPTH + 1):
            trust = self.trust_at_depth(root_trust, depth, decay)
            rows.append((depth, trust))
            if trust == 0:
                break
        return rows

    def safety_analysis(
        self,
        root_trust: int,
        decay: int,
        operational_minimum: int = 1,
    ) -> str:
        """Describe at what depth trust drops below the operational minimum.

        Args:
            root_trust: Starting trust level (0–5).
            decay: Trust decay per delegation level.
            operational_minimum: Lowest trust considered operationally viable.

        Returns:
            A human-readable safety analysis string.
        """
        max_safe_depth = self.calculate_max_depth(root_trust, operational_minimum, decay)
        table = self.generate_depth_table(root_trust, decay)

        lines: list[str] = [
            "Delegation Depth Safety Analysis",
            "=" * 40,
            f"  Root trust       : L{root_trust}",
            f"  Decay per level  : {decay} trust unit(s)",
            f"  Operational min  : L{operational_minimum}",
            f"  Max safe depth   : {max_safe_depth}",
            "",
            "  Depth table:",
            f"  {'Depth':>6}  {'Trust':>6}  {'Status':>12}",
            "  " + "-" * 28,
        ]

        for depth, trust in table:
            status = "operational" if trust >= operational_minimum else "below minimum"
            marker = " <--" if trust < operational_minimum and (depth == 0 or table[depth - 1][1] >= operational_minimum) else ""
            lines.append(f"  {depth:>6}  {'L' + str(trust):>6}  {status}{marker}")

        return "\n".join(lines)

    def plot_trust_decay(
        self,
        root_trust: int,
        decay: int,
        operational_minimum: int = 1,
        output_path: str = "trust_decay.png",
    ) -> None:
        """Plot the trust decay curve against delegation depth.

        Marks the operational minimum as a horizontal reference line.
        """
        table = self.generate_depth_table(root_trust, decay)
        depths = [row[0] for row in table]
        trusts = [row[1] for row in table]
        max_safe_depth = self.calculate_max_depth(root_trust, operational_minimum, decay)

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(depths, trusts, "o-", color="#1565C0", linewidth=2, markersize=7, label="Trust at depth")
        ax.axhline(
            y=operational_minimum,
            color="#C62828", linestyle="--", linewidth=1.5,
            label=f"Operational minimum (L{operational_minimum})",
        )
        ax.axvline(
            x=max_safe_depth,
            color="#2E7D32", linestyle=":", linewidth=1.5,
            label=f"Max safe depth ({max_safe_depth})",
        )
        ax.fill_between(
            depths, trusts, operational_minimum,
            where=[t >= operational_minimum for t in trusts],
            alpha=0.12, color="#1565C0", label="Safe zone",
        )
        ax.set_xlabel("Delegation Depth")
        ax.set_ylabel("Trust Level (0–5)")
        ax.set_title(
            f"Trust Decay by Delegation Depth\n"
            f"Root L{root_trust}, decay={decay}/level — Synthetic Simulation"
        )
        ax.set_ylim(-0.3, 5.5)
        ax.set_xticks(depths)
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=120)
        plt.show()


# ── Example usage ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    calculator = DepthCalculator()

    print(calculator.safety_analysis(root_trust=5, decay=1, operational_minimum=1))
    print()

    # Print a comparison table for different root trust levels
    print("Max Safe Depth Comparison (decay=1, min_leaf=1)")
    print("=" * 40)
    print(f"  {'Root Trust':>12}  {'Max Depth':>10}")
    print("  " + "-" * 26)
    for root in range(6):
        max_depth = calculator.calculate_max_depth(root, min_leaf_trust=1, decay=1)
        print(f"  {'L' + str(root):>12}  {max_depth:>10}")

    calculator.plot_trust_decay(root_trust=5, decay=1, operational_minimum=1)
