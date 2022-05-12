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

@csrf_exempt

def registration(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email", "")
        password = data.get("password", "")
        confirmation = data.get("confirmation", "")

        phone = data.get("phone", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        middle_name = data.get("middle_name", "")
        birthday = data.get("birthday", "")
        disability_type = data.get("disability_type", "")

        school_id = data.get("school_id", "")
        grade_number = data.get("grade_number", "")
        grade_letter = data.get("grade_letter", "")
        school = School.objects.get(id=school_id)

        if disability_type.isdigit():
            disability_type = DisabilityType.objects.filter(id=disability_type)
            if len(disability_type) != 0:
                disability_type = disability_type[0]
        else:
            disability_type = None
        if password != confirmation:
            return JsonResponse({"message": "Password mismatch."}, status=201)
        try:
            user = User.objects.create_user(email, password)
            user.first_name = first_name
            user.middle_name  = middle_name
            user.last_name = last_name
            user.birthday = birthday
            user.phone_number = phone
            user.disability_type = disability_type

            user.role = 'ST'
            school_class = SchoolClass.objects.filter(
                school=school,
                grade_number=grade_number,
                grade_letter=grade_letter
            )
            if len(school_class) != 0:
                school_class = school_class[0]
            else:
                school_class = SchoolClass(
                    school=school,
                    grade_number=int(grade_number),
                    grade_letter=grade_letter.upper()
                )
                school_class.save()
            user.school = school
            user.school_class = school_class
            user.save()
        except IntegrityError:
            return JsonResponse({"message": "Email already taken."}, status=201)

        return JsonResponse({"message": "Account created successfully."}, status=201)
    return HttpResponseRedirect(reverse("login"))


def reg_stage(request, stage):
    return HttpResponseRedirect(reverse("login"))

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