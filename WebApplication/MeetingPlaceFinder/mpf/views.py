from django.shortcuts import render
from .forms import EnterLocationsForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader


def index(request):
    if request.method == 'POST':
        form = EnterLocationsForm(request.POST)
        if form.is_valid():
            request.session['location_input'] = form.cleaned_data
            return HttpResponseRedirect('/results')
    else:
        form = EnterLocationsForm()

    return render(request, 'mpf/index.html', {'form': form})


def about(request):
    print(request.session.get('location_input'))
    return render(request, 'mpf/about.html')


def contact(request):
    return render(request, 'mpf/contact.html')


def results(request):
    return render(request, 'mpf/results.html')


def help(request):
    return render(request, 'mpf/help.html')
