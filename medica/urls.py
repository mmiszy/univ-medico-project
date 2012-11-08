from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'medica.views.home', name='home'),
    #url(r'^appointments/', 'appointments.views.index'),
    #url(r'
    url(r'^datetime', 'medica.views.current_datetime'),

    url(r'^appointments/$', 'appointments.views.index'),
    url(r'^appointments/(?P<id>\d+)/$', 'appointments.views.show'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
