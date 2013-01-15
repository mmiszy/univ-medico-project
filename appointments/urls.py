from django.conf.urls import patterns, include, url
from django.views.generic import ListView, DetailView

from appointments.models import Appointment
from appointments.views import *

from django.contrib.auth.decorators import login_required

date_regexp = '[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|[3][01])'

urlpatterns = patterns('',
    url(r'^list/$', login_required(AppointmentListView.as_view())),
   # url(r'^(?P<id>\d+)/$', 'appointments.views.show'),
	url(r'^calendar/(?P<date_start>' + date_regexp + ')/$', AppointmentCalendarView.as_view()),
    url(r'^calendar/$', 'appointments.views.redirectToCurrentDate'),
    url(r'^(?P<pk>\d+)/$', AppointmentConfirmView.as_view()),
    url(r'^delete/(?P<pk>\d+)/$', AppointmentDeleteView.as_view()),
    url(r'^edit/(?P<pk>\d+)/$', AppointmentEditView.as_view()),
    url(r'^prefs/$', WorkingHoursSetView.as_view()),
    # url(r'^appointments/edit/(?P<id>\d+)/$', 'appointments.views.edit'), 
    # url(r'^create/$', login_required(AppointmentCreateView.as_view())),
    url(r'^create/(?P<date>' + date_regexp + ')/(?P<time>\d{4})/$', login_required(AppointmentCreateView.as_view())),
    url(r'^id/(?P<slug>[a-fA-F0-9]{5})/$', DetailView.as_view(model = Appointment)),
    url(r'^id/$', 'appointments.views.redirectByHash'),
    # url(r'^$', 'appointments.views.index'),
)
