from datetime import date
from click import Group
from django import template
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter
from django.db.models import Sum, F, Q

from federal_empl_program.models import ProjectYear, FlowStatus, Application


register = template.Library()

find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
check_wrk_status = FlowStatus.objects.get(off_name='Ожидаем трудоустройства')


@register.filter
def check_stage(stage, status):
    return int(stage) > int(status)

@register.filter
def filter_docs(docs, doc_type):
    return docs.filter(doc_type=doc_type)

@register.filter
def count_rows_activity(activity, equipment=False):
    rows = activity.competencies.all().count() + 2
    if equipment:
        for competency in activity.competencies.all():
            equipments = competency.equipment.all().count()
            if equipments != 0:
                rows += equipments
    else:
        for competency in activity.competencies.all():
            indicators = competency.indicators.all().count()
            if indicators != 0:
                rows += indicators + 1
    return rows

@register.filter
def count_rows_competence(competence):
    rows = competence.indicators.all().count()
    if rows == 0:
        return 1
    else:
        return rows + 2
 

@register.filter
def get_groups(invoice):
    from education_centers.models import Group
    return Group.objects.filter(
        students__in=invoice.applications.all()  
    ).distinct()

@register.filter
def get_employement_pay(group):
    if group.employed_count == 0:
        return '0 в счёте (0.00%)'
    return f'{group.employee_paid_count} в счёте ({group.employee_paid_count/group.employed_count * 100:.2f}%)'

@register.filter
def get_employement(group):
    if group.students_count == 0:
        return '0/0 (0.00%) | 0'
    return f'{group.employed_count}/{group.students_count} ({group.employed_count/group.students_count * 100:.2f}%) | {group.check_count}'

@register.filter
def order_by_paid_field(documents):
    return documents.order_by('is_paid')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def float_format(number):
    return "{:.2f}".format(float(number))

@register.filter
def money_format(number):
    return "{:,.2f} ₽".format(float(number)).replace(',', ' ')

@register.filter
def multiply(factor_1, factor_2):
    return "{:,.2f} ₽".format(factor_1 * factor_2).replace(',', ' ')

@register.filter
def count_budget(ed_center, project_year):
    return "{:,.2f} ₽".format(
            ed_center['quota_72'] * project_year.price_72 +\
            ed_center['quota_144'] * project_year.price_144 +\
            ed_center['quota_256'] * project_year.price_256).replace(',', ' ')

@register.filter
def count_budget_remainder(ed_centers):
    project_year = ProjectYear.objects.get(year=2023)
    quota_72 = ed_centers.aggregate(quota_sum=Sum('quota_72'))['quota_sum']
    quota_144 = ed_centers.aggregate(quota_sum=Sum('quota_144'))['quota_sum']
    quota_256 = ed_centers.aggregate(quota_sum=Sum('quota_256'))['quota_sum']
    budget = quota_72 * project_year.price_72 +\
            quota_144 * project_year.price_144 +\
            quota_256 * project_year.price_256
    return "{:,.2f} ₽".format(project_year.full_budget - budget).replace(',', ' ')

@register.filter
def count_budget_summary(ed_centers, duration=None):
    project_year = ProjectYear.objects.get(year=2023)
    if duration == None:
        quota_72 = ed_centers.aggregate(quota_sum=Sum('quota_72'))['quota_sum']
        quota_144 = ed_centers.aggregate(quota_sum=Sum('quota_144'))['quota_sum']
        quota_256 = ed_centers.aggregate(quota_sum=Sum('quota_256'))['quota_sum']
        budget = quota_72 * project_year.price_72 +\
                quota_144 * project_year.price_144 +\
                quota_256 * project_year.price_256
    elif duration == 72:
        budget = ed_centers.aggregate(quota_sum=Sum('quota_72'))['quota_sum'] * project_year.price_72
    elif duration == 144:
        budget = ed_centers.aggregate(quota_sum=Sum('quota_144'))['quota_sum'] * project_year.price_144
    elif duration == 256:
        budget = ed_centers.aggregate(quota_sum=Sum('quota_256'))['quota_sum'] * project_year.price_256
    return "{:,.2f} ₽".format(budget).replace(',', ' ')

@register.filter
def count_average_price(applications):
    applications = applications.exclude(price=None)
    appl_count = applications.count()
    appl_sum = applications.aggregate(price_sum=Sum('price'))['price_sum']
    return "{:,.2f} ₽".format(appl_sum / appl_count).replace(',', ' ')

@register.filter
def count_appl_budget_summary(applications, duration=None):
    project_year = ProjectYear.objects.get(year=2023)
    if duration == None:
        budget = applications.aggregate(price_sum=Sum('price'))['price_sum']
    elif duration == 72:
        budget = applications.filter(
            education_program__duration__lte=72,
        ).aggregate(price_sum=Sum('price'))['price_sum']
    elif duration == 144:
        budget = applications.filter(
            education_program__duration__gt=72,
            education_program__duration__lt=256,
        ).aggregate(price_sum=Sum('price'))['price_sum']
    elif duration == 256:
        budget = applications.filter(
            education_program__duration__gte=256,
        ).aggregate(price_sum=Sum('price'))['price_sum']
    return "{:,.2f} ₽".format(budget).replace(',', ' ')

@register.filter
def count_appl_budget_72(applications, ed_center):
    project_year = ProjectYear.objects.get(year=2023)
    price_sum = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__lte=72,
        ).aggregate(price_sum=Sum('price'))['price_sum']
    if price_sum == None:
        return "0.00 ₽"
    return "{:,.2f} ₽".format(price_sum).replace(',', ' ')

@register.filter
def count_appl_budget_144(applications, ed_center):
    project_year = ProjectYear.objects.get(year=2023)
    price_sum = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gt=72,
            education_program__duration__lt=256,
        ).aggregate(price_sum=Sum('price'))['price_sum']
    if price_sum == None:
        return "0.00 ₽"
    return "{:,.2f} ₽".format(price_sum).replace(',', ' ')

@register.filter
def count_appl_budget_256(applications, ed_center):
    project_year = ProjectYear.objects.get(year=2023)
    price_sum = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gte=256,
        ).aggregate(price_sum=Sum('price'))['price_sum']
    if price_sum == None:
        return "0.00 ₽"
    return "{:,.2f} ₽".format(price_sum).replace(',', ' ')

@register.filter
def count_appl_budget_all(applications, ed_center):
    project_year = ProjectYear.objects.get(year=2023)
    price_sum = applications.filter(
            education_center__id=ed_center['ed_center__id'],
        ).aggregate(price_sum=Sum('price'))['price_sum']
    if price_sum == None:
        return "0.00 ₽"
    return "{:,.2f} ₽".format(price_sum).replace(',', ' ')

@register.filter
def count_quota(ed_centers, duration=None):
    if duration == None:
        return ed_centers.aggregate(quota_sum=Sum(
                F('quota_72') + F('quota_144') + F('quota_256')
            ))['quota_sum']
    return ed_centers.aggregate(quota_sum=Sum(f'quota_{duration}'))['quota_sum']

@register.filter
def filter_strt_center_72(applications, ed_center):
    #quota = ed_center['quota_72']
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__lte=72,
            group__start_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()
    
    return applications_count

@register.filter
def filter_chs_center_72(applications, ed_center):
    quota = ed_center['quota_72']
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__lte=72,
        ).exclude(Q(csn_prv_date=None)| Q(group=None)).count()
    if quota == 0:
        return f'{applications_count}/{quota} (0%)'
    return f'{applications_count}/{quota} ({round(applications_count / quota * 100, 2)}%)'

@register.filter
def filter_strt_center_144(applications, ed_center):
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gt=72,
            education_program__duration__lt=256,
            group__start_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()
    
    return applications_count

@register.filter
def filter_strt_center_256(applications, ed_center):
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gte=256,
            group__start_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()

    return applications_count

@register.filter
def filter_end_center_72(applications, ed_center):
    quota = ed_center['quota_72']
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__lte=72,
            group__end_date__lte=date.today(),
            flow_status__in=[check_wrk_status, find_wrk_status]
        ).exclude(csn_prv_date=None).count()
    
    if quota == 0:
        return f'{applications_count}/{quota} (0%)'
    return f'{applications_count}/{quota} ({round(applications_count / quota * 100, 2)}%)'

@register.filter
def filter_end_center_144(applications, ed_center):
    quota = ed_center['quota_144']
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gt=72,
            education_program__duration__lt=256,
            group__end_date__lte=date.today(),
            flow_status__in=[check_wrk_status, find_wrk_status]
        ).exclude(csn_prv_date=None).count()
    
    if quota == 0:
        return f'{applications_count}/{quota} (0%)'
    return f'{applications_count}/{quota} ({round(applications_count / quota * 100, 2)}%)'

@register.filter
def filter_end_center_256(applications, ed_center):
    quota = ed_center['quota_256']
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gte=256,
            group__end_date__lte=date.today(),
            flow_status__in=[check_wrk_status, find_wrk_status]
        ).exclude(csn_prv_date=None).count()

    if quota == 0:
        return f'{applications_count}/{quota} (0%)'
    return f'{applications_count}/{quota} ({round(applications_count / quota * 100, 2)}%)'

@register.filter
def filter_wrk_center_72(applications, ed_center):
    find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__lte=72,
            flow_status=find_wrk_status
        ).exclude(csn_prv_date=None).count()
    applications_f_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__lte=72,
            group__end_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()
    
    if applications_f_count == 0:
        return f'{applications_count}/{applications_f_count} (0%)'
    return f'{applications_count}/{applications_f_count} ({round(applications_count / applications_f_count * 100, 2)}%)'


@register.filter
def filter_wrk_center_144(applications, ed_center):
    #quota = ed_center['quota_144']
    find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gt=72,
            education_program__duration__lt=256,
            flow_status=find_wrk_status
        ).exclude(csn_prv_date=None).count()
    applications_f_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gt=72,
            education_program__duration__lt=256,
            group__end_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()
    
    if applications_f_count == 0:
        return f'{applications_count}/{applications_f_count} (0%)'
    return f'{applications_count}/{applications_f_count} ({round(applications_count / applications_f_count * 100, 2)}%)'

@register.filter
def filter_wrk_center_256(applications, ed_center):
    #quota = ed_center['quota_256']
    find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
    applications_count = applications.filter(
            flow_status=find_wrk_status,
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gte=256,
        ).exclude(csn_prv_date=None).count()
    applications_f_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gte=256,
            group__end_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()

    if applications_f_count == 0:
        return f'{applications_count}/{applications_f_count} (0%)'
    return f'{applications_count}/{applications_f_count} ({round(applications_count / applications_f_count * 100, 2)}%)'

@register.filter
def filter_strt_center(applications, ed_center):
    #quota = ed_center['quota_256'] + ed_center['quota_144'] + ed_center['quota_72']
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            group__start_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()
    return applications_count

@register.filter
def filter_end_center(applications, ed_center):
    quota = ed_center['quota_256'] + ed_center['quota_144'] + ed_center['quota_72']
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            group__end_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()
    if quota == 0:
        return f'{applications_count}/{quota} (0%)'
    return f'{applications_count}/{quota} ({round(applications_count / quota * 100, 2)}%)'

@register.filter
def filter_wrk_center(applications, ed_center):
    quota = ed_center['quota_256'] + ed_center['quota_144'] + ed_center['quota_72']
    find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
    applications_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            flow_status=find_wrk_status,
        ).exclude(csn_prv_date=None).count()
    applications_f_count = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            group__end_date__lte=date.today(),
        ).exclude(csn_prv_date=None).count()
    if applications_f_count == 0:
        return f'{applications_count}/{applications_f_count} (0%)'
    return f'{applications_count}/{applications_f_count} ({round(applications_count / applications_f_count * 100, 2)}%)'

@register.filter
def filter_strt_center_all_72(applications, ed_centers):
    #quota_sum = ed_centers.aggregate(quota_sum=Sum('quota_72'))['quota_sum']
    applications_count = applications.filter(
                education_program__duration__lte=72,
                group__start_date__lte=date.today(),
            ).exclude(csn_prv_date=None).count()
    return applications_count

@register.filter
def filter_chs_center_all_72(applications, ed_centers):
    quota_sum = ed_centers.aggregate(quota_sum=Sum('quota_72'))['quota_sum']
    applications_count = applications.filter(
                education_program__duration__lte=72,
            ).exclude(Q(csn_prv_date=None)| Q(group=None)).count()
    return f'{applications_count}/{quota_sum} ({round(applications_count / quota_sum * 100, 2)}%)'

@register.filter
def filter_strt_center_all_144(applications, ed_centers):
    applications_count = applications.filter(
                education_program__duration__gt=72,
                education_program__duration__lt=256,
                group__start_date__lte=date.today(),
            ).exclude(csn_prv_date=None).count()
    return applications_count

@register.filter
def filter_strt_center_all_256(applications, ed_centers):
    applications_count = applications.filter(
                education_program__duration__gte=256,
                group__start_date__lte=date.today(),
            ).exclude(csn_prv_date=None).count()
    return applications_count

@register.filter
def filter_end_center_all_72(applications, ed_centers):
    quota_sum = ed_centers.aggregate(quota_sum=Sum('quota_72'))['quota_sum']
    applications_count = applications.filter(
                education_program__duration__lte=72,
                group__end_date__lte=date.today(),
                flow_status__in=[check_wrk_status, find_wrk_status]
            ).exclude(csn_prv_date=None).count()
    return f'{applications_count}/{quota_sum} ({round(applications_count / quota_sum * 100, 2)}%)'

@register.filter
def filter_end_center_all_144(applications, ed_centers):
    quota_sum = ed_centers.aggregate(quota_sum=Sum('quota_144'))['quota_sum']
    applications_count = applications.filter(
                education_program__duration__gt=72,
                education_program__duration__lt=256,
                group__end_date__lte=date.today(),
                flow_status__in=[check_wrk_status, find_wrk_status]
            ).exclude(csn_prv_date=None).count()
    return f'{applications_count}/{quota_sum} ({round(applications_count / quota_sum * 100, 2)}%)'

@register.filter
def filter_end_center_all_256(applications, ed_centers):
    quota_sum = ed_centers.aggregate(quota_sum=Sum('quota_256'))['quota_sum']
    applications_count = applications.filter(
                education_program__duration__gte=256,
                group__end_date__lte=date.today(),
                flow_status__in=[check_wrk_status, find_wrk_status]
            ).exclude(csn_prv_date=None).count()
    return f'{applications_count}/{quota_sum} ({round(applications_count / quota_sum * 100, 2)}%)'

@register.filter
def filter_wrk_center_all_72(applications, ed_centers):
    #quota_sum = ed_centers.aggregate(quota_sum=Sum('quota_144'))['quota_sum']
    find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
    applications_count = applications.filter(
                education_program__duration__lte=72,
                flow_status=find_wrk_status,
            ).exclude(csn_prv_date=None).count()
    applications_f_count = applications.filter(
                education_program__duration__lte=72,
                group__end_date__lte=date.today(),
            ).exclude(csn_prv_date=None).count()
    return f'{applications_count}/{applications_f_count} ({round(applications_count / applications_f_count * 100, 2)}%)'

@register.filter
def filter_wrk_center_all_144(applications, ed_centers):
    #quota_sum = ed_centers.aggregate(quota_sum=Sum('quota_144'))['quota_sum']
    find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
    applications_count = applications.filter(
                education_program__duration__gt=72,
                education_program__duration__lt=256,
                flow_status=find_wrk_status,
            ).exclude(csn_prv_date=None).count()
    applications_f_count = applications.filter(
                education_program__duration__gt=72,
                education_program__duration__lt=256,
                group__end_date__lte=date.today(),
            ).exclude(csn_prv_date=None).count()
    return f'{applications_count}/{applications_f_count} ({round(applications_count / applications_f_count * 100, 2)}%)'

@register.filter
def filter_wrk_center_all_256(applications, ed_centers):
    quota_sum = ed_centers.aggregate(quota_sum=Sum('quota_256'))['quota_sum']
    find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
    applications_count = applications.filter(
                education_program__duration__gte=256,
                flow_status=find_wrk_status,
            ).exclude(csn_prv_date=None).count()
    applications_f_count = applications.filter(
                education_program__duration__gte=256,
                group__end_date__lte=date.today(),
            ).exclude(csn_prv_date=None).count()
    return f'{applications_count}/{applications_f_count} ({round(applications_count / applications_f_count * 100, 2)}%)'

@register.filter
def filter_strt_center_all(applications, ed_centers):
    applications_count = applications.filter(
                group__start_date__lte=date.today(),
            ).exclude(csn_prv_date=None).count()
    return applications_count

@register.filter
def filter_end_center_all(applications, ed_centers):
    quota_sum = ed_centers.aggregate(quota_sum=Sum(
                F('quota_72') + F('quota_144') + F('quota_256')
            ))['quota_sum']
    applications_count = applications.filter(
                group__end_date__lte=date.today(),
            ).exclude(csn_prv_date=None).count()
    return f'{applications_count}/{quota_sum} ({round(applications_count / quota_sum * 100, 2)}%)'

@register.filter
def filter_wrk_center_all(applications, ed_centers):
    find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
    applications_f_count = applications.filter(
        group__end_date__lte=date.today(),
    ).exclude(csn_prv_date=None).count()
    applications_count = applications.filter(
        flow_status=find_wrk_status,
        group__start_date__lte=date.today(),
    ).exclude(csn_prv_date=None).count()
    return f'{applications_count}/{applications_f_count} ({round(applications_count / applications_f_count * 100, 2)}%)'

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
    applications_count = applications.exclude(csn_prv_date=None).count()
    return applications_count


@register.filter
def count_procent_all_72(applications, ed_centers):
    applications_count = applications.filter(
        education_program__duration__lte=72).exclude(csn_prv_date=None).count()
    return applications_count

@register.filter
def count_procent_all_144(applications, ed_centers):
    applications_count = applications.filter(
        education_program__duration__gt=72,
        education_program__duration__lt=256).exclude(csn_prv_date=None).count()
    return applications_count

@register.filter
def count_procent_all_256(applications, ed_centers):
    applications_count = applications.filter(
            education_program__duration__gte=256).exclude(csn_prv_date=None).count()
    return applications_count



@register.filter
def filter_prvvd(applications, ed_center):
    return applications.filter(education_center__id=ed_center['ed_center__id']).exclude(csn_prv_date=None).count()

@register.filter
def filter_center(applications, ed_center):
    return applications.filter(education_center__id=ed_center['ed_center__id']).count()

@register.filter
def count_procent(applications, ed_center):
    prvd_quota = applications.filter(
            education_center__id=ed_center['ed_center__id']
        ).exclude(csn_prv_date=None).count()
    return prvd_quota

@register.filter
def filter_center_72(applications, ed_center):
    return applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__lte=72
        ).count()

@register.filter
def count_procent_72(applications, ed_center):
    prvd_quota = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__lte=72
        ).exclude(csn_prv_date=None).count()
    return prvd_quota

@register.filter
def filter_center_144(applications, ed_center):
    return applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gt=72,
            education_program__duration__lt=256,
        ).count()

@register.filter
def count_procent_144(applications, ed_center):
    prvd_quota = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gt=72,
            education_program__duration__lt=256,
        ).exclude(csn_prv_date=None).count()
    return prvd_quota

@register.filter
def filter_center_256(applications, ed_center):
    return applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gte=256
        ).count()

@register.filter
def count_procent_256(applications, ed_center):
    prvd_quota = applications.filter(
            education_center__id=ed_center['ed_center__id'],
            education_program__duration__gte=256
        ).exclude(csn_prv_date=None).count()

    return prvd_quota

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