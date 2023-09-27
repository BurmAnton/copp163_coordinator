from datetime import timedelta
from django import template
import pandas

register = template.Library()

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