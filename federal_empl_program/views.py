import calendar
import json
import random
import string
from datetime import date, datetime, timedelta
from email.mime import application

import unidecode
from dateutil.relativedelta import relativedelta
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models import (Avg, Case, Count, IntegerField, Q, Sum, Value,
                              When)
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from pysendpulse.pysendpulse import PySendPulse

from citizens.models import Citizen
from education_centers.models import (AbilimpicsWinner, Competence,
                                      EducationCenter, EducationProgram, Group)
from federal_empl_program.imports import import_applications
from federal_empl_program.models import (Application, CitizenApplication,
                                         ClosingDocument, EdCenterQuotaRequest,
                                         EducationCenterProjectYear,
                                         FlowStatus, Grant,
                                         ProgramQuotaRequest, ProjectYear,
                                         QuotaRequest)
from users.models import User

from . import exports
from .forms import ActChangeDataForm, ActDataForm, BillDataForm, ImportDataForm
from .utils import get_applications_plot, get_flow_applications_plot


@login_required
def index(request):
    return HttpResponseRedirect(reverse('login'))

@login_required
@csrf_exempt
def import_flow(request):
    form = ImportDataForm()
    message = None
    if request.method == "POST":
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            message = import_applications(form, 2023)
            cache.clear()
        else:
            data = form.errors

    return render(request, "federal_empl_program/import_flow.html",{
        'form': form,
        'message': message
    })

@csrf_exempt
def login(request):
    message = None
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
        if user is None:
            message = "Неверный логин и/или пароль."

    if request.user.is_authenticated:
        winner = AbilimpicsWinner.objects.filter(email=request.user.email)
        if len(winner) > 0:
            return HttpResponseRedirect(reverse("abilimpics"))
        if request.user.role == 'CNT':
            return HttpResponseRedirect(reverse(
                "groups_list", 
                kwargs={'year': 2023})
            )
        if request.user.role == 'CO':
            ed_center_id = request.user.education_centers.first().id
            return HttpResponseRedirect(reverse(
                "ed_center_application", 
                kwargs={'ed_center_id': ed_center_id})
            )
        return HttpResponseRedirect(reverse("admin:index"))

    return render(request, "federal_empl_program/login.html", {
        "message": message,
        "page_name": "ЦОПП СО | Авторизация"
    })

@login_required
def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return HttpResponseRedirect(reverse("login"))


def applications_dashboard(request, year=2023):
    project_year = get_object_or_404(ProjectYear, year=year)
    ed_centers = EducationCenterProjectYear.objects.filter(
        project_year=project_year)
    applications = Application.objects.filter(
        project_year=project_year, appl_status__in=['ADM', 'SED', 'COMP'])

    competencies = Competence.objects.filter(
        competence_applicants__in=applications).distinct()
    
    programs = EducationProgram.objects.filter(
        programm_applicants__in=applications).distinct()
    
    grants = Grant.objects.filter(project_year=project_year)
    if grants != None:
        grant_1 = grants.filter(grant_name='Грант 1')[0]
        grant_1_sum = grant_1.qouta_72 + grant_1.qouta_144 + grant_1.qouta_256
        ratio = f'{applications.filter(grant="1", appl_status="COMP").count()}/{(grant_1_sum)}'
        procent = round(applications.filter(grant="1", appl_status="COMP").count() / (grant_1_sum) * 100, 2)
        grant_1_full = f'{ratio} ({procent}%)'
        grant_2 = grants.filter(grant_name='Грант 2')[0]
        grant_2_sum = grant_2.qouta_72 + grant_2.qouta_144 + grant_2.qouta_256
        ratio = f'{applications.filter(grant="2", appl_status="COMP").count()}/{(grant_2_sum)}'
        procent = round(applications.filter(grant="2", appl_status="COMP").count() / (grant_2_sum) * 100, 2)
        grant_2_full = f'{ratio} ({procent}%)'
        grants_full_sum = grant_1_sum + grant_2_sum
        ratio = f'{applications.filter(appl_status="COMP").count()}/{(grants_full_sum)}'
        procent = round(applications.filter(appl_status="COMP").count() / (grants_full_sum) * 100, 2)
        grants_full = f'{ratio} ({procent}%)'
        grant_y = grants.filter(grant_name='Молодёжь')[0]
    else:
        grant_1 = None
        grant_2 = None
        grant_y = None
    
    start_month = 3
    end_month = 12
    monthly_applications = {}
    monthly_applications['Подали заявку'] = []
    monthly_applications['Завершили обучение'] = []
    months = []
    comp_applications = applications.filter(appl_status="COMP")
    for month in range(start_month, end_month+1):
        start_date = datetime(year, month, 1)
        next_month = start_date.replace(day=28) + timedelta(days=4)
        res = next_month - timedelta(days=next_month.day)
        end_date = res.date()
        monthly_applications['Подали заявку'].append(
            comp_applications.filter(
                creation_date__gte=start_date,
                creation_date__lte=end_date,
            ).count()
        )
        monthly_applications['Завершили обучение'].append(
            comp_applications.filter(
                change_status_date__gte=start_date,
                change_status_date__lte=end_date,
            ).count()
        )
        months.append(calendar.month_name[month])
        
    chart = get_applications_plot(months, monthly_applications)

    return render(request, 'federal_empl_program/applications_dashboard.html', {
        'chart': chart,
        'project_year': project_year,
        'ed_centers_count': len(ed_centers),
        'competencies_count': len(competencies),
        'programs_count': len(programs),
        'applications': applications,
        'grant_1': grant_1,
        'grant_1_full': grant_1_full,
        'grant_2': grant_2,
        'grant_2_full': grant_2_full,
        'grant_y': grant_y,
        'grants_full': grants_full,
        'adm_grant_1': applications.filter(grant='1', appl_status='ADM'),
        'adm_grant_2': applications.filter(grant='2', appl_status='ADM'),
        'sed_grant_1': applications.filter(grant='1', appl_status='SED'),
        'sed_grant_2': applications.filter(grant='2', appl_status='SED'),
        'comp_grant_1': applications.filter(grant='1', appl_status='COMP'),
        'comp_grant_2': applications.filter(grant='2', appl_status='COMP'),
        'grant_1_72': applications.filter(
            grant='1', education_program__duration=72, appl_status='COMP'),
        'grant_1_144': applications.filter(
            grant='1', education_program__duration=144, appl_status='COMP'),
        'grant_1_256': applications.filter(
            grant='1', education_program__duration=256, appl_status='COMP'),
        'grant_2_72': applications.filter(
            grant='2', education_program__duration=72, appl_status='COMP'),
        'grant_2_144': applications.filter(
            grant='2', education_program__duration=144, appl_status='COMP'),
        'grant_2_256': applications.filter(
            grant='2', education_program__duration=256, appl_status='COMP'),
        'duration_72': applications.filter(
            education_program__duration=72, appl_status='COMP'),
        'duration_144': applications.filter(
            education_program__duration=144, appl_status='COMP'),
        'duration_256': applications.filter(
            education_program__duration=256, appl_status='COMP'),
    })

@cache_page(None, key_prefix="flow")
@csrf_exempt
def flow_appls_dashboard(request, year=2023):
    project_year = get_object_or_404(ProjectYear, year=year)
    ed_centers_year = EducationCenterProjectYear.objects.filter(
        project_year=project_year).exclude(
            quota_72=0, quota_144=0, quota_256=0
        ).order_by('-quota_256', '-quota_144', '-quota_72'
                   ).select_related( 'ed_center')
    ed_centers = EducationCenter.objects.filter(
        project_years__in=ed_centers_year)
    applications = Application.objects.filter(
        education_center__in=ed_centers,
        project_year=project_year,
        flow_status__is_rejected=False
    )
    price_256 = applications.filter(
        education_program__duration__gte=256).aggregate(
            avg_price=Avg('price'))['avg_price']
    project_year.price_256 = price_256
    project_year.save()
    appls_stat = applications.aggregate(
        appls_count=Count('id'),
        appls_count_72=Count(Case(
            When(education_program__duration__lte=72, then=1),
            output_field=IntegerField())),
        appls_count_144=Count(Case(
            When(Q(education_program__duration__gt=72) & 
                 Q(education_program__duration__lt=256), then=1),
            output_field=IntegerField())),
        appls_count_256=Count(Case(
            When(education_program__duration__gte=256, then=1),
            output_field=IntegerField())),
    )
    prvd_appls_stat = applications.exclude(csn_prv_date=None).aggregate(
        appls_count=Count('id'),
        appls_count_72=Count(Case(
            When(education_program__duration__lte=72, then=1),
            output_field=IntegerField())),
        appls_count_144=Count(Case(
            When(Q(education_program__duration__gt=72) & 
                 Q(education_program__duration__lt=256), then=1),
            output_field=IntegerField())),
        appls_count_256=Count(Case(
            When(education_program__duration__gte=256, then=1),
            output_field=IntegerField())),
    )
    ed_centers_year = ed_centers_year.values(
        'quota_72', 'quota_144', 'quota_256', 'ed_center__flow_name', 
        'ed_center__id', 'ed_center__name', 'ed_center__short_name'
    )
    applications = applications.values(
        "education_center__id", "group__start_date",
        "education_program__duration", "csn_prv_date"
    )

    #day_stats = {}
    #day_stats['Новые'] = applications.filter(creation_date=today).count()
    #day_stats['Одобрено ЦЗН'] = applications.filter(csn_prv_date=today).count()
    #day_stats['Начали обучение'] = applications.filter(group__start_date=today).count()
    #chart
    if 'change-start-date' in request.POST:
        start_date_p = datetime.strptime(request.POST["date"], "%Y-%m-%d"
                                       )
        week_now = start_date_p.isocalendar()[1]
    else:
        week_now = date.today().isocalendar()[1]
    weeks = []
    weeks_stat = {
        'Начали обучение': [],
        'Завершили обучение': [],
        'Трудоустроенны': [],
    }
    cumulative_weeks_stat = {
        'Начали обучение': [],
        'Завершили обучение': [],
        'Трудоустроенны': [],
    }
    find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
    for week in range(5, -1, -1):
        start_date = f'{year}-{week_now - week}-1'
        end_date = f'{year}-{week_now - week}-6'
        week_dates = {'start_date': datetime.strptime(start_date, '%Y-%U-%w')}
        week_dates['end_date'] = datetime.strptime(end_date, '%Y-%U-%w')\
                                + timedelta(1)
        if 'change-start-date' in request.POST:
            week_dates['end_date'] = min(week_dates['end_date'], start_date_p)
        elif week_dates['end_date'] > datetime.now():
            week_dates['end_date'] = datetime.now()

        weeks_stat['Начали обучение'].append(applications.filter(
            group__start_date__gte=week_dates['start_date'],
            group__start_date__lte=week_dates['end_date']
        ).exclude(csn_prv_date=None).count())
        weeks_stat['Завершили обучение'].append(applications.filter(
            group__end_date__gte=week_dates['start_date'],
            group__end_date__lte=week_dates['end_date'],
        ).count())
        weeks_stat['Трудоустроенны'].append(applications.filter(
            group__end_date__gte=week_dates['start_date'],
            group__end_date__lte=week_dates['end_date'],
            flow_status=find_wrk_status
        ).count())

        cumulative_weeks_stat['Начали обучение'].append(applications.filter(
            group__start_date__lte=week_dates['end_date']
        ).exclude(csn_prv_date=None).count())
        cumulative_weeks_stat['Завершили обучение'].append(applications.filter(
            group__end_date__lte=week_dates['end_date'],
        ).count())
        cumulative_weeks_stat['Трудоустроенны'].append(applications.filter(
            group__end_date__lte=week_dates['end_date'],
            flow_status=find_wrk_status
        ).count())

        weeks.append(f'{week_dates["start_date"].strftime("%d/%m")}-{week_dates["end_date"].strftime("%d/%m")}')
    chart = get_flow_applications_plot(weeks, weeks_stat)
    cumulative_chart = get_flow_applications_plot(weeks, cumulative_weeks_stat)

    return render(request, 'federal_empl_program/flow_appls_dashboard.html', {
        'project_year': project_year,
        'ed_centers': ed_centers_year,
        'chart': chart,
        'cumulative_chart': cumulative_chart,
        'applications': applications,
        'appls_stat': appls_stat,
        'prvd_appls_stat': prvd_appls_stat
    })
    

@csrf_exempt
def quota_center_request(request, ed_center_id):
    project_year = get_object_or_404(ProjectYear, year=2023)
    ed_center = get_object_or_404(EducationCenter, id=ed_center_id)
    ed_center_year = EducationCenterProjectYear.objects.filter(
        project_year=project_year, ed_center=ed_center).first()
    if ed_center_year.stage != 'FNSHD':
        return HttpResponseRedirect(reverse('login'))
    quota_request = QuotaRequest.objects.first()
    ed_center_request, is_new = EdCenterQuotaRequest.objects.get_or_create(
        request=quota_request,
        ed_center_year=ed_center_year,
        request_number=1
    )
    conditions = False
    if 'send-request' in request.POST:
        ed_center_request.status = 'LCK'
        ed_center_request.save()
        programs_quota = ProgramQuotaRequest.objects.filter(
            ed_center_request=ed_center_request)
        programs_quota.filter(price=0).delete()
        programs_quota.filter(req_quota=0).delete()
    if 'add-programs' in request.POST:
        programs = request.POST.getlist('programs')
        for program_id in programs:
            program = get_object_or_404(EducationProgram, id=program_id)
            program_quota, is_new = ProgramQuotaRequest.objects.get_or_create(
                ed_center_request=ed_center_request,
                program=program,
            )
            program_quota.save()
    programs_quota = ProgramQuotaRequest.objects.filter(
        ed_center_request=ed_center_request)
    programs_quota_72 = programs_quota.filter(program__duration__lte=72)
    programs_quota_144 = programs_quota.filter(
        program__duration__gt=72, program__duration__lte=144
    )
    programs_quota_256 = programs_quota.filter(program__duration__gt=144)

    if 'set-quota' in request.POST:
        quota = request.POST['quota']
        if quota == '72': programs_quota = programs_quota_72
        elif quota == '144': programs_quota = programs_quota_144
        elif quota == '256': programs_quota = programs_quota_256
        for program_quota in programs_quota:
            program_quota.price = int(request.POST[f'price_{program_quota.id}'])
            program_quota.req_quota = int(request.POST[f'req_quota_{program_quota.id}'])
            program_quota.save()
    
    
    sum_72 = 0
    quota_72 = 0
    for program_quota in programs_quota_72:
        sum_72 += program_quota.price * program_quota.req_quota
        quota_72 += program_quota.req_quota
    if (sum_72 != 0 and quota_72 != 0):avrg_72 = sum_72 / quota_72
    else: avrg_72 = 0
    sum_144 = 0
    quota_144 = 0
    for program_quota in programs_quota_144:
        sum_144 += program_quota.price * program_quota.req_quota
        quota_144 += program_quota.req_quota
    if (quota_144 != 0 and quota_144 != 0): avrg_144 = sum_144 / quota_144
    else: avrg_144 = 0
    sum_256 = 0
    quota_256 = 0
    for program_quota in programs_quota_256:
        sum_256 += program_quota.price * program_quota.req_quota
        quota_256 += program_quota.req_quota
    if (sum_256 != 0 and quota_256 != 0): avrg_256 = sum_256 / quota_256
    else: avrg_256 = 0

    if ((quota_72 + quota_144 + quota_256) != 0):
        avrg = (sum_72+sum_144+sum_256) / (quota_72 + quota_144 + quota_256)
    else: avrg = 0
    if avrg_72 <= 27435 and avrg_144 <= 40920 and avrg_256 <= 61380 and avrg <= 48962 and avrg > 0:
        conditions = True

    programs_72 = EducationProgram.objects.filter(
        ed_center=ed_center, duration__lte=72,
    ).exclude(quota_requests__in=programs_quota)
    programs_144 = EducationProgram.objects.filter(
        ed_center=ed_center, duration__gt=72, duration__lte=144
    ).exclude(quota_requests__in=programs_quota)
    programs_256 = EducationProgram.objects.filter(
        ed_center=ed_center, duration__gt=144
    ).exclude(quota_requests__in=programs_quota)

    return render(request, 'federal_empl_program/quota_center_request.html', {
        'ed_center': ed_center,
        'ed_center_request': ed_center_request,
        'programs_quota_72': programs_quota_72,
        'programs_quota_144': programs_quota_144,
        'programs_quota_256': programs_quota_256,
        'programs_72': programs_72,
        'programs_144': programs_144,
        'programs_256': programs_256,
        'conditions': conditions
    })


@csrf_exempt
def quota_request(request):
    project_year = get_object_or_404(ProjectYear, year=2023)
    quota_request = QuotaRequest.objects.first()
    ed_centers_requests = EdCenterQuotaRequest.objects.filter(
        request=quota_request).exclude(status='DRFT')
    ed_centers = EducationCenterProjectYear.objects.filter(
        quota_requests__in=ed_centers_requests
    ).distinct().values('ed_center__id', 'ed_center__short_name')
    
    programs_quota = ProgramQuotaRequest.objects.filter(
        ed_center_request__in=ed_centers_requests).exclude(price=0).exclude(
        req_quota=0)
    programs_quota_72 = programs_quota.filter(program__duration__lte=72)
    programs_quota_144 = programs_quota.filter(
        program__duration__gt=72, program__duration__lte=144
    )
    programs_quota_256 = programs_quota.filter(program__duration__gt=144)
    programs = EducationProgram.objects.filter(
        quota_requests__in=programs_quota
    ).distinct()
    
    if 'set-quota' in request.POST:
        quota = request.POST['quota']
        if quota == '72': programs_quota = programs_quota_72
        elif quota == '144': programs_quota = programs_quota_144
        elif quota == '256': programs_quota = programs_quota_256
        for program_quota in programs_quota:
            program_quota.ro_quota = int(request.POST[f'req_quota_{program_quota.id}'])
            program_quota.save()
    if 'export-request' in request.POST:
        quota_request.send_date = request.POST['send_date']
        quota_request.status = 'SND'
        return exports.quota_request(quota_request)
    
    return render(request, 'federal_empl_program/quota_request.html', {
        'project_year': project_year,
        'quota_request': quota_request,
        'programs_quota_72': programs_quota_72,
        'programs_quota_144': programs_quota_144,
        'programs_quota_256': programs_quota_256,
        'ed_centers': ed_centers,
        'programs': programs
    })
    
@login_required
@csrf_exempt
def groups_list(request, year=2023):
    project_year = get_object_or_404(ProjectYear, year=year)
    ed_centers = EducationCenter.objects.exclude(flow_name="")
    start_date = date(2023, 1, 1)
    end_date = date(2023, 12, 31)
    groups = Group.objects.filter(
        start_date__gte=start_date, end_date__lte=end_date
    ).exclude(students=None).select_related(
        'education_program', 'education_program__ed_center'
    ).prefetch_related('closing_documents').order_by(
        Case( 
            When (pay_status="UPB", then=Value(0)),
            When (pay_status="WFB", then=Value(1)),
            default = Value(2)
        ),
        Case( 
            When (closing_documents=None, then=Value(1)),
            default = Value(0)
        ),
        'end_date',
        'education_program__ed_center'
    ).distinct()
    if 'pay_bills' in request.POST:
        for group in groups.exclude(closing_documents=None):
            for document in group.closing_documents.all():
                document.is_paid = f'doc_{document.id}' in request.POST
                document.save()
                if len(group.closing_documents.exclude(bill_file='').filter(is_paid=False)) == 0:
                    group.pay_status = 'PDB'
                else:  group.pay_status = 'UPB'
                group.save()

    return render(request, 'federal_empl_program/groups_list.html', {
        'groups': groups,
        'project_year': project_year,
        'ed_centers': ed_centers
    })
     
@login_required
@csrf_exempt
def group_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    applicants = Application.objects.filter(
        group=group, flow_status__is_rejected=False
    )
    documents = ClosingDocument.objects.filter(group=group)

    if 'add_to_act' in request.POST:
        for applicant in applicants:
            applicant.added_to_act = f'act{applicant.id}' in request.POST
            applicant.save()
    elif 'add-doc' in request.POST:
        doc = ClosingDocument(
            group=group,
            doc_type = request.POST['doc_type'],
            bill_sum = request.POST['bill_sum']
        )
        doc.doc_file = request.FILES['act_file']
        doc.doc_file.name = unidecode.unidecode(doc.doc_file.name)
        if 'bill_file' in request.FILES:
            doc.bill_file = request.FILES['bill_file']
            doc.bill_file.name = unidecode.unidecode(doc.bill_file.name)
            doc.bill_id = request.POST['bill_id']
        doc.save()
        group.pay_status = 'WFB'
        group.save()
    elif 'add-bill' in request.POST:
        doc_id = request.POST['doc_id']
        doc = ClosingDocument.objects.get(id=doc_id)
        doc.bill_file = request.FILES['bill_file']
        doc.bill_id = request.POST['bill_id']
        doc.save()
        group.pay_status = 'WFB'
        group.save()
    elif 'group-comment' in request.POST:
        group.group_commentary = request.POST['group_commentary']
        group.save()
    elif 'add-group-link' in request.POST:
        group.group_link = request.POST['group_link']
        group.save()
    elif 'change-doc' in request.POST:
        doc_id = request.POST['doc_id']
        doc = ClosingDocument.objects.get(id=doc_id)
        doc.doc_type = request.POST['doc_type']
        doc.bill_sum = request.POST['bill_sum']
        doc.bill_id = request.POST['bill_id']
        if 'act_file' in request.FILES:
            doc.doc_file = request.FILES['act_file']
            doc.doc_file.name = unidecode.unidecode(doc.doc_file.name)
        if 'bill_file' in request.FILES:
            doc.bill_file = request.FILES['bill_file']
            doc.bill_file.name = unidecode.unidecode(doc.bill_file.name)
        group.pay_status = 'WFB'
        group.save()
        doc.save()
    elif 'delete-doc' in request.POST:
        doc_id = request.POST['doc_id']
        doc = ClosingDocument.objects.get(id=doc_id)
        doc.delete()
    elif 'send-bill' in request.POST:
        group.pay_status = 'UPB'
        group.save()
    if request.method == 'POST':
        return HttpResponseRedirect(reverse(
            'group_view', kwargs={'group_id': group.id}
        ))
    ed_price = applicants.filter(added_to_act=True).aggregate(price=Sum('price'))['price']
    ed_price = 0 if ed_price is None else ed_price * 0.7
    find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
    wrk_price = applicants.filter(added_to_act=True,
        flow_status=find_wrk_status).aggregate(price=Sum('price'))['price']
    if wrk_price is None: wrk_price = 0
    wrk_price = wrk_price * 0.3
    full_price = ed_price + wrk_price
    paid_price = documents.filter(
        is_paid=True).aggregate(bill_sum=Sum('bill_sum'))['bill_sum']
    if paid_price is None: paid_price = 0

    return render(request, 'federal_empl_program/group_view.html', {
        'group': group,
        'documents': documents,
        'applicants': applicants,
        'ed_price': ed_price,
        'wrk_price': wrk_price,
        'full_price': full_price,
        'paid_price': paid_price,
        'act_form': ActDataForm(),
        'bill_form': BillDataForm(),
        'act_change_form': ActChangeDataForm()
    })

@csrf_exempt
def citizen_application(request):
    is_register = False
    if request.method == "POST":
        middle_name = request.POST["middle_name"]
        if middle_name == '': middle_name = None
        birthday = request.POST["birthday"]
        birthday = datetime.strptime(birthday, "%Y-%m-%d")
        sex = request.POST.getlist("GenderOptions")
        sex = 'M' if 'male' in sex else 'F'
        consultation = request.POST.getlist("consultation")
        consultation =  len(consultation) != 0
        citizen_application = CitizenApplication.objects.get_or_create(
            last_name=request.POST["last_name"],
            first_name=request.POST["first_name"],
            middle_name=middle_name,
            email=request.POST["email"],
            phone_number=request.POST["phone"],
            competence=request.POST["competence"],
            birthday=birthday,
            education_type=request.POST["education_type"],
            employment_status=request.POST["employment_status"],
            practice_time=request.POST["practice_time"],
            planned_employment=request.POST["planned_employment"],
            consultation=consultation,
            sex=sex
        )
        is_register = True
        
    return render(request, 'federal_empl_program/citizen_application.html', {
        'is_register': is_register
    })