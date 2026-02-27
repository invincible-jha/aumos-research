# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
# DISCLAIMER: This is simulation code for academic reproduction, not production implementation
"""
cost_ungoverned.py — "Cost of Ungoverned AI" Monte Carlo simulation.

Simulates the financial risk exposure of ungoverned versus governed AI agent
deployments across multiple cost categories using synthetic probabilistic models.

All cost figures and probabilities are illustrative and synthetic.
They do not represent real incident data or actuarial estimates.
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple


# ── Enumerations ───────────────────────────────────────────────────────────────

class CostCategory(str, Enum):
    """Categories of financial cost from ungoverned AI incidents."""

    API_OVERCHARGE = "api_overcharge"
    DATA_BREACH_FINE = "data_breach_fine"
    COMPLIANCE_PENALTY = "compliance_penalty"
    REPUTATION_DAMAGE = "reputation_damage"
    OPERATIONAL_DISRUPTION = "operational_disruption"


# ── Data models ────────────────────────────────────────────────────────────────

@dataclass
class UngovermedScenario:
    """A single ungoverned AI cost scenario with probabilistic cost model."""

    name: str
    category: CostCategory
    probability_per_month: float         # 0.0–1.0 chance of occurring in any given month
    cost_range: tuple[float, float]      # (min_usd, max_usd) — uniform draw when incident occurs
    description: str
    governance_reduction_factor: float = 0.85  # fraction by which governance reduces probability

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability_per_month <= 1.0:
            raise ValueError(f"probability_per_month must be 0–1, got {self.probability_per_month}")
        if self.cost_range[0] > self.cost_range[1]:
            raise ValueError("cost_range min must be <= max")


@dataclass
class IncidentRecord:
    """A single incident that occurred in the simulation."""

    month: int
    scenario_name: str
    category: CostCategory
    cost: float


@dataclass
class SimulationResult:
    """Aggregate result of a single simulation run."""

    total_cost: float
    incidents: list[IncidentRecord]
    monthly_breakdown: list[float]       # total cost per month
    governed: bool


class ComparisonResult(NamedTuple):
    governed_result: SimulationResult
    ungoverned_result: SimulationResult
    savings: float
    roi_percentage: float


# ── Pre-built scenarios ────────────────────────────────────────────────────────

def _build_scenarios() -> list[UngovermedScenario]:
    return [
        UngovermedScenario(
            name="runaway_api_calls",
            category=CostCategory.API_OVERCHARGE,
            probability_per_month=0.20,
            cost_range=(500.0, 50_000.0),
            description="Agent enters a loop or makes excessive API calls without rate limiting.",
            governance_reduction_factor=0.90,
        ),
        UngovermedScenario(
            name="pii_exposure",
            category=CostCategory.DATA_BREACH_FINE,
            probability_per_month=0.05,
            cost_range=(10_000.0, 1_000_000.0),
            description="Agent inadvertently exposes PII to an external system or log.",
            governance_reduction_factor=0.80,
        ),
        UngovermedScenario(
            name="gdpr_violation",
            category=CostCategory.COMPLIANCE_PENALTY,
            probability_per_month=0.03,
            cost_range=(50_000.0, 20_000_000.0),
            description="Agent processes EU citizen data without lawful basis, triggering DPA investigation.",
            governance_reduction_factor=0.88,
        ),
        UngovermedScenario(
            name="unauthorized_tool_use",
            category=CostCategory.OPERATIONAL_DISRUPTION,
            probability_per_month=0.12,
            cost_range=(1_000.0, 100_000.0),
            description="Agent invokes tools outside its approved scope, causing system disruption.",
            governance_reduction_factor=0.92,
        ),
        UngovermedScenario(
            name="model_hallucination_liability",
            category=CostCategory.REPUTATION_DAMAGE,
            probability_per_month=0.08,
            cost_range=(5_000.0, 500_000.0),
            description="Agent outputs fabricated information used in a business decision, causing harm.",
            governance_reduction_factor=0.70,
        ),
        UngovermedScenario(
            name="cloud_resource_overprovisioning",
            category=CostCategory.API_OVERCHARGE,
            probability_per_month=0.15,
            cost_range=(200.0, 25_000.0),
            description="Agent provisions cloud resources without budget guardrails.",
            governance_reduction_factor=0.95,
        ),
        UngovermedScenario(
            name="supply_chain_compromise",
            category=CostCategory.OPERATIONAL_DISRUPTION,
            probability_per_month=0.02,
            cost_range=(20_000.0, 2_000_000.0),
            description="Agent fetches and executes a malicious dependency without validation.",
            governance_reduction_factor=0.75,
        ),
        UngovermedScenario(
            name="insider_data_exfiltration",
            category=CostCategory.DATA_BREACH_FINE,
            probability_per_month=0.01,
            cost_range=(100_000.0, 5_000_000.0),
            description="Agent is manipulated into exfiltrating sensitive internal data.",
            governance_reduction_factor=0.85,
        ),
    ]


BUILT_IN_SCENARIOS: list[UngovermedScenario] = _build_scenarios()


# ── Simulator ──────────────────────────────────────────────────────────────────

class CostSimulator:
    """Monte Carlo simulator for governed vs ungoverned AI cost exposure.

    Uses numpy random with a fixed seed for reproducibility.
    All figures are synthetic and illustrative only.
    """

    def __init__(
        self,
        scenarios: list[UngovermedScenario] | None = None,
        random_seed: int = 42,
    ) -> None:
        self._scenarios: list[UngovermedScenario] = scenarios if scenarios is not None else BUILT_IN_SCENARIOS
        self._rng = np.random.default_rng(random_seed)

    def simulate_months(self, months: int, governed: bool) -> SimulationResult:
        """Run a single simulation over the specified number of months.

        In governed mode, the probability of each incident is reduced by
        the scenario's governance_reduction_factor.
        """
        incidents: list[IncidentRecord] = []
        monthly_breakdown: list[float] = []

        for month in range(months):
            month_cost = 0.0
            for scenario in self._scenarios:
                prob = scenario.probability_per_month
                if governed:
                    prob = prob * (1.0 - scenario.governance_reduction_factor)

                if self._rng.random() < prob:
                    cost = float(self._rng.uniform(scenario.cost_range[0], scenario.cost_range[1]))
                    incidents.append(IncidentRecord(month, scenario.name, scenario.category, cost))
                    month_cost += cost

            monthly_breakdown.append(month_cost)

        total_cost = sum(monthly_breakdown)
        return SimulationResult(
            total_cost=total_cost,
            incidents=incidents,
            monthly_breakdown=monthly_breakdown,
            governed=governed,
        )

    def compare_governed_vs_ungoverned(self, months: int, runs: int = 100) -> ComparisonResult:
        """Run multiple Monte Carlo trials and average governed vs ungoverned costs.

        Args:
            months: Duration of each simulation in months.
            runs: Number of independent Monte Carlo trials to average.

        Returns a ComparisonResult with averaged outcomes and computed ROI.
        """
        gov_totals: list[float] = []
        ungov_totals: list[float] = []

        for _ in range(runs):
            gov_totals.append(self.simulate_months(months, governed=True).total_cost)
            ungov_totals.append(self.simulate_months(months, governed=False).total_cost)

        avg_gov = float(np.mean(gov_totals))
        avg_ungov = float(np.mean(ungov_totals))
        savings = avg_ungov - avg_gov
        roi = (savings / avg_gov * 100.0) if avg_gov > 0 else 0.0

        # Build representative single-run results for the comparison object
        gov_result = self.simulate_months(months, governed=True)
        ungov_result = self.simulate_months(months, governed=False)
        # Override totals with averaged values for the comparison
        gov_result.total_cost = avg_gov
        ungov_result.total_cost = avg_ungov

        return ComparisonResult(
            governed_result=gov_result,
            ungoverned_result=ungov_result,
            savings=savings,
            roi_percentage=roi,
        )

    def plot_comparison(self, result: ComparisonResult) -> None:
        """Render a matplotlib chart comparing governed vs ungoverned outcomes.

        Produces a two-panel figure: cumulative cost trajectories and
        per-category incident breakdown.
        """
        gov = result.governed_result
        ungov = result.ungoverned_result
        months = list(range(len(gov.monthly_breakdown)))

        gov_cumulative = list(np.cumsum(gov.monthly_breakdown))
        ungov_cumulative = list(np.cumsum(ungov.monthly_breakdown))

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))

        # Panel 1: cumulative cost trajectories
        axes[0].plot(months, gov_cumulative, color="#2E7D32", linewidth=2, label="Governed")
        axes[0].plot(months, ungov_cumulative, color="#C62828", linestyle="--", linewidth=2, label="Ungoverned")
        axes[0].fill_between(months, gov_cumulative, ungov_cumulative, alpha=0.12, color="#757575")
        axes[0].set_xlabel("Month")
        axes[0].set_ylabel("Cumulative Cost (USD)")
        axes[0].set_title("Cumulative Cost Trajectories\n(single representative run)")
        axes[0].legend()
        axes[0].grid(alpha=0.3)

        # Panel 2: savings by category
        categories = [c.value for c in CostCategory]
        gov_by_cat = {c: sum(inc.cost for inc in gov.incidents if inc.category.value == c) for c in categories}
        ungov_by_cat = {c: sum(inc.cost for inc in ungov.incidents if inc.category.value == c) for c in categories}

        x = np.arange(len(categories))
        width = 0.35
        axes[1].bar(x - width / 2, [gov_by_cat[c] for c in categories], width,
                    label="Governed", color="#42A5F5", alpha=0.85)
        axes[1].bar(x + width / 2, [ungov_by_cat[c] for c in categories], width,
                    label="Ungoverned", color="#EF5350", alpha=0.85)
        axes[1].set_xticks(x)
        axes[1].set_xticklabels([c.replace("_", "\n") for c in categories], fontsize=7)
        axes[1].set_ylabel("Total Incident Cost (USD)")
        axes[1].set_title("Cost by Category")
        axes[1].legend()
        axes[1].grid(axis="y", alpha=0.3)

        plt.suptitle(
            f"Cost of Ungoverned AI — Synthetic Simulation\n"
            f"Avg savings: ${result.savings:,.0f}  |  ROI: {result.roi_percentage:.0f}%",
            fontsize=12,
        )
        plt.tight_layout()
        plt.savefig("cost_ungoverned_comparison.png", dpi=120)
        plt.show()


# ── Example usage ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    simulator = CostSimulator(random_seed=42)
    comparison = simulator.compare_governed_vs_ungoverned(months=24, runs=200)

    print("Cost of Ungoverned AI — Monte Carlo Simulation")
    print("=" * 52)
    print(f"  Governed avg total:    ${comparison.governed_result.total_cost:>12,.2f}")
    print(f"  Ungoverned avg total:  ${comparison.ungoverned_result.total_cost:>12,.2f}")
    print(f"  Avg savings:           ${comparison.savings:>12,.2f}")
    print(f"  ROI of governance:     {comparison.roi_percentage:>10.1f}%")

    simulator.plot_comparison(comparison)
