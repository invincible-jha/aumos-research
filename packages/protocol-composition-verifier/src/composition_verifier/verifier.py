# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Bounded model checker for protocol composition formal properties.

RESEARCH TOOL — not production orchestration.
Implements the three formal properties from Papers 9/25 using BFS-based
bounded model checking over the product state machine. All state spaces
are synthetic and deliberately small (3–5 states per protocol).

The verifier provides no completeness guarantees beyond the checked bound.
It is not a theorem prover, SMT solver, or certified verifier.
"""

from __future__ import annotations

import logging
from itertools import product as cartesian_product

from composition_verifier.composer import ProtocolComposer
from composition_verifier.model import (
    ComposedState,
    ProtocolModel,
    VerificationResult,
)

logger = logging.getLogger(__name__)


class VerifierError(Exception):
    """Raised when the verifier receives invalid inputs.

    RESEARCH TOOL — not production orchestration.
    """


class ProtocolCompositionVerifier:
    """Verify formal properties of composed governance protocol state machines.

    RESEARCH TOOL — not production orchestration.

    The verifier operates by enumerating the Cartesian product of per-protocol
    state sets (or the BFS-reachable subset thereof) and checking each composed
    state against the specified property. All state spaces are intentionally
    small and synthetic.

    Three properties are supported:

    - **Monotonic restriction** — composing protocols never expands the
      permission set of any single protocol (Section 4.1 of Papers 9/25).
    - **Deadlock freedom** — no reachable composed state exists in which every
      action in the union alphabet is blocked (Section 4.2).
    - **Priority ordering** — a total order over protocols such that a
      higher-priority protocol's deny cannot be overridden by a
      lower-priority protocol's permit (Section 4.3).

    Args:
        max_states: Upper bound on composed states examined per check.
            Default is 10,000.

    Example:
        >>> verifier = ProtocolCompositionVerifier()
        >>> result = verifier.verify_deadlock_freedom([atp, asp])
        >>> result.holds
        True
        >>> result.states_checked
        9
    """

    def __init__(self, max_states: int = 10_000) -> None:
        self.max_states: int = max_states

    # ------------------------------------------------------------------
    # Public verification interface
    # ------------------------------------------------------------------

    def verify_monotonic_restriction(
        self, protocols: list[ProtocolModel]
    ) -> VerificationResult:
        """Check that composing protocols never INCREASES permissions.

        RESEARCH TOOL — not production orchestration.

        Formal statement:
            For every reachable composed state S and every action a in the
            union alphabet, if the composed system permits a in S then every
            individual protocol must also permit a in its component of S.

        Equivalently: the set of globally-permitted actions in any composed
        state is a *subset* of the permitted actions of every component
        protocol. Composition can only restrict, never expand.

        This property characterises the AND-composition semantics and is the
        central claim of Papers 9/25 Section 4.1.

        Args:
            protocols: The list of :class:`ProtocolModel` instances to check.

        Returns:
            A :class:`VerificationResult`. ``holds=True`` if the property is
            satisfied across all explored states. ``holds=False`` if a
            counterexample is found, in which case ``counterexample`` is set.

        Raises:
            VerifierError: If ``protocols`` is empty.
        """
        self._require_nonempty(protocols, "verify_monotonic_restriction")
        composer = ProtocolComposer(protocols)
        all_joint_states = composer.enumerate_all_joint_states()
        union_alphabet = composer._union_action_alphabet()

        states_checked = 0
        for joint_dict in all_joint_states:
            if states_checked >= self.max_states:
                logger.warning(
                    "verify_monotonic_restriction: state bound %d reached; "
                    "result is valid only within checked bound.",
                    self.max_states,
                )
                break
            states_checked += 1

            # Set each protocol to the joint state
            self._set_protocols_to_joint(protocols, joint_dict)

            for action in union_alphabet:
                composed_decision = composer.compose_decisions(action)
                if not composed_decision.globally_permitted:
                    continue

                # Composed permits this action — every individual must also permit it
                for individual_decision in composed_decision.individual_decisions:
                    if not individual_decision.permitted:
                        counterexample = ComposedState(
                            states=dict(joint_dict),
                            actions=[action],
                        )
                        self._reset_all(protocols)
                        return VerificationResult(
                            holds=False,
                            property_name="monotonic_restriction",
                            states_checked=states_checked,
                            counterexample=counterexample,
                            violating_protocol=individual_decision.protocol,
                        )

        self._reset_all(protocols)
        return VerificationResult(
            holds=True,
            property_name="monotonic_restriction",
            states_checked=states_checked,
        )

    def verify_deadlock_freedom(
        self, protocols: list[ProtocolModel]
    ) -> VerificationResult:
        """Check that no reachable composed state blocks ALL actions.

        RESEARCH TOOL — not production orchestration.

        Formal statement:
            For every reachable composed state S, there exists at least one
            action a in the union alphabet such that the composed system
            permits a in S.

        A state where no action is globally permitted is a deadlock — the
        system has reached a configuration from which no progress is possible.
        Papers 9/25 Section 4.2 discusses conditions under which deadlocks
        arise from unsafe protocol composition.

        Note:
            This check operates over *reachable* states (BFS from initial
            state) rather than the full Cartesian product. Unreachable
            deadlock states do not violate this property.

        Args:
            protocols: The list of :class:`ProtocolModel` instances to check.

        Returns:
            A :class:`VerificationResult`. ``holds=True`` if no deadlock is
            found within the bound. ``holds=False`` if a deadlock state is
            reached, with ``counterexample`` showing the path to it.

        Raises:
            VerifierError: If ``protocols`` is empty.
        """
        self._require_nonempty(protocols, "verify_deadlock_freedom")
        composer = ProtocolComposer(protocols)
        reachable_states = composer.enumerate_states(max_states=self.max_states)
        union_alphabet = composer._union_action_alphabet()

        for index, composed_state in enumerate(reachable_states):
            self._set_protocols_to_joint(protocols, composed_state.states)

            any_permitted = any(
                composer.compose_decisions(action).globally_permitted
                for action in union_alphabet
            )

            if not any_permitted:
                self._reset_all(protocols)
                return VerificationResult(
                    holds=False,
                    property_name="deadlock_freedom",
                    states_checked=index + 1,
                    counterexample=composed_state,
                )

        self._reset_all(protocols)
        return VerificationResult(
            holds=True,
            property_name="deadlock_freedom",
            states_checked=len(reachable_states),
        )

    def verify_priority_ordering(
        self,
        protocols: list[ProtocolModel],
        priority: list[str],
    ) -> VerificationResult:
        """Check that higher-priority protocols always override lower ones.

        RESEARCH TOOL — not production orchestration.

        Formal statement:
            For every reachable composed state S, every action a, and every
            pair of protocols P_high (higher priority) and P_low (lower
            priority): if P_high denies a in its component of S, then the
            composed system also denies a in S — regardless of what P_low
            decides.

        Equivalently: a lower-priority protocol's permit cannot rescue an
        action that a higher-priority protocol has explicitly denied.

        This property verifies the *veto semantics* of the priority ordering
        described in Papers 9/25 Section 4.3.

        Args:
            protocols: The list of :class:`ProtocolModel` instances to check.
            priority: Protocol names ordered from highest to lowest priority.
                All protocol names appearing in ``protocols`` should appear in
                ``priority``. Protocols absent from ``priority`` are treated
                as lowest priority.

        Returns:
            A :class:`VerificationResult`. ``holds=True`` if the priority
            ordering is respected in all explored states. ``holds=False`` if
            a violation is found.

        Raises:
            VerifierError: If ``protocols`` is empty or if ``priority``
                contains names not found in ``protocols``.
        """
        self._require_nonempty(protocols, "verify_priority_ordering")
        protocol_map = {p.name: p for p in protocols}
        unknown = [name for name in priority if name not in protocol_map]
        if unknown:
            raise VerifierError(
                f"verify_priority_ordering: priority list contains unknown "
                f"protocol names: {unknown}. Known: {list(protocol_map)}"
            )

        composer = ProtocolComposer(protocols)
        # Enumerate ALL joint states (not just reachable) for a stronger check
        all_joint_states = composer.enumerate_all_joint_states()
        union_alphabet = composer._union_action_alphabet()

        # Build priority rank map: lower index = higher priority
        priority_rank: dict[str, int] = {name: i for i, name in enumerate(priority)}
        # Protocols not in the priority list get the lowest rank
        default_rank = len(priority)

        states_checked = 0
        for joint_dict in all_joint_states:
            if states_checked >= self.max_states:
                logger.warning(
                    "verify_priority_ordering: state bound %d reached; "
                    "result is valid only within checked bound.",
                    self.max_states,
                )
                break
            states_checked += 1

            self._set_protocols_to_joint(protocols, joint_dict)

            for action in union_alphabet:
                composed_decision = composer.compose_decisions(action)

                # Find the highest-priority protocol that denies this action
                denying_decisions = [
                    d for d in composed_decision.individual_decisions if not d.permitted
                ]
                if not denying_decisions:
                    # No protocol denies — composed should permit; nothing to check
                    continue

                # The composed system should deny since at least one protocol denies
                if composed_decision.globally_permitted:
                    # The AND-composition CANNOT permit when any denies, so this
                    # branch indicates a bug in the composer, not a property violation.
                    # We treat it as a priority ordering violation for reporting.
                    highest_denier = min(
                        denying_decisions,
                        key=lambda d: priority_rank.get(d.protocol, default_rank),
                    )
                    counterexample = ComposedState(
                        states=dict(joint_dict),
                        actions=[action],
                    )
                    self._reset_all(protocols)
                    return VerificationResult(
                        holds=False,
                        property_name="priority_ordering",
                        states_checked=states_checked,
                        counterexample=counterexample,
                        violating_protocol=highest_denier.protocol,
                    )

                # Verify that the highest-priority denier is correctly reflected.
                # Under AND semantics this always holds by construction, so we
                # additionally verify that the priority ordering is CONSISTENT:
                # if the highest-priority protocol PERMITS the action, no
                # lower-priority deny should be able to block a future override.
                # (This is the Papers 9/25 consistency check — see Section 4.3.)
                permitting_decisions = [
                    d for d in composed_decision.individual_decisions if d.permitted
                ]
                if permitting_decisions and denying_decisions:
                    highest_permitter_rank = min(
                        priority_rank.get(d.protocol, default_rank)
                        for d in permitting_decisions
                    )
                    highest_denier_rank = min(
                        priority_rank.get(d.protocol, default_rank)
                        for d in denying_decisions
                    )
                    # Violation: a higher-priority protocol permits but a
                    # lower-priority protocol's deny still blocks the action.
                    # Under the veto semantics this is only a violation if the
                    # deny comes from a LOWER-priority protocol than the permit.
                    if highest_denier_rank > highest_permitter_rank:
                        # Lower-priority deny is blocking a higher-priority permit
                        worst_denier = min(
                            denying_decisions,
                            key=lambda d: priority_rank.get(d.protocol, default_rank),
                        )
                        counterexample = ComposedState(
                            states=dict(joint_dict),
                            actions=[action],
                        )
                        self._reset_all(protocols)
                        return VerificationResult(
                            holds=False,
                            property_name="priority_ordering",
                            states_checked=states_checked,
                            counterexample=counterexample,
                            violating_protocol=worst_denier.protocol,
                        )

        self._reset_all(protocols)
        return VerificationResult(
            holds=True,
            property_name="priority_ordering",
            states_checked=states_checked,
        )

    # ------------------------------------------------------------------
    # Convenience: run all three properties in one call
    # ------------------------------------------------------------------

    def verify_all(
        self,
        protocols: list[ProtocolModel],
        priority: list[str] | None = None,
    ) -> dict[str, VerificationResult]:
        """Run all three verification checks and return a summary dict.

        RESEARCH TOOL — not production orchestration.

        Args:
            protocols: The list of :class:`ProtocolModel` instances to check.
            priority: Optional priority ordering for ``verify_priority_ordering``.
                If omitted, priority ordering is checked in declaration order.

        Returns:
            Dict mapping property name to :class:`VerificationResult`.
            Keys: ``"monotonic_restriction"``, ``"deadlock_freedom"``,
            ``"priority_ordering"``.
        """
        if priority is None:
            priority = [p.name for p in protocols]

        return {
            "monotonic_restriction": self.verify_monotonic_restriction(protocols),
            "deadlock_freedom": self.verify_deadlock_freedom(protocols),
            "priority_ordering": self.verify_priority_ordering(protocols, priority),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _require_nonempty(protocols: list[ProtocolModel], method: str) -> None:
        """Raise VerifierError if the protocol list is empty."""
        if not protocols:
            raise VerifierError(
                f"ProtocolCompositionVerifier.{method}: protocols list must not be empty."
            )

    @staticmethod
    def _set_protocols_to_joint(
        protocols: list[ProtocolModel],
        joint_dict: dict[str, str],
    ) -> None:
        """Directly set each protocol's current_state from a joint state dict.

        RESEARCH TOOL — not production orchestration.

        This is an internal helper that bypasses the normal transition
        mechanism to position the verifier at an arbitrary joint state.

        Args:
            protocols: List of :class:`ProtocolModel` instances to update.
            joint_dict: Mapping from protocol name to target state name.
        """
        for protocol in protocols:
            target = joint_dict.get(protocol.name)
            if target is not None and target in protocol.states:
                protocol.current_state = target

    @staticmethod
    def _reset_all(protocols: list[ProtocolModel]) -> None:
        """Reset all protocols to their initial states after verification.

        RESEARCH TOOL — not production orchestration.
        """
        for protocol in protocols:
            protocol.reset()

    def __repr__(self) -> str:
        return f"ProtocolCompositionVerifier(max_states={self.max_states})"
