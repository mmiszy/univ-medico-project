# coding=utf-8
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django import forms
from django.utils.safestring import mark_safe

def render_response(req, *args, **kwargs):
	""" Działa jak render_to_response,
	ale dodaje RequestContext podanego zapytania """
	if not kwargs.has_key('context_instance'):
		kwargs['context_instance'] = RequestContext(req)
	return render_to_response(*args, **kwargs)

class PrettyForm(forms.Form):
	def as_table(self):
		s = u''
		for field in self.visible_fields():
			if field.field.required:
				star = ' class="required"'
			else:
				star = ''
			s += u'<tr %s><td >%s</td><td>%s</td></tr>'%(star, field.label, field.as_widget())
			if field.help_text is not '':
				s+= u'<tr class="help_text"><td>&nbsp;</td><td>%s</td></tr>'%field.help_text
			for error in field.errors:
				s+= u'<tr class="error"><td>&nbsp;</td><td>%s</td></tr>'%error
		for field in self.hidden_fields():
			s += u'<tr><td colspan="2">%s</td></tr>'%field.as_widget()
		return mark_safe(s)
class PrettyModelForm(forms.ModelForm):
	def as_table(self):
		s = u''
		for field in self.visible_fields():
			if field.field.required:
				star = 'class="required"'
			else:
				star = ''
			s += u'<tr %s><td>%s</td><td>%s</td></tr>'%(star, field.label, field.as_widget())
			if field.help_text is not '':
				s+= u'<tr class="help_text"><td>&nbsp;</td><td>%s</td></tr>'%field.help_text
			for error in field.errors:
				s+= u'<tr class="error"><td>&nbsp;</td><td>%s</td></tr>'%error
		for field in self.hidden_fields():
			s += u'<tr><td colspan="2">%s</td></tr>'%field.as_widget()
		return mark_safe(s)
def option_get(name):
	""" Zwraca wartość opcji o podanej nazwie """
	from frog.admin.models import Option
	try:
		return Option.objects.get(name = name).value
	except Option.DoesNotExist:
		raise ValueError, "Option %s does not exist"%name
def option_set(name, value):
	""" Ustawia wartość opcji o podanej nazwie """
	from frog.admin.models import Option
	try:
		opt = Option.objects.get(name = name)
		opt.value = value
		opt.save()
	except Option.DoesNotExist:
		raise ValueError, "Option %s does not exist"%name
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

