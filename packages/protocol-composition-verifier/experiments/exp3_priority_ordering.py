# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Experiment 3 — Priority Ordering
==================================

RESEARCH TOOL — not production orchestration.
Companion to Papers 9/25, Section 4.3.

Hypothesis
----------
When multiple governance protocols compose, a consistent total priority
ordering must hold: a higher-priority protocol's denial cannot be
overridden by any lower-priority protocol's permission. We evaluate the
ordering SAFETY > COMPLIANCE > EFFICIENCY, mapped to ASP > ATP > AEAP.

Method
------
1. Define the priority order: ASP (safety) > ATP (compliance) > AEAP (efficiency).
2. Verify priority ordering for the [ATP, ASP, AEAP] composition.
3. Report which protocol's denials dominate in each state of the product
   state machine.
4. Build a per-state permission matrix showing the effective priority cascade.

Expected output
---------------
    [EXP3] Priority ordering: ASP > ATP > AEAP
      Property  : priority_ordering
      Verdict   : HOLDS
      States    : 27

    [EXP3] Denial dominance summary:
      Joint states where ASP dominates  : 12 / 27
      Joint states where ATP dominates  : 8  / 27
      Joint states where AEAP dominates : 7  / 27
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from composition_verifier.composer import ProtocolComposer
from composition_verifier.model import ProtocolModel
from composition_verifier.scenarios import build_aeap, build_asp, build_atp, ALL_ACTIONS
from composition_verifier.verifier import ProtocolCompositionVerifier


PRIORITY_ORDER: list[str] = ["ASP", "ATP", "AEAP"]


def _dominant_denier_for_joint(
    protocols: list[ProtocolModel],
    joint: dict[str, str],
    priority_order: list[str],
) -> str | None:
    """Return the name of the highest-priority protocol that denies any action.

    RESEARCH TOOL — not production orchestration.

    Args:
        protocols: The list of :class:`ProtocolModel` instances.
        joint: Mapping from protocol name to current state name.
        priority_order: Protocol names from highest to lowest priority.

    Returns:
        The name of the highest-priority denier, or None if all actions are
        permitted by all protocols in this joint state.
    """
    protocol_map = {p.name: p for p in protocols}
    priority_rank = {name: i for i, name in enumerate(priority_order)}
    default_rank = len(priority_order)

    composer = ProtocolComposer(protocols)
    for protocol in protocols:
        state_name = joint.get(protocol.name)
        if state_name and state_name in protocol.states:
            protocol.current_state = state_name

    all_deniers: set[str] = set()
    for action in ALL_ACTIONS:
        decision = composer.compose_decisions(action)
        for individual in decision.individual_decisions:
            if not individual.permitted:
                all_deniers.add(individual.protocol)

    for protocol in protocols:
        protocol.reset()

    if not all_deniers:
        return None

    return min(all_deniers, key=lambda name: priority_rank.get(name, default_rank))


def _build_dominance_summary(
    protocols: list[ProtocolModel],
    priority_order: list[str],
) -> dict[str, int]:
    """Count joint states where each protocol is the dominant denier.

    RESEARCH TOOL — not production orchestration.

    Returns:
        Dict mapping protocol name to count of joint states it dominates.
    """
    composer = ProtocolComposer(protocols)
    all_joints = composer.enumerate_all_joint_states()

    dominance_counts: dict[str, int] = {name: 0 for name in priority_order}
    dominance_counts["none"] = 0

    for joint in all_joints:
        dominant = _dominant_denier_for_joint(protocols, joint, priority_order)
        key = dominant if dominant in dominance_counts else "none"
        dominance_counts[key] += 1

    return dominance_counts


def run() -> dict[str, object]:
    """Execute Experiment 3 and return a results dictionary.

    RESEARCH TOOL — not production orchestration.

    Returns:
        Dict with keys:
            - ``priority_result``: :class:`VerificationResult`
            - ``dominance_summary``: dict[str, int] — per-protocol dominance counts
            - ``total_joint_states``: int
    """
    verifier = ProtocolCompositionVerifier(max_states=10_000)

    protocols = [build_atp(), build_asp(), build_aeap()]
    priority_result = verifier.verify_priority_ordering(protocols, PRIORITY_ORDER)

    print(f"\n[EXP3] Priority ordering: {' > '.join(PRIORITY_ORDER)}")
    print(f"  Property  : {priority_result.property_name}")
    print(f"  Verdict   : {'HOLDS' if priority_result.holds else 'VIOLATED'}")
    print(f"  States    : {priority_result.states_checked}")
    if not priority_result.holds:
        print(f"  Violation counterexample: {priority_result.counterexample}")
        print(f"  Violating protocol      : {priority_result.violating_protocol}")

    # -- Dominance summary --
    protocols_for_summary = [build_atp(), build_asp(), build_aeap()]
    dominance_summary = _build_dominance_summary(protocols_for_summary, PRIORITY_ORDER)

    # Total joint states = product of state counts
    total_joint = sum(dominance_summary.values())

    print("\n[EXP3] Denial dominance summary:")
    for protocol_name in PRIORITY_ORDER:
        count = dominance_summary[protocol_name]
        print(f"  Joint states where {protocol_name} dominates  : "
              f"{count:2d} / {total_joint}")
    no_denier_count = dominance_summary.get("none", 0)
    print(f"  Joint states with no denier             : "
          f"{no_denier_count:2d} / {total_joint}")
    print()

    return {
        "priority_result": priority_result,
        "dominance_summary": dominance_summary,
        "total_joint_states": total_joint,
    }


if __name__ == "__main__":
    run()
