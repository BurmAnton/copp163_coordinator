import calendar
from datetime import date, datetime, timedelta
from email.mime import application
from dateutil.relativedelta import relativedelta
import string
import random
import json

from django.db.models import Q, Count, Sum
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

from education_centers.models import Competence, EducationCenter, EducationProgram

from . import exports
from .forms import ImportDataForm
from .imports import express_import

from pysendpulse.pysendpulse import PySendPulse

from .utils import get_applications_plot
from users.models import User
from citizens.models import Citizen
from federal_empl_program.models import Application, CitizenApplication, EdCenterQuotaRequest, EducationCenterProjectYear, \
                                        EdCenterQuota, Grant, ProgramQuotaRequest,  ProjectYear, QuotaRequest


@login_required
def index(request):
    return HttpResponseRedirect(reverse('login'))

@login_required
@csrf_exempt
def import_express(request):
    if request.method == "POST":
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            message = express_import(form)
        else:
            data = form.errors
        form = ImportDataForm()
        return render(request, "federal_empl_program/import_express.html",{
            'form': form,
            'message': message
        })
    else:
        form = ImportDataForm()
        return render(request, "federal_empl_program/import_express.html",{
            'form': form
        })

@csrf_exempt
def login(request):
    message = None
    if request.user.is_authenticated:
        #Переадресация авторизованных пользователей
        if request.user.role == 'CTZ':
            ed_center_id = request.user.education_centers.first().id
            return HttpResponseRedirect(reverse("applicant_profile", kwargs={'user_id': request.user.id}))
        if request.user.role == 'CO':
            ed_center_id = request.user.education_centers.first().id
            return HttpResponseRedirect(reverse("ed_center_application", kwargs={'ed_center_id': ed_center_id}))
        return HttpResponseRedirect(reverse("admin:index"))
        
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            if request.user.role == 'CO':
                ed_center_id = user.education_centers.first().id
                return HttpResponseRedirect(reverse("ed_center_application", kwargs={'ed_center_id': ed_center_id}))
            return HttpResponseRedirect(reverse("admin:index"))
        else:
            message = "Неверный логин и/или пароль."

    return render(request, "federal_empl_program/login.html", {
        "message": message,
        "page_name": "ЦОПП СО | Авторизация"
    })

@login_required
def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return HttpResponseRedirect(reverse("login"))



@csrf_exempt
def quota_dashboard(request):
    project_year = get_object_or_404(ProjectYear, year=2023)
    ed_centers_year = EducationCenterProjectYear.objects.filter(
        project_year=project_year
    ) 
    centers_quota = EdCenterQuota.objects.filter(
        ed_center_year__in=ed_centers_year
    ).order_by("-quota_72", "-quota_144", "-quota_256")
    aggregated_quota = centers_quota.aggregate(
        sum_quota72=Sum("quota_72"), 
        sum_quota144=Sum("quota_144"), 
        sum_quota256=Sum("quota_256")
    )

    return render(request, 'federal_empl_program/quota_dashboard.html', {
        'centers_quota': centers_quota,
        'aggregated_quota': aggregated_quota
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
        if 'male' in sex: sex = 'M'
        else: sex = 'F'
        consultation = request.POST.getlist("consultation")
        if len(consultation) == 0: consultation = False
        else: consultation = True
        citizen_application = CitizenApplication.objects.get_or_create(
            last_name=request.POST["last_name"],
            first_name=request.POST["first_name"],
            middle_name=middle_name,
            email=request.POST["email"],
            phone_number=request.POST["phone"],
            birthday=request.POST["competence"],
            education_type=request.POST["education_type"],
            employment_status=request.POST["employment_status"],
            practice_time=request.POST["practice_time"],
            planned_employment=request.POST["planned_employment"]
        )
        is_register = True
        
    return render(request, 'federal_empl_program/citizen_application.html', {
        'is_register': is_register
    })

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
    monthly_applications = dict()
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
    
    if (len(programs_quota_72) != 0):
        sum_72 = programs_quota_72.aggregate(Sum("price"))['price__sum']
        avrg_72 = sum_72 / programs_quota_72.count()
    else:
        sum_72 = 0
        avrg_72 = 0
    if (len(programs_quota_144) != 0):
        sum_144 = programs_quota_144.aggregate(Sum("price"))['price__sum']
        avrg_144 = sum_144 / programs_quota_144.count()
    else:
        sum_144 = 0
        avrg_144 = 0
    if (len(programs_quota_256) != 0):
        sum_256 = programs_quota_256.aggregate(Sum("price"))['price__sum']
        avrg_256 = sum_256 / programs_quota_256.count()
    else:
        sum_256 = 0
        avrg_256 = 0
    if (programs_quota.count() != 0):
        avrg = (sum_72+sum_144+sum_256) / (programs_quota.count())
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
    
    programs_quota = ProgramQuotaRequest.objects.filter(
        ed_center_request__in=ed_centers_requests).exclude(price=0).exclude(
        req_quota=0)
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
    })