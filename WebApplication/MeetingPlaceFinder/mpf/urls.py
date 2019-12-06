from django.urls import path
from . import views


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
]
