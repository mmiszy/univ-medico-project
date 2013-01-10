# -*- coding: utf-8 -*-
from django import template
import datetime

register = template.Library()

@register.filter()
def field_type(field):
    return field.field.__class__.__name__

@register.filter()
def polish_day(date):
    polish_days = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So']
    return polish_days[int(date.strftime("%u"))-1]

@register.filter()
def isInThePast(date, time):
    try:
        if date and datetime.datetime.now().date() < date:
            return False;
        elif time and datetime.datetime.now().time() < time:
            return False;
        else:
            return True;
    except TypeError:
        if date and datetime.datetime.now() < date:
            return False;
        else:
            return True;

@register.filter()
def getUsername(author):
    return author.username


@register.filter()
def toDatetime(date, time):
    dateNew = datetime.datetime.strptime(date[:10] + (time[:5] or "00:00"), "%Y-%m-%d%H:%M")
    return dateNew



