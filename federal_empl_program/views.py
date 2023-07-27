from datetime import date, datetime
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

from .forms import ImportDataForm
from .imports import express_import

from pysendpulse.pysendpulse import PySendPulse

from users.models import User
from citizens.models import Citizen
from federal_empl_program.models import CitizenApplication, EducationCenterProjectYear, \
                                        EdCenterQuota,  ProjectYear


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
            birthday=birthday,
            sex=sex,
            competence=request.POST["competence"],
            education_type=request.POST["education_type"],
            employment_status=request.POST["employment_status"],
            practice_time=request.POST["practice_time"],
            planned_employment=request.POST["planned_employment"]
        )
        is_register = True
        
    return render(request, 'federal_empl_program/citizen_application.html', {
        'is_register': is_register
    })