from django.shortcuts import render
from .forms import EnterLocationsForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader


def index(request):
    if request.method == 'POST':
        form = EnterLocationsForm(request.POST)
        if form.is_valid():
            locations = form.cleaned_data
            request.session['location_input'] = form.cleaned_data
            return HttpResponseRedirect('/results', {'locations': locations})
    else:
        form = EnterLocationsForm()

    return render(request, 'mpf/index.html', {'form': form})


def about(request):

    return render(request, 'mpf/about.html')


def contact(request):
    return render(request, 'mpf/contact.html')


def results(request):
    locations = request.session['location_input']
    location_list = list(locations.values())[:-1]
    mapbox_private_token = "sk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazJwNWtodXgwMHQwM25ybXo1a3BmY295In0.7oyWAaqB1aJJJp9oGmZPug"
    return render(request, 'mpf/results.html', {'locations': locations, 'mapbox_private_token': mapbox_private_token,
                                                'location_list': location_list})


def help(request):
    return render(request, 'mpf/help.html')
