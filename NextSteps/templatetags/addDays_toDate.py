import datetime

from django import template

register = template.Library()

@register.filter
def plus_days(value, days):
    return value + datetime.timedelta(days=days)
	

@register.filter()
def addToToday(days):
   newDate = datetime.date.today() + datetime.timedelta(days=days)
   return newDate