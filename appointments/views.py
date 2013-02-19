# -*- coding: utf-8 -*-
# Create your views here.
from appointments.models import *
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView, FormView
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

from utils import *

def user_can_modify_own(request, *args, **kwargs):
	app = Appointment.objects.get(pk = kwargs['pk'])
	return (request.user.has_perm('Appointment.confirm_app') or (request.user.id == app.author.id))
	
def user_can_delete_own(request, *args, **kwargs):
	app = Appointment.objects.get(pk = kwargs['pk'])
	return (request.user.has_perm('Appointment.confirm_app') or (request.user.id == app.author.id and app.status == 0))

from utils import *
class WorkingHoursSetForm(forms.Form):
	#start = forms.TimeField(label=u"Poczatkowa godzina pracy", initial=lambda: datetime.datetime.strptime(option_get("start_work_hours"), "%H:%M"))
	#end = forms.TimeField(label=u"Koncowa godzina pracy", initial=lambda: datetime.datetime.strptime(option_get("end_work_hours"), "%H:%M"))
	start = forms.CharField(label=u"Poczatkowa godzina pracy", initial=lambda: option_get("start_work_hours"))
	end = forms.CharField(label=u"Koncowa godzina pracy", initial=lambda: option_get("end_work_hours"))
	
	def save(self):
		cd = self.cleaned_data
		option_set("start_work_hours", cd['start'])
		option_set("end_work_hours", cd['end'])

class WorkingHoursSetView(FormView):
	form_class=WorkingHoursSetForm
	success_url="/"
	template_name="appointments/prefs_form.html"
	
	def form_valid(self, form):
		form.save()
		return super(WorkingHoursSetView, self).form_valid(form)
		
	@method_decorator(permission_required('Appointment.confirm_app'))
	def dispatch(self, *args, **kwargs):
		 return super(WorkingHoursSetView, self).dispatch(*args, **kwargs)

class AppointmentCreateForm(ModelForm):
	class Meta:
		model = Appointment
		exclude = ('author', 'status', 'slug', 'doctor_notes')
		
class AppointmentDirectCreateForm(ModelForm):
	class Meta:
		model = Appointment
		exclude = ('author', 'status', 'slug', 'date', 'time', 'doctor_notes')
	
class AppointmentConfirmForm(ModelForm):
	class Meta:
		model = Appointment
		fields = ("status",)
		
		STATUS_CHOICES = (('1', 'confirm'),
                            ('99', 'decline'))
		widgets = {
			'status': Select(choices = STATUS_CHOICES),
		}
		
class AppointmentPatientEditForm(ModelForm):
	class Meta:
		model = Appointment
		fields = ('notes',)
		
class AppointmentDoctorEditForm(ModelForm):
	class Meta:
		model = Appointment
		fields = ('notes','doctor_notes')	
		# wywiad, badania fizykalne, rozpoznanie, zalecenia, recepty, badania
		# laboratoryjne i obrazowe, informacja zwrotna
		# 
		# tylko zalecenia i recepty + informacja zwrotna widoczne dla pacjenta,
		# ale wszystkie dla lekarza
		# 
		# lekarz nie może edytować appointmentów po 1. dniu od ich
		# odbycia
		# 
		# + superuser, który może wszystko

class AppointmentEditView(UpdateView):
	model=Appointment
	template_name="appointments/appointment_confirm_form.html"
	success_url="/appointments/list/"
	
	def get_form_class(self):
		if self.request.user.has_perm('Appointment.confirm_app'):
			return AppointmentDoctorEditForm
		else:
			return AppointmentPatientEditForm
	
	@method_decorator(ext_user_passes_test(user_can_modify_own, "/appointments/list"))
	def dispatch(self, *args, **kwargs):
		 return super(AppointmentEditView, self).dispatch(*args, **kwargs)
			
class AppointmentConfirmView(UpdateView):
	template_name="appointments/appointment_confirm_form.html"
	model=Appointment
	success_url="/appointments/list/"
	form_class = AppointmentConfirmForm
	
	def get_context_data(self, **kwargs):
		context = super(AppointmentConfirmView, self).get_context_data(**kwargs)
		context['slug'] = self.kwargs['slug']
		context['appointment'] = Appointment.objects.get(slug = self.kwargs['slug'])
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
	start_work_hours = datetime.datetime.strptime(option_get("start_work_hours"), "%H:%M")
	end_work_hours = datetime.datetime.strptime(option_get("end_work_hours"), "%H:%M")
	hours_diff = end_work_hours - start_work_hours
	for i in range(6):
		hours = OrderedDict()
		day = (date_start + datetime.timedelta(days = i))
		vacation = Vacation.objects.filter(date = day)
		for j in range(hours_diff.seconds/1800):
			dateNtime = day + datetime.timedelta(hours = start_work_hours.hour + j/2, minutes = start_work_hours.minute + j%2*30)
			hours[dateNtime.strftime("%H:%M")] = dateNtime
			
			# If there's a vacation on that day, don't process it
			if vacation:
				hours[dateNtime.strftime("%H:%M")] = None
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
   			context['admin'] = True
   		return context


#class UserListAllAppointments/Info etc. etc.


# powrót do kalendarza na każdym ekranie

   	

#class UserProfileForm(ModelForm):
#	first_name = forms.CharField(label='imie', max_length=30)
#	last_name = forms.CharField(label='imie', max_length=30)
	
#	class Meta:
#		model = PatientCard
#		#fields= ('description',)
#		exclude=('user',)

class UserProfileForm(ModelForm):
    first_name = forms.CharField(label='Imie', max_length=30)
    last_name = forms.CharField(label='Nazwisko', max_length=30)

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
        # pesel, email

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
        
class VacationAddForm(forms.Form):
	start = forms.CharField("Poczatek")
	end = forms.CharField("Koniec")
	
	def save(self):
		cd = self.cleaned_data
		start = datetime.datetime.strptime(cd['start'], "%Y-%m-%d")
		end = datetime.datetime.strptime(cd['end'], "%Y-%m-%d")
		
		d = start
		delta = datetime.timedelta(days=1)
		while d <= end:
			if not Vacation.objects.filter(date = d):
				Vacation.objects.create(date = d)
			d += delta
		
	class Meta:
		model = Vacation

class VacationAddView(FormView):
	template_name="appointments/vacation_form.html"
	success_url = "/appointments/vacations"
	form_class=VacationAddForm
	
	def form_valid(self, form):
		form.save()
		return super(VacationAddView, self).form_valid(form)
		
	@method_decorator(permission_required('Appointment.confirm_app'))
	def dispatch(self, *args, **kwargs):
		 return super(VacationAddView, self).dispatch(*args, **kwargs)

	@method_decorator(permission_required('Appointment.confirm_app'))
	def dispatch(self, *args, **kwargs):
		return super(VacationAddView, self).dispatch(*args, **kwargs)

class VacationListView(ListView):
   	context_object_name = "vacations"
   	model = Vacation

	@method_decorator(permission_required('Appointment.confirm_app'))
	def dispatch(self, *args, **kwargs):
		return super(VacationListView, self).dispatch(*args, **kwargs)

class VacationDeleteForm(forms.Form):
	start = forms.CharField("Poczatek")
	end = forms.CharField("Koniec")
	
	def save(self):
		cd = self.cleaned_data
		start = datetime.datetime.strptime(cd['start'], "%Y-%m-%d")
		end = datetime.datetime.strptime(cd['end'], "%Y-%m-%d")
		
		d = start
		delta = datetime.timedelta(days=1)
		while d <= end:
			if Vacation.objects.filter(date = d):
				Vacation.objects.filter(date = d).delete()
			d += delta
		
	class Meta:
		model = Vacation

class VacationDeleteView(FormView):
	template_name="appointments/vacation_delete_form.html"
	success_url = "/appointments/vacations"
	form_class=VacationDeleteForm
	
	def form_valid(self, form):
		form.save()
		return super(VacationDeleteView, self).form_valid(form)

	@method_decorator(permission_required('Appointment.confirm_app'))
	def dispatch(self, *args, **kwargs):
		return super(VacationDeleteView, self).dispatch(*args, **kwargs)

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
	

