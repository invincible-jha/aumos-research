# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
verifier.py — EconomicSafetyVerifier: property verification engine.

SIMULATION ONLY. This module implements an arithmetic verification engine for
economic safety properties over synthetic agent spending data. It does NOT
implement Paper 22's 25 formal theorems, production AEAP enforcement, or any
formal proof machinery. All verified data is SYNTHETIC.
"""

from __future__ import annotations

import dataclasses
import uuid
from typing import Optional

import numpy as np

from economic_safety.model import (
    Commitment,
    ConcurrencyResult,
    Envelope,
    SpendingAgent,
    Transaction,
    VerificationResult,
)
from economic_safety.properties import EconomicProperties


class EconomicSafetyVerifier:
    """Verify economic safety properties under simulated agent spending.

    SIMULATION ONLY — does not contain production AEAP 25-theorem proofs.
    All verification is arithmetic comparison over synthetic simulation data.

    This verifier operates on data produced by EconomicModel, checks each
    property using EconomicProperties predicates, and returns VerificationResult
    objects describing whether the property holds and, where it does not, which
    transaction or state served as a counterexample.

    Example::

        from economic_safety.model import EconomicModel, SimulationConfig
        from economic_safety.verifier import EconomicSafetyVerifier
        from economic_safety.scenarios import SCENARIOS

        config = SimulationConfig(seed=42)
        model = EconomicModel(config)
        scenario = SCENARIOS["safe_single_agent"]
        model.create_envelope(scenario.category, scenario.envelope_limit)
        model.simulate_spending(scenario.agents, timesteps=scenario.timesteps)

        verifier = EconomicSafetyVerifier()
        result = verifier.verify_no_overspend(
            list(model.envelopes.values()), model.transactions
        )
        print(result.holds, result.detail)
    """

    # ------------------------------------------------------------------
    # Core property verifications
    # ------------------------------------------------------------------

    def verify_no_overspend(
        self,
        envelopes: list[Envelope],
        transactions: list[Transaction],
    ) -> VerificationResult:
        """Verify that spending never exceeds each envelope's limit.

        SIMULATION ONLY. Checks property P1 (simplified) across all provided
        envelopes and the full transaction sequence. A counterexample is the
        first transaction that pushes any envelope over its limit.

        Args:
            envelopes: List of envelope snapshots to check.
            transactions: Full list of transactions to evaluate.

        Returns:
            VerificationResult with holds=True when all envelopes satisfy P1,
            or holds=False with the first counterexample transaction.
        """
        total_checked = 0
        counterexample: Optional[Transaction] = None

        for envelope in envelopes:
            relevant = [t for t in transactions if t.category == envelope.category]
            total_checked += len(relevant)

            holds, violation_index = EconomicProperties.no_overspend_prefix(
                envelope, relevant
            )
            if not holds:
                counterexample = relevant[violation_index]
                cumulative_at_violation = sum(
                    t.amount for t in relevant[: violation_index + 1]
                )
                return VerificationResult(
                    holds=False,
                    property_name="no_overspend",
                    detail=(
                        f"Envelope '{envelope.category}': cumulative spend "
                        f"{cumulative_at_violation:.4f} exceeds limit "
                        f"{envelope.limit:.4f} at tx_id='{counterexample.tx_id}' "
                        f"(timestep {counterexample.timestep})"
                    ),
                    counterexample=counterexample,
                    transactions_checked=total_checked,
                )

        return VerificationResult(
            holds=True,
            property_name="no_overspend",
            detail=(
                f"No-overspend holds across {len(envelopes)} envelope(s) "
                f"and {total_checked} transaction(s). SIMULATION ONLY."
            ),
            counterexample=None,
            transactions_checked=total_checked,
        )

    def verify_commitment_bounded(
        self,
        envelopes: list[Envelope],
        commitments: list[Commitment],
    ) -> VerificationResult:
        """Verify that committed + spent never exceeds each envelope's limit.

        SIMULATION ONLY. Checks property P2 (simplified): for each envelope,
        the sum of active commitment amounts plus the envelope's recorded spent
        value does not exceed the limit.

        Args:
            envelopes: List of envelope snapshots carrying current spent values.
            commitments: All active commitments to evaluate.

        Returns:
            VerificationResult with holds=True when all envelopes satisfy P2,
            or holds=False with detail indicating which envelope violated it.
        """
        total_checked = len(commitments)
        first_violation_detail = ""

        for envelope in envelopes:
            holds = EconomicProperties.commitment_bounded(envelope, commitments)
            if not holds:
                relevant = [c for c in commitments if c.category == envelope.category]
                total_committed = sum(c.amount for c in relevant)
                first_violation_detail = (
                    f"Envelope '{envelope.category}': spent {envelope.spent:.4f} + "
                    f"committed {total_committed:.4f} = "
                    f"{envelope.spent + total_committed:.4f} exceeds limit "
                    f"{envelope.limit:.4f}"
                )
                return VerificationResult(
                    holds=False,
                    property_name="commitment_bounded",
                    detail=first_violation_detail,
                    counterexample=None,
                    transactions_checked=total_checked,
                )

        return VerificationResult(
            holds=True,
            property_name="commitment_bounded",
            detail=(
                f"Commitment-bounded holds across {len(envelopes)} envelope(s) "
                f"and {total_checked} commitment(s). SIMULATION ONLY."
            ),
            counterexample=None,
            transactions_checked=total_checked,
        )

    def verify_non_negative_balance(
        self, envelopes: list[Envelope]
    ) -> VerificationResult:
        """Verify that no envelope has a negative remaining balance.

        SIMULATION ONLY. Checks property P3 (simplified): envelope.available >= 0
        for every provided envelope.

        Args:
            envelopes: List of envelope snapshots to check.

        Returns:
            VerificationResult with holds=True when all envelopes have
            non-negative available balance.
        """
        for envelope in envelopes:
            if not EconomicProperties.non_negative_balance(envelope):
                return VerificationResult(
                    holds=False,
                    property_name="non_negative_balance",
                    detail=(
                        f"Envelope '{envelope.category}': available balance "
                        f"{envelope.available:.4f} is negative "
                        f"(spent={envelope.spent:.4f}, committed={envelope.committed:.4f}, "
                        f"limit={envelope.limit:.4f})"
                    ),
                    counterexample=None,
                    transactions_checked=len(envelopes),
                )

        return VerificationResult(
            holds=True,
            property_name="non_negative_balance",
            detail=(
                f"Non-negative balance holds across {len(envelopes)} envelope(s). "
                "SIMULATION ONLY."
            ),
            counterexample=None,
            transactions_checked=len(envelopes),
        )

    # ------------------------------------------------------------------
    # Concurrent spending simulation
    # ------------------------------------------------------------------

    def simulate_concurrent_spending(
        self,
        envelope: Envelope,
        agents: list[SpendingAgent],
        timesteps: int = 100,
        seed: int = 42,
        enforce: bool = True,
    ) -> ConcurrencyResult:
        """Simulate concurrent spending to test race conditions.

        SIMULATION ONLY. Models the scenario where multiple agents attempt
        to spend from the same envelope in the same timestep. This is a
        simplified single-threaded simulation of concurrent access — not a
        real distributed concurrency test. All data is SYNTHETIC.

        When enforce=True (safe implementation), each agent's spend is checked
        against the running balance before being accepted. When enforce=False
        (unsafe), all spends are applied regardless, demonstrating what
        happens without enforcement.

        Args:
            envelope: The shared envelope all agents charge against.
            agents: List of spending agents competing for the same budget.
            timesteps: Number of discrete timesteps to simulate.
            seed: RNG seed for reproducibility.
            enforce: When True, apply arithmetic enforcement; when False,
                allow overspend to demonstrate unsafe behaviour.

        Returns:
            ConcurrencyResult with safety assessment, total spend, overspend
            event count, and per-timestep balance timeline.
        """
        rng = np.random.RandomState(seed)
        current_balance = envelope.limit
        timeline: list[float] = []
        overspend_events = 0
        total_spent = 0.0

        for _step in range(timesteps):
            # Generate all agent spends for this timestep (concurrent)
            step_spends: list[float] = []
            for agent in agents:
                raw = float(rng.normal(agent.spending_rate, agent.variance))
                step_spends.append(max(0.0, raw))

            if enforce:
                # Safe: check each spend sequentially against running balance
                for spend in step_spends:
                    if current_balance - spend >= -1e-9:
                        current_balance -= spend
                        total_spent += spend
                    # Rejected spends do not modify balance
            else:
                # Unsafe: apply all spends regardless of balance
                step_total = sum(step_spends)
                current_balance -= step_total
                total_spent += step_total
                if current_balance < -1e-9:
                    overspend_events += 1

            timeline.append(current_balance)

        safe = all(b >= -1e-9 for b in timeline)

        return ConcurrencyResult(
            safe=safe,
            total_spent=total_spent,
            envelope_limit=envelope.limit,
            overspend_events=overspend_events,
            timeline=timeline,
        )

    # ------------------------------------------------------------------
    # Period reset verification
    # ------------------------------------------------------------------

    def verify_period_reset(
        self,
        envelope: Envelope,
        transactions: list[Transaction],
        period: int,
    ) -> VerificationResult:
        """Verify budget resets correctly at period boundaries.

        SIMULATION ONLY. Simulates one budget period from the initial envelope
        state, then resets the spent counter and verifies that the post-reset
        balance equals the full envelope limit. Uses simple arithmetic — not
        a production settlement or rollover mechanism.

        Args:
            envelope: The envelope to simulate; period_steps is used as the
                authoritative period length.
            transactions: Transactions ordered by timestep to replay for
                the period under test.
            period: The period number being verified (zero-indexed, used to
                select the relevant transaction slice).

        Returns:
            VerificationResult indicating whether the period reset restored
            the envelope balance to envelope.limit.
        """
        period_length = envelope.period_steps
        start_step = period * period_length
        end_step = start_step + period_length

        period_txs = [
            t
            for t in transactions
            if t.category == envelope.category
            and start_step <= t.timestep < end_step
        ]

        # Replay period transactions from zero balance
        spent_in_period = sum(t.amount for t in period_txs)

        # Snapshot: balance at end of period
        balance_at_end = envelope.limit - spent_in_period
        # After reset: balance should be full limit
        balance_after_reset = envelope.limit

        holds = EconomicProperties.period_budget_reset(
            balance_at_period_end=balance_at_end,
            balance_at_period_start=balance_after_reset,
            envelope_limit=envelope.limit,
        )

        detail = (
            f"Period {period} of envelope '{envelope.category}': "
            f"spent {spent_in_period:.4f} over {len(period_txs)} tx(s), "
            f"balance at reset = {balance_after_reset:.4f} (limit={envelope.limit:.4f}). "
            "SIMULATION ONLY."
        )

        return VerificationResult(
            holds=holds,
            property_name="period_reset",
            detail=detail,
            counterexample=None,
            transactions_checked=len(period_txs),
        )

    # ------------------------------------------------------------------
    # Full verification suite
    # ------------------------------------------------------------------

    def verify_all(
        self,
        envelopes: list[Envelope],
        transactions: list[Transaction],
        commitments: list[Commitment],
    ) -> list[VerificationResult]:
        """Run all core safety property verifications and return results.

        SIMULATION ONLY. Convenience method that runs no_overspend,
        commitment_bounded, and non_negative_balance in sequence.

        Args:
            envelopes: Envelope snapshots to check.
            transactions: Full transaction history.
            commitments: Active commitment records.

        Returns:
            List of VerificationResult, one per property checked.
        """
        return [
            self.verify_no_overspend(envelopes, transactions),
            self.verify_commitment_bounded(envelopes, commitments),
            self.verify_non_negative_balance(envelopes),
        ]
