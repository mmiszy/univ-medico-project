from django.conf.urls import patterns, include, url
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView

from appointments.models import Appointment
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

def redirectAfterLogin(req):
    return redirect("/appointments/calendar/", permanent=True)

urlpatterns = patterns('',
    url(r'^$', 'medica.views.index'),
    url(r'^appointments/', include('appointments.urls')),
    
    url(r'^accounts/create/$', CreateView.as_view(
    	model = User,
    	template_name='registration/user_form.html',
    	form_class=UserCreationForm,
    	success_url='/'
    )),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),

    url(r'^accounts/profile/$', redirectAfterLogin),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
