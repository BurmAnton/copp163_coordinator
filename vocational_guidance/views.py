from django.db.models.query import QuerySet
from django.db.models.query_utils import refs_expression
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db import IntegrityError

from users.models import User, Group
from citizens.models import Citizen, School, SchoolClass
from vocational_guidance.models import VocGuidBundle

# Create your views here.
@login_required(login_url='bilet/login/')
def index(request):
    school_group = School.objects.get(name='Школьник')
    if school_group in request.user.groups:
        citizen = Citizen.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email,
        )
        profile(citizen.id)
    return HttpResponseRedirect(reverse("index"))    
    #school_dash(school.id)
    #ed_center_dash(ed_center.id)
    #region_dash()

def profile(request, citizen_id):
    citizen = Citizen.objects.get(id=citizen_id)
    choosen_bundles = VocGuidBundle.objects.filter(participants=citizen).values(
        "name", "description", "img_link", "guid_type"
    )
    bundles = VocGuidBundle.objects.exclude(participants=citizen).values(
        "name", "description", "img_link", "guid_type"
    )
    
    choosen_type_presence = set()
    choosen_bundles_dict = {}
    for guid_type in VocGuidBundle.TYPE_CHOICES:
        choosen_bundles_dict[guid_type[0]] = {}
    for bundle in choosen_bundles:
        choosen_bundles_dict[bundle["guid_type"]][bundle['name']] = {
            'name': bundle['name'],
            'description': bundle['description'],
        }
        choosen_type_presence.add(bundle["guid_type"])

    type_presence = set()
    bundles_dict = {}
    for guid_type in VocGuidBundle.TYPE_CHOICES:
        bundles_dict[guid_type[0]] = {}
    for bundle in bundles:
        bundles_dict[bundle["guid_type"]][bundle['name']] = {
            'name': bundle['name'],
            'description': bundle['description'],
            'img_link': bundle['img_link']
        }
        type_presence.add(bundle["guid_type"])

    message = ""
    if len(choosen_type_presence) == 0:
        message = "На данные момент Вы не записались не на одно из доступных профориентационных мероприятий. Вы можете просмотреть и выбрать интересующие вас их ниже."
    
    schools = School.objects.exclude(name=citizen.school.name)

    disability_types = Citizen.disability_types
    return render(request, "vocational_guidance/index.html",{
        'page_name': 'Личный кабинет',
        'user': citizen,
        'choosen_bundles': choosen_bundles_dict,
        'choosen_type_presence': choosen_type_presence,
        'bundles': bundles_dict,
        'type_presence': type_presence,
        'message': message,
        "birthday": citizen.birthday.isoformat(),
        'schools': schools,
        "disability_types": disability_types
    })

def school_dash(request, school_id):
    pass

def ed_center_dash(request, ed_center_id):
    pass

def region_dash(request):
    pass

@csrf_exempt
def choose_bundle(request):
    if request.method == "POST":
        bundle_name = request.POST["bundle_name"]
        citizen_id = request.POST["citizen"]
        bundle = VocGuidBundle.objects.get(name=bundle_name)
        citizen = Citizen.objects.get(id=citizen_id)
        previous_bundles = VocGuidBundle.objects.filter(
            participants=citizen_id,
            guid_type=bundle.guid_type
        )
        if len(previous_bundles) != 0:
            citizen.voc_guid_bundles.remove(previous_bundles[0])
        bundle.participants.add(citizen_id)
        bundle.save()
    return HttpResponseRedirect(reverse("index"))

@csrf_exempt
def reject_bundle(request):
    if request.method == "POST":
        bundle_name = request.POST["bundle_name"]
        citizen_id = request.POST["citizen"]
        bundle = VocGuidBundle.objects.get(name=bundle_name)
        citizen = Citizen.objects.get(id=citizen_id)
        citizen.voc_guid_bundles.remove(bundle)
        bundle.save()
    return HttpResponseRedirect(reverse("index"))

@csrf_exempt
def signin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "vocational_guidance/login.html", {
                "message": "Неверный логин и/или пароль."
            })
    else:
        return render(request, "vocational_guidance/login.html") 

@login_required(login_url='bilet/login')
@csrf_exempt
def change_password(request):
    if request.method == "POST":
        email = request.user.email
        current_password = request.POST["current_password"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        user = authenticate(email=email, password=current_password)
        if user is not None:
            if password == confirmation:
                user.set_password(password)
                user.save()
                login(request, user)
    return HttpResponseRedirect(reverse("index"))

@csrf_exempt
def signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        phone = request.POST["phone"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        first_name = request.POST['name']
        last_name = request.POST['last_name']
        middle_name = request.POST['middle_name']
        birthday = request.POST['birthday']
        grade_number = request.POST['school_class']
        grade_letter = request.POST['school_class_latter']
        school_name = request.POST['school']
        school = School.objects.get(name=school_name)
        try:
            disability_check = request.POST['disability-check']
        except:
            disability_check = False
        if disability_check != False:
            disability_type = request.POST['disability_type']
        else:
            disability_type = None
        if password != confirmation:
            return render(request, "vocational_guidance/registration.html", {
                "message": "Введённые пароли не совпадают"
            })
        try:
            user = User.objects.create_user(email, password)
            user.save()
            user.first_name = first_name
            user.last_name = last_name
            user.save()
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
            citizen = Citizen(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                birthday=birthday,
                email=email,
                social_status='SCHS',
                school=school,
                school_class=school_class,
                phone_number = phone,
                disability_type = disability_type
            )
            citizen.save()
        except IntegrityError:
            schools = School.objects.all()
            cities = set()
            for school in schools:
                cities.add(school.city) 
            return render(request, "vocational_guidance/registration.html", {
                "message": "Email уже использован",
                'schools': schools,
                'cities': cities,
                "disability_types": Citizen.disability_types
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        schools = School.objects.all()
        cities = set()
        for school in schools:
            cities.add(school.city) 
    
        return render(request, "vocational_guidance/registration.html", {
            'schools': schools,
            'cities': cities,
            "disability_types": Citizen.disability_types
        })

@login_required(login_url='bilet/login')
@csrf_exempt
def change_profile(request):
    if request.method == "POST":
        citizen_id = request.POST["id"]
        citizen = Citizen.objects.get(id=citizen_id)
        citizen.email = request.POST["email"]
        request.user.email = request.POST["email"]
        citizen.phone_number = request.POST["phone"]
        citizen.first_name = request.POST['name']
        request.user.first_name = request.POST["name"]
        citizen.last_name = request.POST['last_name']
        request.user.last_name = request.POST["last_name"]
        citizen.middle_name = request.POST['middle_name']
        citizen.birthday = request.POST['birthday']
        school_name = request.POST['school']
        school = School.objects.get(name=school_name)
        citizen.school = school
        grade_number = request.POST['school_class']
        grade_letter = request.POST['school_class_latter']
        try:
            disability_check = request.POST['disability-check']
        except:
            disability_check = False
        if disability_check != False:
            disability_type = request.POST['disability_type']
        else:
            disability_type = None
        citizen.disability_type = disability_type
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
        citizen.school_class = school_class
        request.user.save()
        citizen.save()
        return HttpResponseRedirect(reverse("index"))
    return HttpResponseRedirect(reverse("index"))



@login_required(login_url='bilet/login')
def signout(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse("signin"))
