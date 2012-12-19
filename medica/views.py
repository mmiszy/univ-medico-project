from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from appointments.models import *
import datetime

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def index(req):
	return render_to_response('index.html',context_instance=RequestContext(req))
