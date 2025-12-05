"""
PyBalance - Assembly Line Balancing Library

PyBalance is a Python package for creating, processing, and analyzing assembly lines.
It provides tools for line balancing using various algorithms including heuristic methods,
COMSOAL, and genetic algorithms.

Example:
    >>> from pybalance import Line
    >>> tasks = [
    ...     [1, [0], 2],
    ...     [2, [1], 5],
    ...     [3, [1], 4],
    ...     [4, [2, 3], 3]
    ... ]
    >>> line = Line(tasks)
    >>> stations = line.balance(6)
    >>> print(stations)
    [[1, 3], [2], [4]]
"""

from .core import Line
from .metrics import (
    calculate_smooth_index,
    calculate_line_efficiency,
    calculate_loss_balance
)
from .algorithms import (
    heuristic_method,
    comsoal_algorithm,
    genetic_algorithms,
    local_search_procedure,
    u_type_balance
)

from .utils import (
    visualize_balance,
    balance_line,
    calculate_metrics,
    export_results
)

__version__ = '2.0.0'
__author__ = 'Onur Mert Çeldir'
__license__ = 'GPL-3.0'

__all__ = [
    'Line',
    'calculate_smooth_index',
    'calculate_line_efficiency',
    'calculate_loss_balance',
    'heuristic_method',
    'comsoal_algorithm',
    'genetic_algorithms',
    'local_search_procedure',
    'u_type_balance',
    'visualize_balance',
    'balance_line',
    'calculate_metrics',
    'export_results',
]
