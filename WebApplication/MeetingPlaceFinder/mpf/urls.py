from django.urls import path
from . import views


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    # /
    path('', views.index, name='index'),

    # /about
    path('about/', views.about, name='about'),

    # /contact
    path('contact/', views.contact, name='contact'),

    # /results
    path('results/', views.results, name='results'),

    # /help
    path('help/', views.help, name='help'),

    # success on email send
    path('success/', views.success, name='success'),

    path('sentry-debug/', trigger_error)
]
