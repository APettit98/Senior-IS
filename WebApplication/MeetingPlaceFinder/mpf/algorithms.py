from multiprocessing import Pool
import osmnx as ox
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

    logger.info("Initializing Dijkstra's algorithm")
    for node in list(graph.nodes()):
        if node != start:
            distances[node] = (infinity, None)

    logger.info("Running Dijkstra's algorithm")
    q = list(graph.nodes())
    while q:
        u = min((distances[i][0], i) for i in (distances.keys() - seen))[1]
        seen.append(u)
        try:
            q.remove(u)
        except ValueError:
            logger.error("Tried to remove node that was not in the list")
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
    logger.info("Beginning execution for dijkstra_brute_force meeting place algorithm")

    # process_pool = Pool(processes=len(start_nodes))
    # dijkstra_results = [process_pool.apply_async(dijkstra, (graph, start_nodes[i])).get() for i in range(len(start_nodes))]
    dijkstra_results = []
    for node in start_nodes:
        logger.info("Running Dijkstra's algorithm on node: {}".format(node))
        dijkstra_results.append(dijkstra(graph, node))
    logger.info("Successfully ran Dijkstra's algorithm on all nodes")

    node_sums = {}
    logger.info("Calculating sums for each node")
    for node in graph.nodes():
        node_sum = 0
        for result in dijkstra_results:
            node_sum += result[node][0]
        node_sums[node] = node_sum

    logger.info("Finding minimum sum")
    meeting_node = min((node_sums[i], i) for i in node_sums.keys())[1]

    paths = {}
    logger.info("Finding path from nodes to meeting node")
    for i in range(len(start_nodes)):
        path = [meeting_node]
        res = dijkstra_results[i]
        current = meeting_node

        while res[current][1] is not None:
            path.insert(0, res[current][1])
            current = res[current][1]
        paths[start_nodes[i]] = path

    return meeting_node, paths


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


def find_meeting_place(initial_locations, algorithm="bf"):
    """
    Finds meeting place on graph between initial locations
    :param initial_locations: List of tuples containing initial location geocodes (lat, long)
    :param algorithm: String describing which algorithm to use
    :return: Returns dictionary of relevant data of meeting place
    """
    logger.info("find_meeting_place begins execution")
    startTime = int(round(time.time() * 1000))
    ox.config(use_cache=True)

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
    if algorithm == "bf":
        initial_nodes = []
        for location in initial_locations:
            initial_nodes.append(ox.get_nearest_node(G, location))
        meeting_place, _ = dijkstra_brute_force(G, initial_nodes)

    logger.info("Meeting place found")
    node_data = dict(G.nodes(data=True))[meeting_place]

    endTime = int(round(time.time() * 1000))
    print("Time elapsed: {}".format(endTime-startTime))
    logger.info("Returning meeting place node data")
    return node_data
