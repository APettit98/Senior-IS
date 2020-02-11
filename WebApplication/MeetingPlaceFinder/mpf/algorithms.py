from multiprocessing import Pool
import osmnx as ox
import networkx as nx
import math
import geopy
from geopy import exc
import sys
import time
import logging
logging.basicConfig(format="%(asctime)s - %(message)s",
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger("mpfLogger")

mapbox_access_token = 'pk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazNscmN1czcwOHRsM29sanhzcm95ZmlxIn0.pRSXcRGiHLQfxj4AH1_lGg'


class InvalidLocationError(Exception):
    """
    Raised when an invalid location is given by the user
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


def get_travel_time(endpoint_1, endpoint_2, edge):
    """
    :param endpoint_1: number representing on endpoint of the edge - used by networkx when this function is used to calculate weight
    :param endpoint_2: number representing on endpoint of the edge - used by networkx when this function is used to calculate weight
    :param edge: dictionary containing edge data
    :return: approximate time in minutes to travel along the edge
    """
    if endpoint_1 and endpoint_2:
        edge = edge[0]

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
    if 'maxspeed' in edge:
        if type(edge['maxspeed']) == str:
            if 'mph' in edge['maxspeed']:
                maxspeed = int(edge['maxspeed'][:-3])
            else:
                maxspeed = int(edge['maxspeed'])
        elif type(edge['maxspeed']) == list:
            maxspeeds = []
            for speed in edge['maxspeed']:
                if 'mph' in speed:
                    maxspeeds.append(int(speed[:-3]))
                else:
                    maxspeeds.append(int(speed))
            maxspeed = max(maxspeeds)
    else:
        road_type = edge['highway']
        if type(road_type) == list:
            road_type = road_type[0]
        if road_type in default_speed_limits:
            maxspeed = default_speed_limits[road_type]
        else:
            maxspeed = 25

    if maxspeed == 0:
        maxspeed = 25

    travel_time = (distance_mi / maxspeed) * 60
    return travel_time


def find_average_coordinate(coords):
    """
    Function which calculates the average of a list of geographic coordinates

    :param coords: list of tuples representing geographic coordinates
    :return: tuple containing the average latitute, longitude coordinate of the list
    """

    lat_sum = 0
    long_sum = 0
    for coord in coords:
        lat_sum += coord[0]
        long_sum += coord[1]

    return lat_sum/len(coords), long_sum/len(coords)


def dijkstra_brute_force(graph, initial_nodes):
    """
    Brute force meeting place finding algorithm
    :param graph: Networkx graph
    :param initial_nodes: list of nodes to use as starting locations
    :return: Meeting node and paths from each start node to the meeting node
    """
    logger.info("Beginning execution for dijkstra_brute_force meeting place algorithm")

    dijkstra_results = []
    paths = []
    for node in initial_nodes:
        logger.info("Running Dijkstra's algorithm on node: {}".format(node))
        dijkstra_output = nx.single_source_dijkstra(graph, node, weight=get_travel_time)
        dijkstra_results.append(dijkstra_output[0])
        paths.append(dijkstra_output[1])

    logger.info("Successfully ran Dijkstra's algorithm on all nodes")

    minimum_node = (None, math.inf)
    logger.info("Calculating sums for each node")
    for node in graph.nodes():
        node_sum = 0
        for result in dijkstra_results:
            node_sum += result[node][0]
        if node_sum < minimum_node[1]:
            minimum_node = (node, node_sum)

    paths = [path[minimum_node] for path in paths]

    return minimum_node, paths


def geographic_mean_neighbor_walk(graph, initial_nodes, mean_coordinate, max_depth, with_paths=False):
    """
    Algorithm which finds meeting place by starting at the geographic middle point and iterating through nodes
    in its neighborhood to see if any are better. If so, it travels to the best node and searches its neighborhood.
    The process repeats until no better node is found or max depth is reached.

    :param graph: Networkx Graph
    :param initial_nodes: list of nodes to use as starting locations
    :param mean_coordinate: Geographic mean of the initial points given by the user
    :param max_depth: Maximum depth of neighbor walk
    :param with_paths: Boolean determining if algorithm will find paths to meeting point
    :return: Meeting node, paths; if with_paths = False then paths=None
    """

    middle_node = ox.get_nearest_node(graph, mean_coordinate)
    dist_to_middle = 0
    found_distances = {}
    for node in initial_nodes:
        found_distances[node] = {middle_node: nx.single_source_dijkstra(graph, node, target=middle_node, weight=get_travel_time)}

    minimum_node = (middle_node, dist_to_middle)
    new_best_found = True
    max_depth = int(max_depth)
    current_depth = 0
    while new_best_found and current_depth < max_depth:
        current_node = minimum_node[0]
        new_best_found = False
        for neighbor in graph.neighbors(current_node):
            node_dist = 0
            for node in initial_nodes:
                if neighbor in found_distances[node]:
                    node_dist += found_distances[node][neighbor][0]

                found_distances[node] = {neighbor:nx.single_source_dijkstra(graph, node, target=neighbor, weight=get_travel_time)}
                node_dist += found_distances[node][neighbor][0]

            if node_dist < minimum_node[1]:
                minimum_node = (neighbor, node_dist)
                new_best_found = True

        current_depth += 1

    if with_paths:
        paths = [nx.dijkstra_path(graph, source, minimum_node[0], weight=get_travel_time) for source in initial_nodes]
    else:
        paths = None

    return minimum_node[0], paths


def midpoint_intersection(graph, initial_locations, with_paths=False):
    """
    Algorithm which finds a meeting place by taking the geographic mean of all but one point and finding the path
    from the removed point to the mean point. This is done for all points, then the algorithm finds nodes which exist
    on at least two paths and check those nodes to determine which one is best. If no such intersections exists, then
    the algorithm checks the mean nodes found and the overall geographic mean.

    :param graph: Networkx Graph
    :param initial_nodes: list of nodes to use as starting locations
    :param with_paths: Boolean determining if algorithm will find paths to meeting point
    :return: Meeting node, paths; if with_paths = False then paths=None
    """
    midpoints = []
    for location in initial_locations:
        copy = initial_locations.copy()
        copy.remove(location)
        midpoints.append(find_average_coordinate(copy))

    initial_nodes = [ox.get_nearest_node(graph, location) for location in initial_locations]
    midpoint_nodes = [ox.get_nearest_node(graph, m) for m in midpoints]

    on_path = nx.dijkstra_path(graph, initial_nodes[0], midpoint_nodes[0], weight=get_travel_time)
    for i in range(1, len(initial_nodes)):
        i_path = nx.dijkstra_path(graph, initial_nodes[i], midpoint_nodes[i], weight=get_travel_time)
        on_path = on_path + i_path

    intersections = [node for node in on_path if on_path.count(node) >= 2]

    if len(intersections) == 1:
        return intersections[0], None

    elif len(intersections) == 0:
        midpoint_nodes.append(ox.get_nearest_node(graph, find_average_coordinate(initial_locations)))
        intersections = midpoint_nodes

    minimum_node = (None, math.inf)
    for node in intersections:
        node_length = 0
        for init in initial_nodes:
            node_length += nx.dijkstra_path_length(graph, init, node, weight=get_travel_time)
        if node_length < minimum_node[1]:
            minimum_node = (node, node_length)

    if with_paths:
        paths = [nx.dijkstra_path(graph, source, minimum_node[0], weight=get_travel_time) for source in initial_nodes]
    else:
        paths = None

    return minimum_node[0], paths


def to_coords(locations, retries=0):
    """
    Get coordinates of given locations
    :param locations: List of strings representing geographical locations
    :param retries: Number of times that the geocoder has retried to find the location,
    this parameter should not be set by the user and is only used by the function itself when an
    exception occurs
    :return: list of tuples containing coordinates of locations
    """
    coordinates = []
    logger.info("Creating geopy locator")
    locator = geopy.geocoders.MapBox(mapbox_access_token)

    for location in locations:
        try:
            logger.info("Attempting to geocode: {}".format(location))
            location_coords = locator.geocode(location, timeout=60)[1]
        except TypeError:
            logger.error("InvalidLocationError caused by: {}".format(location))
            raise InvalidLocationError("Invalid location: {}".format(location))
        except exc.GeocoderTimedOut:
            logger.warning("Geocoder timed out finding: {}".format(location))
            if retries < 5:
                logger.warning("Trying to geocode {} again".format(location))
                to_coords(locations, retries=retries+1)
            else:
                logger.error("Unable to find location: {}".format(location))
                raise InvalidLocationError("Geocoder timed out")

        coordinates.append(location_coords)
        logger.info("Successfully found coordinates for {}: {}".format(location, location_coords))
    return coordinates


def create_graph(initial_locations):
    """
    Creates a graph to perform meeting place finding algorithm
    :param initial_locations: List of tuples containing initial location geocodes (lat, long)
    :return: Networkx graph
    """

    lat = []
    long = []

    for coord in initial_locations:
        lat.append(coord[0])
        long.append(coord[1])

    north = max(lat)
    south = min(lat)
    east = max(long)
    west = min(long)
    logger.info("Bounding box values found: North={}, South={}, East={}, West={}".format(north, south, east, west))
    logger.info("Creating graph from bounding box")
    return ox.graph_from_bbox(north, south, east, west, network_type='drive', truncate_by_edge=True, clean_periphery=True)


def find_meeting_place(initial_locations, algorithm="Brute-Force"):
    """
    Finds meeting place on graph between initial locations
    :param initial_locations: List of tuples containing initial location geocodes (lat, long)
    :param algorithm: String describing which algorithm to use
    :return: Returns dictionary of relevant data of meeting place
    """
    logger.info("find_meeting_place begins execution")
    start_time = int(round(time.time() * 1000))

    try:
        logger.info("Try creating graph")
        G = create_graph(initial_locations)
    except InvalidLocationError as e:
        logger.error("Unable to create a graph")
        raise e

    logger.info("Successfully created graph")

    if G is None:
        print("Invalid location was specified", file=sys.stderr)
        return None

    logger.info("Ready to call meeting place finding algorithm")
    if algorithm == "Brute-Force":
        initial_nodes = []
        for location in initial_locations:
            initial_nodes.append(ox.get_nearest_node(G, location))
        meeting_place, paths = dijkstra_brute_force(G, initial_nodes)

    elif algorithm == "Neighbor-Walk":
        initial_nodes = []
        for location in initial_locations:
            initial_nodes.append(ox.get_nearest_node(G, location))
        middle_node = find_average_coordinate(initial_locations)
        meeting_place, paths = geographic_mean_neighbor_walk(G, initial_nodes, middle_node, 15)

    elif algorithm == "Midpoint-Intersection":
        meeting_place, paths = midpoint_intersection(G, initial_locations)

    logger.info("Meeting place found")
    node_data = dict(G.nodes(data=True))[meeting_place]

    end_time = int(round(time.time() * 1000))
    logger.info("Time elapsed: {}".format(end_time-start_time))
    logger.info("Returning meeting place node data")
    return node_data, paths
