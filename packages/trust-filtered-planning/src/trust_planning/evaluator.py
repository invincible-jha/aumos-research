# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
evaluator.py — PlanEvaluator: quality metrics for plan assessment.

SIMULATION ONLY. Computes simple arithmetic metrics over plans produced by
TrustFilteredPlanner and SimplePlanner: step count, action type diversity,
and optimality gap. No production plan quality scoring or behavioral analysis.
All planning data is SYNTHETIC.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from trust_planning.model import Plan


# ---------------------------------------------------------------------------
# Quality metric dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlanQualityMetrics:
    """Quality metrics for a single plan.

    SIMULATION ONLY. All metrics use simple arithmetic — no semantic scoring,
    no behavioral analysis.

    Attributes:
        goal_id: Identifier of the goal this plan addresses.
        trust_level: Trust level used when generating this plan.
        reachable: True when the goal was reachable at this trust level.
        step_count: Number of actions in the plan.
        total_cost: Sum of action costs.
        action_diversity: Fraction of unique action IDs in the plan (0.0–1.0).
            1.0 means all actions are distinct; 0.0 means empty plan.
        optimality_gap: Ratio of this plan's cost to the baseline optimal cost.
            0.0 = optimal (or plan not reachable), 1.0 = twice the optimal cost.
        mean_action_cost: Arithmetic mean cost per action step.
    """

    goal_id: str
    trust_level: int
    reachable: bool
    step_count: int
    total_cost: int
    action_diversity: float
    optimality_gap: float
    mean_action_cost: float


@dataclass(frozen=True)
class TrustComparisonRow:
    """A single row in a trust-level comparison table.

    SIMULATION ONLY.

    Attributes:
        trust_level: Integer trust level [0, 5].
        reachable: Whether the goal was reachable at this trust level.
        step_count: Plan length in actions.
        total_cost: Plan total cost.
        optimality_gap: Cost ratio relative to the trust=5 baseline plan.
        available_action_count: Number of actions available at this trust level.
    """

    trust_level: int
    reachable: bool
    step_count: int
    total_cost: int
    optimality_gap: float
    available_action_count: int


# ---------------------------------------------------------------------------
# PlanEvaluator
# ---------------------------------------------------------------------------


class PlanEvaluator:
    """Compute quality metrics over plans produced by TrustFilteredPlanner or SimplePlanner.

    SIMULATION ONLY — does not implement production plan quality scoring or Paper 12's
    full evaluation methodology. Uses simple arithmetic metrics only. All data SYNTHETIC.

    Example::

        evaluator = PlanEvaluator()
        metrics = evaluator.evaluate(plan, baseline_optimal_cost=3)
        print(metrics.optimality_gap)
    """

    def evaluate(
        self,
        plan: Plan,
        baseline_optimal_cost: int = 0,
    ) -> PlanQualityMetrics:
        """Compute quality metrics for a single plan.

        SIMULATION ONLY. Computes step_count, total_cost, action_diversity,
        optimality_gap, and mean_action_cost. All metrics use simple arithmetic.

        Args:
            plan: The Plan to evaluate.
            baseline_optimal_cost: The known optimal cost (e.g., from SimplePlanner
                with trust_level=5). Used to compute optimality_gap.
                Pass 0 to skip optimality_gap computation (returns 0.0).

        Returns:
            PlanQualityMetrics with all computed values.
        """
        if not plan.reachable or not plan.actions:
            return PlanQualityMetrics(
                goal_id=plan.goal_id,
                trust_level=plan.trust_level,
                reachable=plan.reachable,
                step_count=0,
                total_cost=0,
                action_diversity=0.0,
                optimality_gap=0.0,
                mean_action_cost=0.0,
            )

        step_count = len(plan.actions)
        unique_actions = len({a.action_id for a in plan.actions})
        action_diversity = round(unique_actions / step_count, 6)

        optimality_gap = 0.0
        if baseline_optimal_cost > 0 and plan.total_cost > baseline_optimal_cost:
            optimality_gap = round(
                (plan.total_cost - baseline_optimal_cost) / baseline_optimal_cost, 6
            )

        mean_action_cost = round(plan.total_cost / step_count, 6)

        return PlanQualityMetrics(
            goal_id=plan.goal_id,
            trust_level=plan.trust_level,
            reachable=plan.reachable,
            step_count=step_count,
            total_cost=plan.total_cost,
            action_diversity=action_diversity,
            optimality_gap=optimality_gap,
            mean_action_cost=mean_action_cost,
        )

    def compare_across_trust_levels(
        self,
        plans: list[Plan],
        total_domain_actions: int,
    ) -> list[TrustComparisonRow]:
        """Build a comparison table of plan quality across trust levels.

        SIMULATION ONLY. Takes a list of plans (one per trust level, sorted
        ascending) and computes per-row metrics with optimality gap relative
        to the highest-trust plan in the list. All data is SYNTHETIC.

        Args:
            plans: List of Plan objects, one per trust level (sorted ascending).
            total_domain_actions: Total actions in the domain (for availability ratio).

        Returns:
            List of TrustComparisonRow objects, one per plan.
        """
        if not plans:
            return []

        # Baseline optimal: last reachable plan in the list (highest trust level)
        reachable_plans = [plan for plan in plans if plan.reachable]
        baseline_cost = (
            min(plan.total_cost for plan in reachable_plans)
            if reachable_plans
            else 0
        )

        rows: list[TrustComparisonRow] = []
        for plan in plans:
            if plan.reachable and plan.total_cost > 0 and baseline_cost > 0:
                optimality_gap = round(
                    (plan.total_cost - baseline_cost) / baseline_cost, 6
                )
            else:
                optimality_gap = 0.0

            # Available actions at this trust level: actions with required_trust <= level
            # We derive this from the plan's trust_level; count not available here directly
            # so we use step_count / total as a proxy, capped at 1.0
            available_count = plan.trust_level + 1  # simplified proxy: levels 0..trust_level
            # Overriding with a simple formula: available ≈ total * (trust+1) / 6
            available_count = max(
                plan.length,
                round(total_domain_actions * (plan.trust_level + 1) / 6),
            )

            rows.append(TrustComparisonRow(
                trust_level=plan.trust_level,
                reachable=plan.reachable,
                step_count=plan.length,
                total_cost=plan.total_cost,
                optimality_gap=optimality_gap,
                available_action_count=available_count,
            ))

        return rows

    def reachability_by_trust(self, plans: list[Plan]) -> dict[int, bool]:
        """Return a dict mapping trust level to reachability flag.

        SIMULATION ONLY.

        Args:
            plans: List of Plan objects from compare_trust_levels.

        Returns:
            Dict mapping trust_level integer to reachable boolean.
        """
        return {plan.trust_level: plan.reachable for plan in plans}

    def quality_degradation_rate(
        self,
        plans: list[Plan],
        baseline_cost: int,
    ) -> list[float]:
        """Compute cost degradation rate from baseline as trust level decreases.

        SIMULATION ONLY. Returns a list of fractional cost increases relative
        to the baseline, one per plan, in the same order as the input list.
        Unreachable plans get a degradation of float('inf').

        Args:
            plans: List of Plan objects ordered by trust level.
            baseline_cost: The optimal plan cost (from the highest trust level).

        Returns:
            List of float degradation values, one per plan.
        """
        degradation: list[float] = []
        for plan in plans:
            if not plan.reachable or baseline_cost == 0:
                degradation.append(float("inf"))
            elif plan.total_cost <= baseline_cost:
                degradation.append(0.0)
            else:
                rate = round((plan.total_cost - baseline_cost) / baseline_cost, 6)
                degradation.append(rate)
        return degradation
