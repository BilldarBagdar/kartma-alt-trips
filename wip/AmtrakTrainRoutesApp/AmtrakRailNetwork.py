# AmtrakRailNetwork.py
import networkx as nx
from GtfsParser import AmtrakGtfsParser

class AmtrakRailNetwork:
    def __init__(self, parser: AmtrakGtfsParser = None):
        self.parser = parser or AmtrakGtfsParser()
        self.graph = nx.DiGraph()
        self._bootstrap_network()

    def _bootstrap_network(self):
        """Task A.1: Dynamically loads the base graph from the GTFS Parser"""
        self.graph = self.parser.build_base_graph()

    def get_unique_named_trains(self) -> set:
        """Task A: Filters the network layout to extract unique Named Trains"""
        named_trains = set()
        for u, v, data in self.graph.edges(data=True):
            for (route_name, train_num) in data.get('services', {}).keys():
                named_trains.add(route_name)
        return named_trains

    def filter_graph_by_named_train(self, train_name: str) -> nx.DiGraph:
        """Returns a subgraph matching only a specific line like 'Coast Starlight'"""
        subgraph = nx.DiGraph()
        for u, v, data in self.graph.edges(data=True):
            matching_services = {
                k: v for k, v in data.get('services', {}).items()
                if k[0].lower() == train_name.lower()
            }
            if matching_services:
                subgraph.add_node(u, **self.graph.nodes[u])
                subgraph.add_node(v, **self.graph.nodes[v])
                subgraph.add_edge(u, v, services=matching_services)
        return subgraph


# import networkx as nx
#
#
# class AmtrakRailNetwork:
#     def __init__(self):
#         self.graph = nx.DiGraph()
#         self._bootstrap_network()
#
#     def _bootstrap_network(self):
#         """
#         Seed the graph with actual Named Trains and their explicit sequence of stations.
#         This ensures 100% rail-legal routes without generating ghost paths.
#         """
#         # Example 1: Coast Starlight (Train 11 / 14)
#         coast_starlight_stations = ["SEA", "TAC", "PDX", "SAC", "OAK", "SJC", "SBA", "LAX"]
#         self.add_named_route("Coast Starlight", coast_starlight_stations, train_numbers=["11", "14"])
#
#         # Example 2: Southwest Chief (Train 3 / 4)
#         southwest_chief_stations = ["CHI", "GAY", "KC_", "ABQ", "FLG", "BAR", "LAX"]
#         self.add_named_route("Southwest Chief", southwest_chief_stations, train_numbers=["3", "4"])
#
#         # Example 3: Pacific Surfliner
#         surfliner_stations = ["SLO", "SBA", "LAX", "ANA", "SAN"]
#         self.add_named_route("Pacific Surfliner", surfliner_stations, train_numbers=["761", "762"])
#
#     def add_named_route(self, route_name: str, stations: list, train_numbers: list):
#         for i in range(len(stations) - 1):
#             u, v = stations[i], stations[i + 1]
#             # Bi-directional rail configuration
#             for node_from, node_to in [(u, v), (v, u)]:
#                 if not self.graph.has_edge(node_from, node_to):
#                     self.graph.add_edge(node_from, node_to, routes={})
#
#                 self.graph[node_from][node_to]['routes'][route_name] = {
#                     "trains": train_numbers
#                 }
#
#     def find_train_centric_trips(self, origin: str, destination: str):
#         """Finds routes prioritizing single-train paths or explicit physical cross-platform transfers."""
#         try:
#             # Find all simple physical paths within structural rail layout
#             paths = list(nx.all_simple_paths(self.graph, source=origin, target=destination, cutoff=4))
#             valid_itineraries = []
#
#             for path in paths:
#                 segments = []
#                 for i in range(len(path) - 1):
#                     u, v = path[i], path[i + 1]
#                     segments.append(self.graph[u][v]['routes'])
#
#                 valid_itineraries.append({
#                     "station_sequence": path,
#                     "segment_options": segments
#                 })
#             return valid_itineraries
#         except nx.NetworkXNoPath:
#             return []
#
#
# # # Usage example on your local environment
# # network = AmtrakRailNetwork()
# # # Find how to get from Seattle to San Diego via physical trains
# # trips = network.find_train_centric_trips("SEA", "SAN")
