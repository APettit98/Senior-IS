from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from .forms import EnterLocationsForm, ContactForm, LocationFormSet
from django.http import HttpResponse, HttpResponseRedirect
import geopy
from geopy import exc
import logging
from .algorithms import find_meeting_place, InvalidLocationError

# Configuration for logging
logging.basicConfig(format="%(asctime)s - %(message)s",
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger("mpfLogger")

# API token for mapbox
mapbox_access_token = 'pk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazNscmN1czcwOHRsM29sanhzcm95ZmlxIn0.pRSXcRGiHLQfxj4AH1_lGg'

globals()['most_recent_enter_locations_form'] = None
globals()['most_recent_location_formset'] = None


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
            request.session['algorithm'] = enter_locations_form.cleaned_data['algorithm']

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
                send_mail(subject, message, email, ['admin@example.com'])
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

    algorithm_options = {'1': 'Brute-Force',
                         '2': "Neighbor-Walk",
                         '3': 'Midpoint-Intersection'}

    locations = request.session['location_input']
    algorithm_idx = request.session['algorithm']

    algorithm = algorithm_options[algorithm_idx]

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

    logger.info("Location list: {}".format(locations))
    try:
        meeting_place, _ = find_meeting_place(location_geocodes, algorithm=algorithm)
    except InvalidLocationError as e:
        logger.error("InvalidLocationError found: {}".format(e.message))
        logger.info("Redirecting to home page with error notification")
        return render(request, 'mpf/index.html', {'form': EnterLocationsForm(), 'error': e.message})

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
