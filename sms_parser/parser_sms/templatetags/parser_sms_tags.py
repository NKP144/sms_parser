from django import template
from django.template.defaultfilters import floatformat
from parser_sms.models import *

register = template.Library()


@register.simple_tag
def get_verbose_field_name(instance, field_name):
    """
    Returns verbose_name for a field.
    """
    return instance._meta.get_field(field_name).verbose_name


def formatted_float(value):
    value = floatformat(value, arg=4)
    return str(value).replace(',', '.')


register.filter('formatted_float', formatted_float)
