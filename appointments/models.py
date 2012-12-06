# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

def get_admin():
	return User.objects.get(id = 1)

import base64
import hashlib	
def gethash(id):
	hasher = hashlib.md5(id)
#	id_hash = base64.urlsafe_b64encode(hasher.digest()[0:5])
	id_hash = hasher.hexdigest()[0:5]
	return id_hash

from time import strftime, gmtime
class Appointment(models.Model):
	title = models.CharField('Tytuł', max_length=50)
	date = models.DateField('Data spotkania')
	time = models.TimeField('Godzina spotkania')
	notes = models.TextField('Notatki', max_length=500)
	slug = models.SlugField('URL', max_length=5, db_index = True)
	
	status = models.SmallIntegerField(default = 0, choices = (
		(0, 'New'),
		(1, 'Confirmed'),
		(99, 'Declined'),
		)
	)
	
	author = models.ForeignKey(User)
	def __unicode__(self):
       		return self.title
       		
	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = gethash(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
		super(Appointment, self).save(*args, **kwargs)
	
	class Meta:
		permissions = (
			("confirm_app", "Can confirm and schedule appointment"),
			("view_all_app", "Can view all appointments"),
			("create_more_than_one_app", "Can create more than one appointment")
		)
		
class PatientCard(models.Model):
	user = models.OneToOneField(User)
	description = models.TextField(max_length=2000)

from django.db.models.signals import post_save
def create_patient_card(sender, instance, created, **kwargs):
    if created:
        PatientCard.objects.create(user=instance)
       
post_save.connect(create_patient_card, sender=User)
