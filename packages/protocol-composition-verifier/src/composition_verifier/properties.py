# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Formal property definitions for protocol composition verification.

RESEARCH TOOL — not production orchestration.
Defines the three formal properties investigated in Papers 9/25:

    1. Monotonic Restriction — composition never expands permissions
    2. Deadlock Freedom     — no reachable state blocks all actions
    3. Priority Ordering    — higher-priority protocols always override

These are simplified, bounded approximations suitable for research
exploration on small synthetic state machines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class PropertyKind(Enum):
    """The category of formal property being checked.

    RESEARCH TOOL — not production orchestration.

    Members:
        MONOTONIC_RESTRICTION: The composed system never permits an action
            that every component individually would deny.
        DEADLOCK_FREEDOM: No reachable composed state exists in which every
            action in the union alphabet is blocked.
        PRIORITY_ORDERING: A total order over protocols such that a
            higher-priority protocol's deny always overrides a
            lower-priority protocol's permit.
    """

    MONOTONIC_RESTRICTION = auto()
    DEADLOCK_FREEDOM = auto()
    PRIORITY_ORDERING = auto()


@dataclass(frozen=True)
class PropertySpec:
    """A fully specified formal property ready for verification.

    RESEARCH TOOL — not production orchestration.

    Attributes:
        kind: The category of the property.
        name: Human-readable name (used in ``VerificationResult.property_name``).
        description: One-sentence description suitable for reports and figures.
        priority_order: For ``PRIORITY_ORDERING`` properties, an ordered list
            of protocol names from highest to lowest priority. Empty for other
            property kinds.

    Example:
        >>> spec = PropertySpec(
        ...     kind=PropertyKind.DEADLOCK_FREEDOM,
        ...     name="deadlock_freedom",
        ...     description="No reachable state blocks all actions.",
        ... )
    """

    kind: PropertyKind
    name: str
    description: str
    priority_order: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Ensure priority_order is always a plain list (defensive copy).
        # Uses object.__setattr__ because the dataclass is frozen.
        object.__setattr__(self, "priority_order", list(self.priority_order))


# ------------------------------------------------------------------
# Standard property catalogue — used by experiments and the verifier
# ------------------------------------------------------------------

MONOTONIC_RESTRICTION: PropertySpec = PropertySpec(
    kind=PropertyKind.MONOTONIC_RESTRICTION,
    name="monotonic_restriction",
    description=(
        "Composing protocols never increases permissions: the composed "
        "system is at most as permissive as the most restrictive component."
    ),
)

DEADLOCK_FREEDOM: PropertySpec = PropertySpec(
    kind=PropertyKind.DEADLOCK_FREEDOM,
    name="deadlock_freedom",
    description=(
        "No reachable composed state exists in which every action in the "
        "union alphabet is blocked by at least one protocol."
    ),
)


def priority_ordering_spec(priority_order: list[str]) -> PropertySpec:
    """Construct a priority-ordering property for a given protocol ranking.

    RESEARCH TOOL — not production orchestration.

    Args:
        priority_order: Protocol names ordered from highest to lowest
            priority. The first name is the most authoritative.

    Returns:
        A :class:`PropertySpec` with ``kind=PropertyKind.PRIORITY_ORDERING``.

    Example:
        >>> spec = priority_ordering_spec(["ASP", "ATP", "AEAP"])
        >>> spec.priority_order[0]
        'ASP'
    """
    label = " > ".join(priority_order)
    return PropertySpec(
        kind=PropertyKind.PRIORITY_ORDERING,
        name="priority_ordering",
        description=(
            f"Higher-priority protocols always override lower ones. "
            f"Verified order: {label}."
        ),
        priority_order=list(priority_order),
    )


# ------------------------------------------------------------------
# Property violation descriptions — for human-readable reporting
# ------------------------------------------------------------------

def describe_violation(kind: PropertyKind, counterexample_path: list[str]) -> str:
    """Produce a human-readable description of a property violation.

    RESEARCH TOOL — not production orchestration.

    Args:
        kind: The property that was violated.
        counterexample_path: The sequence of actions leading to the
            violating state.

    Returns:
        A string suitable for printing in experiment output.

    Example:
        >>> describe_violation(PropertyKind.DEADLOCK_FREEDOM, ["read", "write"])
        'Deadlock found after actions: read -> write'
    """
    path_str = " -> ".join(counterexample_path) if counterexample_path else "(initial state)"
    match kind:
        case PropertyKind.MONOTONIC_RESTRICTION:
            return (
                f"Monotonic restriction violated: composition expanded permissions "
                f"after actions: {path_str}"
            )
        case PropertyKind.DEADLOCK_FREEDOM:
            return f"Deadlock found after actions: {path_str}"
        case PropertyKind.PRIORITY_ORDERING:
            return (
                f"Priority ordering violated: lower-priority protocol overrode "
                f"higher-priority denial after actions: {path_str}"
            )
        case _:  # pragma: no cover
            return f"Unknown property violated after actions: {path_str}"
