from datetime import timedelta
from django import template
from django.db.models import Count
import pandas

from future_ticket.models import StudentBVB, TicketEvent


register = template.Library()

@register.filter
def count_participants(quota):
    events = TicketEvent.objects.filter(quotas__in=quota.events.all())
    participants_count = StudentBVB.objects.filter(
        event__in=events, 
        school=quota.school,
        is_double=False,
        is_attend=True
    ).count()
    return participants_count

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter()
def filter_events(events, ed_center):
    return events.filter(ed_center=ed_center)

@register.filter()
def get_available_dates(cycle):
    return pandas.date_range(cycle.start_period_date,
            cycle.end_period_date, freq='d')

@register.filter()
def get_event_quota(quota, event):
    return quota.filter(profession=event.profession).exclude(free_quota=0)

@register.filter()
def quota_filter_school(schools, ter_admin):
    return schools.filter(territorial_administration=ter_admin)