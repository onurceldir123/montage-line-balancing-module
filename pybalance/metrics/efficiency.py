"""
Efficiency metrics for assembly line balancing.

This module provides functions to calculate various performance metrics
for assembly lines, including smoothness index, line efficiency, and balance loss.
"""

from typing import List, Dict
import numpy as np


def get_station_time(station: List[int], task_times: Dict[int, float]) -> float:
    """
    Calculate total time for a station.

    Args:
        station: List of task numbers in the station
        task_times: Dictionary mapping task numbers to their durations

    Returns:
        Total time required for all tasks in the station
    """
    return sum(task_times.get(task_num, 0) for task_num in station)


def calculate_smooth_index(
    station_list: List[List[int]],
    task_times: Dict[int, float],
    cycle_time: float = 0
) -> float:
    """
    Calculate the smoothness index of an assembly line.

    The smoothness index measures how balanced the line is. Lower values
    indicate better balance.

    Args:
        station_list: List of stations, where each station is a list of task numbers
        task_times: Dictionary mapping task numbers to their durations
        cycle_time: Target cycle time. If 0, uses the maximum station time

    Returns:
        Smoothness index value

    Example:
        >>> task_times = {1: 2, 2: 5, 3: 4, 4: 3}
        >>> stations = [[1, 3], [2], [4]]
        >>> calculate_smooth_index(stations, task_times, 6)
        1.0
    """
    # Calculate station times
    station_times = [get_station_time(station, task_times) for station in station_list]

    if cycle_time == 0:
        cycle_time = max(station_times)

    # Calculate smoothness index
    s = sum((max(station_times) - st) ** 2 for st in station_times)
    smooth_index = np.sqrt(s)

    return smooth_index


def calculate_line_efficiency(
    station_list: List[List[int]],
    task_times: Dict[int, float],
    cycle_time: float = 0
) -> float:
    """
    Calculate the line efficiency percentage.

    Line efficiency represents how effectively the available time is utilized
    across all stations.

    Args:
        station_list: List of stations, where each station is a list of task numbers
        task_times: Dictionary mapping task numbers to their durations
        cycle_time: Target cycle time. If 0, uses the maximum station time

    Returns:
        Line efficiency as a percentage (0-100)

    Example:
        >>> task_times = {1: 2, 2: 5, 3: 4, 4: 3}
        >>> stations = [[1, 3], [2], [4]]
        >>> calculate_line_efficiency(stations, task_times, 6)
        85.04
    """
    # Calculate station times
    station_times = [get_station_time(station, task_times) for station in station_list]

    if cycle_time == 0:
        cycle_time = max(station_times)

    # Calculate smoothness index
    smooth_index = calculate_smooth_index(station_list, task_times, cycle_time)

    # Calculate line efficiency
    line_efficiency = 100 - ((100 * smooth_index) / (len(station_times) * cycle_time))

    return line_efficiency


def calculate_loss_balance(
    station_list: List[List[int]],
    task_times: Dict[int, float],
    cycle_time: float = 0
) -> float:
    """
    Calculate the balance delay (loss of balance) percentage.

    Balance delay represents the percentage of idle time in the assembly line.
    It is complementary to line efficiency.

    Args:
        station_list: List of stations, where each station is a list of task numbers
        task_times: Dictionary mapping task numbers to their durations
        cycle_time: Target cycle time. If 0, uses the maximum station time

    Returns:
        Balance delay as a percentage (0-100)

    Example:
        >>> task_times = {1: 2, 2: 5, 3: 4, 4: 3}
        >>> stations = [[1, 3], [2], [4]]
        >>> calculate_loss_balance(stations, task_times, 6)
        14.96
    """
    loss_balance = 100 - calculate_line_efficiency(station_list, task_times, cycle_time)
    return loss_balance


def total_work_time(station_list: List[List[int]], task_times: Dict[int, float]) -> float:
    """
    Calculate total work time across all stations.

    Args:
        station_list: List of stations, where each station is a list of task numbers
        task_times: Dictionary mapping task numbers to their durations

    Returns:
        Total work time for all tasks in all stations
    """
    return sum(get_station_time(station, task_times) for station in station_list)
