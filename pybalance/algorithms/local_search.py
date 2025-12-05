"""
Local search procedures for improving assembly line solutions.

This module provides local search methods to improve initial solutions
by exploring neighboring configurations.
"""

from typing import List, TYPE_CHECKING
import copy
import random as rd
import numpy as np

if TYPE_CHECKING:
    from ..core.line import Line


def mutation_local(line: 'Line', station_list: List[List[int]], cycle_time: float) -> List[List[int]]:
    """
    Apply mutation operator to a station configuration.

    Moves the last task from a random station to the next station,
    then fixes any violations.

    Args:
        line: Line object
        station_list: Current station configuration
        cycle_time: Target cycle time

    Returns:
        Mutated station configuration
    """
    stations = copy.deepcopy(station_list)
    k = rd.randint(0, len(stations) - 1)

    # Move last task from station k to station k+1
    if len(stations[k]) > 1:
        if len(stations) == k + 1:
            stations.append([])
        stations[k + 1].insert(0, stations[k][-1])
        stations[k].pop()

    # Fix stations that exceed cycle time
    for i in range(k, len(stations)):
        is_fixed = False
        while not is_fixed:
            if line.get_station_time(stations[i]) > cycle_time:
                if len(stations) <= i + 1:
                    stations.append([])
                stations[i + 1].insert(0, stations[i][-1])
                stations[i].pop()
                if line.get_station_time(stations[i]) <= cycle_time:
                    is_fixed = True
            else:
                is_fixed = True

    return stations


def local_search_heuristic(
    line: 'Line',
    initial_list: List[List[int]],
    cycle_time: float,
    population: int = 30
) -> List[List[List[int]]]:
    """
    Local search using simple heuristic neighborhood exploration.

    Args:
        line: Line object
        initial_list: Initial station configuration
        cycle_time: Target cycle time
        population: Number of neighbors to generate

    Returns:
        List of unique station configurations
    """
    all_stations = [initial_list]

    for _ in range(population - 1):
        neighbor = mutation_local(line, initial_list, cycle_time)
        all_stations.append(neighbor)

    # Return unique solutions
    unique_solutions = []
    for solution in all_stations:
        if solution not in unique_solutions:
            unique_solutions.append(solution)

    return unique_solutions


def local_search_genetic(
    line: 'Line',
    initial_list: List[List[int]],
    cycle_time: float,
    population: int = 30,
    generations: int = 15,
    p_m: float = 0.7
) -> List[List[List[int]]]:
    """
    Local search using genetic algorithm approach.

    Args:
        line: Line object
        initial_list: Initial station configuration
        cycle_time: Target cycle time
        population: Population size
        generations: Number of generations
        p_m: Mutation probability

    Returns:
        List of unique best solutions from all generations
    """
    # Generate initial population
    current_population = [initial_list]

    for _ in range(population - 1):
        neighbor = mutation_local(line, initial_list, cycle_time)
        current_population.append(neighbor)

    best_solutions = []

    for gen in range(generations):
        generation_children = []
        generation_scores = []

        # Include initial solution
        initial_score = line.calculate_line_efficiency(initial_list)
        generation_children.append(initial_list)
        generation_scores.append(initial_score)

        # Evolve population
        for _ in range(population - 1):
            # Tournament selection (3 warriors)
            warriors_idx = np.random.choice(len(current_population), size=3, replace=False)
            warriors = [current_population[i] for i in warriors_idx]

            # Evaluate warriors
            scores = [line.calculate_line_efficiency(w) for w in warriors]

            # Select winner
            winner = warriors[np.argmax(scores)]

            # Apply mutation
            if np.random.rand() < p_m:
                child = mutation_local(line, winner, cycle_time)
            else:
                child = winner

            child_score = line.calculate_line_efficiency(child)
            generation_children.append(child)
            generation_scores.append(child_score)

        # Find best in generation
        best_idx = np.argmax(generation_scores)
        best_solutions.append(generation_children[best_idx])

        # Update population
        current_population = generation_children[:]

    # Return unique solutions
    unique_solutions = []
    for solution in best_solutions:
        if solution not in unique_solutions:
            unique_solutions.append(solution)

    return unique_solutions


def local_search_procedure(
    line: 'Line',
    initial_solution: List[List[int]],
    cycle_time: float,
    local_search: str = "local",
    out: int = 1
) -> List[List[List[int]]]:
    """
    Apply local search to improve an initial solution.

    Args:
        line: Line object
        initial_solution: Initial station configuration
        cycle_time: Target cycle time
        local_search: Search method
            - 'local': Simple neighborhood exploration
            - 'genetics': Genetic algorithm-based search
            - 'heuristic': Same as 'local'
        out: Number of solutions to return (not used, kept for compatibility)

    Returns:
        List of improved station configurations

    Example:
        >>> from pybalance import Line
        >>> tasks = [[1, [0], 2], [2, [1], 5], [3, [1], 4], [4, [2, 3], 3]]
        >>> line = Line(tasks)
        >>> initial = [[1, 3, 2, 6], [5, 4, 7], [8, 9]]
        >>> improved = local_search_procedure(line, initial, 12, 'local')
    """
    if local_search == "genetics":
        return local_search_genetic(line, initial_solution, cycle_time)
    else:  # 'local' or 'heuristic'
        return local_search_heuristic(line, initial_solution, cycle_time)
