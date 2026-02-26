# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Protocol composition — product state machine construction.

RESEARCH TOOL — not production orchestration.
Composes multiple simplified protocol models into a synchronous product
automaton for use by the bounded model checker in verifier.py.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from composition_verifier.model import (
    ComposedState,
    ProtocolDecision,
    ProtocolModel,
    ProtocolModelError,
)


@dataclass(frozen=True)
class ComposedDecision:
    """The aggregate decision produced by evaluating one action across all protocols.

    RESEARCH TOOL — not production orchestration.

    The composition rule is: an action is globally permitted if and only if
    *every* protocol permits it (logical AND). This implements conservative
    restriction — the composed system is no more permissive than its most
    restrictive component.

    Attributes:
        action: The action that was evaluated.
        globally_permitted: True when all component protocols permit the action.
        individual_decisions: The per-protocol decisions in protocol order.
        blocking_protocols: Names of protocols that denied the action. Empty
            when ``globally_permitted`` is True.

    Example:
        >>> d = ComposedDecision(
        ...     action="read",
        ...     globally_permitted=True,
        ...     individual_decisions=[...],
        ...     blocking_protocols=[],
        ... )
        >>> d.globally_permitted
        True
    """

    action: str
    globally_permitted: bool
    individual_decisions: list[ProtocolDecision]
    blocking_protocols: list[str] = field(default_factory=list)


class ComposerError(Exception):
    """Raised when the ProtocolComposer is used incorrectly.

    RESEARCH TOOL — not production orchestration.
    """


class ProtocolComposer:
    """Compose multiple protocol models into a product state machine.

    RESEARCH TOOL — not production orchestration.

    The product state machine is constructed lazily via BFS during
    ``enumerate_states``. The composition semantics are synchronous:
    all protocols observe every action simultaneously, and the action
    is globally permitted only when every protocol permits it.

    This implements the *monotonic restriction* semantics described in
    Papers 9/25 — the composed system can only restrict, never expand,
    the permission set of any individual protocol.

    Args:
        protocols: The list of :class:`ProtocolModel` instances to compose.
            Must contain at least one protocol.

    Raises:
        ComposerError: If ``protocols`` is empty.

    Example:
        >>> composer = ProtocolComposer([atp_model, asp_model])
        >>> decision = composer.compose_decisions("read")
        >>> decision.globally_permitted
        True
        >>> states = composer.enumerate_states()
        >>> len(states)
        9
    """

    def __init__(self, protocols: list[ProtocolModel]) -> None:
        if not protocols:
            raise ComposerError("ProtocolComposer requires at least one protocol.")
        self.protocols: list[ProtocolModel] = list(protocols)

    # ------------------------------------------------------------------
    # Decision evaluation
    # ------------------------------------------------------------------

    def compose_decisions(self, action: str) -> ComposedDecision:
        """Evaluate ``action`` across all protocols. Result is AND of all decisions.

        RESEARCH TOOL — not production orchestration.

        Each protocol's ``decide`` method is called with the action. The
        action is globally permitted only when *every* protocol returns
        ``permitted=True``.

        Note:
            This method does not advance any protocol's state. It is a pure
            read-only evaluation of the current joint state.

        Args:
            action: The action label to evaluate.

        Returns:
            A :class:`ComposedDecision` summarising all per-protocol outcomes.

        Example:
            >>> composer.compose_decisions("delete").globally_permitted
            False
        """
        decisions: list[ProtocolDecision] = [
            protocol.decide(action) for protocol in self.protocols
        ]
        blocking: list[str] = [
            d.protocol for d in decisions if not d.permitted
        ]
        return ComposedDecision(
            action=action,
            globally_permitted=len(blocking) == 0,
            individual_decisions=decisions,
            blocking_protocols=blocking,
        )

    def apply_composed_action(self, action: str) -> ComposedDecision:
        """Evaluate ``action`` and advance all protocols if globally permitted.

        RESEARCH TOOL — not production orchestration.

        If and only if all protocols permit the action, each protocol's state
        is advanced. If any protocol blocks, no state changes occur.

        Args:
            action: The action label to apply.

        Returns:
            A :class:`ComposedDecision` describing the outcome.
        """
        decision = self.compose_decisions(action)
        if decision.globally_permitted:
            for protocol in self.protocols:
                protocol.apply_transition(action)
        return decision

    # ------------------------------------------------------------------
    # State space enumeration
    # ------------------------------------------------------------------

    def current_composed_state(self, action_history: list[str] | None = None) -> ComposedState:
        """Snapshot the current joint state of all protocols.

        RESEARCH TOOL — not production orchestration.

        Args:
            action_history: Optional list of actions taken to reach this
                joint state (for traceability in counterexamples).

        Returns:
            A :class:`ComposedState` reflecting ``protocol.current_state``
            for each protocol.
        """
        return ComposedState(
            states={protocol.name: protocol.current_state for protocol in self.protocols},
            actions=list(action_history) if action_history else [],
        )

    def reset_all(self) -> None:
        """Reset all protocols to their initial states.

        RESEARCH TOOL — not production orchestration.
        """
        for protocol in self.protocols:
            protocol.reset()

    def enumerate_states(self, max_states: int = 10_000) -> list[ComposedState]:
        """Enumerate reachable composed states via bounded BFS.

        RESEARCH TOOL — not production orchestration.

        Performs a breadth-first traversal of the product state machine,
        starting from the joint initial state. Traversal stops when the
        number of discovered states reaches ``max_states``.

        The action alphabet used during enumeration is the union of all
        actions defined across all component protocols.

        Args:
            max_states: Upper bound on the number of composed states to
                explore. Default is 10,000. Larger values increase runtime
                but improve coverage for protocols with larger state spaces.

        Returns:
            A list of :class:`ComposedState` objects, one per reachable
            joint state. The first element is always the initial state.

        Note:
            States that are unreachable under the AND-composition semantics
            (because every path to them is blocked) will not appear in the
            returned list.

        Example:
            >>> states = composer.enumerate_states(max_states=500)
            >>> len(states) <= 500
            True
        """
        all_actions = self._union_action_alphabet()
        initial_joint = tuple(
            protocol.initial_state for protocol in self.protocols
        )

        visited: set[tuple[str, ...]] = {initial_joint}
        result: list[ComposedState] = [
            ComposedState(
                states={p.name: p.initial_state for p in self.protocols},
                actions=[],
            )
        ]
        queue: deque[tuple[tuple[str, ...], list[str]]] = deque(
            [(initial_joint, [])]
        )

        while queue and len(result) < max_states:
            current_joint, path = queue.popleft()
            self._set_joint_state(current_joint)

            for action in all_actions:
                composed_decision = self.compose_decisions(action)
                if not composed_decision.globally_permitted:
                    continue

                next_joint = tuple(d.next_state for d in composed_decision.individual_decisions)
                if next_joint in visited:
                    continue

                visited.add(next_joint)
                next_path = path + [action]
                result.append(
                    ComposedState(
                        states={
                            self.protocols[i].name: next_joint[i]
                            for i in range(len(self.protocols))
                        },
                        actions=next_path,
                    )
                )
                queue.append((next_joint, next_path))

                if len(result) >= max_states:
                    break

        self.reset_all()
        return result

    def enumerate_all_joint_states(self) -> list[dict[str, str]]:
        """Return the Cartesian product of all per-protocol state sets.

        RESEARCH TOOL — not production orchestration.

        Unlike ``enumerate_states``, this returns *all* combinations of
        states regardless of reachability. Used by the verifier to check
        properties across the full product space.

        Returns:
            List of dicts mapping protocol name to state name for every
            element of the Cartesian product.
        """
        from itertools import product as cartesian_product

        state_lists = [
            [(protocol.name, state_name) for state_name in protocol.states]
            for protocol in self.protocols
        ]
        return [dict(combo) for combo in cartesian_product(*state_lists)]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _union_action_alphabet(self) -> list[str]:
        """Return sorted union of all action labels across all protocols.

        RESEARCH TOOL — not production orchestration.
        """
        return sorted({action for p in self.protocols for action in p.all_actions()})

    def _set_joint_state(self, joint: tuple[str, ...]) -> None:
        """Directly set each protocol's current_state without validation.

        RESEARCH TOOL — not production orchestration.

        This is an internal helper used during BFS enumeration. It bypasses
        the normal transition mechanism to navigate the state space directly.

        Args:
            joint: Tuple of state names in protocol order.

        Raises:
            ProtocolModelError: If any state name is invalid for its protocol.
        """
        for protocol, state_name in zip(self.protocols, joint):
            if state_name not in protocol.states:
                raise ProtocolModelError(
                    f"Protocol '{protocol.name}' has no state '{state_name}'."
                )
            protocol.current_state = state_name

    @property
    def protocol_names(self) -> list[str]:
        """Return the names of all composed protocols in order.

        RESEARCH TOOL — not production orchestration.
        """
        return [p.name for p in self.protocols]

    def __repr__(self) -> str:
        names = [p.name for p in self.protocols]
        return f"ProtocolComposer(protocols={names})"
