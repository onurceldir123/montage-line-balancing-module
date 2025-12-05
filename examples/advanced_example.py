"""
Advanced Line Balancing Example

This example demonstrates advanced features including:
- Complex precedence relationships
- Optimization constraints
- Comparison of multiple algorithms
- Detailed performance analysis
"""

from pybalance import balance_line, calculate_metrics, export_results
import json


def create_complex_assembly_line():
    """
    Create a more complex assembly line with 15 tasks.
    This represents a typical electronics assembly process.
    """
    tasks = [
        {"id": 1, "time": 8, "dependencies": [], "name": "Prepare PCB"},
        {"id": 2, "time": 5, "dependencies": [1], "name": "Mount resistors"},
        {"id": 3, "time": 6, "dependencies": [1], "name": "Mount capacitors"},
        {"id": 4, "time": 7, "dependencies": [2, 3], "name": "Mount ICs"},
        {"id": 5, "time": 4, "dependencies": [4], "name": "Solder components"},
        {"id": 6, "time": 9, "dependencies": [], "name": "Prepare casing"},
        {"id": 7, "time": 5, "dependencies": [5], "name": "Inspect PCB"},
        {"id": 8, "time": 6, "dependencies": [6], "name": "Install mounting brackets"},
        {"id": 9, "time": 7, "dependencies": [7, 8], "name": "Mount PCB in casing"},
        {"id": 10, "time": 4, "dependencies": [9], "name": "Connect wiring"},
        {"id": 11, "time": 5, "dependencies": [], "name": "Prepare display"},
        {"id": 12, "time": 6, "dependencies": [11], "name": "Connect display"},
        {"id": 13, "time": 8, "dependencies": [10, 12], "name": "Assemble housing"},
        {"id": 14, "time": 5, "dependencies": [13], "name": "Quality test"},
        {"id": 15, "time": 3, "dependencies": [14], "name": "Final packaging"},
    ]
    return tasks


def analyze_line_balance(tasks, cycle_time):
    """Analyze line balancing with multiple algorithms and compare results."""

    print("=" * 80)
    print("ADVANCED LINE BALANCING ANALYSIS")
    print("=" * 80)

    # Calculate theoretical minimum number of stations
    total_time = sum(task["time"] for task in tasks)
    theoretical_min = -(-total_time // cycle_time)  # Ceiling division

    print(f"\nProblem Parameters:")
    print(f"  Number of tasks: {len(tasks)}")
    print(f"  Total work content: {total_time} seconds")
    print(f"  Cycle time: {cycle_time} seconds")
    print(f"  Theoretical minimum stations: {theoretical_min}")

    # Test different algorithms
    algorithms = {
        "largest_candidate": "Largest Candidate Rule",
        "ranked_positional_weight": "Ranked Positional Weight",
        "random": "Random Assignment",
    }

    results = {}

    for algo_key, algo_name in algorithms.items():
        print(f"\n{'-' * 80}")
        print(f"Testing: {algo_name}")
        print("-" * 80)

        try:
            # Balance the line
            result = balance_line(tasks, cycle_time, algorithm=algo_key)
            metrics = calculate_metrics(result)

            results[algo_key] = {"result": result, "metrics": metrics}

            # Display results
            print(f"\nResults:")
            print(f"  Workstations used: {result['num_stations']}")
            print(f"  Line efficiency: {metrics['line_efficiency']:.2%}")
            print(f"  Balance delay: {metrics['balance_delay']:.2%}")
            print(f"  Smoothness index: {metrics['smoothness_index']:.2f}")
            print(f"  Deviation from theoretical min: {result['num_stations'] - theoretical_min}")

            # Show detailed station information
            print(f"\n  Station Details:")
            for station_id, station_tasks in result["stations"].items():
                station_time = sum(t["time"] for t in station_tasks)
                utilization = (station_time / cycle_time) * 100
                task_names = [t.get("name", f"Task {t['id']}") for t in station_tasks]

                print(f"    Station {station_id}:")
                print(f"      Tasks: {', '.join(task_names)}")
                print(f"      Time: {station_time}/{cycle_time}s ({utilization:.1f}% utilized)")

        except Exception as e:
            print(f"  Error: {str(e)}")

    # Compare algorithms
    if len(results) > 1:
        print(f"\n{'=' * 80}")
        print("ALGORITHM COMPARISON")
        print("=" * 80)

        print(f"\n{'Algorithm':<35} {'Stations':<12} {'Efficiency':<12} {'Smoothness':<12}")
        print("-" * 80)

        for algo_key, algo_name in algorithms.items():
            if algo_key in results:
                r = results[algo_key]
                print(
                    f"{algo_name:<35} "
                    f"{r['result']['num_stations']:<12} "
                    f"{r['metrics']['line_efficiency']:.2%}          "
                    f"{r['metrics']['smoothness_index']:.2f}"
                )

        # Find best algorithm
        best_algo = min(
            results.items(), key=lambda x: x[1]["result"]["num_stations"]
        )
        print(f"\nBest algorithm by station count: {algorithms[best_algo[0]]}")

        best_efficiency = max(
            results.items(), key=lambda x: x[1]["metrics"]["line_efficiency"]
        )
        print(f"Best algorithm by efficiency: {algorithms[best_efficiency[0]]}")

    return results


def export_solution(results, filename="line_balance_solution.json"):
    """Export the best solution to a JSON file."""
    # Find the best solution (by efficiency)
    best_algo = max(results.items(), key=lambda x: x[1]["metrics"]["line_efficiency"])

    solution = {
        "algorithm": best_algo[0],
        "stations": best_algo[1]["result"]["stations"],
        "metrics": best_algo[1]["metrics"],
    }

    with open(filename, "w") as f:
        json.dump(solution, f, indent=2)

    print(f"\nBest solution exported to: {filename}")


def main():
    # Create the assembly line
    tasks = create_complex_assembly_line()

    # Set cycle time
    cycle_time = 20  # seconds

    # Analyze different algorithms
    results = analyze_line_balance(tasks, cycle_time)

    # Export the best solution
    if results:
        export_solution(results)

    print(f"\n{'=' * 80}")
    print("Analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
