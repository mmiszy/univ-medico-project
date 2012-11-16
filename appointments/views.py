# Create your views here.
from django.shortcuts import render_to_response
from appointments.models import *
from django.views.generic import CreateView, UpdateView, DetailView
from django.http import HttpResponse
from django.forms import ModelForm
from django.http import Http404
from django.forms.widgets import Select
from django.shortcuts import redirect

import json

class AppointmentCreateForm(ModelForm):
	class Meta:
		model = Appointment
		exclude = ('author', 'status', 'slug')
	
class AppointmentConfirmForm(ModelForm):
	class Meta:
		model = Appointment
		fields = ("status",)
		
		STATUS_CHOICES = ((1, 'confirm'),
                            (99, 'decline'))
		widgets = {
			'status': Select(choices = STATUS_CHOICES),
		}
			
class AppointmentConfirmView(UpdateView):
	template_name="appointments/appointment_confirm_form.html"
	model=Appointment
	success_url="/appointments/list/"
	form_class = AppointmentConfirmForm
	
	def get_context_data(self, **kwargs):
		context = super(AppointmentConfirmView, self).get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		return context
		
class AppointmentCreateView(CreateView):		
	model=Appointment
	success_url="/appointments/id/%(slug)s/"
	form_class = AppointmentCreateForm
	
def index(req):
	appos = Appointment.objects.all()
	return render_to_response('appointments/index.html')

def redirectByHash(req):
	try:
		app = Appointment.objects.get(slug=req.GET['hash'])
	except Appointment.DoesNotExist:
		raise Http404
	return redirect("/appointments/id/"+req.GET['hash'], permanent=True)
 
def show(req, id):
	try:
		app = Appointment.objects.get(pk=id)
	except Appointment.DoesNotExist:
		raise Http404
	return render_to_response('appointments/show.html', {'app': app})
	

