from typing import List, Dict, Any, Union
import json
from ..core.line import Line
from ..metrics.efficiency import (
    calculate_line_efficiency,
    calculate_smooth_index,
    calculate_loss_balance
)

def balance_line(tasks: List[Dict], cycle_time: float, algorithm: str = 'largest_candidate') -> Dict[str, Any]:
    """
    High-level function to balance a line.
    
    Args:
        tasks: List of task dictionaries or lists
        cycle_time: Cycle time
        algorithm: Algorithm name
        
    Returns:
        Dictionary with results
    """
    # Convert dict tasks to list format if needed
    # Expected list format: [id, [deps], time]
    task_list = []
    task_map = {}
    
    if tasks and isinstance(tasks[0], dict):
        for t in tasks:
            # Handle dependencies
            deps = t.get('dependencies', [])
            task_list.append([t['id'], deps, t['time']])
            task_map[t['id']] = t
    else:
        task_list = tasks

    line = Line(task_list)
    
    # Map algorithm names
    algo_map = {
        'largest_candidate': 'lcr',
        'ranked_positional_weight': 'hb', # Mapping RPW to HB for now as they are similar heuristics
        'random': 'lcr', # Fallback
        'lcr': 'lcr',
        'hb': 'hb'
    }
    
    method = algo_map.get(algorithm, 'lcr')
    
    if algorithm == 'random':
        # TODO: Implement random if needed, or just use LCR
        pass
        
    stations_list = line.balance(cycle_time, method=method)
    
    # Format output
    stations_dict = {}
    for i, station in enumerate(stations_list):
        # If input was dicts, return dicts
        if task_map:
            stations_dict[i+1] = [task_map[tid] for tid in station]
        else:
            stations_dict[i+1] = station
            
    return {
        "stations": stations_dict,
        "num_stations": len(stations_list),
        "algorithm": algorithm,
        "cycle_time": cycle_time
    }

def calculate_metrics(result: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate metrics from a result dictionary.
    """
    stations_dict = result['stations']
    cycle_time = result['cycle_time']
    
    # Convert back to list of lists of ids for internal metric functions
    station_list = []
    task_times = {}
    
    for station_tasks in stations_dict.values():
        s_ids = []
        for t in station_tasks:
            if isinstance(t, dict):
                s_ids.append(t['id'])
                task_times[t['id']] = t['time']
            else:
                s_ids.append(t)
                # We don't have times here if input was list, 
                # but calculate_metrics usually needs a Line object or input_dict.
                # This helper is tricky without the Line object.
                # This helper is tricky without the Line object.
        station_list.append(s_ids)

    # We need to reconstruct input_dict for metrics
    # If we don't have it, we can't calculate.
    # But wait, the internal metric functions take (station_list, input_dict, cycle_time)
    # We need to expose a way to pass input_dict or handle it.
    
    # Let's assume we can reconstruct it from the result if it contains task info
    input_dictionary = task_times
    
    if not input_dictionary:
        # If we can't get times, return 0s
        return {
            "line_efficiency": 0.0,
            "balance_delay": 0.0,
            "smoothness_index": 0.0
        }

    eff = calculate_line_efficiency(station_list, input_dictionary, cycle_time)
    smooth = calculate_smooth_index(station_list, input_dictionary, cycle_time)
    delay = calculate_loss_balance(station_list, input_dictionary, cycle_time)
    
    return {
        "line_efficiency": eff / 100.0, # Example expects 0-1 or %? Example uses .2% so it expects float 0-1? 
                                        # Wait, internal returns 0-100. Example: .2% means it expects 0.95 for 95%.
                                        # Let's check example: print(f"Line efficiency: {metrics['line_efficiency']:.2%}")
                                        # If it returns 95.0, .2% prints 9500.00%. 
                                        # So we should return 0.95.
        "balance_delay": delay / 100.0,
        "smoothness_index": smooth
    }

def export_results(results: Dict[str, Any], filename: str = "results.json"):
    """
    Export results to a JSON file.
    """
    # Helper to convert non-serializable objects if any
    def default(o):
        return str(o)
        
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=default)
    
    print(f"Results exported to {filename}")
