from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse

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
        return HttpResponseRedirect(reverse("signin"))
    else:
        return render(request, "vocational_guidance/registration.html") 

@login_required(login_url='bilet/login')
def signout(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse("signin"))
