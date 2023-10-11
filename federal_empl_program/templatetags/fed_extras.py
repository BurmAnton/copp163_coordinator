from django import template
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter
def filter_prvvd(applications, ed_center):
    return len(applications.filter(education_center=ed_center).exclude(csn_prv_date=None))

@register.filter
def filter_center(applications, ed_center):
    return len(applications.filter(education_center=ed_center))

@register.filter
def count_procent(applications, ed_center):
    quota = ed_center.quota_72 + ed_center.quota_144 + ed_center.quota_256
    prvd_quota = len(applications.filter(
            education_center=ed_center.ed_center
        ).exclude(csn_prv_date=None))
    if quota != 0 and prvd_quota != 0:
        return f'{round(prvd_quota / quota *100, 2)}%'
    return "-"

@register.filter
def filter_prvvd_72(applications, ed_center):
    return len(applications.filter(
            education_center=ed_center,
            education_program__duration__lte=72
        ).exclude(csn_prv_date=None))

@register.filter
def filter_center_72(applications, ed_center):
    return len(applications.filter(
            education_center=ed_center,
            education_program__duration__lte=72
        ))

@register.filter
def count_procent_72(applications, ed_center):
    quota = ed_center.quota_72
    prvd_quota = len(applications.filter(
            education_center=ed_center.ed_center,
            education_program__duration__lte=72
        ).exclude(csn_prv_date=None))
    if quota != 0 and prvd_quota != 0:
        return f'{round(prvd_quota / quota *100, 2)}%'
    return "-"

@register.filter
def filter_prvvd_144(applications, ed_center):
    return len(applications.filter(
            education_center=ed_center,
            education_program__duration__gt=72,
            education_program__duration__lt=256,
        ).exclude(csn_prv_date=None))

@register.filter
def filter_center_144(applications, ed_center):
    return len(applications.filter(
            education_center=ed_center,
            education_program__duration__gt=72,
            education_program__duration__lt=256,
        ))

@register.filter
def count_procent_144(applications, ed_center):
    quota = ed_center.quota_144
    prvd_quota = len(applications.filter(
            education_center=ed_center.ed_center,
            education_program__duration__gt=72,
            education_program__duration__lt=256,
        ).exclude(csn_prv_date=None))
    if quota != 0 and prvd_quota != 0:
        return f'{round(prvd_quota / quota *100, 2)}%'
    return "-"

@register.filter
def filter_prvvd_256(applications, ed_center):
    return len(applications.filter(
            education_center=ed_center,
            education_program__duration__gte=256
        ).exclude(csn_prv_date=None))

@register.filter
def filter_center_256(applications, ed_center):
    return len(applications.filter(
            education_center=ed_center,
            education_program__duration__gte=256
        ))

@register.filter
def count_procent_256(applications, ed_center):
    quota = ed_center.quota_256
    prvd_quota = len(applications.filter(
            education_center=ed_center.ed_center,
            education_program__duration__gte=256
        ).exclude(csn_prv_date=None))
    if quota != 0 and prvd_quota != 0:
        return f'{round(prvd_quota / quota *100, 2)}%'
    return "-"

@register.filter
def get_full_price(price):
    return round((price / 0.93 * 100), 0) / 100

@register.filter
def count_appl(applications, params):
    stage, grant = params[0], params[1]
    if grant == None:
        applications = applications.filter(stage=stage)
    else:
        applications = applications.filter(grant=grant, stage=stage)
    return len(applications)

@register.filter
def count_grant_appl(applications, grant_qoute):
    ratio = f'{applications}/{(grant_qoute.qouta_72 + grant_qoute.qouta_144 + grant_qoute.qouta_256)}'
    procent = f'{int(applications / (grant_qoute.qouta_72 + grant_qoute.qouta_144 + grant_qoute.qouta_256) * 100)}%'
    return f'{ratio} ({procent})'

@register.filter
def count_qouta(applications, duration, grant=None):
    if grant == None:
        applications = applications.filter(
            education_program__duration=duration
        )
    else:
        applications = applications.filter(
            education_program__duration=duration,
            grant=grant
        )
    return len(applications)