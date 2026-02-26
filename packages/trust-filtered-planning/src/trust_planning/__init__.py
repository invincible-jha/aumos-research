# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
trust_planning — Research companion for Paper 12.

SIMULATION ONLY. This package implements a simplified trust-filtered forward-search
planner for synthetic agent planning domains. It does NOT contain Paper 12's full
planning theory, production cognitive planning loops, adaptive trust assignment,
or stochastic action models.

Trust levels are INTEGERS 0–5. Actions with required trust above the agent's
assigned level are excluded from the planning search space. All planning data
is SYNTHETIC. All results are generated deterministically.

FIRE LINE: Simple forward-search planner ONLY, not production cognitive loop.
"""

from trust_planning.model import (
    Action,
    Plan,
    PlanningDomain,
    PlanningGoal,
    TrustFilteredPlanner,
)
from trust_planning.planner import SimplePlanner
from trust_planning.evaluator import PlanEvaluator

__version__ = "0.1.0"
__all__ = [
    # Model
    "TrustFilteredPlanner",
    "Action",
    "Plan",
    "PlanningDomain",
    "PlanningGoal",
    # Planner
    "SimplePlanner",
    # Evaluator
    "PlanEvaluator",
]
