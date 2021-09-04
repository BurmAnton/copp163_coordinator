from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .forms import ImportDataForm
from .imports import express_import, import_in_db_gd, import_statuses

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
        return HttpResponseRedirect(reverse('admin:federal_empl_program_application_changelist'))
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
