# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
planner.py — SimplePlanner: forward BFS search through allowed actions.

SIMULATION ONLY. Implements a simple BFS-based forward planner that operates
over a fixed action set without trust filtering. Serves as the baseline
comparison for TrustFilteredPlanner in experiments. All dynamics are
deterministic. All planning data is SYNTHETIC.

FIRE LINE: Simple forward-search planner ONLY, not production cognitive loop.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from trust_planning.model import Action, Plan, PlanningDomain, PlanningGoal


# ---------------------------------------------------------------------------
# SimplePlanner — SIMULATION ONLY
# ---------------------------------------------------------------------------


class SimplePlanner:
    """Forward BFS planner over the full action space (no trust filtering).

    SIMULATION ONLY — does not contain production planning logic, cognitive
    loops, or stochastic planning. Uses BFS over the complete action set to
    find the shortest plan (fewest actions). Serves as the unconstrained
    baseline for comparison against TrustFilteredPlanner. All data SYNTHETIC.

    Example::

        planner = SimplePlanner(domain)
        plan = planner.plan(goal)
        print(plan.length)
    """

    def __init__(self, domain: PlanningDomain) -> None:
        """Initialise the planner with a planning domain.

        SIMULATION ONLY. Uses the full action set without trust filtering.

        Args:
            domain: The PlanningDomain with all available actions and goals.
        """
        self.domain = domain
        # Pre-build forward adjacency over all actions
        self._adjacency: dict[str, list[tuple[Action, str]]] = {}
        for action in domain.actions:
            if action.requires not in self._adjacency:
                self._adjacency[action.requires] = []
            self._adjacency[action.requires].append((action, action.produces))

    def plan(self, goal: PlanningGoal) -> Plan:
        """Find a plan from goal.initial_state to goal.target_state using BFS.

        SIMULATION ONLY. Uses the full unfiltered action space (trust_level=5
        is implied — all actions are available). Returns the shortest plan by
        BFS expansion. Returns an unreachable Plan when no path exists.
        All data is SYNTHETIC.

        Args:
            goal: The PlanningGoal defining start and target states.

        Returns:
            Plan with the shortest action sequence and total cost.
        """
        initial = goal.initial_state
        target = goal.target_state

        if initial == target:
            return Plan(
                goal_id=goal.goal_id,
                actions=[],
                total_cost=0,
                reachable=True,
                trust_level=5,
                states_visited=[initial],
            )

        visited: set[str] = {initial}
        queue: deque[tuple[str, list[Action], list[str]]] = deque(
            [(initial, [], [initial])]
        )

        while queue:
            current_state, action_path, states_path = queue.popleft()

            for action, next_state in self._adjacency.get(current_state, []):
                if next_state == target:
                    final_actions = action_path + [action]
                    final_states = states_path + [next_state]
                    return Plan(
                        goal_id=goal.goal_id,
                        actions=final_actions,
                        total_cost=sum(a.cost for a in final_actions),
                        reachable=True,
                        trust_level=5,
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
            trust_level=5,
            states_visited=[],
        )

    def all_reachable_states(self, initial_state: str) -> set[str]:
        """Return all states reachable from initial_state using BFS.

        SIMULATION ONLY. Uses the full unfiltered action space. Produces the
        maximal reachable state set. All data is SYNTHETIC.

        Args:
            initial_state: The state label to begin BFS from.

        Returns:
            Set of all reachable state labels (including initial_state).
        """
        visited: set[str] = {initial_state}
        queue: deque[str] = deque([initial_state])
        while queue:
            current = queue.popleft()
            for _action, next_state in self._adjacency.get(current, []):
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append(next_state)
        return visited


# ---------------------------------------------------------------------------
# Greedy planner variant — SIMULATION ONLY
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GreedyPlanResult:
    """Result of a greedy (lowest-cost first) planning pass.

    SIMULATION ONLY. Greedy selection by minimum action cost at each step,
    not guaranteed optimal. Used to illustrate non-BFS baselines.

    Attributes:
        goal_id: Identifier of the goal planned for.
        actions: Ordered action sequence chosen.
        total_cost: Sum of action costs.
        reachable: True when the goal was reached.
        trust_level: Trust level in effect during planning.
    """

    goal_id: str
    actions: list[Action]
    total_cost: int
    reachable: bool
    trust_level: int


class GreedyPlanner:
    """Forward greedy planner: at each step, select the lowest-cost available action.

    SIMULATION ONLY. Not guaranteed to find the optimal plan or even a plan
    when one exists (greedy may get stuck). Used as an illustration of a
    non-BFS strategy. All data is SYNTHETIC.

    Example::

        planner = GreedyPlanner(domain, trust_level=2, max_steps=20)
        result = planner.plan(goal)
    """

    def __init__(
        self,
        domain: PlanningDomain,
        trust_level: int = 5,
        max_steps: int = 50,
    ) -> None:
        """Initialise the greedy planner.

        SIMULATION ONLY.

        Args:
            domain: The PlanningDomain with all available actions.
            trust_level: Integer trust level in [0, 5] for action filtering.
            max_steps: Maximum number of greedy steps before declaring failure.
        """
        if not (0 <= trust_level <= 5):
            raise ValueError(f"trust_level must be in [0, 5]; got {trust_level}")
        self.domain = domain
        self.trust_level = trust_level
        self.max_steps = max_steps

        # Build adjacency over trust-filtered actions
        self._adjacency: dict[str, list[tuple[Action, str]]] = {}
        for action in domain.actions:
            if action.required_trust <= trust_level:
                if action.requires not in self._adjacency:
                    self._adjacency[action.requires] = []
                self._adjacency[action.requires].append((action, action.produces))

    def plan(self, goal: PlanningGoal) -> GreedyPlanResult:
        """Find a plan using greedy lowest-cost-first action selection.

        SIMULATION ONLY. At each state, selects the action with the lowest cost
        that transitions to an unvisited state. Stops when goal is reached or
        no actions remain. All data is SYNTHETIC.

        Args:
            goal: The PlanningGoal to solve.

        Returns:
            GreedyPlanResult with the action sequence chosen.
        """
        current_state = goal.initial_state
        chosen_actions: list[Action] = []
        visited: set[str] = {current_state}

        for _step in range(self.max_steps):
            if current_state == goal.target_state:
                return GreedyPlanResult(
                    goal_id=goal.goal_id,
                    actions=chosen_actions,
                    total_cost=sum(a.cost for a in chosen_actions),
                    reachable=True,
                    trust_level=self.trust_level,
                )

            candidates = [
                (action, next_state)
                for action, next_state in self._adjacency.get(current_state, [])
                if next_state not in visited
            ]

            if not candidates:
                break

            # Greedy: pick lowest-cost action
            best_action, best_next = min(candidates, key=lambda pair: pair[0].cost)
            chosen_actions.append(best_action)
            visited.add(best_next)
            current_state = best_next

        if current_state == goal.target_state:
            return GreedyPlanResult(
                goal_id=goal.goal_id,
                actions=chosen_actions,
                total_cost=sum(a.cost for a in chosen_actions),
                reachable=True,
                trust_level=self.trust_level,
            )

        return GreedyPlanResult(
            goal_id=goal.goal_id,
            actions=chosen_actions,
            total_cost=sum(a.cost for a in chosen_actions),
            reachable=False,
            trust_level=self.trust_level,
        )
