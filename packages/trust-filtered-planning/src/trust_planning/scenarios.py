# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
scenarios.py — Planning scenarios with different action sets and goals.

SIMULATION ONLY. All planning domains, actions, and goals in this module are
SYNTHETIC. They are designed to reproduce the figures in Paper 12's companion
experiments. No real agent tasks, plans, or trust assignments are used.

Trust levels are INTEGERS 0–5. Actions with required_trust > agent trust level
are excluded from the planning search space.
"""

from __future__ import annotations

from trust_planning.model import Action, PlanningDomain, PlanningGoal


# ---------------------------------------------------------------------------
# Domain 1: Linear pipeline — SIMULATION ONLY
# ---------------------------------------------------------------------------


def domain_linear_pipeline() -> PlanningDomain:
    """A linear, sequential processing pipeline domain.

    SIMULATION ONLY. Actions form a strict chain: each action requires the
    output state of the previous one. Higher-trust actions are more efficient
    (lower cost) or unlock shorter paths. Goal: reach 'delivered'.

    Returns:
        PlanningDomain with 8 actions and 2 goals. All data SYNTHETIC.
    """
    actions = [
        Action("lp-a0", "receive_input", required_trust=0, cost=1,
               requires="start", produces="input_received"),
        Action("lp-a1", "validate_basic", required_trust=0, cost=2,
               requires="input_received", produces="validated"),
        Action("lp-a2", "validate_strict", required_trust=3, cost=1,
               requires="input_received", produces="validated"),
        Action("lp-a3", "transform_standard", required_trust=0, cost=3,
               requires="validated", produces="transformed"),
        Action("lp-a4", "transform_optimised", required_trust=2, cost=1,
               requires="validated", produces="transformed"),
        Action("lp-a5", "review_manual", required_trust=0, cost=4,
               requires="transformed", produces="reviewed"),
        Action("lp-a6", "review_automated", required_trust=4, cost=1,
               requires="transformed", produces="reviewed"),
        Action("lp-a7", "deliver", required_trust=0, cost=1,
               requires="reviewed", produces="delivered"),
    ]
    goals = [
        PlanningGoal(
            goal_id="lp-g1",
            description="Process input through pipeline to delivery. SIMULATION ONLY.",
            target_state="delivered",
            initial_state="start",
        ),
        PlanningGoal(
            goal_id="lp-g2",
            description="Fast-track from validated to delivered. SIMULATION ONLY.",
            target_state="delivered",
            initial_state="validated",
        ),
    ]
    return PlanningDomain(
        name="linear_pipeline",
        description=(
            "Linear processing pipeline. Higher-trust actions reduce cost. "
            "SIMULATION ONLY — synthetic data."
        ),
        actions=actions,
        goals=goals,
    )


# ---------------------------------------------------------------------------
# Domain 2: Branching domain — SIMULATION ONLY
# ---------------------------------------------------------------------------


def domain_branching() -> PlanningDomain:
    """A branching planning domain with multiple paths to the goal.

    SIMULATION ONLY. Multiple parallel routes exist; trust level determines
    which shortcuts and efficient branches are available. All data SYNTHETIC.

    Returns:
        PlanningDomain with 10 actions and 2 goals.
    """
    actions = [
        # Main path (low trust)
        Action("br-a0", "init_standard", required_trust=0, cost=2,
               requires="idle", produces="initialised"),
        Action("br-a1", "process_batch", required_trust=0, cost=5,
               requires="initialised", produces="processed"),
        Action("br-a2", "finalise_standard", required_trust=0, cost=3,
               requires="processed", produces="complete"),
        # Shortcut path (medium trust)
        Action("br-a3", "init_fast", required_trust=2, cost=1,
               requires="idle", produces="initialised"),
        Action("br-a4", "process_stream", required_trust=2, cost=3,
               requires="initialised", produces="processed"),
        # High-trust direct path
        Action("br-a5", "init_privileged", required_trust=4, cost=1,
               requires="idle", produces="ready"),
        Action("br-a6", "direct_complete", required_trust=4, cost=2,
               requires="ready", produces="complete"),
        # Finalise variants
        Action("br-a7", "finalise_optimised", required_trust=3, cost=1,
               requires="processed", produces="complete"),
        # Recovery path
        Action("br-a8", "retry_process", required_trust=0, cost=8,
               requires="idle", produces="processed"),
        Action("br-a9", "finalise_retry", required_trust=0, cost=3,
               requires="processed", produces="complete"),
    ]
    goals = [
        PlanningGoal(
            goal_id="br-g1",
            description="Reach 'complete' from 'idle'. SIMULATION ONLY.",
            target_state="complete",
            initial_state="idle",
        ),
        PlanningGoal(
            goal_id="br-g2",
            description="Reach 'complete' from 'initialised'. SIMULATION ONLY.",
            target_state="complete",
            initial_state="initialised",
        ),
    ]
    return PlanningDomain(
        name="branching",
        description=(
            "Multi-path branching domain. Trust unlocks shorter routes. "
            "SIMULATION ONLY — synthetic data."
        ),
        actions=actions,
        goals=goals,
    )


# ---------------------------------------------------------------------------
# Domain 3: Tiered access domain — SIMULATION ONLY
# ---------------------------------------------------------------------------


def domain_tiered_access() -> PlanningDomain:
    """A tiered access domain where each tier of actions requires higher trust.

    SIMULATION ONLY. Actions are organised into trust tiers 0–5. The goal
    is reachable at all trust levels but the path length and cost differ
    significantly by tier. Designed to demonstrate quality degradation. SYNTHETIC.

    Returns:
        PlanningDomain with 12 actions and 1 goal.
    """
    actions = [
        # Tier 0 (always available)
        Action("ta-a0", "step0_slow", required_trust=0, cost=6,
               requires="s0", produces="s1"),
        Action("ta-a1", "step1_slow", required_trust=0, cost=6,
               requires="s1", produces="s2"),
        Action("ta-a2", "step2_slow", required_trust=0, cost=6,
               requires="s2", produces="s3"),
        Action("ta-a3", "step3_slow", required_trust=0, cost=6,
               requires="s3", produces="goal"),
        # Tier 2 (medium trust)
        Action("ta-a4", "step01_medium", required_trust=2, cost=3,
               requires="s0", produces="s2"),
        Action("ta-a5", "step23_medium", required_trust=2, cost=3,
               requires="s2", produces="goal"),
        # Tier 4 (high trust)
        Action("ta-a6", "shortcut_high", required_trust=4, cost=4,
               requires="s0", produces="s3"),
        Action("ta-a7", "finalise_high", required_trust=4, cost=2,
               requires="s3", produces="goal"),
        # Tier 5 (maximum trust — direct path)
        Action("ta-a8", "direct_max", required_trust=5, cost=2,
               requires="s0", produces="goal"),
        # Auxiliary transitions (always available)
        Action("ta-a9", "aux_s1s2", required_trust=0, cost=7,
               requires="s1", produces="s2"),
        Action("ta-a10", "aux_s2s3", required_trust=0, cost=7,
               requires="s2", produces="s3"),
        Action("ta-a11", "aux_s3goal", required_trust=0, cost=7,
               requires="s3", produces="goal"),
    ]
    goals = [
        PlanningGoal(
            goal_id="ta-g1",
            description="Reach 'goal' from 's0'. Trust level affects path cost. SIMULATION ONLY.",
            target_state="goal",
            initial_state="s0",
        ),
    ]
    return PlanningDomain(
        name="tiered_access",
        description=(
            "Tiered access domain: trust level determines action shortcuts. "
            "SIMULATION ONLY — synthetic data."
        ),
        actions=actions,
        goals=goals,
    )


# ---------------------------------------------------------------------------
# Domain 4: High-restriction domain — SIMULATION ONLY
# ---------------------------------------------------------------------------


def domain_high_restriction() -> PlanningDomain:
    """A heavily restricted domain where many actions require high trust.

    SIMULATION ONLY. Most actions require trust level >= 3. Low-trust agents
    are severely constrained and may be unable to reach many goals. Designed
    to show sharp quality degradation below trust level 3. All data SYNTHETIC.

    Returns:
        PlanningDomain with 10 actions and 2 goals.
    """
    actions = [
        Action("hr-a0", "basic_open", required_trust=0, cost=2,
               requires="locked", produces="unlocked"),
        Action("hr-a1", "privileged_scan", required_trust=3, cost=2,
               requires="unlocked", produces="scanned"),
        Action("hr-a2", "privileged_analyse", required_trust=3, cost=2,
               requires="scanned", produces="analysed"),
        Action("hr-a3", "secure_submit", required_trust=4, cost=1,
               requires="analysed", produces="submitted"),
        Action("hr-a4", "admin_approve", required_trust=5, cost=1,
               requires="submitted", produces="approved"),
        Action("hr-a5", "manual_fallback", required_trust=0, cost=20,
               requires="unlocked", produces="approved"),
        Action("hr-a6", "admin_shortcut", required_trust=5, cost=2,
               requires="locked", produces="approved"),
        Action("hr-a7", "partial_analyse", required_trust=2, cost=5,
               requires="unlocked", produces="analysed"),
        Action("hr-a8", "basic_submit", required_trust=1, cost=6,
               requires="analysed", produces="submitted"),
        Action("hr-a9", "manual_approve", required_trust=0, cost=10,
               requires="submitted", produces="approved"),
    ]
    goals = [
        PlanningGoal(
            goal_id="hr-g1",
            description="Reach 'approved' from 'locked'. SIMULATION ONLY.",
            target_state="approved",
            initial_state="locked",
        ),
        PlanningGoal(
            goal_id="hr-g2",
            description="Reach 'submitted' from 'unlocked'. SIMULATION ONLY.",
            target_state="submitted",
            initial_state="unlocked",
        ),
    ]
    return PlanningDomain(
        name="high_restriction",
        description=(
            "High-restriction domain: most actions require trust >= 3. "
            "SIMULATION ONLY — synthetic data."
        ),
        actions=actions,
        goals=goals,
    )


# ---------------------------------------------------------------------------
# Dataset accessors
# ---------------------------------------------------------------------------


def all_domains() -> list[PlanningDomain]:
    """Return all synthetic planning domains.

    SIMULATION ONLY. All domains and actions are SYNTHETIC.

    Returns:
        List of all PlanningDomain instances.
    """
    return [
        domain_linear_pipeline(),
        domain_branching(),
        domain_tiered_access(),
        domain_high_restriction(),
    ]
