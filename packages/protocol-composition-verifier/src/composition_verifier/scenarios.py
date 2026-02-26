# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Predefined synthetic protocol models for Papers 9/25 experiments.

RESEARCH TOOL — not production orchestration.
All state machines here are intentionally simplified (3–5 states, 4–5
actions) and entirely synthetic. They are designed to illustrate the
formal properties in Papers 9/25, not to represent any real system.

Defined scenarios
-----------------
- ``build_atp()``  — Adaptive Trust Protocol (3 states)
- ``build_asp()``  — Adaptive Security Protocol (3 states)
- ``build_aeap()`` — Adaptive Efficiency / Allocation Protocol (3 states)
- ``build_broken_deadlock_protocol()`` — intentionally deadlock-inducing model
- ``standard_composition()`` — convenience function returning [ATP, ASP, AEAP]
"""

from __future__ import annotations

from composition_verifier.model import (
    ProtocolModel,
    State,
    Transition,
)

# ---------------------------------------------------------------------------
# Action alphabet used across all scenarios
# ---------------------------------------------------------------------------
# Keeping the alphabet consistent across protocols ensures the union alphabet
# is well-defined and that cross-protocol composition checks are meaningful.

ACTION_READ = "read"
ACTION_WRITE = "write"
ACTION_EXECUTE = "execute"
ACTION_DELETE = "delete"
ACTION_ESCALATE = "escalate"

ALL_ACTIONS: list[str] = [
    ACTION_READ,
    ACTION_WRITE,
    ACTION_EXECUTE,
    ACTION_DELETE,
    ACTION_ESCALATE,
]


# ---------------------------------------------------------------------------
# ATP — Adaptive Trust Protocol
# ---------------------------------------------------------------------------

def build_atp() -> ProtocolModel:
    """Build the Adaptive Trust Protocol (ATP) state machine.

    RESEARCH TOOL — not production orchestration.

    The ATP models a simplified trust tier for an agent interaction. It has
    three states representing increasing levels of established trust:

    - ``low``    — minimal trust; only ``read`` is permitted
    - ``medium`` — partial trust; ``read`` and ``write`` are permitted
    - ``high``   — full trust; all non-destructive actions permitted

    The protocol advances from low to medium on ``write`` (demonstrating
    benign intent) and from medium to high on ``execute``. Trust degrades
    via ``escalate`` (treated as a potentially risky action that resets
    trust to ``low``).

    State diagram::

        low  --[write, permitted]--> medium
        low  --[read,  permitted]--> low
        low  --[execute, denied]--> low
        low  --[delete,  denied]--> low
        low  --[escalate, denied]--> low
        medium --[read,    permitted]--> medium
        medium --[write,   permitted]--> medium
        medium --[execute, permitted]--> high
        medium --[delete,  denied]---> medium
        medium --[escalate,denied]---> low
        high --[read,    permitted]--> high
        high --[write,   permitted]--> high
        high --[execute, permitted]--> high
        high --[delete,  permitted]--> high
        high --[escalate,denied]---> low

    Returns:
        A :class:`ProtocolModel` named ``"ATP"`` with initial state ``"low"``.

    Example:
        >>> atp = build_atp()
        >>> atp.decide("read").permitted
        True
        >>> atp.decide("delete").permitted
        False
    """
    states = [
        State(name="low",    is_accepting=True, metadata={"tier": 1, "label": "Low Trust"}),
        State(name="medium", is_accepting=True, metadata={"tier": 2, "label": "Medium Trust"}),
        State(name="high",   is_accepting=True, metadata={"tier": 3, "label": "High Trust"}),
    ]

    transitions: list[Transition] = [
        # --- from low ---
        Transition("low", "low",    ACTION_READ,    permitted=True),
        Transition("low", "medium", ACTION_WRITE,   permitted=True,
                   guard="first_benign_write_observed"),
        Transition("low", "low",    ACTION_EXECUTE, permitted=False),
        Transition("low", "low",    ACTION_DELETE,  permitted=False),
        Transition("low", "low",    ACTION_ESCALATE, permitted=False),
        # --- from medium ---
        Transition("medium", "medium", ACTION_READ,     permitted=True),
        Transition("medium", "medium", ACTION_WRITE,    permitted=True),
        Transition("medium", "high",   ACTION_EXECUTE,  permitted=True,
                   guard="two_or_more_successful_interactions"),
        Transition("medium", "medium", ACTION_DELETE,   permitted=False),
        Transition("medium", "low",    ACTION_ESCALATE, permitted=False),
        # --- from high ---
        Transition("high", "high", ACTION_READ,    permitted=True),
        Transition("high", "high", ACTION_WRITE,   permitted=True),
        Transition("high", "high", ACTION_EXECUTE, permitted=True),
        Transition("high", "high", ACTION_DELETE,  permitted=True),
        Transition("high", "low",  ACTION_ESCALATE, permitted=False),
    ]

    return ProtocolModel(
        name="ATP",
        states=states,
        transitions=transitions,
        initial_state="low",
    )


# ---------------------------------------------------------------------------
# ASP — Adaptive Security Protocol
# ---------------------------------------------------------------------------

def build_asp() -> ProtocolModel:
    """Build the Adaptive Security Protocol (ASP) state machine.

    RESEARCH TOOL — not production orchestration.

    The ASP models a simplified security posture. It has three states:

    - ``normal``   — default operation; read/write/execute permitted
    - ``elevated`` — heightened scrutiny; only read permitted
    - ``lockdown`` — full restriction; no actions permitted

    The protocol escalates on ``execute`` (triggers elevated review),
    escalates further to ``lockdown`` on ``delete``, and resets on
    ``read`` once elevated.

    State diagram::

        normal --[read,    permitted]--> normal
        normal --[write,   permitted]--> normal
        normal --[execute, permitted]--> elevated
        normal --[delete,  denied]---> lockdown
        normal --[escalate,denied]---> elevated
        elevated --[read,    permitted]--> normal
        elevated --[write,   denied]---> elevated
        elevated --[execute, denied]---> lockdown
        elevated --[delete,  denied]---> lockdown
        elevated --[escalate,denied]---> lockdown
        lockdown --[read,    denied]--> lockdown
        lockdown --[write,   denied]--> lockdown
        lockdown --[execute, denied]--> lockdown
        lockdown --[delete,  denied]--> lockdown
        lockdown --[escalate,denied]--> lockdown

    Returns:
        A :class:`ProtocolModel` named ``"ASP"`` with initial state ``"normal"``.

    Example:
        >>> asp = build_asp()
        >>> asp.decide("execute").permitted
        True
        >>> asp.decide("delete").permitted
        False
    """
    states = [
        State(name="normal",   is_accepting=True,  metadata={"risk": "low",  "label": "Normal"}),
        State(name="elevated", is_accepting=True,  metadata={"risk": "med",  "label": "Elevated"}),
        State(name="lockdown", is_accepting=False, metadata={"risk": "high", "label": "Lockdown"}),
    ]

    transitions: list[Transition] = [
        # --- from normal ---
        Transition("normal", "normal",   ACTION_READ,     permitted=True),
        Transition("normal", "normal",   ACTION_WRITE,    permitted=True),
        Transition("normal", "elevated", ACTION_EXECUTE,  permitted=True,
                   guard="execute_triggers_review"),
        Transition("normal", "lockdown", ACTION_DELETE,   permitted=False),
        Transition("normal", "elevated", ACTION_ESCALATE, permitted=False),
        # --- from elevated ---
        Transition("elevated", "normal",   ACTION_READ,     permitted=True,
                   guard="read_clears_elevated_state"),
        Transition("elevated", "elevated", ACTION_WRITE,    permitted=False),
        Transition("elevated", "lockdown", ACTION_EXECUTE,  permitted=False),
        Transition("elevated", "lockdown", ACTION_DELETE,   permitted=False),
        Transition("elevated", "lockdown", ACTION_ESCALATE, permitted=False),
        # --- from lockdown ---
        Transition("lockdown", "lockdown", ACTION_READ,     permitted=False),
        Transition("lockdown", "lockdown", ACTION_WRITE,    permitted=False),
        Transition("lockdown", "lockdown", ACTION_EXECUTE,  permitted=False),
        Transition("lockdown", "lockdown", ACTION_DELETE,   permitted=False),
        Transition("lockdown", "lockdown", ACTION_ESCALATE, permitted=False),
    ]

    return ProtocolModel(
        name="ASP",
        states=states,
        transitions=transitions,
        initial_state="normal",
    )


# ---------------------------------------------------------------------------
# AEAP — Adaptive Efficiency / Allocation Protocol
# ---------------------------------------------------------------------------

def build_aeap() -> ProtocolModel:
    """Build the Adaptive Efficiency and Allocation Protocol (AEAP) state machine.

    RESEARCH TOOL — not production orchestration.

    The AEAP models a simplified resource budget / allocation governor. It
    has three states:

    - ``available`` — budget available; most actions permitted
    - ``warning``   — budget near limit; only read and execute permitted
    - ``exhausted`` — budget depleted; only read permitted

    State diagram::

        available --[read,    permitted]--> available
        available --[write,   permitted]--> warning
        available --[execute, permitted]--> available
        available --[delete,  permitted]--> warning
        available --[escalate,denied]---> available
        warning --[read,    permitted]--> warning
        warning --[write,   denied]---> exhausted
        warning --[execute, permitted]--> warning
        warning --[delete,  denied]---> exhausted
        warning --[escalate,denied]---> available
        exhausted --[read,    permitted]--> exhausted
        exhausted --[write,   denied]---> exhausted
        exhausted --[execute, denied]---> exhausted
        exhausted --[delete,  denied]---> exhausted
        exhausted --[escalate,denied]---> available

    Returns:
        A :class:`ProtocolModel` named ``"AEAP"`` with initial state ``"available"``.

    Example:
        >>> aeap = build_aeap()
        >>> aeap.decide("write").permitted
        True
        >>> aeap.apply_transition("write")  # moves to "warning"
        >>> aeap.decide("write").permitted
        False
    """
    states = [
        State(name="available", is_accepting=True,
              metadata={"budget": "full",    "label": "Budget Available"}),
        State(name="warning",   is_accepting=True,
              metadata={"budget": "partial", "label": "Budget Warning"}),
        State(name="exhausted", is_accepting=True,
              metadata={"budget": "none",    "label": "Budget Exhausted"}),
    ]

    transitions: list[Transition] = [
        # --- from available ---
        Transition("available", "available", ACTION_READ,     permitted=True),
        Transition("available", "warning",   ACTION_WRITE,    permitted=True,
                   guard="write_consumes_budget"),
        Transition("available", "available", ACTION_EXECUTE,  permitted=True),
        Transition("available", "warning",   ACTION_DELETE,   permitted=True,
                   guard="delete_consumes_budget"),
        Transition("available", "available", ACTION_ESCALATE, permitted=False),
        # --- from warning ---
        Transition("warning", "warning",   ACTION_READ,     permitted=True),
        Transition("warning", "exhausted", ACTION_WRITE,    permitted=False),
        Transition("warning", "warning",   ACTION_EXECUTE,  permitted=True),
        Transition("warning", "exhausted", ACTION_DELETE,   permitted=False),
        Transition("warning", "available", ACTION_ESCALATE, permitted=False),
        # --- from exhausted ---
        Transition("exhausted", "exhausted", ACTION_READ,     permitted=True),
        Transition("exhausted", "exhausted", ACTION_WRITE,    permitted=False),
        Transition("exhausted", "exhausted", ACTION_EXECUTE,  permitted=False),
        Transition("exhausted", "exhausted", ACTION_DELETE,   permitted=False),
        Transition("exhausted", "available", ACTION_ESCALATE, permitted=False),
    ]

    return ProtocolModel(
        name="AEAP",
        states=states,
        transitions=transitions,
        initial_state="available",
    )


# ---------------------------------------------------------------------------
# Broken protocol — intentionally deadlock-inducing (for exp2)
# ---------------------------------------------------------------------------

def build_broken_deadlock_protocol() -> ProtocolModel:
    """Build an intentionally broken protocol that causes deadlock.

    RESEARCH TOOL — not production orchestration.

    This model is used in Experiment 2 to demonstrate that the deadlock
    freedom check correctly identifies a violating composition.

    The protocol has one state (``sink``) from which no action is permitted.
    When composed with other protocols, any joint state that includes ``sink``
    is a deadlock under AND-composition semantics because this protocol will
    deny every action.

    Note:
        This model is deliberately pathological. It is not intended to
        represent any real protocol.

    Returns:
        A :class:`ProtocolModel` named ``"BROKEN"`` with initial state ``"sink"``.

    Example:
        >>> broken = build_broken_deadlock_protocol()
        >>> broken.decide("read").permitted
        False
        >>> broken.decide("write").permitted
        False
    """
    states = [
        State(name="sink", is_accepting=False, metadata={"label": "Deadlock Sink"}),
    ]

    # All actions explicitly denied from the single state
    transitions: list[Transition] = [
        Transition("sink", "sink", ACTION_READ,     permitted=False),
        Transition("sink", "sink", ACTION_WRITE,    permitted=False),
        Transition("sink", "sink", ACTION_EXECUTE,  permitted=False),
        Transition("sink", "sink", ACTION_DELETE,   permitted=False),
        Transition("sink", "sink", ACTION_ESCALATE, permitted=False),
    ]

    return ProtocolModel(
        name="BROKEN",
        states=states,
        transitions=transitions,
        initial_state="sink",
    )


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

def standard_composition() -> list[ProtocolModel]:
    """Return the three standard protocols as a fresh list.

    RESEARCH TOOL — not production orchestration.

    Returns a new list ``[ATP, ASP, AEAP]`` constructed via the builder
    functions above. Each call returns independent model instances.

    Returns:
        List containing one instance each of ATP, ASP, and AEAP in that order.

    Example:
        >>> protocols = standard_composition()
        >>> [p.name for p in protocols]
        ['ATP', 'ASP', 'AEAP']
    """
    return [build_atp(), build_asp(), build_aeap()]
