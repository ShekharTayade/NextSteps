from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

# Vijay: replace space with underscore
@register.filter
@stringfilter
def to_underscore(value):
    return value.replace(" ","_")