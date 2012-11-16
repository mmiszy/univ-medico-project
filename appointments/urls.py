from django.conf.urls import patterns, include, url
from django.views.generic import ListView, DetailView

from appointments.models import Appointment
from appointments.views import *

urlpatterns = patterns('',
    url(r'^list/$', ListView.as_view(
    	model=Appointment,
    	context_object_name = "appointments"
    )),
   # url(r'^(?P<id>\d+)/$', 'appointments.views.show'),
    url(r'^(?P<pk>\d+)/$', AppointmentConfirmView.as_view()),
    # url(r'^appointments/edit/(?P<id>\d+)/$', 'appointments.views.edit'), 
    url(r'^create/$', AppointmentCreateView.as_view()),
    url(r'^getbyhash/(?P<slug>[a-z0-9]+)/$', DetailView.as_view(model = Appointment)),
    url(r'^$', 'appointments.views.index'),
)
