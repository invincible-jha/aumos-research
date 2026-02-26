# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""Formal property verification for retention policies.

SIMULATION ONLY — not production AMGP implementation.
This module provides a simplified, research-grade verifier that checks
structural properties of retention policies and simulation results.
It is not a proof assistant and makes no correctness guarantees beyond
the explicit checks performed on the supplied synthetic data.
"""

from __future__ import annotations

from governed_forgetting.policies import ConsentBasedPolicy, ConsentRevocation, RetentionPolicy
from governed_forgetting.types import MemoryRecord, RetentionResult, VerificationResult


class RetentionVerifier:
    """Verify formal properties of retention policies and simulation outcomes.

    SIMULATION ONLY — not production AMGP implementation.
    Each ``verify_*`` method performs exhaustive or model-based checking over
    the supplied synthetic data and returns a :class:`~governed_forgetting.types.VerificationResult`
    that records whether the property held and enumerates any violations found.

    This is a research tool for exploring policy correctness on toy workloads.
    It is not suitable for auditing production systems.

    Example::

        from governed_forgetting.verifier import RetentionVerifier
        from governed_forgetting.policies import TimeBasedPolicy
        from governed_forgetting.model import MemoryRetentionModel
        from governed_forgetting.types import SimulationConfig

        policy = TimeBasedPolicy(ttl=100)
        config = SimulationConfig(policies=[policy])
        model = MemoryRetentionModel(config)
        stream = model.generate_synthetic_stream(n=100)
        result = model.simulate(stream)

        verifier = RetentionVerifier()
        completeness = verifier.verify_completeness(policy, stream)
        print(completeness.holds)  # True
    """

    # ------------------------------------------------------------------
    # Property 1 — Completeness
    # ------------------------------------------------------------------

    def verify_completeness(
        self,
        policy: RetentionPolicy,
        memory_stream: list[MemoryRecord],
        probe_timesteps: int = 10,
    ) -> VerificationResult:
        """Every memory record produces a definite retain/forget decision.

        SIMULATION ONLY — not production AMGP implementation.
        Completeness means ``should_retain`` returns a plain boolean (True/False)
        for every record in the stream without raising an exception. This check
        probes the policy at ``probe_timesteps`` evenly spaced timesteps across
        the expected simulation range (0–500).

        Args:
            policy: The retention policy to verify.
            memory_stream: Synthetic records to evaluate.
            probe_timesteps: Number of timestep probes to perform per record.

        Returns:
            VerificationResult with ``holds=True`` if all calls return booleans
            without error, or ``holds=False`` with a violation list otherwise.
        """
        violations: list[str] = []
        step_size = max(1, 500 // probe_timesteps)
        probed_timesteps = list(range(0, 500, step_size))[:probe_timesteps]
        records_checked = 0

        for record in memory_stream:
            for t in probed_timesteps:
                records_checked += 1
                try:
                    result = policy.should_retain(record, t)
                    if not isinstance(result, bool):
                        violations.append(
                            f"record={record.record_id} t={t}: "
                            f"should_retain returned {type(result).__name__!r}, expected bool"
                        )
                except Exception as exc:  # noqa: BLE001
                    violations.append(
                        f"record={record.record_id} t={t}: "
                        f"should_retain raised {type(exc).__name__}: {exc}"
                    )

        return VerificationResult(
            holds=len(violations) == 0,
            violations=violations,
            records_checked=records_checked,
        )

    # ------------------------------------------------------------------
    # Property 2 — Monotonic forgetting
    # ------------------------------------------------------------------

    def verify_monotonic_forgetting(
        self,
        policy: RetentionPolicy,
        memory_stream: list[MemoryRecord],
        max_timestep: int = 500,
    ) -> VerificationResult:
        """Once a record is forgotten it is never resurrected.

        SIMULATION ONLY — not production AMGP implementation.
        Monotonic forgetting is verified by scanning each record from timestep 0
        to ``max_timestep`` and checking that once ``should_retain`` returns
        ``False`` for a given record, it never returns ``True`` at a later timestep.

        Note: ``ConsentBasedPolicy`` is mutable (consent can be re-granted), so
        this property is checked against the policy's state at the time of the
        call without modifying the consent store.

        Args:
            policy: The retention policy to evaluate.
            memory_stream: Synthetic records to check.
            max_timestep: Upper bound of the timestep scan range.

        Returns:
            VerificationResult with ``holds=True`` if monotonicity holds
            everywhere, otherwise ``holds=False`` with a violation list.
        """
        violations: list[str] = []
        records_checked = 0

        for record in memory_stream:
            records_checked += 1
            forgotten_at: int | None = None
            for t in range(max_timestep + 1):
                decision = policy.should_retain(record, t)
                if not decision and forgotten_at is None:
                    forgotten_at = t
                elif decision and forgotten_at is not None:
                    violations.append(
                        f"record={record.record_id}: forgotten at t={forgotten_at} "
                        f"but resurrected at t={t}"
                    )
                    break  # one violation per record is sufficient

        return VerificationResult(
            holds=len(violations) == 0,
            violations=violations,
            records_checked=records_checked,
        )

    # ------------------------------------------------------------------
    # Property 3 — Consent compliance
    # ------------------------------------------------------------------

    def verify_consent_compliance(
        self,
        policy: RetentionPolicy,
        consent_revocations: list[ConsentRevocation],
        memory_stream: list[MemoryRecord],
        max_delay: int = 1,
    ) -> VerificationResult:
        """All memories are forgotten within ``max_delay`` timesteps of revocation.

        SIMULATION ONLY — not production AMGP implementation.
        For each consent revocation event, this method checks that every record
        belonging to the revoked owner is no longer retained at timestep
        ``revocation.at_timestep + max_delay``.

        This check is only meaningful when ``policy`` is or contains a
        :class:`~governed_forgetting.policies.ConsentBasedPolicy`. If no such
        policy is detected, a warning violation is recorded.

        Args:
            policy: The retention policy to evaluate (should be consent-aware).
            consent_revocations: List of ConsentRevocation events to simulate.
            memory_stream: Synthetic records to check.
            max_delay: Maximum number of timesteps between revocation and
                       confirmed forgetting. The simulation processes forgetting
                       instantly (delay=0 inherent), so ``max_delay=1`` is the
                       default to account for the end-of-tick evaluation model.

        Returns:
            VerificationResult with ``holds=True`` if all revoked owners'
            records are forgotten within the allowed delay, else ``holds=False``.
        """
        from governed_forgetting.policies import CompositePolicy  # noqa: PLC0415

        violations: list[str] = []
        records_checked = 0

        # Check that the policy is consent-aware
        def _has_consent_policy(p: RetentionPolicy) -> bool:
            if isinstance(p, ConsentBasedPolicy):
                return True
            if isinstance(p, CompositePolicy):
                return any(_has_consent_policy(child) for child in p.policies)
            return False

        if not _has_consent_policy(policy):
            violations.append(
                "policy does not contain a ConsentBasedPolicy; "
                "consent compliance cannot be evaluated"
            )
            return VerificationResult(
                holds=False,
                violations=violations,
                records_checked=0,
            )

        for revocation in consent_revocations:
            check_timestep = revocation.at_timestep + max_delay
            owner_records = [
                r for r in memory_stream if r.consent_owner == revocation.owner
            ]
            for record in owner_records:
                records_checked += 1
                still_retained = policy.should_retain(record, check_timestep)
                if still_retained:
                    violations.append(
                        f"record={record.record_id} owner={revocation.owner}: "
                        f"still retained at t={check_timestep} "
                        f"(revoked at t={revocation.at_timestep})"
                    )

        return VerificationResult(
            holds=len(violations) == 0,
            violations=violations,
            records_checked=records_checked,
        )

    # ------------------------------------------------------------------
    # Property 4 — Bounded retention
    # ------------------------------------------------------------------

    def verify_bounded_retention(
        self,
        result: RetentionResult,
        max_retention: int,
    ) -> VerificationResult:
        """No memory is retained beyond ``max_retention`` timesteps.

        SIMULATION ONLY — not production AMGP implementation.
        Examines the ``retained`` set of a completed simulation run and checks
        that no record's age (computed as the simulation's final timestep minus
        ``record.created_at``) exceeds ``max_retention``.

        The final timestep is inferred from the last entry in ``result.history``.
        If ``result.history`` is empty, the check is vacuously true.

        Args:
            result: A completed RetentionResult from MemoryRetentionModel.simulate.
            max_retention: Maximum permissible retention age in simulation timesteps.

        Returns:
            VerificationResult with ``holds=True`` if every retained record is
            within the allowed age, else ``holds=False`` with a violation list.
        """
        violations: list[str] = []
        records_checked = len(result.retained)

        if not result.history:
            return VerificationResult(
                holds=True,
                violations=[],
                records_checked=records_checked,
            )

        final_timestep = result.history[-1].timestep

        for record in result.retained:
            age = final_timestep - record.created_at
            if age > max_retention:
                violations.append(
                    f"record={record.record_id} created_at={record.created_at}: "
                    f"age={age} exceeds max_retention={max_retention} "
                    f"at final timestep={final_timestep}"
                )

        return VerificationResult(
            holds=len(violations) == 0,
            violations=violations,
            records_checked=records_checked,
        )
