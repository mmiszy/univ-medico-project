# -*- coding: utf-8 -*-
from django import template
import datetime

register = template.Library()

@register.filter()
def field_type(field):
    return field.field.__class__.__name__

@register.filter()
def polish_day(val):
    polish_days = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So']
    return polish_days[int(val)-1]

@register.filter()
def isInThePast(date, time):
    if datetime.datetime.now().date() < date:
        return False;
    elif datetime.datetime.now().time() < time:
        return False;
    else:
        return True;
