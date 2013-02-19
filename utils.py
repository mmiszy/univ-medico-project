# coding=utf-8
from django import forms
from django.template import Context
from django.utils.safestring import mark_safe
from appointments.models import Option

def option_get(name):
	""" Zwraca wartość opcji o podanej nazwie """
	try:
		return Option.objects.get(name = name).value
	except Option.DoesNotExist:
		#raise ValueError, "Option %s does not exist"%name
		return ""
def option_set(name, value):
	""" Ustawia wartość opcji o podanej nazwie """
	try:
		opt = Option.objects.get(name = name)
		opt.value = value
		opt.save()
	except Option.DoesNotExist:
		opt = Option(name = name, value = value)
		opt.save()
#		raise ValueError, "Option %s does not exist"%name
		
def send_email(subject, template_text, template_html, recipients, context = Context):
	""" Wysyła email z domyślnego adresu do podanych odbiorców.
	Zawartością jest podany szablon wyrenderowany z podanym kontekstem"""
	from django.core.mail import EmailMultiAlternatives
	from django.conf import settings
	from django.template import loader
	tpl_html = loader.get_template(template_html)
	tpl_txt = loader.get_template(template_text)
	msg = EmailMultiAlternatives(
		subject,
		tpl_txt.render(context),
		settings.DEFAULT_FROM_EMAIL,
		recipients
		)
	msg.attach_alternative(tpl_html.render(context), "text/html")
	msg.send()

