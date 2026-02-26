# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
model.py — TrustFilteredPlanner and core dataclasses for trust-filtered planning simulation.

SIMULATION ONLY. This module implements a simplified trust-filtered action space model
for synthetic agent planning. Trust levels are INTEGERS 0–5. Actions with required
trust level above the agent's assigned level are excluded from the search space.

This does NOT contain Paper 12's full planning theory, production cognitive planning
loops, adaptive trust assignment, or stochastic action models. All dynamics are
deterministic. All planning data is SYNTHETIC.

FIRE LINE: Simple forward-search planner ONLY, not production cognitive loop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Core dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Action:
    """A discrete action available in a planning domain.

    SIMULATION ONLY. Actions have a required trust level; agents with a trust
    level below this threshold cannot use this action in planning.

    Trust levels are INTEGERS in [0, 5]. Level 0 means always available;
    level 5 means only the highest-trust agents may plan with this action.

    Attributes:
        action_id: Unique action identifier.
        name: Human-readable action name.
        required_trust: Minimum agent trust level required (integer 0–5).
        cost: Planning cost of this action (integer, used for optimality gap).
        produces: State label this action transitions to.
        requires: State label that must be current state for this action.
    """

    action_id: str
    name: str
    required_trust: int
    cost: int
    produces: str
    requires: str

    def __post_init__(self) -> None:
        if not (0 <= self.required_trust <= 5):
            raise ValueError(
                f"required_trust must be in [0, 5]; got {self.required_trust}"
            )
        if self.cost < 0:
            raise ValueError(f"cost must be >= 0; got {self.cost}")


@dataclass(frozen=True)
class PlanningGoal:
    """A goal state for the forward-search planner.

    SIMULATION ONLY.

    Attributes:
        goal_id: Unique identifier.
        description: Human-readable goal description.
        target_state: The state label the planner must reach.
        initial_state: The state label the planner starts from.
    """

    goal_id: str
    description: str
    target_state: str
    initial_state: str


@dataclass
class Plan:
    """A sequence of actions forming a plan from initial to target state.

    SIMULATION ONLY. Produced by TrustFilteredPlanner or SimplePlanner.
    Not a production plan record.

    Attributes:
        goal_id: Identifier of the goal this plan addresses.
        actions: Ordered list of Action objects forming the plan.
        total_cost: Sum of action costs along the plan.
        reachable: True when the goal state is reachable with the given trust level.
        trust_level: Trust level used when filtering the action space.
        states_visited: Ordered list of state labels traversed (includes initial).
    """

    goal_id: str
    actions: list[Action]
    total_cost: int
    reachable: bool
    trust_level: int
    states_visited: list[str] = field(default_factory=list)

    @property
    def length(self) -> int:
        """Number of actions in this plan."""
        return len(self.actions)


@dataclass(frozen=True)
class PlanningDomain:
    """A complete planning domain: actions and goals.

    SIMULATION ONLY. Encapsulates the action space and planning goals for a
    synthetic planning scenario.

    Attributes:
        name: Short identifier for the domain.
        description: Human-readable description.
        actions: All actions available in the domain (pre-trust-filtering).
        goals: List of planning goals to solve.
    """

    name: str
    description: str
    actions: list[Action]
    goals: list[PlanningGoal]


# ---------------------------------------------------------------------------
# TrustFilteredPlanner
# ---------------------------------------------------------------------------


class TrustFilteredPlanner:
    """Plan over a trust-filtered action space using forward BFS search.

    SIMULATION ONLY — does not contain production cognitive planning loops,
    Paper 12's full planning theory, adaptive trust assignment, or stochastic
    dynamics. Uses static trust-threshold filtering and deterministic BFS.
    All planning data is SYNTHETIC.

    Trust levels are INTEGERS 0–5. An action is available to an agent when
    action.required_trust <= agent_trust_level. The planner performs BFS
    over the filtered action space to find the shortest path to the goal.

    Example::

        planner = TrustFilteredPlanner(domain, trust_level=3)
        plan = planner.plan(goal)
        print(plan.length, plan.total_cost)
    """

    def __init__(
        self,
        domain: PlanningDomain,
        trust_level: int,
    ) -> None:
        """Initialise the planner with a domain and a static trust level.

        SIMULATION ONLY. Trust level is set externally and never updated
        automatically based on plan outcomes or agent behavior.

        Args:
            domain: The PlanningDomain containing actions and goals.
            trust_level: Integer trust level in [0, 5] for this planner instance.

        Raises:
            ValueError: If trust_level is outside [0, 5].
        """
        if not (0 <= trust_level <= 5):
            raise ValueError(
                f"trust_level must be in [0, 5]; got {trust_level}"
            )
        self.domain = domain
        self.trust_level = trust_level

    def available_actions(self) -> list[Action]:
        """Return the subset of domain actions available at this trust level.

        SIMULATION ONLY. Filters actions where required_trust <= self.trust_level.

        Returns:
            List of Action objects the planner may use. Sorted by required_trust.
        """
        return sorted(
            [a for a in self.domain.actions if a.required_trust <= self.trust_level],
            key=lambda action: action.required_trust,
        )

    def plan(self, goal: PlanningGoal) -> Plan:
        """Find a plan from goal.initial_state to goal.target_state via BFS.

        SIMULATION ONLY. Applies BFS over the trust-filtered action space.
        Returns the shortest plan (fewest actions) when one exists. Returns
        an unreachable Plan when no path exists. All data is SYNTHETIC.

        Args:
            goal: The PlanningGoal defining start and target states.

        Returns:
            Plan with actions, total_cost, and reachability flag.
        """
        actions = self.available_actions()

        # Build forward adjacency: state -> list of (action, next_state)
        adjacency: dict[str, list[tuple[Action, str]]] = {}
        for action in actions:
            if action.requires not in adjacency:
                adjacency[action.requires] = []
            adjacency[action.requires].append((action, action.produces))

        # BFS from initial_state
        from collections import deque

        initial = goal.initial_state
        target = goal.target_state

        if initial == target:
            return Plan(
                goal_id=goal.goal_id,
                actions=[],
                total_cost=0,
                reachable=True,
                trust_level=self.trust_level,
                states_visited=[initial],
            )

        # Each queue entry: (current_state, path_of_actions, states_visited)
        visited: set[str] = {initial}
        queue: deque[tuple[str, list[Action], list[str]]] = deque(
            [(initial, [], [initial])]
        )

        while queue:
            current_state, action_path, states_path = queue.popleft()

            for action, next_state in adjacency.get(current_state, []):
                if next_state == target:
                    final_actions = action_path + [action]
                    final_states = states_path + [next_state]
                    return Plan(
                        goal_id=goal.goal_id,
                        actions=final_actions,
                        total_cost=sum(a.cost for a in final_actions),
                        reachable=True,
                        trust_level=self.trust_level,
                        states_visited=final_states,
                    )
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append(
                        (
                            next_state,
                            action_path + [action],
                            states_path + [next_state],
                        )
                    )

        return Plan(
            goal_id=goal.goal_id,
            actions=[],
            total_cost=0,
            reachable=False,
            trust_level=self.trust_level,
            states_visited=[],
        )

    def compare_trust_levels(
        self,
        goal: PlanningGoal,
        trust_levels: Optional[list[int]] = None,
    ) -> list[Plan]:
        """Compare plan quality across multiple trust levels for a given goal.

        SIMULATION ONLY. Creates a fresh planner at each specified trust level
        and runs plan() to compare reachability and plan length. All SYNTHETIC.

        Args:
            goal: The PlanningGoal to plan for.
            trust_levels: List of integer trust levels to evaluate.
                Defaults to [0, 1, 2, 3, 4, 5] if not provided.

        Returns:
            List of Plan objects, one per trust level.
        """
        levels = trust_levels if trust_levels is not None else list(range(6))
        results: list[Plan] = []
        for level in levels:
            sub_planner = TrustFilteredPlanner(self.domain, trust_level=level)
            plan_result = sub_planner.plan(goal)
            results.append(plan_result)
        return results
