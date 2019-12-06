import osmnx as ox
import math
import networkx as nx
import json

lchs_lat = 39.12
lchs_long = -77.58
douglass_lat = 39.11
douglass_long = -77.55

# G = ox.graph_from_place("Leesburg, Virginia, USA", network_type='drive')
# G2 = ox.graph_from_bbox(lchs_lat, douglass_lat, douglass_long, lchs_long, network_type='drive')
# G is a multidigraph created by the networkx python package

# for (u, v, l) in G.edges(data='length'):
#     print(u, v, l)

# lchs = ox.get_nearest_node(G, (lchs_lat, lchs_long))
# douglass = ox.get_nearest_node(G, (douglass_lat, douglass_long))


def generate_int(n):
    for i in range(n):
        yield i


def get_travel_time(edge):
    """
    :param edge: dictionary containing edge data
    :return: approximate time in minutes to travel along the edge
    """

    # dictionary of default speed limits to be used when no speed limit is given
    # based off of descriptions found on https://wiki.openstreetmap.org/wiki/Key:highway
    default_speed_limits = {
        'motorway': 55,
        'trunk': 55,
        'primary': 45,
        'secondary': 45,
        'tertiary': 35,
        'unclassified': 30,
        'residential': 25,
        'motorway_link': 45,
        'trunk_link': 45,
        'primary_link': 35,
        'secondary_link': 35,
        'tertiary_link': 25,
        'living_street': 15,
    }

    distance_mi = edge['length'] / 1609.0 # convert from meters to miles
    try:
        edge['maxspeed']
        if type(edge['maxspeed']) == str:
            maxspeed = int(edge['maxspeed'][:-3])
        elif type(edge['maxspeed']) == list:
            maxspeed = int(edge['maxspeed'][-1][:-3])
    except KeyError:
        road_type = edge['highway']
        try:
            maxspeed = default_speed_limits[road_type]
        except KeyError:
            maxspeed = 25

    travel_time = (distance_mi / maxspeed) * 60
    return travel_time


def dijkstra(start, graph):
    infinity = math.inf
    distances = {start: (0, None)}
    seen = []

    for node in list(graph.nodes()):
        if node != start:
            distances[node] = (infinity, None)

    q = list(graph.nodes())
    while q:
        u = min((distances[i][0], i) for i in (distances.keys() - seen))[1]
        seen.append(u)
        try:
            q.remove(u)
        except ValueError:
            print("{} not in list: {}".format(u, u not in q))
            break
        neighbors = graph.neighbors(u)
        for n in neighbors:
            travel_time = get_travel_time(graph.get_edge_data(u, n)[0])
            if distances[n][0] > distances[u][0] + travel_time:
                distances[n] = (distances[u][0] + travel_time, u)

    return distances


test_graph = nx.Graph()
test_graph.add_nodes_from("abcdefg")
test_graph.add_edges_from([("a", "b", {0: {'length': 1600, 'maxspeed': '55 mph'}}),
                           ("a", "c", {0: {'length': 1810, 'maxspeed': '45 mph'}}),
                           ("a", "g", {0: {'length': 300, 'maxspeed': '25 mpg'}}),
                           ("b", "d", {0: {'length': 800, 'maxspeed': '45 mpg'}}),
                           ("c", "d", {0: {'length': 1650, 'maxspeed': '45 mpg'}}),
                           ("c", "e", {0: {'length': 510, 'maxspeed': '35 mpg'}}),
                           ("d", "e", {0: {'length': 743, 'maxspeed': '25 mpg'}}),
                           ("e", "f", {0: {'length': 621, 'maxspeed': '25 mpg'}}),
                           ("f", "g", {0: {'length': 750, 'maxspeed': '25 mpg'}})])


def dijkstra_brute_force(start_nodes, graph):
    dijkstra_results = []
    for node in start_nodes:
        dijkstra_results.append(dijkstra(node, graph))
    for res in dijkstra_results:
        print(res)

    node_sums = {}
    for node in graph.nodes():
        node_sum = 0
        for result in dijkstra_results:
            node_sum += result[node][0]
        node_sums[node] = node_sum

    meeting_node = min((node_sums[i], i) for i in node_sums.keys())[1]

    paths = {}
    for i in range(len(start_nodes)):
        path = [meeting_node]
        res = dijkstra_results[i]
        current = meeting_node

        while res[current][1] is not None:
            path.insert(0, res[current][1])
            current = res[current][1]
        paths[start_nodes[i]] = path

    return meeting_node, paths


meeting_node, paths = dijkstra_brute_force(['a', 'd', 'f'], test_graph)
print(meeting_node)
print(paths)

def floyd_warshall(graph):
    infinity = math.inf
    distances = {}
    q = list(graph.nodes())
    print(q)

    num_nodes = graph.number_of_nodes()
    for i in generate_int(num_nodes):
        for j in generate_int(num_nodes):
            if (q[i], q[j]) in graph.edges():
                road_length = graph.get_edge_data(q[i], q[j])[0]['length']
                try:
                    max_speed = graph.get_edge_data(q[i], q[j])[0]['max_speed']
                except KeyError:
                    road_type = graph.get_edge_data(q[i], q[j])[0]['highway']
                    if road_type == 'residential':
                        max_speed = 25
                    else:
                        print(road_type)

                travel_time = get_travel_time(road_length, max_speed)
                distances[(q[i], q[j])] = travel_time
            else:
                distances[(q[i], q[j])] = infinity

    for k in generate_int(num_nodes):
        for i in generate_int(num_nodes):
            for j in generate_int(num_nodes):
                if (q[i], q[k]) in graph.edges():
                    length_i_k = graph.get_edge_data(q[i], q[k])[0]['length']
                    try:
                        max_speed_i_k = graph.get_edge_data(q[i], q[k])[0]['max_speed']
                    except KeyError:
                        road_type = graph.get_edge_data(q[i], q[k])[0]['highway']
                        if road_type == 'residential':
                            max_speed_i_k = 25
                        else:
                            print(road_type)
                    travel_time_i_k = get_travel_time(length_i_k, max_speed_i_k)

                    if (q[k], q[j]) in graph.edges():
                        length_k_j = graph.get_edge_data(q[k], q[j])[0]['length']
                        try:
                            max_speed_k_j = graph.get_edge_data(q[k], q[j])[0]['max_speed']
                        except KeyError:
                            road_type = graph.get_edge_data(q[k], q[j])[0]['highway']
                            if road_type == 'residential':
                                max_speed_k_j = 25
                            else:
                                print(road_type)
                        travel_time_k_j = get_travel_time(length_k_j, max_speed_k_j)

                        new_dist = travel_time_i_k + travel_time_k_j
                        if distances[(q[i], q[j])] > new_dist:
                            distances[(q[i], q[j])] = new_dist

    for item in distances:
        print("{} --> {}".format(item, distances[item]))

    for edge in graph.edges():
        print(graph.get_edge_data(edge[0], edge[1]))




