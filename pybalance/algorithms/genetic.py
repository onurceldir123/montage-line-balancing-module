"""
Genetic algorithms for assembly line balancing.

This module implements genetic algorithm approaches for finding optimal
or near-optimal assembly line configurations.

The implementation is based on the method proposed by:
Çeldir, O.M., Utku, S. (2022). Montaj Hattı Dengelemede Genetik Algoritmaların
Kullanımı: Yeni Bir Yöntem. DEUFMD, 24(71), 365-373.
DOI: 10.21205/deufmd.2022247103
"""

from __future__ import annotations
from typing import List, Tuple, Set, TYPE_CHECKING, Optional
import copy
import random
import logging
import numpy as np
import networkx as nx

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..core.line import Line


def find_articulation_points(graph: nx.DiGraph) -> List[int]:
    """
    Find articulation points (cut vertices) in the precedence graph.

    Articulation points are nodes where the graph branches or
    where branched sections merge.

    Args:
        graph: Precedence graph

    Returns:
        List of articulation point node numbers
    """
    # Convert to undirected for articulation point detection
    undirected = graph.to_undirected()

    # Find articulation points (excluding dummy nodes 0 and -1)
    articulation_points = list(nx.articulation_points(undirected))

    # Filter out dummy nodes
    articulation_points = [node for node in articulation_points
                          if node not in [0, -1]]

    return sorted(articulation_points)


def find_regions(graph: nx.DiGraph, articulation_points: List[int]) -> List[Set[int]]:
    """
    Find regions between articulation points.

    Args:
        graph: Precedence graph
        articulation_points: List of articulation points

    Returns:
        List of regions, where each region is a set of node numbers
    """
    regions = []

    if len(articulation_points) < 2:
        # Not enough articulation points for regions
        all_nodes = set(graph.nodes()) - {0, -1}
        if all_nodes:
            regions.append(all_nodes)
        return regions

    # Find regions between consecutive articulation points
    for i in range(len(articulation_points) - 1):
        start = articulation_points[i]
        end = articulation_points[i + 1]

        # Get all nodes reachable from start
        reachable_from_start = set(nx.descendants(graph, start))

        # Get all nodes that can reach end
        can_reach_end = set(nx.ancestors(graph, end))

        # Region is intersection of these sets, plus the boundary points
        region = (reachable_from_start & can_reach_end) | {start, end}
        region = region - {0, -1}  # Remove dummy nodes

        if len(region) > 2:  # Must have nodes between boundaries
            regions.append(region)

    return regions


def precedence_preserving_crossover(
    parent1: List[int],
    parent2: List[int],
    line: 'Line'
) -> Tuple[List[int], List[int]]:
    """
    Perform precedence-preserving crossover using region-based method.

    Based on the method in Section 3.2.1 of the paper:
    - Find articulation points in precedence graph
    - Identify regions between articulation points
    - Select random region
    - Exchange tasks in that region while preserving order

    Args:
        parent1: First parent chromosome (task sequence)
        parent2: Second parent chromosome (task sequence)
        line: Line object containing precedence graph

    Returns:
        Tuple of two children chromosomes
    """
    # Find articulation points and regions
    articulation_points = find_articulation_points(line.graph)
    regions = find_regions(line.graph, articulation_points)

    if not regions:
        # No regions found, return copies of parents
        return parent1[:], parent2[:]

    # Select random region
    selected_region = random.choice(regions)

    # Extract genes from selected region for each parent
    p1_region_genes = [gene for gene in parent1 if gene in selected_region]
    p2_region_genes = [gene for gene in parent2 if gene in selected_region]

    # Find positions of region genes in each parent
    p1_positions = [i for i, gene in enumerate(parent1) if gene in selected_region]
    p2_positions = [i for i, gene in enumerate(parent2) if gene in selected_region]

    # Create children
    child1 = parent1[:]
    child2 = parent2[:]

    # Replace region genes while preserving order from other parent
    for i, pos in enumerate(p1_positions):
        if i < len(p2_region_genes):
            child1[pos] = p2_region_genes[i]

    for i, pos in enumerate(p2_positions):
        if i < len(p1_region_genes):
            child2[pos] = p1_region_genes[i]

    return child1, child2


def region_based_mutation(chromosome: List[int], line: 'Line') -> List[int]:
    """
    Perform region-based mutation.

    Based on the method in Section 3.2.2 of the paper:
    - Select random region
    - Select random gene (not articulation point)
    - Move gene within region boundaries
    - Shift other genes accordingly

    Args:
        chromosome: Task sequence to mutate
        line: Line object containing precedence graph

    Returns:
        Mutated chromosome
    """
    # Find articulation points and regions
    articulation_points = find_articulation_points(line.graph)
    regions = find_regions(line.graph, articulation_points)

    if not regions:
        # No regions, return copy
        return chromosome[:]

    # Select random region
    selected_region = random.choice(regions)

    # Find non-articulation genes in this region
    non_articulation = list(selected_region - set(articulation_points))

    if len(non_articulation) < 2:
        # Not enough genes to mutate
        return chromosome[:]

    # Select random gene to move
    gene_to_move = random.choice(non_articulation)

    # Find current position
    current_pos = chromosome.index(gene_to_move)

    # Find valid positions (within region boundaries)
    region_positions = [i for i, gene in enumerate(chromosome)
                       if gene in selected_region]

    if len(region_positions) < 2:
        return chromosome[:]

    # Select new position
    new_pos = random.choice(region_positions)

    if new_pos == current_pos:
        return chromosome[:]

    # Create mutated chromosome
    mutated = chromosome[:]
    mutated.pop(current_pos)
    mutated.insert(new_pos, gene_to_move)

    return mutated


def genetic_algorithms(
    line: Line,
    cycle_time: float,
    p_m: float = 0.05,
    p_c: float = 0.05,
    generation: int = 100,
    size: int = 100,
    local_search: str = 'genetics',
    out: int = 1,
    seed: Optional[int] = None
) -> List[List[List[int]]]:
    """
    Balance assembly line using genetic algorithms.

    Implementation based on:
    Çeldir, O.M., Utku, S. (2022). Montaj Hattı Dengelemede Genetik
    Algoritmaların Kullanımı: Yeni Bir Yöntem. DEUFMD, 24(71), 365-373.

    This method uses:
    - COMSOAL for initial population generation
    - Region-based precedence-preserving crossover
    - Region-based mutation
    - Tournament selection (3 warriors)
    - Elitism
    - Local search for station assignment optimization

    Args:
        line: Line object to balance
        cycle_time: Target cycle time
        p_m: Probability of mutation (default: 0.05 as in paper)
        p_c: Probability of crossover (default: 0.05 as in paper)
        generation: Number of generations (default: 100 as in paper)
        size: Population size (default: 100 as in paper)
        local_search: Local search method ('genetics', 'local', or 'heuristic')
        local_search: Local search method ('genetics', 'local', or 'heuristic')
        out: Number of solutions to return
        seed: Random seed for reproducibility

    Returns:
        List of best station configurations

    Example:
        >>> from pybalance import Line
        >>> tasks = [[1, [0], 2], [2, [1], 5], [3, [1], 4], [4, [2, 3], 3]]
        >>> line = Line(tasks)
        >>> solutions = genetic_algorithms(line, 23, p_m=0.05, p_c=0.05,
        ...                                generation=100, size=100)
        >>> best = solutions[0]
    """
    from .comsoal import comsoal_algorithm, heuristic_task_allocating
    from .local_search import local_search_procedure

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # Generate initial population using COMSOAL
    logger.info(f"Generating initial population (size={size})...")
    initial_sequences = []

    for _ in range(size):
        # Generate random feasible task sequence
        graph = copy.deepcopy(line.graph)
        task_sequence = []

        while True:
            successors = list(graph.successors(0))
            # Remove non-feasible
            feasible = [t for t in successors
                       if sum(list(graph.predecessors(t))) == 0 and t != -1]

            if not feasible:
                break

            # Random selection
            selected = random.choice(feasible)
            task_sequence.append(selected)

            # Update graph
            for succ in graph.successors(selected):
                graph.add_edge(0, succ)
            graph.remove_edges_from(list(graph.edges(selected)))
            if graph.has_edge(0, selected):
                graph.remove_edge(0, selected)

            if (len(list(graph.successors(0))) == 1 and
                list(graph.successors(0))[0] == -1):
                break

        initial_sequences.append(task_sequence)

    # Convert sequences to station lists
    population = []
    for sequence in initial_sequences:
        stations = heuristic_task_allocating(line, sequence, cycle_time)
        population.append(stations)

    best_solutions = []

    # Evolution loop
    for gen in range(generation):
        new_population = []

        # Generate new population (size/2 iterations)
        for _ in range(size // 2):
            # Tournament selection (3 warriors)
            warriors_idx = np.random.choice(len(population), size=3, replace=False)
            warriors = [population[i] for i in warriors_idx]

            # Evaluate warriors
            scores = [line.calculate_line_efficiency(w, cycle_time) for w in warriors]

            # Select top 2 as parents
            sorted_warriors = sorted(zip(warriors, scores), key=lambda x: x[1], reverse=True)
            parent1_stations = sorted_warriors[0][0]
            parent2_stations = sorted_warriors[1][0]

            # Convert station lists back to task sequences
            parent1_seq = [task for station in parent1_stations for task in station]
            parent2_seq = [task for station in parent2_stations for task in station]

            # Crossover
            if random.random() < p_c:
                child1_seq, child2_seq = precedence_preserving_crossover(
                    parent1_seq, parent2_seq, line
                )
            else:
                child1_seq, child2_seq = parent1_seq[:], parent2_seq[:]

            # Mutation
            if random.random() < p_m:
                child1_seq = region_based_mutation(child1_seq, line)
            if random.random() < p_m:
                child2_seq = region_based_mutation(child2_seq, line)

            # Convert back to station assignments
            child1_stations = heuristic_task_allocating(line, child1_seq, cycle_time)
            child2_stations = heuristic_task_allocating(line, child2_seq, cycle_time)

            # Apply local search if requested
            if local_search != 'heuristic':
                child1_improved = local_search_procedure(
                    line, child1_stations, cycle_time, local_search, out=1
                )
                child2_improved = local_search_procedure(
                    line, child2_stations, cycle_time, local_search, out=1
                )
                child1_stations = child1_improved[0] if child1_improved else child1_stations
                child2_stations = child2_improved[0] if child2_improved else child2_stations

            new_population.extend([child1_stations, child2_stations])

        # Elitism: keep best from old population
        all_solutions = population + new_population
        scored = [(sol, line.calculate_line_efficiency(sol, cycle_time))
                  for sol in all_solutions]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Select top 'size' solutions for next generation
        population = [sol for sol, _ in scored[:size]]

        # Track best solution
        best_solutions.append(scored[0][0])

        if (gen + 1) % 10 == 0:
            logger.info(f"Generation {gen + 1}/{generation}, "
                  f"Best efficiency: {scored[0][1]:.2f}%")

    # Return unique best solutions
    unique_solutions = []
    for solution in best_solutions:
        if solution not in unique_solutions:
            unique_solutions.append(solution)

    # Sort by efficiency and return top 'out'
    final_scored = [(sol, line.calculate_line_efficiency(sol, cycle_time))
                    for sol in unique_solutions]
    final_scored.sort(key=lambda x: x[1], reverse=True)

    return [sol for sol, _ in final_scored[:out]]
