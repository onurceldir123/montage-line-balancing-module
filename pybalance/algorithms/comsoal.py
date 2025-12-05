"""
COMSOAL (Computer Method of Sequencing Operations for Assembly Lines) algorithm.

This module implements the COMSOAL algorithm, a probabilistic method that
generates random feasible task sequences and assigns them to stations.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
import copy
import random as rd
import logging
import networkx as nx

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..core.line import Line


def remove_non_feasibles(task_list: List[int], graph: nx.DiGraph) -> List[int]:
    """
    Remove tasks that are not feasible (have unfulfilled predecessors).

    Args:
        task_list: List of candidate tasks
        graph: Current state of precedence graph

    Returns:
        List of feasible tasks only
    """
    feasible = []
    for task in task_list:
        if sum(list(graph.predecessors(task))) == 0:
            feasible.append(task)
    return feasible


def heuristic_task_allocating(
    line: Line,
    task_sequence: List[int],
    cycle_time: float
) -> List[List[int]]:
    """
    Allocate tasks to stations based on a given sequence.

    Uses a simple heuristic: add tasks to current station until
    cycle time would be exceeded, then start new station.

    Args:
        line: Line object
        task_sequence: Ordered sequence of tasks
        cycle_time: Target cycle time

    Returns:
        List of stations with assigned tasks
    """
    station_list = []
    current_station = []

    for task in task_sequence:
        task_time = line.input_dictionary[task]

        if line.get_station_time(current_station) + task_time <= cycle_time:
            current_station.append(task)
        else:
            station_list.append(current_station)
            current_station = [task]

    if current_station:
        station_list.append(current_station)

    return station_list


def comsoal_algorithm(
    line: Line,
    cycle_time: Optional[float] = None,
    iteration: int = 100,
    local_search: str = 'heuristic',
    out: int = 1
) -> List[List[List[int]]]:
    """
    Balance assembly line using COMSOAL algorithm.

    COMSOAL generates random feasible task sequences by randomly selecting
    from available tasks at each step, then allocates them to stations.

    Args:
        line: Line object to balance
        cycle_time: Target cycle time (auto-calculated if None)
        iteration: Number of random sequences to generate
        local_search: Post-processing method
            - 'heuristic': No post-processing
            - 'local': Apply local search to each solution
            - 'genetics': Apply genetic local search
        out: Number of solutions to return (not used, returns all unique)

    Returns:
        List of unique station configurations

    Example:
        >>> from pybalance import Line
        >>> tasks = [[1, [0], 2], [2, [1], 5], [3, [1], 4], [4, [2, 3], 3]]
        >>> line = Line(tasks)
        >>> solutions = comsoal_algorithm(line, 12, iteration=250)
        >>> best = solutions[0]  # Solutions are typically sorted by quality
    """
    # Auto-calculate cycle time if not provided
    if cycle_time is None:
        total_time = sum(task[2] for task in line.task_list)
        # Estimate minimum stations (ceiling of total_time / max_task_time)
        max_task_time = max(task[2] for task in line.task_list)
        estimated_stations = max(2, int(total_time / max_task_time))
        cycle_time = total_time / estimated_stations

    generation_list = []

    for _ in range(iteration):
        graph = copy.deepcopy(line.graph)
        task_sequence = []
        is_finished = False

        # Generate random feasible sequence
        while not is_finished:
            successors = list(graph.successors(0))
            feasible_tasks = remove_non_feasibles(successors, graph)

            # Randomly select a feasible task
            selected_task = rd.choice(feasible_tasks)
            task_sequence.append(selected_task)

            # Update graph
            for successor in list(graph.successors(selected_task)):
                graph.add_edge(0, successor)

            graph.remove_edges_from(list(graph.edges(selected_task)))
            graph.remove_edge(0, selected_task)

            # Check if finished
            if (len(list(graph.successors(0))) == 1 and
                list(graph.successors(0))[0] == -1):
                is_finished = True

        # Allocate tasks to stations
        station_list = heuristic_task_allocating(line, task_sequence, cycle_time)

        # Apply local search if requested
        if local_search != 'heuristic':
            from .local_search import local_search_procedure
            improved_solutions = local_search_procedure(
                line, station_list, cycle_time, local_search
            )
            generation_list.extend(improved_solutions)
        else:
            generation_list.append(station_list)

    # Return unique solutions
    unique_solutions = []
    for solution in generation_list:
        if solution not in unique_solutions:
            unique_solutions.append(solution)

    return unique_solutions
