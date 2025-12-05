"""
U-shaped assembly line balancing algorithms.

This module provides algorithms for balancing U-shaped assembly lines,
where tasks can be assigned to either the front or back side of the line.
"""

from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING
import copy
import random
import logging
import networkx as nx

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..core.line import Line


def find_reversed_candidate_list(
    line: Line,
    back_tasks: List[int],
    front_tasks: List[int],
    graph: nx.DiGraph
) -> List[Tuple[int, float]]:
    """
    Find candidates for U-shaped line, considering both front and back.

    Args:
        line: Line object
        back_tasks: Tasks that can be assigned to back side
        front_tasks: Tasks that can be assigned to front side
        graph: Current graph with reversed weights

    Returns:
        Sorted list of (task, weight) tuples
    """
    node_weights = {}

    for task in back_tasks:
        node_weights[task] = graph.nodes[task]['reversed_total_weight']

    for task in front_tasks:
        node_weights[task] = graph.nodes[task]['total_weight']

    return sorted(node_weights.items(), key=lambda x: x[1], reverse=True)


def u_type_balance(
    line: Line,
    cycle_time: float,
    method: str = 'lcr',
    iteration: int = 100,
    out: int = 1
) -> Tuple[List[List[int]], List[str]]:
    """
    Balance U-shaped assembly line.

    In U-shaped lines, tasks can be assigned to either the front or back
    side of the line, providing more flexibility in balancing.

    Args:
        line: Line object to balance
        cycle_time: Target cycle time
        method: Balancing method
            - 'lcr': Largest Candidate Rule (default)
            - 'hb': Helgeson-Birnie
            - 'comsoal': COMSOAL algorithm
        iteration: Number of iterations (only for COMSOAL)
        out: Number of solutions to return (only for COMSOAL)

    Returns:
        Tuple of (station_list, task_sides) where:
        - station_list: List of stations with assigned tasks
        - task_sides: List indicating side for each task
          ('F' = Front, 'B' = Back, 'F-B' = Either)

    Example:
        >>> from pybalance import Line
        >>> tasks = [[1, [0], 2], [2, [1], 5], [3, [1], 4], [4, [2, 3], 3]]
        >>> line = Line(tasks)
        >>> stations, sides = u_type_balance(line, 12, 'lcr')
        >>> print(stations)
        [[1, 9, 8, 2], [7, 3, 4], [5, 6]]
        >>> print(sides)
        ['F', 'B', 'B', 'F', 'B', 'F', 'F-B', 'F-B', 'F-B']
    """
    if method == 'comsoal':
        # Use COMSOAL for U-type
        return u_type_comsoal(line, cycle_time, iteration, out)

    # Initialize graph with reversed weights
    graph = copy.deepcopy(line.graph)
    graph = line._create_graph_for_ushape(line.task_list, graph)

    station_list = []
    current_station = []
    task_sides = []
    is_finished = False
    first = True

    while not is_finished:
        # Get feasible tasks from front (successors of start)
        front_successors = list(graph.successors(0))
        # Get feasible tasks from back (predecessors of end)
        back_predecessors = list(graph.predecessors(-1))

        # Remove non-feasible tasks
        front_feasible = [
            task for task in front_successors
            if sum(list(graph.predecessors(task))) == 0
        ]
        back_feasible = [
            task for task in back_predecessors
            if sum(list(graph.successors(task))) == 0
        ]

        # Get sorted candidate list
        candidate_list = find_reversed_candidate_list(
            line, back_feasible, front_feasible, graph
        )

        # Special handling for first task (prefer back to front)
        if first and len(candidate_list) > 1:
            candidate_list[0], candidate_list[-1] = candidate_list[-1], candidate_list[0]
            first = False

        task_added = False

        # Try to add tasks to current station
        for task_num, _ in candidate_list:
            task_time = graph.nodes[task_num]['time']

            if line.get_station_time(current_station) + task_time <= cycle_time:
                current_station.append(task_num)

                # Determine which side this task is on
                if task_num in front_feasible and task_num in back_feasible:
                    task_sides.append('F-B')
                    task_added = True
                    # Remove from front
                    for successor in list(graph.successors(task_num)):
                        graph.add_edge(0, successor)
                    graph.remove_edges_from(list(graph.edges(task_num)))
                    graph.remove_edge(0, task_num)
                    break
                elif task_num in back_feasible:
                    task_sides.append('B')
                    task_added = True
                    # Remove from back
                    for predecessor in list(graph.predecessors(task_num)):
                        graph.add_edge(predecessor, -1)
                        graph.remove_edge(predecessor, task_num)
                    graph.remove_edge(task_num, -1)
                    break
                else:  # in front_feasible
                    task_sides.append('F')
                    task_added = True
                    # Remove from front
                    for successor in list(graph.successors(task_num)):
                        graph.add_edge(0, successor)
                    graph.remove_edges_from(list(graph.edges(task_num)))
                    graph.remove_edge(0, task_num)
                    break

        # If no task could be added, start new station
        if not task_added:
            if current_station:
                station_list.append(current_station)
            current_station = []

            # Add first candidate to new station
            task_num = candidate_list[0][0]
            current_station.append(task_num)

            if task_num in front_feasible and task_num in back_feasible:
                task_sides.append('F-B')
                for successor in list(graph.successors(task_num)):
                    graph.add_edge(0, successor)
                graph.remove_edges_from(list(graph.edges(task_num)))
                graph.remove_edge(0, task_num)
            elif task_num in back_feasible:
                task_sides.append('B')
                for predecessor in list(graph.predecessors(task_num)):
                    graph.add_edge(predecessor, -1)
                    graph.remove_edge(predecessor, task_num)
                graph.remove_edge(task_num, -1)
            else:  # in front_feasible
                task_sides.append('F')
                for successor in list(graph.successors(task_num)):
                    graph.add_edge(0, successor)
                graph.remove_edges_from(list(graph.edges(task_num)))
                graph.remove_edge(0, task_num)

        # Check if finished
        if (len(list(graph.successors(0))) == 1 and
            list(graph.successors(0))[0] == -1):
            is_finished = True
            if current_station:
                station_list.append(current_station)

    return station_list, task_sides


def u_type_comsoal(
    line: Line,
    cycle_time: float,
    iteration: int = 100,
    out: int = 1
) -> Tuple[List[List[int]], List[str]]:
    """
    Balance U-shaped line using COMSOAL algorithm.
    
    Args:
        line: Line object
        cycle_time: Target cycle time
        iteration: Number of iterations
        out: Number of solutions to return
        
    Returns:
        Tuple of (station_list, task_sides) for the best solution
    """
    best_solution = None
    best_efficiency = -1.0
    best_sides = []
    
    logger.info(f"Running U-Type COMSOAL with {iteration} iterations...")
    
    for _ in range(iteration):
        # Initialize graph with reversed weights
        graph = copy.deepcopy(line.graph)
        graph = line._create_graph_for_ushape(line.task_list, graph)

        station_list = []
        current_station = []
        task_sides = []
        is_finished = False
        
        while not is_finished:
            # Get feasible tasks
            front_successors = list(graph.successors(0))
            back_predecessors = list(graph.predecessors(-1))

            front_feasible = [
                task for task in front_successors
                if sum(list(graph.predecessors(task))) == 0
            ]
            back_feasible = [
                task for task in back_predecessors
                if sum(list(graph.successors(task))) == 0
            ]
            
            # Combine all feasible tasks
            all_feasible = list(set(front_feasible + back_feasible))
            
            if not all_feasible:
                break
                
            # Randomly select a task (COMSOAL logic)
            selected_task = random.choice(all_feasible)
            
            task_time = graph.nodes[selected_task]['time']
            
            # Try to add to current station
            if line.get_station_time(current_station) + task_time <= cycle_time:
                current_station.append(selected_task)
            else:
                if current_station:
                    station_list.append(current_station)
                current_station = [selected_task]
                
            # Determine side and update graph
            if selected_task in front_feasible and selected_task in back_feasible:
                # Randomly choose side if available on both
                side = random.choice(['F', 'B'])
                task_sides.append('F-B') # But we record it as F-B flexibility
                
                if side == 'F':
                     # Remove from front
                    for successor in list(graph.successors(selected_task)):
                        graph.add_edge(0, successor)
                    graph.remove_edges_from(list(graph.edges(selected_task)))
                    graph.remove_edge(0, selected_task)
                else:
                    # Remove from back
                    for predecessor in list(graph.predecessors(selected_task)):
                        graph.add_edge(predecessor, -1)
                        graph.remove_edge(predecessor, selected_task)
                    graph.remove_edge(selected_task, -1)
                    
            elif selected_task in back_feasible:
                task_sides.append('B')
                # Remove from back
                for predecessor in list(graph.predecessors(selected_task)):
                    graph.add_edge(predecessor, -1)
                    graph.remove_edge(predecessor, selected_task)
                graph.remove_edge(selected_task, -1)
            else: # in front_feasible
                task_sides.append('F')
                # Remove from front
                for successor in list(graph.successors(selected_task)):
                    graph.add_edge(0, successor)
                graph.remove_edges_from(list(graph.edges(selected_task)))
                graph.remove_edge(0, selected_task)
            
            # Check if finished
            if (len(list(graph.successors(0))) == 1 and
                list(graph.successors(0))[0] == -1):
                is_finished = True
                if current_station:
                    station_list.append(current_station)
        
        # Evaluate solution
        efficiency = line.calculate_line_efficiency(station_list, cycle_time)
        
        if efficiency > best_efficiency:
            best_efficiency = efficiency
            best_solution = station_list
            best_sides = task_sides
            
    return best_solution, best_sides
