from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from .forms import EnterLocationsForm, ContactForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import geopy


def index(request):
    if request.method == 'POST':
        form = EnterLocationsForm(request.POST)
        if form.is_valid():
            locations = form.cleaned_data
            print(locations)
            request.session['location_input'] = form.cleaned_data
            return HttpResponseRedirect('/results', {'locations': locations})
    else:
        form = EnterLocationsForm()

    return render(request, 'mpf/index.html', {'form': form})


def about(request):

    return render(request, 'mpf/about.html')


def contact(request):
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
            return redirect('success')
    return render(request, 'mpf/contact.html', {'form': form})


def success(request):
    return HttpResponseRedirect('/success')


def results(request):
    locations = request.session['location_input']
    location_list = list(locations.values())[:-1]
    locator = geopy.Nominatim(user_agent="myGeocoder")
    location_geocodes = []
    for location in location_list:
        location_code = locator.geocode(location)
        location_geocodes.append(location_code[1])
    mapbox_private_token = "sk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazJwNWtodXgwMHQwM25ybXo1a3BmY295In0.7oyWAaqB1aJJJp9oGmZPug"

    return render(request, 'mpf/results.html', {'locations': locations, 'mapbox_private_token': mapbox_private_token,
                                                'location_list': location_list,
                                                'location_geocodes': location_geocodes})


def help(request):
    return render(request, 'mpf/help.html')
