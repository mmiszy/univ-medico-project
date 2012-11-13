# Create your views here.
from django.shortcuts import render_to_response
from appointments.models import *
from django.views.generic import CreateView
from django.http import HttpResponse
import json

def index(req):
	appos = Appointment.objects.all()
	return render_to_response('appointments/index.html')

# wymaga znania id lub hasha
def show(req, id):
	try:
		app = Appointment.objects.get(pk=id)
	except Appointment.DoesNotExist:
		raise Http404
	return render_to_response('appointments/show.html', {'app': app})
	
import base64
import hashlib	
def gethash(req, id):
	hasher = hashlib.md5(id)
#	id_hash = base64.urlsafe_b64encode(hasher.digest()[0:5])
	id_hash = hasher.hexdigest()[0:8]
	
	response_data = { }
	response_data['id'] = id 
	response_data['hash'] = id_hash
	return HttpResponse(json.dumps(response_data), mimetype="application/json")
