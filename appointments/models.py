from django.db import models
from django.contrib.auth.models import User

class Appointment(models.Model):
	title = models.CharField(max_length=50)
	date = models.DateField('date of the appointment')
	time = models.TimeField('time of the appointment')
	notes = models.TextField(max_length=500)
	author = models.ForeignKey(User)
	def __unicode__(self):
       		return self.title
