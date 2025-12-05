import pytest
import logging
from pybalance import Line
from pybalance.algorithms.u_type import u_type_balance

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

def test_u_type_balance_lcr(simple_tasks):
    line = Line(simple_tasks)
    cycle_time = 6
    stations, sides = u_type_balance(line, cycle_time, method='lcr')
    
    assert len(stations) > 0
    assert len(sides) == 4 # 4 tasks
    
    # Verify all tasks assigned
    assigned = [t for s in stations for t in s]
    assert sorted(assigned) == [1, 2, 3, 4]

def test_u_type_balance_comsoal(simple_tasks):
    line = Line(simple_tasks)
    cycle_time = 6
    # Run COMSOAL
    stations, sides = u_type_balance(line, cycle_time, method='comsoal', iteration=50)
    
    assert len(stations) > 0
    assert len(sides) == 4
    
    # Verify all tasks assigned
    assigned = [t for s in stations for t in s]
    assert sorted(assigned) == [1, 2, 3, 4]
    
    # Verify cycle time constraint
    for station in stations:
        assert line.get_station_time(station) <= cycle_time

def test_u_type_comsoal_reproducibility(simple_tasks):
    # Since we didn't add seed to u_type_balance explicitly but random is used,
    # we can set random seed externally.
    import random
    line = Line(simple_tasks)
    cycle_time = 6
    
    random.seed(42)
    stations1, _ = u_type_balance(line, cycle_time, method='comsoal', iteration=10)
    
    random.seed(42)
    stations2, _ = u_type_balance(line, cycle_time, method='comsoal', iteration=10)
    
    assert stations1 == stations2
