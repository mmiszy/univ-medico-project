# Create your views here.
from django.shortcuts import render_to_response
from appointments.models import *
from django.views.generic import CreateView

def index(req):
	appos = Appointment.objects.all()
	return render_to_response('appointments/index.html', {'appos': appos})

def show(req, id):
	try:
		app = Appointment.objects.get(pk=id)
	except Appointment.DoesNotExist:
		raise Http404
	return render_to_response('appointments/show.html', {'app': app})
