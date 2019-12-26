import osmnx as ox
import math
import geopy
import sys
from shapely import geometry


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

    distance_mi = edge['length'] / 1609.0  # convert from meters to miles
    try:
        edge['maxspeed']
        if type(edge['maxspeed']) == str:
            maxspeed = int(edge['maxspeed'][:-3])
        elif type(edge['maxspeed']) == list:
            maxspeed = int(edge['maxspeed'][-1][:-3])  # get highest speed, remove last three characters (mpg)
    except KeyError:
        road_type = edge['highway']
        try:
            maxspeed = default_speed_limits[road_type]
        except KeyError:
            maxspeed = 25

    travel_time = (distance_mi / maxspeed) * 60
    return travel_time


def dijkstra(graph, start):
    """
    Run dijkstra's algorithm on graph starting at node start
    :param graph: Networkx graph
    :param start: Node in graph
    :return: Dictionary of node,data pairs, data is a tuple containing
    the distance to start node and the previous node in the path to get to start
    """
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


def dijkstra_brute_force(graph, start_nodes):
    """
    Brute force meeting place finding algorithm
    :param graph: Networkx graph
    :param start_nodes: list of nodes to use as starting locations
    :return: Meeting node and paths from each start node to the meeting node
    """
    dijkstra_results = []
    for node in start_nodes:
        dijkstra_results.append(dijkstra(graph, node))

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


def to_coords(locations):
    """
    Get coordinates of given locations
    :param locations: List of strings representing geographical locations
    :return: list of tuples containing coordinates of locations
    """
    coordinates = []
    locator = geopy.Nominatim(user_agent="myGeocoder", scheme='http')

    for location in locations:
        try:
            location_coords = locator.geocode(location)[1]
        except TypeError:
            print("Invalid location: {}".format(location), file=sys.stderr)
            return None
        coordinates.append(location_coords)
    return coordinates


def create_graph(initial_locations):
    """
    Creates a graph to perform meeting place finding algorithm
    :param initial_locations: List of strings containing initial locations
    :return: Networkx graph
    """
    coordinates = to_coords(initial_locations)
    lat = []
    long = []

    for c in coordinates:
        lat.append(c[0])
        long.append(c[1])

    north = max(lat)
    south = min(lat)
    east = max(long)
    west = min(long)

    return ox.graph_from_bbox(north, south, east, west, network_type='drive')


def find_meeting_place(initial_locations, algorithm="bf"):
    """
    Finds meeting place on graph between initial locations
    :param initial_locations: List of strings containing initial locations
    :param algorithm: String describing which algorithm to use
    :return: Returns dictionary of relevant data of meeting place
    """

    G = create_graph(initial_locations)
    coordinates = to_coords(initial_locations)

    if G is None:
        print("Invalid location was specified", file=sys.stderr)
        return None

    if algorithm == "bf":
        initial_nodes = []
        for location in coordinates:
            initial_nodes.append(ox.get_nearest_node(G, location))
        meeting_place, _ = dijkstra_brute_force(G, initial_nodes)

    node_data = dict(G.nodes(data=True))[meeting_place]

    return node_data
