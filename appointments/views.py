# Create your views here.
from appointments.models import *
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from django.http import HttpResponse
from django.forms import ModelForm
from django import forms
from django.http import Http404
from django.forms.widgets import Select
from django.shortcuts import redirect, render, render_to_response
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from custom import *

from collections import OrderedDict
import json
import datetime



class AppointmentCreateForm(ModelForm):
	class Meta:
		model = Appointment
		exclude = ('author', 'status', 'slug')
		
class AppointmentDirectCreateForm(ModelForm):
	class Meta:
		model = Appointment
		exclude = ('author', 'status', 'slug', 'date', 'time')
	
class AppointmentConfirmForm(ModelForm):
	class Meta:
		model = Appointment
		fields = ("status",)
		
		STATUS_CHOICES = (('1', 'confirm'),
                            ('99', 'decline'))
		widgets = {
			'status': Select(choices = STATUS_CHOICES),
		}

def user_can_delete_own(request, *args, **kwargs):
	app = Appointment.objects.get(pk = kwargs['pk'])
	return (request.user.has_perm('Appointment.confirm_app') or (request.user.id == app.author.id and app.status == 0))
			
class AppointmentConfirmView(UpdateView):
	template_name="appointments/appointment_confirm_form.html"
	model=Appointment
	success_url="/appointments/list/"
	form_class = AppointmentConfirmForm
	
	def get_context_data(self, **kwargs):
		context = super(AppointmentConfirmView, self).get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['appointment'] = Appointment.objects.get(pk = self.kwargs['pk'])
		return context

	# @method_decorator(ext_user_passes_test(user_can_edit_own))
	@method_decorator(permission_required('Appointment.confirm_app'))
	def dispatch(self, *args, **kwargs):
		 return super(AppointmentConfirmView, self).dispatch(*args, **kwargs)

class AppointmentDeleteView(DeleteView):
	template_name="appointments/appointment_delete_form.html"
	model=Appointment
	success_url="/appointments/list/"
	
	def get_context_data(self, **kwargs):
		context = super(AppointmentDeleteView, self).get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['appointment'] = Appointment.objects.get(pk = self.kwargs['pk'])
		return context

	@method_decorator(ext_user_passes_test(user_can_delete_own, "/appointments/list"))
	def dispatch(self, *args, **kwargs):
		 return super(AppointmentDeleteView, self).dispatch(*args, **kwargs)

def generate_calendar_dict(self, date_start):	# generates dict of taken/free appointments
	date_format = "%Y-%m-%d"
	week = OrderedDict()
	for i in range(6):
		hours = OrderedDict()
		day = (date_start + datetime.timedelta(days = i))
		for j in range(16): # 8 godzin pracy po pol godzin = 16 przedzialow
			dateNtime = day + datetime.timedelta(hours = 8 + j/2, minutes = j%2*30)
			hours[dateNtime.strftime("%H:%M")] = dateNtime
		week[day.strftime(date_format)] = hours

	for i in AppointmentCalendarView.get_queryset(self):
		if i.date.strftime(date_format) in week and i.time.strftime("%H:%M") in week[i.date.strftime(date_format)]:
			if (self.request.user.has_perm('Appointment.confirm_app') or (self.request.user.id == i.author.id)):
				week[i.date.strftime(date_format)][i.time.strftime("%H:%M")] = i
			else:
				week[i.date.strftime(date_format)][i.time.strftime("%H:%M")] = None
	return week

def normalize_date_to_monday(self, date):	# moves the date to nearest monday
	temp_date = datetime.datetime.strptime(date, "%Y-%m-%d")
	if temp_date.strftime("%u") == '7':
		temp_date = temp_date + datetime.timedelta(days = 1)
	else:
		while temp_date.strftime("%u") != '1':
			temp_date = temp_date + datetime.timedelta(days = -1)

	return temp_date.strftime("%Y-%m-%d")

def months_diff(a, b):
	return abs((a.year - b.year) * 12 + a.month - b.month)

class AppointmentCalendarView(ListView):
	context_object_name = "appointments"
	template_name="appointments/appointment_calendar.html"

	def get_queryset(self):
		norm_date = normalize_date_to_monday(self, self.kwargs['date_start'])
		return Appointment.objects.filter(
			date__gte = norm_date
		).filter(
			date__lte = datetime.datetime.strptime(norm_date, "%Y-%m-%d")
			 + datetime.timedelta(days = 7)
		)

	def get_context_data(self, **kwargs):
		context = super(AppointmentCalendarView, self).get_context_data(**kwargs)
		date_start = datetime.datetime.strptime(normalize_date_to_monday(self, self.kwargs['date_start']), "%Y-%m-%d")

		context['week'] = generate_calendar_dict(self, date_start)
		next_week = datetime.datetime.strptime(normalize_date_to_monday(self, self.kwargs['date_start']), "%Y-%m-%d") + datetime.timedelta(days = 7)
		prev_week = datetime.datetime.strptime(normalize_date_to_monday(self, self.kwargs['date_start']), "%Y-%m-%d") + datetime.timedelta(days = -7)

		if months_diff(next_week, datetime.datetime.now()) < 12:
			context['next_week'] = next_week
		if months_diff(prev_week, datetime.datetime.now()) < 12:
			context['prev_week'] = prev_week
		return context
		
class AppointmentCreateView(CreateView):		
	model=Appointment
	success_url="/appointments/id/%(slug)s/"
	form_class = AppointmentCreateForm
	
	def get(self, request, *args, **kwargs):
		self.object = None
		form_class=None
		if self.kwargs and 'date' in self.kwargs:
			form_class = AppointmentDirectCreateForm
		else:
			form_class = self.get_form_class()

		date = self.kwargs['date']
		if date < datetime.datetime.now().strftime("%Y-%m-%d"):
			return render(self.request, "400.html", status=400)

		form = self.get_form(form_class)
		return self.render_to_response(self.get_context_data(form=form))
	
	def post(self, request, *args, **kwargs):
		self.object = None
		form_class=None
		if self.kwargs and 'date' in self.kwargs:
			form_class = AppointmentDirectCreateForm
		else:
			form_class = self.get_form_class()
			
		form = self.get_form(form_class)
		form.instance.author = request.user
		
		if 'date' in self.kwargs:
			form.instance.date = datetime.datetime.strptime(self.kwargs['date'], "%Y-%m-%d")
			form.instance.time = datetime.datetime.strptime(self.kwargs['time'], "%H%M")
		
		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)
	
class AppointmentListView(ListView):
   	context_object_name = "appointments"
   	
   	def get_queryset(self):
   		if self.request.user.has_perm("Appointment.view_all_app"):
   			return Appointment.objects.order_by('-date', '-time').all()
   		else:
   			return Appointment.objects.order_by('-date', '-time').filter(author = self.request.user)

   	def get_context_data(self, **kwargs):
   		context = super(AppointmentListView, self).get_context_data(**kwargs)
   		if self.request.user.has_perm("Appointment.view_all_app"):
   			context['link'] = True
   		return context

#class UserProfileForm(ModelForm):
#	first_name = forms.CharField(label='imie', max_length=30)
#	last_name = forms.CharField(label='imie', max_length=30)
	
#	class Meta:
#		model = PatientCard
#		#fields= ('description',)
#		exclude=('user',)

class UserProfileForm(ModelForm):
    first_name = forms.CharField(label='Prnom', max_length=30)
    last_name = forms.CharField(label='Nom', max_length=30)

    def __init__(self, *args, **kw):
        super(UserProfileForm, self).__init__(*args, **kw)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name

        self.fields.keyOrder = [
            'first_name',
            'last_name',
            'phone_number',
            'description',
            ]

    def save(self, *args, **kw):
        super(UserProfileForm, self).save(*args, **kw)
        self.instance.user.first_name = self.cleaned_data.get('first_name')
        self.instance.user.last_name = self.cleaned_data.get('last_name')
        self.instance.user.save()

    class Meta:
        model = PatientCard
	
class UserEditView(UpdateView):
	form_class=UserProfileForm
	template_name="registration/user_form.html"
	def get_success_url(self):
		return "/accounts/edit/"
	def get_object(self, queryset=None):
		return self.request.user.get_profile()
	
def index(req):
	appos = Appointment.objects.all()
	return render_to_response('appointments/index.html')

def redirectByHash(req):
	try:
		app = Appointment.objects.get(slug=req.GET['hash'])
	except Appointment.DoesNotExist:
		raise Http404
	return redirect("/appointments/id/"+req.GET['hash'], permanent=True)

def redirectToCurrentDate(req):
	return redirect("/appointments/calendar/" + datetime.datetime.now().strftime("%Y-%m-%d"), permanent=False)
 
def show(req, id):
	try:
		app = Appointment.objects.get(pk=id)
	except Appointment.DoesNotExist:
		raise Http404
	return render_to_response('appointments/show.html', {'app': app})
	

