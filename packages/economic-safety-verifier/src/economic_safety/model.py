# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
model.py — EconomicModel and core dataclasses for spending envelope simulation.

SIMULATION ONLY. This module implements a simplified arithmetic model of agent
spending within budget envelopes. It does NOT contain production AEAP algorithms,
Paper 22's 25 theorem proofs, saga-pattern compensation logic, or adaptive budget
allocation. All data produced is SYNTHETIC.
"""

from __future__ import annotations

import dataclasses
import uuid
from dataclasses import dataclass
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Core dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Envelope:
    """A budget envelope constraining spending within a category.

    SIMULATION ONLY. Represents a static spending limit — not a production
    AEAP budget object. Limits are fixed at creation; there is no adaptive
    reallocation logic.

    Attributes:
        category: Logical category label (e.g., "compute", "storage").
        limit: Maximum cumulative spend allowed within one period.
        spent: Amount already spent (immutable snapshot).
        committed: Amount reserved for pending future transactions.
        period_steps: Number of timesteps in one budget period.
    """

    category: str
    limit: float
    spent: float = 0.0
    committed: float = 0.0
    period_steps: int = 100

    @property
    def available(self) -> float:
        """Remaining balance after accounting for spent and committed funds."""
        return self.limit - self.spent - self.committed

    @property
    def utilisation(self) -> float:
        """Fraction of limit consumed by spending (0.0–1.0+)."""
        if self.limit <= 0.0:
            return 0.0
        return self.spent / self.limit


@dataclass(frozen=True)
class Transaction:
    """A single spending event recorded against an envelope.

    SIMULATION ONLY. Represents a synthetic spending record — not a real
    financial transaction or a production AEAP ledger entry.

    Attributes:
        tx_id: Unique transaction identifier.
        category: Envelope category this transaction charges.
        amount: Non-negative amount spent.
        agent_id: Identifier of the agent that initiated the spend.
        timestep: Simulation timestep at which the transaction occurred.
    """

    tx_id: str
    category: str
    amount: float
    agent_id: str
    timestep: int


@dataclass(frozen=True)
class Commitment:
    """A reservation of budget for a planned future spend.

    SIMULATION ONLY. Represents a synthetic budget reservation — not a
    production saga step or distributed commitment record.

    Attributes:
        commitment_id: Unique commitment identifier.
        category: Envelope category this commitment reserves against.
        amount: Non-negative amount reserved.
        agent_id: Identifier of the agent that created the commitment.
        created_at: Timestep when the commitment was created.
        expires_at: Timestep after which the commitment is released.
    """

    commitment_id: str
    category: str
    amount: float
    agent_id: str
    created_at: int
    expires_at: int


@dataclass(frozen=True)
class SpendingAgent:
    """Parameters for a synthetic agent that generates spending transactions.

    SIMULATION ONLY. Encapsulates spending behaviour as a normal distribution
    parameterised by rate and variance — not a real production agent profile.

    Attributes:
        agent_id: Unique agent identifier.
        spending_rate: Mean spend per timestep (must be >= 0).
        variance: Standard deviation of per-step spend (must be >= 0).
        category: Envelope category this agent charges against.
    """

    agent_id: str
    spending_rate: float
    variance: float
    category: str


@dataclass(frozen=True)
class VerificationResult:
    """Result of evaluating a single economic safety property.

    SIMULATION ONLY. Produced by EconomicSafetyVerifier — NOT by Paper 22's
    formal theorem prover.

    Attributes:
        holds: True when the property is satisfied across all checked data.
        property_name: Human-readable name of the verified property.
        detail: Prose summary of the verification outcome.
        counterexample: First transaction that violates the property, if any.
        transactions_checked: Total number of transactions evaluated.
    """

    holds: bool
    property_name: str
    detail: str = ""
    counterexample: Optional[Transaction] = None
    transactions_checked: int = 0


@dataclass(frozen=True)
class ConcurrencyResult:
    """Outcome of a concurrent multi-agent spending simulation.

    SIMULATION ONLY. Captures the aggregate safety outcome when multiple
    synthetic agents spend concurrently from a shared envelope.

    Attributes:
        safe: True when no overspend occurred throughout the simulation.
        total_spent: Cumulative spend across all agents and timesteps.
        envelope_limit: The limit of the envelope under test.
        overspend_events: Number of timesteps where cumulative spend exceeded limit.
        timeline: Remaining balance at the end of each timestep.
    """

    safe: bool
    total_spent: float
    envelope_limit: float
    overspend_events: int
    timeline: list[float]


@dataclass
class SpendingResult:
    """Aggregate result of a multi-agent spending simulation run.

    SIMULATION ONLY. Produced by EconomicModel.simulate_spending — not by
    any production system.

    Attributes:
        category: The envelope category that was simulated.
        envelope_limit: The budget limit of the simulated envelope.
        total_spent: Cumulative spend over the full simulation.
        transactions: All transactions generated during the simulation.
        balance_timeline: Remaining envelope balance at the end of each timestep.
        agent_ids: Identifiers of all agents that participated.
        overspend_prevented: Count of transactions blocked by enforcement.
    """

    category: str
    envelope_limit: float
    total_spent: float
    transactions: list[Transaction]
    balance_timeline: list[float]
    agent_ids: list[str]
    overspend_prevented: int = 0


# ---------------------------------------------------------------------------
# Simulation configuration
# ---------------------------------------------------------------------------


@dataclass
class SimulationConfig:
    """Configuration for the EconomicModel simulation.

    SIMULATION ONLY.

    Attributes:
        seed: RNG seed for deterministic reproducibility (default 42).
        enforce_limits: When True, transactions that would overspend are
            rejected; when False they are recorded anyway (useful for
            demonstrating what unsafe behaviour looks like).
    """

    seed: int = 42
    enforce_limits: bool = True


# ---------------------------------------------------------------------------
# EconomicModel
# ---------------------------------------------------------------------------


class EconomicModel:
    """Simulate agent spending within budget envelopes.

    SIMULATION ONLY — does not contain production AEAP implementation or
    Paper 22's 25-theorem proofs. Uses simplified arithmetic for academic
    analysis. All produced spending data is SYNTHETIC.

    The model maintains a registry of envelopes keyed by category. Agents
    generate transactions drawn from a normal distribution parameterised by
    their spending_rate and variance. Enforcement is a simple arithmetic
    comparison of cumulative spend against the envelope limit.

    Example::

        config = SimulationConfig(seed=42)
        model = EconomicModel(config)
        model.create_envelope("compute", limit=1000.0)
        agents = [SpendingAgent("a1", spending_rate=8.0, variance=1.5, category="compute")]
        result = model.simulate_spending(agents, timesteps=100)
        print(result.total_spent, result.balance_timeline[-1])
    """

    def __init__(self, config: SimulationConfig) -> None:
        """Initialise the model with the given configuration.

        SIMULATION ONLY.

        Args:
            config: Simulation parameters including seed and enforcement flag.
        """
        self.config = config
        self.envelopes: dict[str, Envelope] = {}
        self.transactions: list[Transaction] = []
        self.commitments: list[Commitment] = []
        self.rng = np.random.RandomState(config.seed)

    # ------------------------------------------------------------------
    # Envelope management
    # ------------------------------------------------------------------

    def create_envelope(
        self, category: str, limit: float, period: int = 100
    ) -> Envelope:
        """Register a new spending envelope for a given category.

        SIMULATION ONLY. Limits are static — no adaptive reallocation.

        Args:
            category: Logical name for the budget category.
            limit: Maximum cumulative spend permitted per period.
            period: Number of timesteps in one budget period.

        Returns:
            The newly created Envelope (also stored in self.envelopes).

        Raises:
            ValueError: If limit is negative or category already registered.
        """
        if limit < 0.0:
            raise ValueError(f"Envelope limit must be non-negative; got {limit}")
        if category in self.envelopes:
            raise ValueError(f"Envelope for category '{category}' already exists")
        envelope = Envelope(
            category=category,
            limit=limit,
            spent=0.0,
            committed=0.0,
            period_steps=period,
        )
        self.envelopes[category] = envelope
        return envelope

    def _get_envelope(self, category: str) -> Envelope:
        """Retrieve the current envelope state for a category."""
        if category not in self.envelopes:
            raise KeyError(f"No envelope registered for category '{category}'")
        return self.envelopes[category]

    # ------------------------------------------------------------------
    # Transaction recording
    # ------------------------------------------------------------------

    def record_transaction(self, tx: Transaction) -> bool:
        """Record a spending transaction against the relevant envelope.

        SIMULATION ONLY. Enforcement is a simple arithmetic comparison — not
        a production AEAP ledger operation.

        If self.config.enforce_limits is True (default), transactions that
        would cause the envelope's cumulative spend to exceed its limit are
        rejected and return False without modifying state.

        Args:
            tx: The transaction to record.

        Returns:
            True when the transaction was accepted; False when rejected due
            to budget enforcement.

        Raises:
            ValueError: If tx.amount is negative.
            KeyError: If no envelope exists for tx.category.
        """
        if tx.amount < 0.0:
            raise ValueError(f"Transaction amount must be non-negative; got {tx.amount}")

        envelope = self._get_envelope(tx.category)

        if self.config.enforce_limits:
            if envelope.spent + tx.amount > envelope.limit:
                return False

        # Build updated envelope (frozen dataclass — replace via dataclasses.replace)
        updated = dataclasses.replace(envelope, spent=envelope.spent + tx.amount)
        self.envelopes[tx.category] = updated
        self.transactions.append(tx)
        return True

    # ------------------------------------------------------------------
    # Commitment management
    # ------------------------------------------------------------------

    def create_commitment(self, commitment: Commitment) -> bool:
        """Reserve budget for a planned future spend.

        SIMULATION ONLY. This is simple balance reservation arithmetic — not
        a production saga step or distributed two-phase commit.

        If the envelope has insufficient available balance (limit - spent - committed),
        the commitment is rejected and returns False.

        Args:
            commitment: The commitment to register.

        Returns:
            True when the commitment was accepted; False when rejected.

        Raises:
            ValueError: If commitment.amount is negative.
            KeyError: If no envelope exists for commitment.category.
        """
        if commitment.amount < 0.0:
            raise ValueError(
                f"Commitment amount must be non-negative; got {commitment.amount}"
            )

        envelope = self._get_envelope(commitment.category)

        if self.config.enforce_limits:
            if envelope.spent + envelope.committed + commitment.amount > envelope.limit:
                return False

        updated = dataclasses.replace(
            envelope, committed=envelope.committed + commitment.amount
        )
        self.envelopes[commitment.category] = updated
        self.commitments.append(commitment)
        return True

    def release_commitment(self, commitment: Commitment) -> None:
        """Release a previously reserved commitment, freeing the balance.

        SIMULATION ONLY.

        Args:
            commitment: The commitment to release.

        Raises:
            KeyError: If no envelope exists for commitment.category.
        """
        envelope = self._get_envelope(commitment.category)
        released = max(0.0, envelope.committed - commitment.amount)
        self.envelopes[commitment.category] = dataclasses.replace(
            envelope, committed=released
        )

    def expire_commitments(self, current_timestep: int) -> int:
        """Release all commitments whose expires_at is <= current_timestep.

        SIMULATION ONLY.

        Args:
            current_timestep: The current simulation timestep.

        Returns:
            Number of commitments that were released.
        """
        expired = [
            c for c in self.commitments if c.expires_at <= current_timestep
        ]
        for commitment in expired:
            self.release_commitment(commitment)
        self.commitments = [
            c for c in self.commitments if c.expires_at > current_timestep
        ]
        return len(expired)

    # ------------------------------------------------------------------
    # Period reset
    # ------------------------------------------------------------------

    def reset_period(self, category: str) -> Envelope:
        """Reset the spent counter for an envelope at a new period boundary.

        SIMULATION ONLY. Simulates a periodic budget refresh — not a production
        settlement or rollover operation.

        Args:
            category: The envelope category to reset.

        Returns:
            The reset Envelope.

        Raises:
            KeyError: If no envelope exists for the category.
        """
        envelope = self._get_envelope(category)
        reset_envelope = dataclasses.replace(envelope, spent=0.0, committed=0.0)
        self.envelopes[category] = reset_envelope
        return reset_envelope

    # ------------------------------------------------------------------
    # Spending simulation
    # ------------------------------------------------------------------

    def simulate_spending(
        self, agents: list[SpendingAgent], timesteps: int = 100
    ) -> SpendingResult:
        """Simulate multiple agents spending concurrently over a number of timesteps.

        SIMULATION ONLY. Per-timestep spend for each agent is drawn from a
        normal distribution N(spending_rate, variance). Negative draws are
        clipped to zero. Enforcement is arithmetic comparison against the
        envelope limit.

        Each agent must reference a category for which an envelope has been
        registered via create_envelope before calling this method.

        Args:
            agents: List of SpendingAgent instances whose categories must
                have registered envelopes.
            timesteps: Number of discrete timesteps to simulate.

        Returns:
            SpendingResult aggregating total spend, all transactions, the
            per-timestep balance timeline, and enforcement statistics.

        Raises:
            KeyError: If any agent references an unregistered category.
        """
        # Validate all agents have registered envelopes
        for agent in agents:
            self._get_envelope(agent.category)

        # We track each category's timeline separately; if multiple agents
        # share a category, the timeline reflects the shared envelope.
        category_timeline: dict[str, list[float]] = {
            agent.category: [] for agent in agents
        }
        overspend_prevented = 0

        for step in range(timesteps):
            # All agents attempt to spend at this timestep (concurrent order)
            for agent in agents:
                raw_spend = float(
                    self.rng.normal(agent.spending_rate, agent.variance)
                )
                amount = max(0.0, raw_spend)

                tx = Transaction(
                    tx_id=str(uuid.uuid4()),
                    category=agent.category,
                    amount=amount,
                    agent_id=agent.agent_id,
                    timestep=step,
                )
                accepted = self.record_transaction(tx)
                if not accepted:
                    overspend_prevented += 1

            # Record end-of-step balance for each category
            for category in category_timeline:
                envelope = self.envelopes[category]
                category_timeline[category].append(envelope.available)

        # Build aggregate result across all categories
        total_spent = sum(
            self.envelopes[c].spent for c in category_timeline
        )

        # For the result timeline, use the first category (single-category
        # experiments) or the sum of remaining balances (multi-category).
        categories = list(category_timeline.keys())
        if len(categories) == 1:
            balance_timeline = category_timeline[categories[0]]
        else:
            balance_timeline = [
                sum(category_timeline[c][step] for c in categories)
                for step in range(timesteps)
            ]

        primary_category = agents[0].category if agents else ""
        primary_limit = (
            self.envelopes[primary_category].limit if primary_category else 0.0
        )

        return SpendingResult(
            category=primary_category,
            envelope_limit=primary_limit,
            total_spent=total_spent,
            transactions=list(self.transactions),
            balance_timeline=balance_timeline,
            agent_ids=[a.agent_id for a in agents],
            overspend_prevented=overspend_prevented,
        )
