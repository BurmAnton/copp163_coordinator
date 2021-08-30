from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError

from users.models import User
from citizens.models import Citizen, School

# Create your views here.
@login_required(login_url='bilet/login')
def index(request):
    return render(request, "vocational_guidance/index.html",{
        'page_name': 'Личный кабинет'
    })

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
        birthday = request.POST['birthday']
        post=request.POST
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
            citizen = Citizen(
                first_name=first_name,
                last_name=last_name,
                birthday=birthday,
                social_status='SCHS',
                school = school
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
