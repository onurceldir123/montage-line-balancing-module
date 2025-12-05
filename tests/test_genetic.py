import pytest
import logging
from pybalance import Line
from pybalance.algorithms.genetic import genetic_algorithms

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

@pytest.fixture
def simple_tasks():
    # [task_num, [predecessors], duration]
    return [
        [1, [0], 2],
        [2, [1], 5],
        [3, [1], 4],
        [4, [2, 3], 3]
    ]

def test_genetic_algorithm_basic(simple_tasks):
    line = Line(simple_tasks)
    cycle_time = 6
    # Use a small population and generation count for speed
    solutions = genetic_algorithms(
        line, 
        cycle_time, 
        generation=10, 
        size=10,
        seed=42
    )
    
    assert len(solutions) > 0
    best_solution = solutions[0]
    
    # Verify solution validity
    assigned_tasks = [task for station in best_solution for task in station]
    assert sorted(assigned_tasks) == [1, 2, 3, 4]
    
    # Verify cycle time constraint
    for station in best_solution:
        assert line.get_station_time(station) <= cycle_time

def test_genetic_algorithm_reproducibility(simple_tasks):
    line = Line(simple_tasks)
    cycle_time = 6
    
    # Run twice with same seed
    solutions1 = genetic_algorithms(
        line, cycle_time, generation=5, size=10, seed=123
    )
    solutions2 = genetic_algorithms(
        line, cycle_time, generation=5, size=10, seed=123
    )
    
    assert solutions1 == solutions2

def test_genetic_algorithm_different_seeds(simple_tasks):
    line = Line(simple_tasks)
    cycle_time = 6
    
    # Run twice with different seeds
    # Note: For small problems/populations, they might still converge to same solution
    # So we check if the internal random state was different by checking if *something* differs
    # or just trust the seed mechanism. 
    # Actually, with small population and few generations, it's likely they differ.
    
    solutions1 = genetic_algorithms(
        line, cycle_time, generation=5, size=10, seed=111
    )
    solutions2 = genetic_algorithms(
        line, cycle_time, generation=5, size=10, seed=222
    )
    
    # It's possible they find the same optimal solution, so we can't strictly assert inequality of result.
    # But for this test, we just want to ensure the code runs without error with different seeds.
    assert len(solutions1) > 0
    assert len(solutions2) > 0

def test_genetic_algorithm_out_parameter(simple_tasks):
    line = Line(simple_tasks)
    cycle_time = 6
    
    solutions = genetic_algorithms(
        line, cycle_time, generation=5, size=20, out=2, seed=42
    )
    
    # We might not get 2 unique solutions if the problem is too simple
    # But we should get at most 2
    assert len(solutions) <= 2
    assert len(solutions) > 0
