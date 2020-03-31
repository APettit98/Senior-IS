from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from .forms import EnterLocationsForm, ContactForm, LocationFormSet
from django.http import HttpResponse, HttpResponseRedirect
import geopy
from geopy import exc
from geopy.distance import distance
import osmnx as ox
import networkx as nx
import logging
from .algorithms import find_meeting_place, InvalidLocationError

# Configuration for logging
logging.basicConfig(format="%(asctime)s - %(message)s",
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger("mpfLogger")

# API token for mapbox
mapbox_access_token = 'pk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazNscmN1czcwOHRsM29sanhzcm95ZmlxIn0.pRSXcRGiHLQfxj4AH1_lGg'

# Globals used to pass form information between views
# This is necessary to properly handle errors
globals()['most_recent_enter_locations_form'] = None
globals()['most_recent_location_formset'] = None


def create_graph_highways(initial_locations, retries=0):
    """
    This function is used to create a graph based on the us highways, with all roads within 10 miles of the initial
    locations. This is done instead of downloading the entire bounding box with these locations and is faster when the
    distance between locations exceeds ~150 miles.

    Attempts to form a graph where all initial locations are in the same connected component, will try up to three times
    to create such a graph, each time expanding the radius around the initial locations. If no such graph can be formed
    than an error is raised.

    :param initial_locations: list of user-given location geocodes
    :param retries: number of times graph creation has been tried
    :return: Graph
    """
    initial_nodes = []
    lat = []
    long = []
    for location in initial_locations:
        lat.append(location[0])
        long.append(location[1])

    one_mile = 0.0167
    north = max(lat) + one_mile
    south = min(lat) - one_mile
    east = max(long) + one_mile
    west = min(long) - one_mile
    nodes_to_add = [node for node in globals()['highway_graph'].nodes() if
                    west <= globals()['highway_graph'].nodes(data=True)[node]['x'] <= east and
                    south <= globals()['highway_graph'].nodes(data=True)[node]['y'] <= north]

    G = globals()['highway_graph'].__class__()
    G.add_nodes_from((n, globals()['highway_graph'].nodes[n]) for n in nodes_to_add)
    G.add_edges_from((n, nbr, key, d)
                     for n, nbrs in globals()['highway_graph'].adj.items() if n in nodes_to_add
                     for nbr, keydict in nbrs.items()if nbr in nodes_to_add
                     for key, d in keydict.items())

    for location in initial_locations:
        new_g = ox.graph_from_point(location, distance=16000 * (retries+1), distance_type='network',
                                    network_type='drive', clean_periphery=True, truncate_by_edge=True)
        G = nx.compose(G, new_g)

    for location in initial_locations:
        initial_nodes.append(ox.get_nearest_node(G, location))

    path_exists = False
    cc = nx.connected_components(G.to_undirected())
    for comp in cc:
        in_cc = [node for node in initial_nodes if node in comp]
        if len(in_cc) == len(initial_nodes):
            path_exists = True
            break
    if path_exists:
        return G

    elif retries >= 3:
        logger.warning("Not able to create a connected graph with locations: {}".format(initial_locations))
        raise Exception("Not able to create a connected graph with locations: {}".format(initial_locations))

    else:
        return create_graph_highways(initial_locations, retries=retries+1)


def index(request):
    """
    index view
    This view is the main page of the website, it handles the form where users enter the locations they want to find
    a meeting place between

    This function also handles cases where an error occurred and uses global variables to retain locations when errors
    do occur
    """
    if request.method == 'POST':
        logger.info("Form posted")
        enter_locations_form = EnterLocationsForm(request.POST)
        location_formset = LocationFormSet(request.POST)
        if enter_locations_form.is_valid() and location_formset.is_valid():
            logger.info("Form is valid")
            globals()['most_recent_enter_locations_form'] = enter_locations_form
            globals()['most_recent_location_formset'] = location_formset

            logger.info("Enter_Locations_Form: {}".format(enter_locations_form.cleaned_data))
            locations = [address['location'] for address in location_formset.cleaned_data]
            request.session['location_input'] = locations
            alg_input = enter_locations_form.cleaned_data['algorithm']
            if alg_input >= 50:
                request.session['algorithm'] = "Brute-Force"
            elif 25 <= alg_input < 50:
                request.session['algorithm'] = "Path-Traversal"
            else:
                request.session['algorithm'] = "Geographic-Mean"

            logger.info("Redirecting to results with locations: {}".format(locations))

            return HttpResponseRedirect('/results', {'locations': locations})
        else:
            logger.warning("Invalid form")
    else:
        logger.info("Displaying blank form")

        enter_locations_form = EnterLocationsForm()
        location_formset = LocationFormSet()

    if 'error' in request.session:
        error = request.session['error']
        del request.session['error']

        enter_locations_form = globals()['most_recent_enter_locations_form']
        location_formset = globals()['most_recent_location_formset']
        return render(request, 'mpf/index.html', {'enter_locations_form': enter_locations_form,
                                                  'location_formset': location_formset,
                                                  'error': error})

    return render(request, 'mpf/index.html', {'enter_locations_form': enter_locations_form,
                                              'location_formset': location_formset,
                                              'error': False})


def about(request):
    """
    Displays the about page
    """
    logger.info("User selected about page")
    return render(request, 'mpf/about.html')


def contact(request):
    """
    Displays the contact page with corresponding form
    Sends email if it is valid, currently sends emails to the console
    """
    logger.info("User selected contact page")
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                logger.info("Sending email message")
                send_mail(subject, message, email, ['aedan@pettitpack.net'], fail_silently=False)
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return HttpResponseRedirect('/success')
    return render(request, 'mpf/contact.html', {'form': form})


def success(request):
    """
    Displays a success message when a user successfully sends an email
    """
    return render(request, 'mpf/success.html')


def results(request):
    """
    Displays a map with the user entered locations and a meeting place

    This function also handles finding the meeting place itself and geocoding the locations
    """
    logger.info("Creating results view")

    locations = request.session['location_input']
    algorithm = request.session['algorithm']

    logger.info("Geocoding user-given locations")
    locator = geopy.geocoders.MapBox(mapbox_access_token)
    location_geocodes = []
    for location in locations:
        try:
            location_code = locator.geocode(location, timeout=60)
        except exc.GeocoderTimedOut:
            try:
                location_code = locator.geocode(location, timeout=60)
            except exc.GeocoderTimedOut as e:
                request.session['error'] = e.message
                return HttpResponseRedirect('/')
        if location_code is None:
            logger.warning("Invalid location specified: {}".format(location))
            request.session['error'] = "Invalid location: {}".format(location)
            return HttpResponseRedirect('/')

        logger.info("Successfully geocoded {}: {}".format(location, location_code))
        location_geocodes.append(location_code[1])

    # Calculate distance between initial locations in order to determine if highways graph should be used
    i = 0
    distance_between = 0
    for coord1 in location_geocodes[:-1]:
        for coord2 in location_geocodes[i+1:]:
            distance_between += float(distance(coord1, coord2).miles)
        i += 1

    logger.info("Location list: {}".format(locations))
    logger.info("Distance between locations: {}".format(distance_between))

    if distance_between < 150.0:
        try:
            meeting_place, _ = find_meeting_place(location_geocodes, algorithm=algorithm)
        except InvalidLocationError as e:
            logger.error("InvalidLocationError found: {}".format(e.message))
            logger.info("Redirecting to home page with error notification")
            request.session['error'] = e.message
            return render(request, 'mpf/index.html', {'form': EnterLocationsForm(), 'error': e.message})
    else:
        try:
            logger.info("Creating graph from highways")
            G = create_graph_highways(location_geocodes)
            meeting_place, _ = find_meeting_place(location_geocodes, algorithm=algorithm, graph=G)
        except Exception as e:
            logger.error("Exception found: {}".format(e))
            logger.info("Redirecting to home page with error notification")
            request.session['error'] = str(e)
            return render(request, 'mpf/index.html', {'form': globals()['most_recent_enter_locations_form'], 'error': e})

    logger.info("Found meeting place: {}".format(meeting_place))

    location_geocodes.append((meeting_place['y'], meeting_place['x']))

    logger.info("Reverse geocoding meeting place")
    meeting_place_text = locator.reverse((meeting_place['y'], meeting_place['x'])).address
    logger.info("Meeting place {}".format(meeting_place_text))
    locations.append(meeting_place_text)

    mapbox_private_token = "sk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazJwNWtodXgwMHQwM25ybXo1a3BmY295In0.7oyWAaqB1aJJJp9oGmZPug"
    logger.info("Rendering results page with user-given locations and meeting place")

    return render(request, 'mpf/results.html', {'locations': locations, 'mapbox_private_token': mapbox_private_token,
                                                'location_list': locations,
                                                'location_geocodes': location_geocodes})


def help(request):
    """
    Displays the help page
    """
    return render(request, 'mpf/help.html')
