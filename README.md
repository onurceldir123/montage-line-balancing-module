# PyBalance

[![PyPI version](https://img.shields.io/badge/pypi-v2.0.0-blue.svg)](https://pypi.org/project/pybalance/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

**PyBalance** is a comprehensive Python library designed for the rigorous analysis and optimization of assembly line configurations. It supports both straight and U-shaped line topologies, offering a robust suite of algorithms that includes classical heuristics (Largest Candidate Rule, Helgeson-Birnie), the probabilistic COMSOAL method, and advanced Genetic Algorithms with local search procedures.

Engineered for operations research and manufacturing applications, the library provides essential performance metrics such as Line Efficiency, Smoothness Index, and Balance Delay. Its modular, type-hinted architecture ensures reliability and allows for easy extension, making it suitable for both academic research and industrial implementation.

## Installation

```bash
pip install pybalance
```

## Usage

### 1. Heuristic Balancing

```python
from pybalance import Line

# Task format: [id, [predecessors], duration]
tasks = [
    [1, [0], 2], [2, [1], 5], [3, [1], 4], [4, [2, 3], 3]
]

line = Line(tasks)

# Balance using Largest Candidate Rule (LCR)
stations_lcr = line.balance(cycle_time=6, method='lcr')
print(f"LCR Stations: {stations_lcr}")

# Balance using Helgeson-Birnie (Ranked Positional Weight)
stations_hb = line.balance(cycle_time=6, method='hb')
print(f"HB Stations: {stations_hb}")

# Calculate Efficiency
efficiency = line.calculate_line_efficiency(stations_lcr, cycle_time=6)
print(f"Efficiency: {efficiency:.2f}%")
```

### 2. Genetic Algorithm Optimization

PyBalance implements the hybrid genetic algorithm proposed by *Çeldir & Utku (2022)*, utilizing graph topology to maintain feasibility. The implementation features **Region-Based Crossover**, which swaps genes within independent graph regions defined by articulation points, and **Region-Based Mutation**, which safely relocates tasks within their valid topological bounds.

```python
solutions = line.genetic_algorithms(
    cycle_time=12,
    generation=50,
    size=30,
    p_m=0.7,
    p_c=0.5
)
print(f"Best Configuration: {solutions[0]}")
```

### 3. U-Shaped Line Balancing

The library supports U-shaped line balancing where tasks can be assigned to either the front or back of the line, maximizing flexibility.

```python
stations, sides = line.u_type_balance(cycle_time=12, method='comsoal')
print(f"Stations: {stations}")
print(f"Sides: {sides}") # ['F' (Front), 'B' (Back), 'F-B' (Either)]
```

## Citation

```bibtex
@article{celdir2022montaj,
  title={Montaj Hatt{\i} Dengelemede Genetik Algoritmalar{\i}n Kullan{\i}m{\i}: Yeni Bir Y{\"o}ntem},
  author={{\c{C}}eldir, Onur Mert and Utku, Semih},
  journal={Dokuz Eyl{\"u}l {\"U}niversitesi M{\"u}hendislik Fak{\"u}ltesi Fen ve M{\"u}hendislik Dergisi},
  volume={24},
  number={71},
  pages={365--373},
  year={2022},
  doi={10.21205/deufmd.2022247103}
}
```

## License

Licensed under the **GPLv3**. See [LICENSE](LICENSE) for details.

## Contact

**Onur Mert Çeldir**  
[GitHub](https://github.com/onurceldir123) | onurceldir123@gmail.com
