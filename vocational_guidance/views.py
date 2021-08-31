from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError

from users.models import User
from citizens.models import Citizen, School, SchoolClass
from vocational_guidance.models import VocGuidBundle

# Create your views here.
@login_required(login_url='bilet/login')
def index(request):
    citizen = Citizen.objects.get(
        first_name=request.user.first_name,
        last_name=request.user.last_name,
        email=request.user.email,
    )

    choosen_bundles = VocGuidBundle.objects.filter(guid_type="SPO", participants=citizen).values(
        "name",
        "description",
        "img_link"
    )
    choosen_bundles_dict = {}
    for bundle in choosen_bundles:
        choosen_bundles_dict[bundle['name']] = {
            'name': bundle['name'],
            'description': bundle['description'],
            'img_link': bundle['img_link'],
            'competences': []
        }
        competences = [VocGuidBundle.objects.filter(guid_type="SPO", name=bundle['name']).values(
                "programs__competence__title"
            )]
        for copmetence in competences[0]:
            choosen_bundles_dict[bundle['name']]['competences'].append(copmetence['programs__competence__title'])
    bundles = VocGuidBundle.objects.filter(guid_type="SPO", ).exclude(participants=citizen).values(
        "name",
        "description",
        "img_link"
    )

    bundles_dict = {}
    for bundle in bundles:
        bundles_dict[bundle['name']] = {
            'name': bundle['name'],
            'description': bundle['description'],
            'img_link': bundle['img_link'],
            'competences': []
        }
        competences = [VocGuidBundle.objects.filter(guid_type="SPO", name=bundle['name']).values(
                "programs__competence__title"
            )]
        for copmetence in competences[0]:
            bundles_dict[bundle['name']]['competences'].append(copmetence['programs__competence__title'])
    
    choosen_online_bundles = VocGuidBundle.objects.filter(guid_type="VO", participants=citizen).values(
        "name",
        "description",
        "img_link"
    )
    choosen_online_bundles_dict = {}
    for bundle in choosen_online_bundles:
        choosen_online_bundles_dict[bundle['name']] = {
            'name': bundle['name'],
            'description': bundle['description'],
            'img_link': bundle['img_link'],
            'competences': []
        }
        competences = [VocGuidBundle.objects.filter(guid_type="VO", name=bundle['name']).values(
                "programs__competence__title"
            )]
        for copmetence in competences[0]:
            choosen_online_bundles_dict[bundle['name']]['competences'].append(copmetence['programs__competence__title'])
    bundles_online = VocGuidBundle.objects.filter(guid_type="VO", ).exclude(participants=citizen).values(
        "name",
        "description",
        "img_link"
    )

    bundles_online_dict = {}
    for bundle in bundles_online:
        bundles_online_dict[bundle['name']] = {
            'name': bundle['name'],
            'description': bundle['description'],
            'img_link': bundle['img_link'],
            'competences': []
        }
        competences = [VocGuidBundle.objects.filter(guid_type="VO", name=bundle['name']).values(
                "programs__competence__title"
            )]
        for copmetence in competences[0]:
            bundles_online_dict[bundle['name']]['competences'].append(copmetence['programs__competence__title'])
    
    if len(choosen_online_bundles_dict) == 0 and len(choosen_bundles_dict) == 0:
        message = "На данные момент Вы не записались не на одно из доступных профориентационных мероприятий. Вы можете просмотреть и выбрать интересующие вас их ниже."

    return render(request, "vocational_guidance/index.html",{
        'page_name': 'Личный кабинет',
        'user': citizen,
        'choosen_bundles': choosen_bundles_dict,
        'bundles': bundles_dict,
        'choosen_online_bundles': choosen_online_bundles_dict,
        'bundles_online': bundles_online_dict,
        'message': message
    })

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

@csrf_exempt
def signup(request):
    if request.method == "POST":
        email = request.POST["email"]
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
        if password != confirmation:
            return render(request, "vocational_guidance/registration.html", {
                "message": "Passwords must match."
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
                    grade_letter=grade_letter
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
                school_class=school_class
            )
            citizen.save()
        except IntegrityError:
            return render(request, "vocational_guidance/registration.html", {
                "message": "Email"
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        schools = School.objects.all()
        return render(request, "vocational_guidance/registration.html", {
            'schools': schools
        })

@login_required(login_url='bilet/login')
def signout(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse("signin"))
