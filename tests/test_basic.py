import pytest
from pybalance import Line, calculate_line_efficiency, calculate_smooth_index

@pytest.fixture
def simple_tasks():
    # [task_num, [predecessors], duration]
    return [
        [1, [0], 2],
        [2, [1], 5],
        [3, [1], 4],
        [4, [2, 3], 3]
    ]

def test_line_creation(simple_tasks):
    line = Line(simple_tasks)
    assert line.graph.number_of_nodes() == 6  # 4 tasks + start(0) + end(-1)
    assert line.get_task_time(1) == 2
    assert line.get_task_time(4) == 3

def test_heuristic_balance_lcr(simple_tasks):
    line = Line(simple_tasks)
    cycle_time = 6
    stations = line.balance(cycle_time, method='lcr')
    
    # Check if all tasks are assigned
    assigned_tasks = [task for station in stations for task in station]
    assert len(assigned_tasks) == 4
    assert sorted(assigned_tasks) == [1, 2, 3, 4]
    
    # Check cycle time constraint
    for station in stations:
        station_time = line.get_station_time(station)
        assert station_time <= cycle_time

def test_metrics(simple_tasks):
    line = Line(simple_tasks)
    stations = [[1, 3], [2], [4]]
    cycle_time = 6
    
    efficiency = line.calculate_line_efficiency(stations, cycle_time)
    assert 0 <= efficiency <= 100
    
    smoothness = line.calculate_smooth_index(stations, cycle_time)
    assert smoothness >= 0

def test_u_type_balance(simple_tasks):
    line = Line(simple_tasks)
    cycle_time = 6
    stations, sides = line.u_type_balance(cycle_time)
    
    assert len(sides) == len(simple_tasks)
    assigned_tasks = [task for station in stations for task in station]
    assert sorted(assigned_tasks) == [1, 2, 3, 4]
