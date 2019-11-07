import osmnx as ox
import networkx as nx
import json

lchs_lat = 39.1109809
lchs_long = -77.5796448
douglass_lat = 39.1101564
douglass_long = -77.555343


ox.config(log_console=True)

G = ox.graph_from_place("Leesburg, Virginia, USA", network_type='drive')
# G is a multidigraph created by the networkx python package

# for (u, v, l) in G.edges(data='length'):
#     print(u, v, l)

lchs = ox.get_nearest_node(G, (lchs_lat, lchs_long))
douglass = ox.get_nearest_node(G, (douglass_lat, douglass_long))

route = nx.shortest_path(G, lchs, douglass)
ox.plot_graph_route(G, route)
