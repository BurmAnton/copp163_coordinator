from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def get_name_r(head):
    return head.get_name(is_r=True)
