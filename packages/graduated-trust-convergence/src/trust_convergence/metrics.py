# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
"""
Convergence and stability metrics for trust progression trajectories.

NOTE: All functions in this module operate on SYNTHETIC simulation data.
They are NOT production metrics and are not used to evaluate real agents.
"""
from __future__ import annotations

import numpy as np
import numpy.typing as npt


def convergence_rate(
    trajectory: npt.NDArray[np.float64],
    window: int = 50,
) -> float:
    """
    Compute the rate at which a trust trajectory stabilises.

    NOTE: This metric applies to SIMULATION trajectories only — NOT production data.

    The rate is estimated as the mean absolute difference between consecutive
    rolling-window means over the second half of the trajectory. A lower value
    indicates faster or more complete convergence.

    Formally, let ``M_t = mean(trajectory[t-w:t])`` for window size ``w``.
    The convergence rate is::

        rate = mean(|M_{t+1} - M_t|)   for t in [T/2, T-w-1]

    Parameters
    ----------
    trajectory:
        Array of shape ``(T,)`` with trust level values in ``[0, L-1]``.
    window:
        Rolling window size for smoothing. Must satisfy ``window < len(trajectory) / 2``.

    Returns
    -------
    float
        Non-negative convergence rate. Zero means perfectly stable in the window.

    Raises
    ------
    ValueError
        If ``trajectory`` is empty or ``window`` is larger than half the trajectory.

    Examples
    --------
    >>> import numpy as np
    >>> traj = np.linspace(0, 5, 1000)
    >>> rate = convergence_rate(traj)  # monotone increase — non-zero
    >>> rate > 0
    True
    """
    if len(trajectory) == 0:
        raise ValueError("trajectory must not be empty")
    half = len(trajectory) // 2
    if window >= half:
        raise ValueError(
            f"window ({window}) must be smaller than half the trajectory length ({half})"
        )

    smoothed: list[float] = []
    for t in range(half, len(trajectory) - window):
        smoothed.append(float(np.mean(trajectory[t : t + window])))

    if len(smoothed) < 2:
        return 0.0

    diffs = np.abs(np.diff(smoothed))
    return float(np.mean(diffs))


def stability_index(
    trajectory: npt.NDArray[np.float64],
    window: int = 100,
) -> float:
    """
    Measure variance in the tail of a trust trajectory.

    NOTE: This metric applies to SIMULATION trajectories only — NOT production data.

    The stability index is the standard deviation of the last ``window`` elements
    of the trajectory. Lower values indicate a more stable (converged) end state.
    A value of 0.0 means the trajectory has become perfectly constant.

    Parameters
    ----------
    trajectory:
        Array of shape ``(T,)`` with trust level values.
    window:
        Number of tail samples to use. If ``window >= len(trajectory)``,
        the entire trajectory is used.

    Returns
    -------
    float
        Non-negative standard deviation. Returns 0.0 for a single-element window.

    Raises
    ------
    ValueError
        If ``trajectory`` is empty.

    Examples
    --------
    >>> import numpy as np
    >>> traj = np.ones(200) * 3.5
    >>> stability_index(traj)
    0.0
    """
    if len(trajectory) == 0:
        raise ValueError("trajectory must not be empty")
    effective_window = min(window, len(trajectory))
    tail = trajectory[-effective_window:]
    return float(np.std(tail))


def convergence_bound(
    trajectory: npt.NDArray[np.float64],
    target_level: float,
    tolerance: float = 0.1,
) -> int | None:
    """
    Find the first timestep at which the trajectory stays within ``tolerance``
    of ``target_level`` for the remainder of the run.

    NOTE: Applies to SIMULATION data only — NOT production trust scores.

    Scans forward from timestep 0 and returns the earliest index ``t*`` such
    that ``|trajectory[t] - target_level| <= tolerance`` for all ``t >= t*``.

    Parameters
    ----------
    trajectory:
        Array of shape ``(T,)`` with trust level values.
    target_level:
        The trust level the trajectory should converge to.
    tolerance:
        Acceptable absolute deviation from ``target_level``. Default ``0.1``.

    Returns
    -------
    int or None
        The first timestep of sustained convergence, or ``None`` if the
        trajectory never converges within the run.

    Raises
    ------
    ValueError
        If ``trajectory`` is empty or ``tolerance`` is negative.

    Examples
    --------
    >>> import numpy as np
    >>> traj = np.concatenate([np.linspace(0, 5, 500), np.full(500, 5.0)])
    >>> cb = convergence_bound(traj, target_level=5.0, tolerance=0.05)
    >>> cb is not None and cb <= 500
    True
    """
    if len(trajectory) == 0:
        raise ValueError("trajectory must not be empty")
    if tolerance < 0:
        raise ValueError(f"tolerance must be non-negative, got {tolerance}")

    within_tolerance: npt.NDArray[np.bool_] = (
        np.abs(trajectory - target_level) <= tolerance
    )

    # Find the last timestep that is NOT within tolerance; the bound is one step after.
    violations = np.where(~within_tolerance)[0]
    if len(violations) == 0:
        # Already within tolerance from the very start
        return 0
    last_violation = int(violations[-1])
    if last_violation == len(trajectory) - 1:
        # The final timestep itself violates tolerance — never converges
        return None
    return last_violation + 1


def mean_trust_level(
    trajectory: npt.NDArray[np.float64],
    start: int = 0,
) -> float:
    """
    Compute the mean trust level from ``start`` to the end of the trajectory.

    NOTE: Applies to SIMULATION data only — NOT production trust levels.

    Parameters
    ----------
    trajectory:
        Array of shape ``(T,)`` with trust level values.
    start:
        Index of the first timestep to include. Default ``0`` uses the full run.
        Positive values can be used to compute the mean after a burn-in period.

    Returns
    -------
    float
        Arithmetic mean of ``trajectory[start:]``.

    Raises
    ------
    ValueError
        If ``trajectory`` is empty or ``start >= len(trajectory)``.

    Examples
    --------
    >>> import numpy as np
    >>> mean_trust_level(np.array([1.0, 2.0, 3.0, 4.0]))
    2.5
    >>> mean_trust_level(np.array([1.0, 2.0, 3.0, 4.0]), start=2)
    3.5
    """
    if len(trajectory) == 0:
        raise ValueError("trajectory must not be empty")
    if start >= len(trajectory):
        raise ValueError(
            f"start ({start}) must be less than trajectory length ({len(trajectory)})"
        )
    return float(np.mean(trajectory[start:]))


def area_under_trajectory(
    trajectory: npt.NDArray[np.float64],
    start: int = 0,
    end: int | None = None,
) -> float:
    """
    Compute the area under the trajectory curve using the trapezoidal rule.

    NOTE: Applies to SIMULATION data only — NOT production data.

    This is the discrete approximation of the integral of trust level over time,
    normalised by the number of intervals. It captures the cumulative trust
    accumulated over a time window, useful for comparing agent types.

    Parameters
    ----------
    trajectory:
        Array of shape ``(T,)`` with trust level values.
    start:
        Start index (inclusive). Default ``0``.
    end:
        End index (exclusive). Default ``None`` uses the full trajectory.

    Returns
    -------
    float
        Normalised area (mean of trapezoidal approximation over the interval).

    Raises
    ------
    ValueError
        If the selected slice has fewer than 2 elements.

    Examples
    --------
    >>> import numpy as np
    >>> area_under_trajectory(np.ones(100) * 3.0)
    3.0
    """
    slice_ = trajectory[start:end]
    if len(slice_) < 2:
        raise ValueError("Selected slice must have at least 2 elements for integration.")
    return float(np.trapz(slice_) / (len(slice_) - 1))


def time_to_first_peak(
    trajectory: npt.NDArray[np.float64],
) -> int | None:
    """
    Return the timestep of the first local maximum in the trajectory.

    NOTE: Applies to SIMULATION data only.

    A local maximum at index ``t`` satisfies
    ``trajectory[t] > trajectory[t-1]`` and ``trajectory[t] > trajectory[t+1]``.
    The endpoints are excluded.

    Parameters
    ----------
    trajectory:
        Array of shape ``(T,)`` with trust level values.

    Returns
    -------
    int or None
        Index of the first local maximum, or ``None`` if none exist.

    Examples
    --------
    >>> import numpy as np
    >>> traj = np.array([0.0, 1.0, 2.0, 1.5, 3.0, 2.5])
    >>> time_to_first_peak(traj)
    2
    """
    for t in range(1, len(trajectory) - 1):
        if trajectory[t] > trajectory[t - 1] and trajectory[t] > trajectory[t + 1]:
            return t
    return None
