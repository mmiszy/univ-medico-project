from django.conf.urls import patterns, include, url
from django.views.generic import CreateView, ListView

from appointments.models import Appointment
from appointments.views import AppointmentCreateForm

urlpatterns = patterns('',
	url(r'^$', 'appointments.views.index'),
    url(r'^list/$', ListView.as_view(
    	model=Appointment,
    	context_object_name = "appointments"
    )),
    url(r'^(?P<id>\d+)/$', 'appointments.views.show'),
    # url(r'^appointments/edit/(?P<id>\d+)/$', 'appointments.views.edit'), 
    url(r'^create/$', CreateView.as_view(
        model=Appointment,
        success_url="/appointments",
        form_class = AppointmentCreateForm,
    	)
    ),
    url(r'^gethash/(?P<id>\d+)/$', 'appointments.views.gethash'),
)
