from django import template
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter
from django.db.models import Sum, F

register = template.Library()


@register.filter
def count_quota(ed_centers, duration=None):
    if duration == None:
        return ed_centers.aggregate(quota_sum=Sum(
                F('quota_72') + F('quota_144') + F('quota_256')
            ))['quota_sum']
    return ed_centers.aggregate(quota_sum=Sum(f'quota_{duration}'))['quota_sum']

@register.filter
def filter_appl(applications, duration=None):
    if duration == None:
        return len(applications)
    elif duration == 72:
        return len(applications.filter(education_program__duration__lte=72))
    elif duration == 144:
        return len(applications.filter(education_program__duration__gt=72,
                                        education_program__duration__lt=256))
    elif duration == 256:
        return len(applications.filter(education_program__duration__gte=256))
    
@register.filter
def filter_prvvd_appl(applications, duration=None):
    if duration == None:
        return len(applications.exclude(csn_prv_date=None))
    elif duration == 72:
        return len(applications.filter(education_program__duration__lte=72
                                       ).exclude(csn_prv_date=None))
    elif duration == 144:
        return len(applications.filter(education_program__duration__gt=72,
                                        education_program__duration__lt=256
                                        ).exclude(csn_prv_date=None))
    elif duration == 256:
        return len(applications.filter(education_program__duration__gte=256
                                       ).exclude(csn_prv_date=None))
@register.filter
def count_procent_all(applications, ed_centers):
    quota_sum = ed_centers.aggregate(quota_sum=Sum(
                F('quota_72') + F('quota_144') + F('quota_256')
            ))['quota_sum']
    applications_count = len(applications.exclude(csn_prv_date=None))
    return f'{round(applications_count / quota_sum * 100, 2)}%'


@register.filter
def count_procent_all_72(applications, ed_centers):
    quota_sum = ed_centers.aggregate(quota_sum=Sum('quota_72'))['quota_sum']
    applications_count = len(applications.filter(
        education_program__duration__lte=72).exclude(csn_prv_date=None))
    return f'{round(applications_count / quota_sum * 100, 2)}%'

@register.filter
def count_procent_all_144(applications, ed_centers):
    quota_sum = ed_centers.aggregate(quota_sum=Sum('quota_144'))['quota_sum']
    applications_count = len(applications.filter(
        education_program__duration__gt=72,
        education_program__duration__lt=256).exclude(csn_prv_date=None))
    return f'{round(applications_count / quota_sum * 100, 2)}%'

@register.filter
def count_procent_all_256(applications, ed_centers):
    quota_sum = ed_centers.aggregate(quota_sum=Sum('quota_256'))['quota_sum']
    applications_count = len(applications.filter(
            education_program__duration__gte=256).exclude(csn_prv_date=None))
    return f'{round(applications_count / quota_sum * 100, 2)}%'

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