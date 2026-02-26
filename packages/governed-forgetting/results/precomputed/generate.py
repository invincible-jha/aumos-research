#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""Bootstrap script: generate all precomputed JSON result files.

SIMULATION ONLY — not production AMGP implementation.
Run this script once from the package root to populate the four precomputed
JSON files used by the paper figures and the experiment loader.

Usage::

    cd packages/governed-forgetting
    python results/precomputed/generate.py
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from dataclasses import dataclass
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Minimal inline implementations so this script needs no package install
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _Record:
    record_id: str
    content_hash: str
    created_at: int
    category: str
    relevance_score: float
    consent_owner: str


def _generate_stream(
    n: int,
    seed: int,
    categories: list[str],
    n_owners: int,
    birth_spread: int,
) -> list[_Record]:
    rng = np.random.RandomState(seed)
    records = []
    for i in range(n):
        created_at = int(rng.randint(0, birth_spread))
        relevance = float(np.clip(rng.beta(2.0, 2.0), 0.01, 1.0))
        category = str(categories[int(rng.randint(0, len(categories)))])
        owner = f"user_{int(rng.randint(0, n_owners))}"
        raw = f"{i}:{created_at}:{category}:{owner}:{seed}"
        content_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        records.append(_Record(
            record_id=f"rec_{i:05d}",
            content_hash=content_hash,
            created_at=created_at,
            category=category,
            relevance_score=relevance,
            consent_owner=owner,
        ))
    return records


def _sim_time_based(
    stream: list[_Record],
    ttl: int,
    timesteps: int,
) -> tuple[list[dict[str, int]], float]:
    active = list(stream)
    forgotten: list[_Record] = []
    history = []
    for t in range(timesteps):
        still, new_f = [], []
        for rec in active:
            (still if (t - rec.created_at) < ttl else new_f).append(rec)
        active = still
        forgotten.extend(new_f)
        history.append({"timestep": t, "active": len(active), "forgotten": len(forgotten)})
    return history, len(active) / max(len(stream), 1)


def _sim_decay(
    stream: list[_Record],
    decay_rate: float,
    threshold: float,
    timesteps: int,
) -> tuple[list[dict[str, int]], float]:
    active = list(stream)
    forgotten: list[_Record] = []
    history = []
    for t in range(timesteps):
        still, new_f = [], []
        for rec in active:
            age = max(0, t - rec.created_at)
            score = rec.relevance_score * math.exp(-decay_rate * age)
            (still if score >= threshold else new_f).append(rec)
        active = still
        forgotten.extend(new_f)
        history.append({"timestep": t, "active": len(active), "forgotten": len(forgotten)})
    return history, len(active) / max(len(stream), 1)


def _sim_consent(
    stream: list[_Record],
    n_owners: int,
    revocation_timesteps: list[int],
    timesteps: int,
) -> tuple[list[dict[str, int]], float]:
    owners = [f"user_{i}" for i in range(n_owners)]
    consent: dict[str, bool] = {o: True for o in owners}
    batch_size = max(1, n_owners // len(revocation_timesteps))
    rev_map: dict[int, list[str]] = {}
    for idx, t in enumerate(revocation_timesteps):
        start = idx * batch_size
        end = start + batch_size if idx < len(revocation_timesteps) - 1 else n_owners
        for owner in owners[start:end]:
            rev_map.setdefault(t, []).append(owner)

    active = list(stream)
    forgotten: list[_Record] = []
    history = []
    for t in range(timesteps):
        if t in rev_map:
            for owner in rev_map[t]:
                consent[owner] = False
        still, new_f = [], []
        for rec in active:
            (still if consent.get(rec.consent_owner, True) else new_f).append(rec)
        active = still
        forgotten.extend(new_f)
        history.append({"timestep": t, "active": len(active), "forgotten": len(forgotten)})
    return history, len(active) / max(len(stream), 1)


def _sim_composite(
    stream: list[_Record],
    ttl: int,
    decay_rate: float,
    threshold: float,
    n_owners: int,
    revocation_timesteps: list[int],
    timesteps: int,
) -> tuple[list[dict[str, int]], float]:
    owners = [f"user_{i}" for i in range(n_owners)]
    consent: dict[str, bool] = {o: True for o in owners}
    batch_size = max(1, n_owners // len(revocation_timesteps))
    rev_map: dict[int, list[str]] = {}
    for idx, t in enumerate(revocation_timesteps):
        start = idx * batch_size
        end = start + batch_size if idx < len(revocation_timesteps) - 1 else n_owners
        for owner in owners[start:end]:
            rev_map.setdefault(t, []).append(owner)

    active = list(stream)
    forgotten: list[_Record] = []
    history = []
    for t in range(timesteps):
        if t in rev_map:
            for owner in rev_map[t]:
                consent[owner] = False
        still, new_f = [], []
        for rec in active:
            age = max(0, t - rec.created_at)
            time_ok = age < ttl
            decay_ok = rec.relevance_score * math.exp(-decay_rate * age) >= threshold
            consent_ok = consent.get(rec.consent_owner, True)
            (still if (time_ok and decay_ok and consent_ok) else new_f).append(rec)
        active = still
        forgotten.extend(new_f)
        history.append({"timestep": t, "active": len(active), "forgotten": len(forgotten)})
    return history, len(active) / max(len(stream), 1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Generate all four precomputed JSON files with seed=42."""
    seed = 42
    n = 500
    timesteps = 500
    categories = ["conversation", "preference", "fact", "event"]
    n_owners = 10
    birth_spread = 250  # timesteps // 2

    out_dir = os.path.dirname(os.path.abspath(__file__))

    stream = _generate_stream(n, seed, categories, n_owners, birth_spread)

    # Fig 1 — time-based
    h1, rr1 = _sim_time_based(stream, ttl=100, timesteps=timesteps)
    with open(os.path.join(out_dir, "fig1_data.json"), "w", encoding="utf-8") as f:
        json.dump({
            "_note": "SIMULATION ONLY — not production AMGP implementation. seed=42.",
            "scenario": "time_based_retention",
            "seed": seed,
            "ttl": 100,
            "n_memories": n,
            "timesteps": timesteps,
            "retention_rate": rr1,
            "history": h1,
        }, f, indent=2)
    print(f"fig1_data.json written (retention_rate={rr1:.4f})")

    # Fig 2 — relevance decay
    h2, rr2 = _sim_decay(stream, decay_rate=0.01, threshold=0.3, timesteps=timesteps)
    with open(os.path.join(out_dir, "fig2_data.json"), "w", encoding="utf-8") as f:
        json.dump({
            "_note": "SIMULATION ONLY — not production AMGP implementation. seed=42.",
            "scenario": "relevance_decay",
            "seed": seed,
            "decay_rate": 0.01,
            "threshold": 0.3,
            "n_memories": n,
            "timesteps": timesteps,
            "retention_rate": rr2,
            "history": h2,
        }, f, indent=2)
    print(f"fig2_data.json written (retention_rate={rr2:.4f})")

    # Fig 3 — consent revocation
    h3, rr3 = _sim_consent(
        stream, n_owners=n_owners,
        revocation_timesteps=[100, 200, 300],
        timesteps=timesteps,
    )
    with open(os.path.join(out_dir, "fig3_data.json"), "w", encoding="utf-8") as f:
        json.dump({
            "_note": "SIMULATION ONLY — not production AMGP implementation. seed=42.",
            "scenario": "consent_revocation",
            "seed": seed,
            "n_owners": n_owners,
            "revocation_timesteps": [100, 200, 300],
            "n_memories": n,
            "timesteps": timesteps,
            "retention_rate": rr3,
            "history": h3,
        }, f, indent=2)
    print(f"fig3_data.json written (retention_rate={rr3:.4f})")

    # Fig 4 — composite + baselines
    # Baselines use same stream but different params
    stream_t = _generate_stream(n, seed, categories, n_owners, birth_spread)
    stream_d = _generate_stream(n, seed, categories, n_owners, birth_spread)
    stream_c = _generate_stream(n, seed, categories, n_owners, birth_spread)

    h4t, rr4t = _sim_time_based(stream_t, ttl=200, timesteps=timesteps)
    h4d, rr4d = _sim_decay(stream_d, decay_rate=0.01, threshold=0.3, timesteps=timesteps)
    h4c, rr4c = _sim_composite(
        stream_c, ttl=200, decay_rate=0.01, threshold=0.3,
        n_owners=n_owners, revocation_timesteps=[150, 300], timesteps=timesteps,
    )
    with open(os.path.join(out_dir, "fig4_data.json"), "w", encoding="utf-8") as f:
        json.dump({
            "_note": "SIMULATION ONLY — not production AMGP implementation. seed=42.",
            "scenario": "composite_policy",
            "seed": seed,
            "n_memories": n,
            "timesteps": timesteps,
            "retention_rate_time": rr4t,
            "retention_rate_decay": rr4d,
            "retention_rate_composite": rr4c,
            "history_time": h4t,
            "history_decay": h4d,
            "history_composite": h4c,
        }, f, indent=2)
    print(f"fig4_data.json written (time={rr4t:.4f}, decay={rr4d:.4f}, composite={rr4c:.4f})")

    print("\nAll precomputed files written successfully.")
    print("SIMULATION ONLY — not production AMGP implementation.")


if __name__ == "__main__":
    main()
