import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, Any, Optional

def visualize_balance(result: Dict[str, Any], save_path: Optional[str] = None):
    """
    Visualize the line balancing result.
    
    Args:
        result: Dictionary containing 'stations' and other info
        save_path: Path to save the image
    """
    stations = result.get('stations', {})
    if not stations:
        print("No stations to visualize")
        return

    # Create a graph
    G = nx.DiGraph()
    
    # Add nodes and edges
    # We need the original task dependencies to draw edges
    # But result might only have stations. 
    # Ideally we should pass the Line object or task list.
    # For now, let's just draw stations as clusters.
    
    pos = {}
    colors = []
    labels = {}
    
    plt.figure(figsize=(12, 8))
    
    # Simple visualization: Stations as boxes
    num_stations = len(stations)
    for i, (station_id, tasks) in enumerate(stations.items()):
        # Draw tasks in this station
        for j, task in enumerate(tasks):
            node_id = task['id'] if isinstance(task, dict) else task
            G.add_node(node_id)
            pos[node_id] = (i * 2, j * 2)
            colors.append(i)
            labels[node_id] = str(node_id)
            
    nx.draw(G, pos, with_labels=True, node_color=colors, cmap=plt.cm.Pastel1, 
            node_size=2000, font_size=16, font_weight='bold')
            
    plt.title("Assembly Line Balancing Result")
    plt.axis('off')
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()
