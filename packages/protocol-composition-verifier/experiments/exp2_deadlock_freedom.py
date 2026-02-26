# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Experiment 2 — Deadlock Freedom
================================

RESEARCH TOOL — not production orchestration.
Companion to Papers 9/25, Section 4.2.

Hypothesis
----------
Well-formed protocol compositions must guarantee that no reachable joint
state exists in which every action in the union alphabet is denied. A
composition that allows such a state is unsafe — the system has reached
a configuration from which no progress is possible.

This experiment demonstrates:
  (a) That the standard [ATP, ASP, AEAP] composition is deadlock-free.
  (b) That introducing a deliberately broken, sink-state protocol causes
      the deadlock-freedom check to correctly identify a violation.

Method
------
1. Verify deadlock freedom for [ATP, ASP, AEAP].
2. Construct a broken protocol (BROKEN) whose single state denies all
   actions.
3. Compose [ATP, BROKEN] and verify deadlock freedom.
4. Confirm that the verifier reports ``holds=False`` and provides a
   counterexample.

Expected output
---------------
    [EXP2] Standard composition (ATP + ASP + AEAP)
      Property  : deadlock_freedom
      Verdict   : HOLDS
      States    : 27

    [EXP2] Broken composition (ATP + BROKEN)
      Property  : deadlock_freedom
      Verdict   : VIOLATED
      States    : 1
      Path      : (initial state)
      Joint     : {'ATP': 'low', 'BROKEN': 'sink'}
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from composition_verifier.scenarios import (
    build_aeap,
    build_asp,
    build_atp,
    build_broken_deadlock_protocol,
)
from composition_verifier.verifier import ProtocolCompositionVerifier


def run() -> dict[str, object]:
    """Execute Experiment 2 and return a results dictionary.

    RESEARCH TOOL — not production orchestration.

    Returns:
        Dict with keys:
            - ``standard``: :class:`VerificationResult` for [ATP, ASP, AEAP]
            - ``broken``: :class:`VerificationResult` for [ATP, BROKEN]
    """
    verifier = ProtocolCompositionVerifier(max_states=10_000)

    # -- Standard (well-formed) composition --
    protocols_standard = [build_atp(), build_asp(), build_aeap()]
    result_standard = verifier.verify_deadlock_freedom(protocols_standard)

    print("\n[EXP2] Standard composition (ATP + ASP + AEAP)")
    print(f"  Property  : {result_standard.property_name}")
    print(f"  Verdict   : {'HOLDS' if result_standard.holds else 'VIOLATED'}")
    print(f"  States    : {result_standard.states_checked}")
    if not result_standard.holds:
        print(f"  UNEXPECTED VIOLATION — counterexample: {result_standard.counterexample}")

    # -- Broken (deliberately deadlock-inducing) composition --
    protocols_broken = [build_atp(), build_broken_deadlock_protocol()]
    result_broken = verifier.verify_deadlock_freedom(protocols_broken)

    print("\n[EXP2] Broken composition (ATP + BROKEN)")
    print(f"  Property  : {result_broken.property_name}")
    print(f"  Verdict   : {'HOLDS' if result_broken.holds else 'VIOLATED'}")
    print(f"  States    : {result_broken.states_checked}")

    if result_broken.counterexample is not None:
        path_str = (
            " → ".join(result_broken.counterexample.actions)
            if result_broken.counterexample.actions
            else "(initial state)"
        )
        print(f"  Path      : {path_str}")
        print(f"  Joint     : {result_broken.counterexample.states}")
    else:
        print("  UNEXPECTED: expected a violation but none found.")
    print()

    return {
        "standard": result_standard,
        "broken": result_broken,
    }


if __name__ == "__main__":
    run()
