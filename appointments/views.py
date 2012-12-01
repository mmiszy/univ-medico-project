# Create your views here.
from django.shortcuts import render_to_response
from appointments.models import *
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.http import HttpResponse
from django.forms import ModelForm
from django.http import Http404
from django.forms.widgets import Select
from django.shortcuts import redirect
from collections import OrderedDict

import json
import datetime

class AppointmentCreateForm(ModelForm):
	class Meta:
		model = Appointment
		exclude = ('author', 'status', 'slug')
	
class AppointmentConfirmForm(ModelForm):
	class Meta:
		model = Appointment
		fields = ("status",)
		
		STATUS_CHOICES = (('1', 'confirm'),
                            ('99', 'decline'))
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
		
class AppointmentCalendarView(ListView):
	context_object_name = "appointments"
	template_name="appointments/appointment_calendar.html"

	def get_queryset(self):
		return Appointment.objects.filter(
			date__gte = self.kwargs['date_start']
		).filter(
			date__lte = datetime.datetime.strptime(self.kwargs['date_start'], "%Y-%m-%d")
			 + datetime.timedelta(days = 7)
		)

	def get_context_data(self, **kwargs):
		context = super(AppointmentCalendarView, self).get_context_data(**kwargs)
		date_start = datetime.datetime.strptime(self.kwargs['date_start'], "%Y-%m-%d")

		week = OrderedDict()
		for i in range(7):
			hours = OrderedDict()
			day = (date_start + datetime.timedelta(days = i))
			for j in range(16): # 8 godzin pracy po pol godzin = 16 przedzialow
				dateNtime = day + datetime.timedelta(hours = 8 + j/2, minutes = j%2*30)
				hours[dateNtime.strftime("%H:%M")] = dateNtime
			week[day.strftime("%Y-%m-%d")] = hours

		context['dupa'] = []
		for i in AppointmentCalendarView.get_queryset(self):
			week[i.date.strftime("%Y-%m-%d")][i.time.strftime("%H:%M")] = None
			
		context['week'] = week
		return context
		
class AppointmentCreateView(CreateView):		
	model=Appointment
	success_url="/appointments/id/%(slug)s/"
	form_class = AppointmentCreateForm
	
	def post(self, request, *args, **kwargs):
		self.object = None
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		form.instance.author = request.user
		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)
	
class AppointmentListView(ListView):
   	model=Appointment
   	context_object_name = "appointments"
	
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
	

