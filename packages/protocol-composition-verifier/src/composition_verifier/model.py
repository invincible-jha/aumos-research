# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Protocol state machine model.

RESEARCH TOOL — not production orchestration.
All state machines here are simplified synthetic constructs for
Papers 9/25. Production governance protocols have substantially
richer state spaces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator


@dataclass(frozen=True)
class State:
    """A single state in a protocol state machine.

    RESEARCH TOOL — not production orchestration.

    Attributes:
        name: Unique identifier for this state within its protocol.
        is_accepting: Whether this state is considered a valid terminal state.
            A state that is not accepting indicates an error or blocked condition.
        metadata: Arbitrary key-value annotations for visualization or analysis.

    Example:
        >>> s = State(name="low_trust", is_accepting=True, metadata={"risk": "low"})
        >>> s.name
        'low_trust'
    """

    name: str
    is_accepting: bool = True
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Transition:
    """A directed edge between two states triggered by an action.

    RESEARCH TOOL — not production orchestration.

    Attributes:
        from_state: The name of the originating state.
        to_state: The name of the destination state.
        action: The action label that triggers this transition.
        permitted: Whether the protocol permits this action in ``from_state``.
            A transition with ``permitted=False`` records that the action is
            explicitly denied (not merely absent).
        guard: Optional string description of an additional guard condition.
            This is descriptive only — the simplified verifier does not
            evaluate guard expressions.

    Example:
        >>> t = Transition(from_state="low", to_state="medium", action="read",
        ...                permitted=True)
        >>> t.permitted
        True
    """

    from_state: str
    to_state: str
    action: str
    permitted: bool
    guard: str | None = None


@dataclass(frozen=True)
class ProtocolDecision:
    """The outcome of evaluating one action against one protocol.

    RESEARCH TOOL — not production orchestration.

    Attributes:
        permitted: Whether the protocol allows the action in the current state.
        next_state: The state the protocol would move to if the action proceeds.
            Equals the current state when the action is blocked.
        protocol: The name of the protocol that produced this decision.
        reason: Human-readable explanation when the action is denied.
            Empty string means the action was explicitly permitted by a transition.

    Example:
        >>> d = ProtocolDecision(permitted=True, next_state="medium",
        ...                      protocol="ATP")
        >>> d.permitted
        True
    """

    permitted: bool
    next_state: str
    protocol: str
    reason: str = ""


@dataclass(frozen=True)
class ComposedState:
    """A snapshot of the joint state across all composed protocols.

    RESEARCH TOOL — not production orchestration.

    Attributes:
        states: Mapping from protocol name to current state name.
        actions: The sequence of actions taken to reach this composed state
            from the initial composed state.

    Example:
        >>> cs = ComposedState(
        ...     states={"ATP": "medium", "ASP": "normal"},
        ...     actions=["read"],
        ... )
        >>> cs.states["ATP"]
        'medium'
    """

    states: dict[str, str]
    actions: list[str]


@dataclass(frozen=True)
class VerificationResult:
    """Outcome of verifying a formal property on a composed protocol.

    RESEARCH TOOL — not production orchestration.

    Attributes:
        holds: True if the property was verified to hold within the checked
            bounded state space. False if a counterexample was found.
        property_name: The name of the verified property (e.g.,
            "monotonic_restriction", "deadlock_freedom", "priority_ordering").
        states_checked: Number of composed states examined during verification.
        counterexample: The composed state that violated the property, or
            None if the property holds.
        violating_protocol: The name of the specific protocol implicated in a
            violation, or None when the property holds or is not protocol-specific.

    Example:
        >>> result = VerificationResult(
        ...     holds=True,
        ...     property_name="deadlock_freedom",
        ...     states_checked=27,
        ... )
        >>> result.holds
        True
    """

    holds: bool
    property_name: str
    states_checked: int
    counterexample: ComposedState | None = None
    violating_protocol: str | None = None


class ProtocolModelError(Exception):
    """Raised when a ProtocolModel is in an invalid or inconsistent state.

    RESEARCH TOOL — not production orchestration.
    """


class ProtocolModel:
    """A simplified governance protocol modeled as a finite state machine.

    RESEARCH TOOL — not production orchestration.

    Each protocol has a small, fixed set of states (typically 3–5) and a set
    of labeled transitions. The ``decide`` method evaluates whether a given
    action is permitted in the current state and determines the next state.

    The composition of multiple ProtocolModels is handled by
    ``ProtocolComposer`` in ``composer.py``.

    NOTE:
        State spaces here are intentionally minimal — 3 to 5 states per
        protocol — to keep the product state space tractable for bounded
        model checking. Production governance protocols have substantially
        richer state representations.

    Args:
        name: A short identifier for this protocol (e.g., "ATP", "ASP").
        states: All states that belong to this protocol.
        transitions: All transitions that define the protocol's behavior.
        initial_state: The name of the state the protocol starts in.

    Raises:
        ProtocolModelError: If ``initial_state`` is not among ``states``, or
            if any transition references an undeclared state name.

    Example:
        >>> from composition_verifier.model import State, Transition, ProtocolModel
        >>> states = [State("low"), State("high")]
        >>> transitions = [
        ...     Transition("low", "high", "elevate", permitted=True),
        ...     Transition("low", "low",  "read",    permitted=True),
        ...     Transition("high", "high", "read",   permitted=True),
        ... ]
        >>> model = ProtocolModel("demo", states, transitions, "low")
        >>> model.decide("read").permitted
        True
        >>> model.decide("delete").permitted
        False
    """

    def __init__(
        self,
        name: str,
        states: list[State],
        transitions: list[Transition],
        initial_state: str,
    ) -> None:
        self.name: str = name
        self.states: dict[str, State] = {s.name: s for s in states}
        self.transitions: list[Transition] = list(transitions)
        self.initial_state: str = initial_state
        self.current_state: str = initial_state
        self._validate()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:
        """Assert internal consistency of the model.

        Raises:
            ProtocolModelError: On any structural inconsistency.
        """
        if self.initial_state not in self.states:
            raise ProtocolModelError(
                f"Protocol '{self.name}': initial_state '{self.initial_state}' "
                f"is not a declared state. Declared states: {list(self.states)}"
            )
        for transition in self.transitions:
            if transition.from_state not in self.states:
                raise ProtocolModelError(
                    f"Protocol '{self.name}': transition references undeclared "
                    f"from_state '{transition.from_state}'."
                )
            if transition.to_state not in self.states:
                raise ProtocolModelError(
                    f"Protocol '{self.name}': transition references undeclared "
                    f"to_state '{transition.to_state}'."
                )

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def decide(self, action: str) -> ProtocolDecision:
        """Evaluate whether ``action`` is permitted in the current state.

        RESEARCH TOOL — not production orchestration.

        Scans all transitions originating from ``self.current_state`` and
        returns the first match for ``action``. If no transition matches,
        the action is implicitly denied and the state does not change.

        Note:
            This method is intentionally stateless with respect to state
            changes — it reports what *would* happen but does not advance
            ``current_state``. Call ``apply_transition`` to advance state.

        Args:
            action: The action label to evaluate.

        Returns:
            A :class:`ProtocolDecision` describing whether the action is
            permitted and what the resulting state would be.

        Example:
            >>> decision = model.decide("read")
            >>> decision.permitted
            True
        """
        for transition in self.transitions:
            if transition.from_state == self.current_state and transition.action == action:
                return ProtocolDecision(
                    permitted=transition.permitted,
                    next_state=transition.to_state,
                    protocol=self.name,
                )
        return ProtocolDecision(
            permitted=False,
            next_state=self.current_state,
            protocol=self.name,
            reason="no_matching_transition",
        )

    def apply_transition(self, action: str) -> ProtocolDecision:
        """Evaluate ``action`` and advance ``current_state`` if permitted.

        RESEARCH TOOL — not production orchestration.

        Unlike ``decide``, this method mutates ``current_state`` when the
        action is permitted. If the action is denied, state is unchanged.

        Args:
            action: The action label to apply.

        Returns:
            A :class:`ProtocolDecision` with the outcome.
        """
        decision = self.decide(action)
        if decision.permitted:
            self.current_state = decision.next_state
        return decision

    def reset(self) -> None:
        """Return the protocol to its initial state.

        RESEARCH TOOL — not production orchestration.

        Example:
            >>> model.apply_transition("elevate")
            >>> model.current_state
            'high'
            >>> model.reset()
            >>> model.current_state
            'low'
        """
        self.current_state = self.initial_state

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def actions_from(self, state_name: str) -> list[str]:
        """Return all distinct action labels reachable from ``state_name``.

        RESEARCH TOOL — not production orchestration.

        Args:
            state_name: The state to query.

        Returns:
            Sorted list of unique action labels that have a transition
            originating from ``state_name``.

        Raises:
            ProtocolModelError: If ``state_name`` is not a declared state.
        """
        if state_name not in self.states:
            raise ProtocolModelError(
                f"Protocol '{self.name}': unknown state '{state_name}'."
            )
        return sorted(
            {t.action for t in self.transitions if t.from_state == state_name}
        )

    def all_actions(self) -> list[str]:
        """Return all distinct action labels defined in this protocol.

        RESEARCH TOOL — not production orchestration.

        Returns:
            Sorted list of unique action labels across all transitions.
        """
        return sorted({t.action for t in self.transitions})

    def permitted_actions_from(self, state_name: str) -> list[str]:
        """Return actions explicitly permitted from ``state_name``.

        RESEARCH TOOL — not production orchestration.

        Args:
            state_name: The state to query.

        Returns:
            Sorted list of action labels where ``permitted=True`` and
            ``from_state == state_name``.
        """
        return sorted(
            {
                t.action
                for t in self.transitions
                if t.from_state == state_name and t.permitted
            }
        )

    def state_names(self) -> list[str]:
        """Return all declared state names in insertion order.

        RESEARCH TOOL — not production orchestration.
        """
        return list(self.states.keys())

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"ProtocolModel(name={self.name!r}, "
            f"states={self.state_names()}, "
            f"current_state={self.current_state!r})"
        )

    def __iter__(self) -> Iterator[State]:
        """Iterate over all states in declaration order."""
        return iter(self.states.values())
