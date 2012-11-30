from django.conf.urls import patterns, include, url
from django.views.generic import ListView, DetailView

from appointments.models import Appointment
from appointments.views import *

from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^list/$', login_required(AppointmentListView.as_view())),
   # url(r'^(?P<id>\d+)/$', 'appointments.views.show'),
    url(r'^(?P<pk>\d+)/$', AppointmentConfirmView.as_view()),
    # url(r'^appointments/edit/(?P<id>\d+)/$', 'appointments.views.edit'), 
    url(r'^create/$', AppointmentCreateView.as_view()),
    url(r'^id/(?P<slug>[a-fA-F0-9]{5})/$', DetailView.as_view(model = Appointment)),
    url(r'^id/$', 'appointments.views.redirectByHash'),
    url(r'^$', 'appointments.views.index'),
)
