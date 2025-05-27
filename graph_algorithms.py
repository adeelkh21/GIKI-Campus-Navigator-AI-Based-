import networkx as nx
from typing import Dict, List, Tuple, Optional, Callable
import math
from osm_parser import parse_osm_file
import folium
from folium import plugins

class CampusGraph:
    def __init__(self, osm_file: str = "giki.osm"):
        self.graph = nx.Graph()
        self.node_positions = {}  # For visualization
        self._initialize_campus_graph(osm_file)

    def _initialize_campus_graph(self, osm_file: str):
        # Parse OSM file to get locations and edges
        locations, edges = parse_osm_file(osm_file)
        
        # Add nodes with positions
        for loc, coords in locations.items():
            self.graph.add_node(loc)
            self.node_positions[loc] = coords

        # Add edges with weights (distances in meters)
        for edge in edges:
            loc1, loc2, distance = edge
            self.graph.add_edge(loc1, loc2, weight=distance)

    def _heuristic(self, node1: str, node2: str) -> float:
        """Calculate Haversine distance between two nodes using real-world coordinates"""
        lat1, lon1 = self.node_positions[node1]
        lat2, lon2 = self.node_positions[node2]
        return self._haversine_distance(lat1, lon1, lat2, lon2)

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the Haversine distance between two points in meters."""
        R = 6371000  # Earth's radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi/2) * math.sin(delta_phi/2) +
             math.cos(phi1) * math.cos(phi2) *
             math.sin(delta_lambda/2) * math.sin(delta_lambda/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

    def find_path(self, start: str, end: str, algorithm: str = "dijkstra") -> Tuple[List[str], float]:
        """Find shortest path using specified algorithm"""
        if algorithm == "astar":
            # Use A* with Haversine distance as heuristic
            path = nx.astar_path(self.graph, start, end, 
                               heuristic=lambda n1, n2: self._heuristic(n1, n2),
                               weight="weight")
        else:
            # Use Dijkstra's algorithm
            path = nx.dijkstra_path(self.graph, start, end, weight="weight")
        
        # Calculate total path distance
        distance = sum(self.graph[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
        return path, distance

    def visualize_path(self, path: List[str] = None) -> folium.Map:
        """Visualize the graph and highlight the given path using folium"""
        # Calculate center of the map
        lats = [lat for lat, _ in self.node_positions.values()]
        lons = [lon for _, lon in self.node_positions.values()]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Create the map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=16)
        
        # Add all nodes as markers
        for node, (lat, lon) in self.node_positions.items():
            color = 'green' if path and node in path else 'blue'
            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                color=color,
                fill=True,
                fill_color=color,
                popup=node
            ).add_to(m)
        
        # Add all edges
        for edge in self.graph.edges():
            node1, node2 = edge
            lat1, lon1 = self.node_positions[node1]
            lat2, lon2 = self.node_positions[node2]
            
            # Create a line between the nodes
            line = folium.PolyLine(
                locations=[[lat1, lon1], [lat2, lon2]],
                color='gray',
                weight=2,
                opacity=0.5
            )
            line.add_to(m)
        
        # Highlight the path if provided
        if path:
            for i in range(len(path) - 1):
                node1 = path[i]
                node2 = path[i + 1]
                lat1, lon1 = self.node_positions[node1]
                lat2, lon2 = self.node_positions[node2]
                
                # Create a highlighted line for the path
                path_line = folium.PolyLine(
                    locations=[[lat1, lon1], [lat2, lon2]],
                    color='red',
                    weight=4,
                    opacity=1
                )
                path_line.add_to(m)
        
        return m 