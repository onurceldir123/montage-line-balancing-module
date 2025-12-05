"""
Basic Line Balancing Example

This example demonstrates how to use PyBalance for a simple assembly line
balancing problem with 8 tasks.
"""

from pybalance import balance_line, visualize_balance, calculate_metrics


def main():
    # Define tasks with their processing times and dependencies
    tasks = [
        {"id": 1, "time": 5, "dependencies": []},
        {"id": 2, "time": 3, "dependencies": [1]},
        {"id": 3, "time": 7, "dependencies": [1]},
        {"id": 4, "time": 4, "dependencies": [2]},
        {"id": 5, "time": 6, "dependencies": [2, 3]},
        {"id": 6, "time": 5, "dependencies": [4]},
        {"id": 7, "time": 3, "dependencies": [5]},
        {"id": 8, "time": 4, "dependencies": [6, 7]},
    ]

    # Set the desired cycle time (takt time)
    cycle_time = 12

    print("=" * 60)
    print("ASSEMBLY LINE BALANCING - Basic Example")
    print("=" * 60)
    print(f"\nNumber of tasks: {len(tasks)}")
    print(f"Cycle time: {cycle_time} seconds")
    print(f"Total work content: {sum(task['time'] for task in tasks)} seconds")

    # Balance the line using different algorithms
    algorithms = ["largest_candidate", "ranked_positional_weight", "random"]

    for algorithm in algorithms:
        print(f"\n{'=' * 60}")
        print(f"Algorithm: {algorithm.upper().replace('_', ' ')}")
        print("=" * 60)

        # Perform line balancing
        result = balance_line(tasks, cycle_time, algorithm=algorithm)

        # Calculate performance metrics
        metrics = calculate_metrics(result)

        # Display results
        print(f"\nNumber of workstations: {result['num_stations']}")
        print(f"Line efficiency: {metrics['line_efficiency']:.2%}")
        print(f"Balance delay: {metrics['balance_delay']:.2%}")
        print(f"Smoothness index: {metrics['smoothness_index']:.2f}")

        print("\nWorkstation assignments:")
        for station_id, station_tasks in result["stations"].items():
            station_time = sum(task["time"] for task in station_tasks)
            idle_time = cycle_time - station_time
            task_ids = [task["id"] for task in station_tasks]

            print(f"  Station {station_id}:")
            print(f"    Tasks: {task_ids}")
            print(f"    Time: {station_time}/{cycle_time} seconds")
            print(f"    Idle: {idle_time} seconds")

        # Visualize the balance (optional - requires matplotlib)
        try:
            visualize_balance(result, save_path=f"balance_{algorithm}.png")
            print(f"\nVisualization saved to: balance_{algorithm}.png")
        except ImportError:
            print("\nNote: Install matplotlib for visualization")


if __name__ == "__main__":
    main()
