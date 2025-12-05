"""
Heuristic algorithms for assembly line balancing.

This module implements heuristic methods including:
- Largest Candidate Rule (LCR)
- Helgeson-Birnie Method (HB)
"""

from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING
import copy
import logging
import networkx as nx

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..core.line import Line


def find_weighed_successor(line: Line, task_list: List[int]) -> List[Tuple[int, float]]:
    """
    Find candidates sorted by total weight (LCR method).

    Args:
        line: Line object
        task_list: List of candidate task numbers

    Returns:
        List of (task_number, weight) tuples sorted by weight descending
    """
    node_weights = {
        node: line.graph.nodes[node]['total_weight']
        for node in task_list
    }
    return sorted(node_weights.items(), key=lambda x: x[1], reverse=True)


def find_number_successor(line: Line, task_list: List[int]) -> List[Tuple[int, int]]:
    """
    Find candidates sorted by number of successors (Helgeson-Birnie method).

    Args:
        line: Line object
        task_list: List of candidate task numbers

    Returns:
        List of (task_number, successor_count) tuples sorted descending
    """
    node_successors = {
        node: len(list(nx.dfs_preorder_nodes(line.graph, source=node)))
        for node in task_list
    }
    return sorted(node_successors.items(), key=lambda x: x[1], reverse=True)


def heuristic_method(line: Line, cycle_time: float, method: str = 'lcr') -> List[List[int]]:
    """
    Balance assembly line using heuristic methods.

    Args:
        line: Line object to balance
        cycle_time: Target cycle time for each station
        method: Heuristic method to use
            - 'lcr': Largest Candidate Rule (default)
            - 'hb': Helgeson-Birnie method

    Returns:
        List of stations, where each station is a list of task numbers

    Example:
        >>> from pybalance import Line
        >>> tasks = [[1, [0], 2], [2, [1], 5], [3, [1], 4], [4, [2, 3], 3]]
        >>> line = Line(tasks)
        >>> stations = heuristic_method(line, 12, 'lcr')
        >>> print(stations)
        [[1, 2, 3, 6], [4, 5, 7], [8, 9]]
    """
    graph = copy.deepcopy(line.graph)
    station_list = []
    current_station = []
    is_finished = False

    while not is_finished:
        # Get feasible successors of node 0 (start node)
        successors = list(graph.successors(0))

        # Remove non-feasible tasks (those with unfulfilled predecessors)
        feasible_tasks = [
            task for task in successors
            if sum(list(graph.predecessors(task))) == 0 and task != -1
        ]

        # Select sorting method
        if method == 'lcr':
            candidate_list = find_weighed_successor(line, feasible_tasks)
        else:  # method == 'hb'
            candidate_list = find_number_successor(line, feasible_tasks)

        task_added = False

        # Try to add tasks to current station
        for task_num, _ in candidate_list:
            task_time = graph.nodes[task_num]['time']

            if line.get_station_time(current_station) + task_time <= cycle_time:
                # Add task to current station
                task_added = True
                current_station.append(task_num)

                # Update graph: connect start node to successors of added task
                for successor in list(graph.successors(task_num)):
                    graph.add_edge(0, successor)

                # Remove added task from graph
                graph.remove_edges_from(list(graph.edges(task_num)))
                graph.remove_edge(0, task_num)
                break

        # If no task could be added, start new station
        if not task_added:
            if current_station:
                station_list.append(current_station)

            current_station = [candidate_list[0][0]]

            # Update graph for the first task in new station
            for successor in list(graph.successors(candidate_list[0][0])):
                graph.add_edge(0, successor)

            graph.remove_edges_from(list(graph.edges(candidate_list[0][0])))
            graph.remove_edge(0, candidate_list[0][0])

        # Check if finished
        if graph.number_of_edges() == 1:
            is_finished = True
            station_list.append(current_station)

    return station_list
