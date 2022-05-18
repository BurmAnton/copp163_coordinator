from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import string
import random
import json

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

from .forms import ImportDataForm
from .imports import express_import, import_in_db_gd, import_statuses, import_schools

from pysendpulse.pysendpulse import PySendPulse

from users.models import User
from citizens.models import Citizen
from federal_empl_program.models import Application, CitizenCategory, Questionnaire

# Create your views here.
@login_required
def index(request):
    return HttpResponseRedirect(reverse('admin:index'))

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

@login_required
@csrf_exempt
def import_gd(request):
    if request.method == "POST":
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            message = import_in_db_gd(form)
        else:
            data = form.errors
        form = ImportDataForm()
        return render(request, "federal_empl_program/import_gd.html",{
            'form': form,
            'message': message
        })
    else:
        form = ImportDataForm()
        return render(request, "federal_empl_program/import_gd.html",{
            'form': form
        })

@login_required
@csrf_exempt
def import_st(request):
    if request.method == "POST":
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            message = import_statuses(form)
        else:
            data = form.errors
        form = ImportDataForm()
        return HttpResponseRedirect(reverse('admin:federal_empl_program_application_changelist'))
    else:
        form = ImportDataForm()
        return render(request, "federal_empl_program/import_statuses.html",{
            'form': form
        })

@login_required
@csrf_exempt
def import_sch(request):
    if request.method == "POST":
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            message = import_schools(form)
        else:
            data = form.errors
        form = ImportDataForm()
        return HttpResponseRedirect(reverse('admin:citizens_school_changelist'))
    else:
        form = ImportDataForm()
        return render(request, "federal_empl_program/import_schools.html",{
            'form': form
        })

@csrf_exempt
def login(request):
    message = None
    if request.user.is_authenticated:
        #Переадресация авторизованных пользователей
        if request.user.role == 'CTZ':
            return HttpResponseRedirect(reverse("dashboard"))
        return HttpResponseRedirect(reverse("admin:index"))
        
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect(reverse("login"))
        else:
            message = "Неверный логин и/или пароль."

    return render(request, "federal_empl_program/login.html", {
        "message": message,
        "page_name": "ЦОПП СО | Авторизация"
    })
@login_required()
@csrf_exempt
def change_password(request):
    if request.method == "POST":
        email = request.user.email
        current_password = request.POST["current_password"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        user = auth.authenticate(email=email, password=current_password)
        if user is not None:
            if password == confirmation:
                user.set_password(password)
                user.save()
                login(request, user)
    return HttpResponseRedirect(reverse("login"))

def category_search(answers):
    prepensioner = answers.get("prepensioner", "")
    if (prepensioner):
        return 'Предпенсионер'
    
    birthday = datetime.strptime(answers.get("birthday", ""),"%Y-%m-%d")
    age = relativedelta(date.today(), birthday).years
    if age >= 50:
        return '50+'

    empl_status = answers.get("empl_status", "")
    if empl_status == 'unempl_czn':
        return 'Безработные зарег. в ЦЗН'
    if empl_status == 'unempl':
        return 'Безработные незарег. в ЦЗН'
    if empl_status == 'vacation':
         return 'В отпуске по уходу за ребенком'

    if age <= 35 and age >= 16:
        education_lvl = answers.get("education_lvl", "")
        if education_lvl == 'fy_student':
            return '16-35 студенты 2022'
        if education_lvl == 'school':
            return '16-35 без ВО/СПО'

    return 'Под риском увольнения'


@csrf_exempt
def registration(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email", "")
        password = data.get("password", "")
        confirmation = data.get("confirmation", "")

        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        middle_name = data.get("middle_name", "")
        gender = data.get("gender", "")
        birthday = data.get("birthday", "")

        phone = data.get("phone", "")
        snils = data.get("snils", "")
        
        convenient_time = data.get("convenient_time", "")
        education_time = data.get("education_time", "")
        education_goal = data.get("education_goal", "")
        
        if password != confirmation:
            return JsonResponse({"message": "Password mismatch."}, status=201)
        try:
            user = User.objects.create_user(email, password)
            user.first_name = first_name
            user.middle_name = middle_name
            user.last_name = last_name
            user.phone_number = phone
            user.role = 'CTZ'
            user.save()
        except IntegrityError:
            return JsonResponse({"message": "Email already taken."}, status=201)

        education_lvl = data.get("education_lvl", "")
        education = 'SCHL'
        if education_lvl in ['fy_student', 'student']:
            education = 'STDN'
        if education_lvl == 'university':
            education = 'SPVO'

        citizen = Citizen(
            first_name = first_name,
            middle_name = middle_name,
            last_name = last_name,
            email = email,
            phone_number = phone,
            snils_number = snils,
            sex=gender,
            birthday=birthday,
            education_type=education
        )
        citizen.save()

        category = CitizenCategory.objects.get(short_name=category_search(data))

        application = Application(
            applicant=citizen,
            creation_date=date.today(),
            admit_status='RECA',
            appl_status='NEW',
            citizen_category=category,
            ed_ready_time=education_time,
        )
        application.save()

        questionnaire = Questionnaire(
            applicant=application,
            convenient_study_periods=convenient_time,
            purpose=education_goal
        )
        questionnaire.save()

        return JsonResponse({"message": "Account created successfully."}, status=201)
    return HttpResponseRedirect(reverse("login"))


def reg_stage(request, stage):
    return render(request, "federal_empl_program/login.html", {
        "page_name": "ЦОПП СО | Регистрация",
        "stage": 'registration'
    })

def code_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def mailing():
    REST_API_ID = 'e071900fe5ab9aa6dd4dec2f42160ead'
    REST_API_SECRET = '7e82daa1ccfd678487a894b3e3487967'
    TOKEN_STORAGE = 'memcached'
    MEMCACHED_HOST = '127.0.0.1:11211'
    SPApiProxy = PySendPulse(REST_API_ID, REST_API_SECRET, TOKEN_STORAGE, memcached_host=MEMCACHED_HOST)
    return SPApiProxy

@csrf_exempt
def password_recovery(request, step):
    if request.method == "POST":
        if step == 1:
            data = json.loads(request.body)
            email = data.get("email", "")
            user = User.objects.filter(email=email)
            if len(user) != 0:
                user = user[0]
                code = code_generator()
                user.code = code
                user.save()
                email = {
                    'subject': 'Востановление пароля skillsguide.ru',
                    'html': f'Здравствуйте!<p>Вы получили это письмо потому, что вы (либо кто-то, выдающий себя за вас) попросили выслать новый пароль к вашей учётной записи на сайте http://skillsguide.ru/. <br> Если вы не просили выслать пароль, то не обращайте внимания на это письмо. <br> Код подтверждения для смены пароля: {code} <br> Это автоматическое письмо на него не нужно отвечать.</p>',
                    'text': f'Здравствуйте!\n Вы получили это письмо потому, что вы (либо кто-то, выдающий себя за вас) попросили выслать новый пароль к вашей учётной записи на сайте http://skillsguide.ru/. \n Если вы не просили выслать пароль, то не обращайте внимания на это письмо. \n Код подтверждения для смены пароля: {code} \n Это автоматическое письмо на него не нужно отвечать.',
                    'from': {'name': 'ЦОПП СО', 'email': 'bvb@copp63.ru'},
                    'to': [
                        {'name': "f{user.first_name} {user.last_name}", 'email': email}
                    ],
                }
                SPApiProxy = mailing()
                SPApiProxy.smtp_send_mail(email)
                return JsonResponse({"message": "Email exist"}, status=201)
            return JsonResponse({"message": "Email not found"}, status=201)
        if step == 2:
            data = json.loads(request.body)
            email = data.get("email", "")
            code = data.get("code", "")
            user = User.objects.get(email=email)
            if user.code == code:
                return JsonResponse({"message": "Code matches"}, status=201)
            return JsonResponse({"message": "Code not matches"}, status=201)
        if step == 3:
            data = json.loads(request.body)
            email = data.get("email", "")
            password = data.get("password", "")
            confirmation = data.get("confirmation", "")
            if password == confirmation:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                return JsonResponse({"message": "Password changed"}, status=201)
            return JsonResponse({"message": "Passwords mismatch"}, status=201)
    return HttpResponseRedirect(reverse("login"))

@login_required
def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return HttpResponseRedirect(reverse("login"))