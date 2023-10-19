from datetime import date
from django import template
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter
from django.db.models import Sum, F

from federal_empl_program.models import EducationCenterProjectYear

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def count_quota(ed_centers, duration=None):
    if duration == None:
        return ed_centers.aggregate(quota_sum=Sum(
                F('quota_72') + F('quota_144') + F('quota_256')
            ))['quota_sum']
    return ed_centers.aggregate(quota_sum=Sum(f'quota_{duration}'))['quota_sum']

@register.filter
def filter_strt_center(applications, ed_center):
    return applications.filter(
            education_center=ed_center,
            group__start_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()

@register.filter
def filter_strt_center_72(applications, ed_center):
    return applications.filter(
            education_center=ed_center,
            education_program__duration__lte=72,
            group__start_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()

@register.filter
def filter_strt_center_144(applications, ed_center):
    return applications.filter(
            education_center=ed_center,
            education_program__duration__gt=72,
            education_program__duration__lt=256,
            group__start_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()

@register.filter
def filter_strt_center_256(applications, ed_center):
    return applications.filter(
            education_center=ed_center,
            education_program__duration__gte=256,
            group__start_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()

@register.filter
def filter_strt_center_all(applications, duration=None):
    if duration is None:
        return applications.filter(
            group__start_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()
    if duration == 72:
        return applications.filter(
                education_program__duration__lte=72,
                group__start_date__lte=date.today(),
            ).exclude(csn_prv_date=None).count()
    if duration == 144:
        return applications.filter(
                education_program__duration__gt=72,
                education_program__duration__lt=256,
                group__start_date__lte=date.today(),
            ).exclude(csn_prv_date=None).count()
    if duration == 256:
        return applications.filter(
                education_program__duration__gte=256,
                group__start_date__lte=date.today(),
            ).exclude(csn_prv_date=None).count()

@register.filter
def filter_appl(applications, duration=None):
    if duration == None:
        return applications.count()
    elif duration == 72:
        return applications.filter(education_program__duration__lte=72).count()
    elif duration == 144:
        return applications.filter(education_program__duration__gt=72,
                                        education_program__duration__lt=256).count()
    elif duration == 256:
        return applications.filter(education_program__duration__gte=256).count()
    
@register.filter
def count_procent_all(applications, ed_centers):
    project_year_center = EducationCenterProjectYear.objects.filter(
        ed_center__in=ed_centers)
    quota_sum = project_year_center.aggregate(quota_sum=Sum(
                F('quota_72') + F('quota_144') + F('quota_256')
            ))['quota_sum']
    applications_count = applications.exclude(csn_prv_date=None).count()
    return f'{applications_count}/{quota_sum} ({round(applications_count / quota_sum * 100, 2)}%)'


@register.filter
def count_procent_all_72(applications, ed_centers):
    project_year_center = EducationCenterProjectYear.objects.filter(
        ed_center__in=ed_centers)
    quota_sum = project_year_center.aggregate(quota_sum=Sum('quota_72'))['quota_sum']
    applications_count = applications.filter(
        education_program__duration__lte=72).exclude(csn_prv_date=None).count()
    return f'{applications_count}/{quota_sum} ({round(applications_count / quota_sum * 100, 2)}%)'

@register.filter
def count_procent_all_144(applications, ed_centers):
    project_year_center = EducationCenterProjectYear.objects.filter(
        ed_center__in=ed_centers)
    quota_sum = project_year_center.aggregate(quota_sum=Sum('quota_144'))['quota_sum']
    applications_count = applications.filter(
        education_program__duration__gt=72,
        education_program__duration__lt=256).exclude(csn_prv_date=None).count()
    return f'{applications_count}/{quota_sum} ({round(applications_count / quota_sum * 100, 2)}%)'

@register.filter
def count_procent_all_256(applications, ed_centers):
    project_year_center = EducationCenterProjectYear.objects.filter(
        ed_center__in=ed_centers)
    quota_sum = project_year_center.aggregate(quota_sum=Sum('quota_256'))['quota_sum']
    applications_count = applications.filter(
            education_program__duration__gte=256).exclude(csn_prv_date=None).count()
    return f'{applications_count}/{quota_sum} ({round(applications_count / quota_sum * 100, 2)}%)'



@register.filter
def filter_prvvd(applications, ed_center):
    return applications.filter(education_center=ed_center).exclude(csn_prv_date=None).count()

@register.filter
def filter_center(applications, ed_center):
    return applications.filter(education_center=ed_center).count()

@register.filter
def count_procent(applications, ed_center):
    ed_center = EducationCenterProjectYear.objects.get(
        ed_center=ed_center)
    quota = ed_center.quota_72 + ed_center.quota_144 + ed_center.quota_256
    prvd_quota = applications.filter(
            education_center=ed_center.ed_center
        ).exclude(csn_prv_date=None).count()
    if quota != 0 and prvd_quota != 0:
        return f'{prvd_quota}/{quota} ({round(prvd_quota / quota *100, 2)}%)'
    return f'{prvd_quota}/{quota} (0%)'

@register.filter
def filter_center_72(applications, ed_center):
    return applications.filter(
            education_center=ed_center,
            education_program__duration__lte=72
        ).count()

@register.filter
def count_procent_72(applications, ed_center):
    ed_center = EducationCenterProjectYear.objects.get(
        ed_center=ed_center)
    quota = ed_center.quota_72
    prvd_quota = applications.filter(
            education_center=ed_center.ed_center,
            education_program__duration__lte=72
        ).exclude(csn_prv_date=None).count()
    if quota != 0 and prvd_quota != 0:
        return f'{prvd_quota}/{quota} ({round(prvd_quota / quota *100, 2)}%)'
    return f'{prvd_quota}/{quota} (0%)'

@register.filter
def filter_center_144(applications, ed_center):
    return applications.filter(
            education_center=ed_center,
            education_program__duration__gt=72,
            education_program__duration__lt=256,
        ).count()

@register.filter
def count_procent_144(applications, ed_center):
    ed_center = EducationCenterProjectYear.objects.get(
        ed_center=ed_center)
    quota = ed_center.quota_144
    prvd_quota = applications.filter(
            education_center=ed_center.ed_center,
            education_program__duration__gt=72,
            education_program__duration__lt=256,
        ).exclude(csn_prv_date=None).count()
    if quota != 0 and prvd_quota != 0:
        return f'{prvd_quota}/{quota} ({round(prvd_quota / quota *100, 2)}%)'
    return f'{prvd_quota}/{quota} (0%)'

@register.filter
def filter_center_256(applications, ed_center):
    return applications.filter(
            education_center=ed_center,
            education_program__duration__gte=256
        ).count()

@register.filter
def count_procent_256(applications, ed_center):
    ed_center = EducationCenterProjectYear.objects.get(
        ed_center=ed_center)
    quota = ed_center.quota_256
    prvd_quota = applications.filter(
            education_center=ed_center.ed_center,
            education_program__duration__gte=256
        ).exclude(csn_prv_date=None).count()
    if quota != 0 and prvd_quota != 0:
        return f'{prvd_quota}/{quota} ({round(prvd_quota / quota *100, 2)}%)'
    return f'{prvd_quota}/{quota} (0%)'

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
    return applications.count()

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
    return applications.count()