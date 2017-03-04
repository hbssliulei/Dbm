from django import template
import datetime

register = template.Library()

@register.filter
def format_date(value):
    if isinstance(value, str):
        return value
    else:
        return value.strftime("%Y-%m-%d")
