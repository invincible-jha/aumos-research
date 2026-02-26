# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
metrics.py — Trust metrics for delegation chain analysis.

SIMULATION ONLY. This module provides arithmetic metrics over synthetic
delegation graph data produced by DelegationTrustModel. No production
trust-scoring algorithms, behavioral analysis, or adaptive logic is
implemented here. All inputs are SYNTHETIC.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from delegation_trust.model import DelegationEdge, DelegationTrustModel


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TransitivityScore:
    """Result of evaluating transitivity across all reachable agent pairs.

    SIMULATION ONLY. Measures how well the delegation graph preserves the
    multiplicative composition property across multi-hop paths.

    Attributes:
        mean_trust: Mean effective trust across all reachable agent pairs.
        std_trust: Standard deviation of effective trust across pairs.
        min_trust: Minimum effective trust observed.
        max_trust: Maximum effective trust observed.
        reachable_pairs: Number of agent pairs with a valid delegation path.
        total_pairs: Total number of ordered agent pairs evaluated.
    """

    mean_trust: float
    std_trust: float
    min_trust: float
    max_trust: float
    reachable_pairs: int
    total_pairs: int


@dataclass(frozen=True)
class DecayProfile:
    """Trust decay profile as a function of hop count.

    SIMULATION ONLY. Captures how effective trust decreases as path length
    increases across synthetic delegation chains.

    Attributes:
        hop_counts: List of hop counts evaluated.
        mean_trust_per_hop: Mean effective trust at each hop count.
        theoretical_decay: Expected trust under uniform multiplicative decay.
        mean_edge_trust: Mean pairwise trust across all edges in the graph.
    """

    hop_counts: list[int]
    mean_trust_per_hop: list[float]
    theoretical_decay: list[float]
    mean_edge_trust: float


@dataclass(frozen=True)
class DepthAnalysis:
    """Analysis of delegation chain depth and its trust implications.

    SIMULATION ONLY. Reports path lengths and terminal trusts for a set of
    source-target pairs in the delegation graph.

    Attributes:
        source: Source agent identifier used for analysis.
        targets_by_depth: Dict mapping depth (hop count) to list of
            (target_agent_id, effective_trust) tuples at that depth.
        max_depth: Maximum delegation chain depth found from source.
        agents_unreachable: Number of registered agents with no path from source.
    """

    source: str
    targets_by_depth: dict[int, list[tuple[str, float]]]
    max_depth: int
    agents_unreachable: int


@dataclass(frozen=True)
class PathReliability:
    """Reliability metrics for a specific delegation path.

    SIMULATION ONLY. Quantifies how reliable a delegation chain is by
    examining edge trust levels, minimum trust (weakest link), and entropy.

    Attributes:
        path: Ordered list of agent identifiers.
        edge_trusts: Pairwise trust levels along each hop.
        terminal_trust: Product of all edge trusts (multiplicative decay).
        min_hop_trust: Weakest single hop trust level on the path.
        trust_entropy: Shannon entropy of edge trust distribution (nats).
    """

    path: list[str]
    edge_trusts: list[float]
    terminal_trust: float
    min_hop_trust: float
    trust_entropy: float


# ---------------------------------------------------------------------------
# Metric functions
# ---------------------------------------------------------------------------


def transitivity_score(model: DelegationTrustModel) -> TransitivityScore:
    """Compute transitive trust statistics across all reachable agent pairs.

    SIMULATION ONLY. Evaluates effective transitive trust for every ordered
    pair of distinct registered agents and returns aggregate statistics.
    All data is SYNTHETIC.

    Args:
        model: A DelegationTrustModel with agents and edges registered.

    Returns:
        TransitivityScore with mean, std, min, max trust and reachability counts.
    """
    agent_ids = list(model._agents.keys())
    total_pairs = len(agent_ids) * (len(agent_ids) - 1)
    trust_values: list[float] = []

    for source in agent_ids:
        for target in agent_ids:
            if source == target:
                continue
            trust = model.compute_transitive_trust(source, target)
            if trust > 0.0:
                trust_values.append(trust)

    reachable = len(trust_values)
    if not trust_values:
        return TransitivityScore(
            mean_trust=0.0,
            std_trust=0.0,
            min_trust=0.0,
            max_trust=0.0,
            reachable_pairs=0,
            total_pairs=total_pairs,
        )

    arr = np.array(trust_values, dtype=float)
    return TransitivityScore(
        mean_trust=float(arr.mean()),
        std_trust=float(arr.std()),
        min_trust=float(arr.min()),
        max_trust=float(arr.max()),
        reachable_pairs=reachable,
        total_pairs=total_pairs,
    )


def decay_over_hops(
    edges: list[DelegationEdge],
    max_hops: int = 8,
) -> DecayProfile:
    """Compute theoretical and sampled trust decay profiles by hop count.

    SIMULATION ONLY. Given a flat list of delegation edges, computes the mean
    pairwise trust level across all edges, then derives:
      - The theoretical decay curve: mean_trust^hop_count
      - Placeholder for empirical per-hop mean trust (uses theoretical here)

    This is a simplified analytical model — NOT a production computation.

    Args:
        edges: List of DelegationEdge instances to analyse.
        max_hops: Maximum chain length to compute the profile for.

    Returns:
        DecayProfile with hop-indexed trust values.
    """
    if not edges:
        return DecayProfile(
            hop_counts=list(range(1, max_hops + 1)),
            mean_trust_per_hop=[0.0] * max_hops,
            theoretical_decay=[0.0] * max_hops,
            mean_edge_trust=0.0,
        )

    all_trusts = np.array([e.trust_level for e in edges], dtype=float)
    mean_edge = float(all_trusts.mean())

    hop_counts = list(range(1, max_hops + 1))
    theoretical = [float(mean_edge**hop) for hop in hop_counts]

    return DecayProfile(
        hop_counts=hop_counts,
        mean_trust_per_hop=theoretical,  # Simplified: uses theoretical as proxy
        theoretical_decay=theoretical,
        mean_edge_trust=mean_edge,
    )


def delegation_depth_analysis(
    model: DelegationTrustModel,
    source: str,
) -> DepthAnalysis:
    """Analyse delegation depth and effective trust from a given source agent.

    SIMULATION ONLY. Computes BFS levels from the source and records effective
    transitive trust at each depth level. All data is SYNTHETIC.

    Args:
        model: A DelegationTrustModel with agents and edges registered.
        source: The source agent identifier to start depth analysis from.

    Returns:
        DepthAnalysis grouping agents by their BFS depth from source.

    Raises:
        KeyError: If source is not registered in the model.
    """
    if source not in model._agents and source not in model._graph:
        raise KeyError(f"Source agent '{source}' not found in model")

    # BFS to find depth of each agent from source
    from collections import deque

    depth_map: dict[str, int] = {source: 0}
    queue: deque[str] = deque([source])

    while queue:
        current = queue.popleft()
        current_depth = depth_map[current]
        for neighbor, _edge in model._graph.get(current, []):
            if neighbor not in depth_map:
                depth_map[neighbor] = current_depth + 1
                queue.append(neighbor)

    targets_by_depth: dict[int, list[tuple[str, float]]] = {}
    agents_unreachable = 0

    for agent_id in model._agents:
        if agent_id == source:
            continue
        if agent_id in depth_map:
            depth = depth_map[agent_id]
            trust = model.compute_transitive_trust(source, agent_id)
            if depth not in targets_by_depth:
                targets_by_depth[depth] = []
            targets_by_depth[depth].append((agent_id, trust))
        else:
            agents_unreachable += 1

    max_depth = max(targets_by_depth.keys()) if targets_by_depth else 0

    return DepthAnalysis(
        source=source,
        targets_by_depth=targets_by_depth,
        max_depth=max_depth,
        agents_unreachable=agents_unreachable,
    )


def path_reliability(
    model: DelegationTrustModel,
    source: str,
    target: str,
) -> PathReliability:
    """Compute reliability metrics for the delegation path from source to target.

    SIMULATION ONLY. Retrieves the BFS-shortest delegation path and computes
    per-hop edge trusts, terminal trust, minimum hop trust (weakest link),
    and the Shannon entropy of the edge trust distribution. All data is SYNTHETIC.

    Args:
        model: A DelegationTrustModel with agents and edges registered.
        source: Source agent identifier.
        target: Target agent identifier.

    Returns:
        PathReliability with path details and trust reliability metrics.
        Returns a zero-trust PathReliability when no path exists.
    """
    found_path = model._find_shortest_path(source, target)

    if found_path is None:
        return PathReliability(
            path=[],
            edge_trusts=[],
            terminal_trust=0.0,
            min_hop_trust=0.0,
            trust_entropy=0.0,
        )

    edge_trusts = [
        model._get_edge_trust(found_path[index], found_path[index + 1])
        for index in range(len(found_path) - 1)
    ]

    terminal = float(np.prod(edge_trusts)) if edge_trusts else 1.0
    min_hop = min(edge_trusts) if edge_trusts else 1.0

    # Shannon entropy of edge trust values treated as a probability vector
    # Normalise to sum-to-one for entropy computation
    if edge_trusts:
        trust_array = np.array(edge_trusts, dtype=float)
        total = trust_array.sum()
        if total > 0:
            probs = trust_array / total
            entropy = float(-np.sum(probs * np.log(probs + 1e-12)))
        else:
            entropy = 0.0
    else:
        entropy = 0.0

    return PathReliability(
        path=found_path,
        edge_trusts=edge_trusts,
        terminal_trust=terminal,
        min_hop_trust=min_hop,
        trust_entropy=entropy,
    )
