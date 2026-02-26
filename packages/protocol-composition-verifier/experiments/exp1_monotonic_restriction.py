# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Experiment 1 — Monotonic Restriction
=====================================

RESEARCH TOOL — not production orchestration.
Companion to Papers 9/25, Section 4.1.

Hypothesis
----------
When multiple governance protocol state machines are composed using AND
semantics, the resulting composed system is *at most* as permissive as
the most restrictive component protocol. Composition can only restrict
permissions; it can never expand them.

Method
------
1. Build the two-protocol composition [ATP, ASP].
2. Verify monotonic restriction holds.
3. Extend to the three-protocol composition [ATP, ASP, AEAP].
4. Verify monotonic restriction holds for the extended composition.
5. Report the number of states checked and the permission reduction
   relative to the most permissive single protocol.

Expected output
---------------
    [EXP1] Two-protocol composition (ATP + ASP)
      Property  : monotonic_restriction
      Verdict   : HOLDS
      States    : 9

    [EXP1] Three-protocol composition (ATP + ASP + AEAP)
      Property  : monotonic_restriction
      Verdict   : HOLDS
      States    : 27

    [EXP1] Permission reduction summary:
      Most permissive single protocol : ATP  (7 / 15 permitted transitions)
      Two-protocol composition permits: 4 actions in initial joint state
      Three-protocol composition      : 2 actions in initial joint state
"""

from __future__ import annotations

import sys
import os

# Allow running as a script without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from composition_verifier.composer import ProtocolComposer
from composition_verifier.model import ProtocolModel
from composition_verifier.scenarios import build_aeap, build_asp, build_atp
from composition_verifier.verifier import ProtocolCompositionVerifier


def _count_permitted_transitions(protocol: ProtocolModel) -> int:
    """Count the total number of explicitly permitted transitions.

    RESEARCH TOOL — not production orchestration.
    """
    return sum(1 for t in protocol.transitions if t.permitted)


def _count_permitted_actions_in_initial_state(protocols: list[ProtocolModel]) -> int:
    """Count actions permitted in the joint initial state.

    RESEARCH TOOL — not production orchestration.
    """
    composer = ProtocolComposer(protocols)
    from composition_verifier.scenarios import ALL_ACTIONS
    permitted = [
        action for action in ALL_ACTIONS
        if composer.compose_decisions(action).globally_permitted
    ]
    return len(permitted)


def run() -> dict[str, object]:
    """Execute Experiment 1 and return a results dictionary.

    RESEARCH TOOL — not production orchestration.

    Returns:
        Dict with keys:
            - ``two_protocol``: :class:`VerificationResult` for [ATP, ASP]
            - ``three_protocol``: :class:`VerificationResult` for [ATP, ASP, AEAP]
            - ``initial_permitted_two``: int — permitted actions in two-protocol initial state
            - ``initial_permitted_three``: int — permitted actions in three-protocol initial state
            - ``most_permissive_name``: str — name of most permissive single protocol
            - ``most_permissive_count``: int — its permitted transition count
    """
    verifier = ProtocolCompositionVerifier(max_states=10_000)

    # -- Two-protocol composition --
    atp = build_atp()
    asp = build_asp()
    protocols_two = [atp, asp]
    result_two = verifier.verify_monotonic_restriction(protocols_two)

    print("\n[EXP1] Two-protocol composition (ATP + ASP)")
    print(f"  Property  : {result_two.property_name}")
    print(f"  Verdict   : {'HOLDS' if result_two.holds else 'VIOLATED'}")
    print(f"  States    : {result_two.states_checked}")
    if not result_two.holds:
        print(f"  UNEXPECTED VIOLATION — counterexample: {result_two.counterexample}")

    # -- Three-protocol composition --
    atp2 = build_atp()
    asp2 = build_asp()
    aeap = build_aeap()
    protocols_three = [atp2, asp2, aeap]
    result_three = verifier.verify_monotonic_restriction(protocols_three)

    print("\n[EXP1] Three-protocol composition (ATP + ASP + AEAP)")
    print(f"  Property  : {result_three.property_name}")
    print(f"  Verdict   : {'HOLDS' if result_three.holds else 'VIOLATED'}")
    print(f"  States    : {result_three.states_checked}")
    if not result_three.holds:
        print(f"  UNEXPECTED VIOLATION — counterexample: {result_three.counterexample}")

    # -- Permission reduction summary --
    single_protocols = [build_atp(), build_asp(), build_aeap()]
    permitted_counts = {
        p.name: _count_permitted_transitions(p) for p in single_protocols
    }
    most_permissive_name = max(permitted_counts, key=lambda k: permitted_counts[k])
    most_permissive_count = permitted_counts[most_permissive_name]

    initial_permitted_two = _count_permitted_actions_in_initial_state(
        [build_atp(), build_asp()]
    )
    initial_permitted_three = _count_permitted_actions_in_initial_state(
        [build_atp(), build_asp(), build_aeap()]
    )

    print("\n[EXP1] Permission reduction summary:")
    print(f"  Most permissive single protocol : {most_permissive_name}"
          f"  ({most_permissive_count} / {sum(len(p.transitions) for p in single_protocols)} "
          f"permitted transitions across all protocols)")
    print(f"  Two-protocol composition permits: "
          f"{initial_permitted_two} actions in initial joint state")
    print(f"  Three-protocol composition      : "
          f"{initial_permitted_three} actions in initial joint state")
    print()

    return {
        "two_protocol": result_two,
        "three_protocol": result_three,
        "initial_permitted_two": initial_permitted_two,
        "initial_permitted_three": initial_permitted_three,
        "most_permissive_name": most_permissive_name,
        "most_permissive_count": most_permissive_count,
    }


if __name__ == "__main__":
    run()
