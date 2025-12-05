"""
Core Line class for assembly line balancing.

This module contains the main Line class that represents an assembly line
and provides methods for balancing using various algorithms.
"""

from typing import List, Tuple, Dict, Optional
import copy
import networkx as nx

from ..metrics.efficiency import (
    get_station_time,
    calculate_smooth_index,
    calculate_line_efficiency,
    calculate_loss_balance,
    total_work_time
)


class Line:
    """
    Assembly line representation and balancing class.

    This class represents an assembly line with tasks and their precedence
    relationships, and provides methods for line balancing using various algorithms.

    Attributes:
        task_list: List of tasks in format [[task_num, [predecessors], duration], ...]
        graph: NetworkX directed graph representing task precedence relationships
        input_dictionary: Dictionary mapping task numbers to their durations

    Example:
        >>> tasks = [
        ...     [1, [0], 2],
        ...     [2, [1], 5],
        ...     [3, [1], 4],
        ...     [4, [2, 3], 3]
        ... ]
        >>> line = Line(tasks)
        >>> stations = line.balance(6)  # Balance with cycle time of 6
        >>> print(stations)
        [[1, 3], [2], [4]]
    """

    def __init__(self, task_list: List[List]):
        """
        Initialize the Line object.

        Args:
            task_list: List of tasks where each task is [task_number, [predecessors], duration]
        """
        self.task_list = task_list
        self.graph = self._draw_graph(task_list)
        self.input_dictionary = self._create_input_dict(task_list)

    def _draw_graph(self, task_list: List[List]) -> nx.DiGraph:
        """
        Create a directed graph from task list.

        Args:
            task_list: List of tasks

        Returns:
            NetworkX DiGraph representing task precedence relationships
        """
        graph = nx.DiGraph()

        # Add dummy start and end nodes
        graph.add_node(-1, time=0)
        graph.add_node(0, time=0)

        # Add tasks and their edges
        for task in task_list:
            task_num, predecessors, duration = task[0], task[1], task[2]
            graph.add_node(task_num, time=duration)

            if not predecessors:
                graph.add_edge(0, task_num)
            else:
                for predecessor in predecessors:
                    graph.add_edge(predecessor, task_num)

        # Add edges from tasks with no successors to dummy end node
        node_list = list(nx.topological_sort(graph))
        for node in node_list:
            if node != -1 and len(list(graph.successors(node))) == 0:
                graph.add_edge(node, -1)

        graph.nodes[0]['total_weight'] = 0

        # Calculate total weights (sum of task and all its successors)
        for i in range(1, len(task_list) + 1):
            node_list = list(nx.dfs_preorder_nodes(graph, source=i))
            total_weight = sum(graph.nodes[node]['time'] for node in node_list)
            graph.nodes[i]['total_weight'] = total_weight

        return graph

    def _create_graph_for_ushape(self, task_list: List[List], graph: nx.DiGraph) -> nx.DiGraph:
        """
        Create reverse graph for U-shaped line balancing.

        Args:
            task_list: List of tasks
            graph: Original graph

        Returns:
            Graph with reversed total weights calculated
        """
        reverse_graph = nx.DiGraph()
        reverse_graph.add_node(0, time=0)

        # Create reverse graph
        for task in task_list:
            task_num, predecessors, duration = task[0], task[1], task[2]
            reverse_graph.add_node(task_num, time=duration)

            for predecessor in predecessors:
                reverse_graph.add_edge(task_num, predecessor)

        reverse_graph.nodes[0]['total_weight'] = 0

        # Calculate reversed total weights
        for i in range(1, len(task_list) + 1):
            node_list = list(nx.dfs_preorder_nodes(reverse_graph, source=i))
            reversed_total_weight = sum(reverse_graph.nodes[node]['time'] for node in node_list)
            graph.nodes[i]['reversed_total_weight'] = reversed_total_weight

        return graph

    def _create_input_dict(self, task_list: List[List]) -> Dict[int, float]:
        """
        Create a dictionary mapping task numbers to their durations.

        Args:
            task_list: List of tasks

        Returns:
            Dictionary {task_number: duration}
        """
        return {task[0]: task[2] for task in task_list}

    def get_task_time(self, task_number: int) -> float:
        """
        Get the duration of a specific task.

        Args:
            task_number: The task number

        Returns:
            Duration of the task
        """
        return self.graph.nodes[task_number]['time']

    def get_station_time(self, station: List[int]) -> float:
        """
        Calculate total time for a station.

        Args:
            station: List of task numbers in the station

        Returns:
            Total time for all tasks in the station
        """
        return get_station_time(station, self.input_dictionary)

    def total_work_time(self, station_list: List[List[int]]) -> float:
        """
        Calculate total work time across all stations.

        Args:
            station_list: List of stations

        Returns:
            Total work time
        """
        return total_work_time(station_list, self.input_dictionary)

    def calculate_smooth_index(self, station_list: List[List[int]], cycle_time: float = 0) -> float:
        """
        Calculate smoothness index for the line configuration.

        Args:
            station_list: List of stations
            cycle_time: Target cycle time (0 for auto-calculate)

        Returns:
            Smoothness index value
        """
        return calculate_smooth_index(station_list, self.input_dictionary, cycle_time)

    def calculate_line_efficiency(self, station_list: List[List[int]], cycle_time: float = 0) -> float:
        """
        Calculate line efficiency percentage.

        Args:
            station_list: List of stations
            cycle_time: Target cycle time (0 for auto-calculate)

        Returns:
            Line efficiency as percentage
        """
        return calculate_line_efficiency(station_list, self.input_dictionary, cycle_time)

    def calculate_loss_balance(self, station_list: List[List[int]], cycle_time: float = 0) -> float:
        """
        Calculate balance delay percentage.

        Args:
            station_list: List of stations
            cycle_time: Target cycle time (0 for auto-calculate)

        Returns:
            Balance delay as percentage
        """
        return calculate_loss_balance(station_list, self.input_dictionary, cycle_time)

    def balance(self, cycle_time: float, method: str = 'lcr') -> List[List[int]]:
        """
        Balance the assembly line using heuristic method.

        This is a convenience method that calls heuristic_method().

        Args:
            cycle_time: Target cycle time for the line
            method: Balancing method ('lcr' or 'hb')

        Returns:
            List of stations with assigned tasks
        """
        from ..algorithms.heuristic import heuristic_method
        return heuristic_method(self, cycle_time, method)

    def heuristic_method(self, cycle_time: float, method: str = 'lcr') -> List[List[int]]:
        """
        Balance line using heuristic methods.

        Args:
            cycle_time: Target cycle time
            method: 'lcr' (Largest Candidate Rule) or 'hb' (Helgeson-Birnie)

        Returns:
            List of stations with assigned tasks
        """
        from ..algorithms.heuristic import heuristic_method
        return heuristic_method(self, cycle_time, method)

    def comsoal_method(
        self,
        cycle_time: Optional[float] = None,
        iteration: int = 100,
        local_search: str = 'heuristic',
        out: int = 1
    ) -> List[List[List[int]]]:
        """
        Balance line using COMSOAL algorithm.

        Args:
            cycle_time: Target cycle time (auto-calculated if None)
            iteration: Number of iterations to perform
            local_search: Local search method ('heuristic', 'local', or 'genetics')
            out: Number of solutions to return

        Returns:
            List of station configurations
        """
        from ..algorithms.comsoal import comsoal_algorithm
        return comsoal_algorithm(self, cycle_time, iteration, local_search, out)

    def genetic_algorithms(
        self,
        cycle_time: float,
        p_m: float = 0.7,
        p_c: float = 0.5,
        generation: int = 50,
        size: int = 30,
        local_search: str = 'genetics',
        out: int = 1
    ) -> List[List[List[int]]]:
        """
        Balance line using genetic algorithms.

        Args:
            cycle_time: Target cycle time
            p_m: Probability of mutation
            p_c: Probability of crossover
            generation: Number of generations
            size: Population size
            local_search: Local search method
            out: Number of solutions to return

        Returns:
            List of station configurations
        """
        from ..algorithms.genetic import genetic_algorithms
        return genetic_algorithms(self, cycle_time, p_m, p_c, generation, size, local_search, out)

    def u_type_balance(
        self,
        cycle_time: float,
        method: str = 'lcr',
        iteration: int = 100,
        out: int = 1
    ) -> Tuple[List[List[int]], List[str]]:
        """
        Balance U-shaped assembly line.

        Args:
            cycle_time: Target cycle time
            method: Balancing method ('lcr', 'hb', or 'comsoal')
            iteration: Number of iterations (for COMSOAL)
            out: Number of solutions to return

        Returns:
            Tuple of (station_list, task_sides) where task_sides indicates
            if each task is on Front (F), Back (B), or either (F-B)
        """
        from ..algorithms.u_type import u_type_balance
        return u_type_balance(self, cycle_time, method, iteration, out)

    def local_search_procedure(
        self,
        initial_solution: List[List[int]],
        cycle_time: float,
        local_search: str = "local",
        out: int = 1
    ) -> List[List[List[int]]]:
        """
        Apply local search to improve an initial solution.

        Args:
            initial_solution: Initial station configuration
            cycle_time: Target cycle time
            local_search: Search method ('local', 'genetics', or 'heuristic')
            out: Number of solutions to return

        Returns:
            List of improved station configurations
        """
        from ..algorithms.local_search import local_search_procedure
        return local_search_procedure(self, initial_solution, cycle_time, local_search, out)
