from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from citizens.models import School
from django.db.models import Sum, Count
from education_centers.models import EducationCenter
from django.http import HttpResponseRedirect
from django.urls import reverse

from future_ticket.models import EducationCenterTicketProjectYear,\
                                 TicketFullQuota, TicketProjectYear, TicketQuota

from .forms import ImportDataForm
from . import imports

def equalize_quotas(request):
    quotas = TicketQuota.objects.all()
    for quota in quotas:
        quota.approved_value = quota.value
        quota.save()

    return HttpResponseRedirect(reverse("quotas"))

@csrf_exempt
def quotas(request):
    if request.method == 'POST':
        for quota in TicketQuota.objects.exclude(value=0):
           approved_value = request.POST[f'{quota.id}']
           quota.approved_value = approved_value
           quota.save()
    project_year = get_object_or_404(TicketProjectYear, year=2023)
    centers_project_year = EducationCenterTicketProjectYear.objects.filter(
        project_year=project_year
    )
    quota_stat = dict()
    quota_stat_all = dict()
    quota_stat_all['full_qouta'] = 0
    quota_stat_all['federal_quota'] = 0
    quota_stat_all['none_federal_quota'] = 0
    quota_stat_all['approved_full_qouta'] = 0
    quota_stat_all['approved_federal_quota'] = 0
    quota_stat_all['approved_none_federal_quota'] = 0
    for ter_admin in School.TER_CHOICES:
        quota_stat[ter_admin[1]] = dict()
        ter_admin_schools = School.objects.filter(territorial_administration=ter_admin[0])
        schools_quota = TicketQuota.objects.filter(school__in=ter_admin_schools).distinct()
        
        federal_quota = schools_quota.filter(is_federal=True).distinct().aggregate(Sum("approved_value"), Sum("value"))
        if federal_quota['value__sum'] == None: federal_quota['value__sum'] = 0
        if federal_quota['approved_value__sum'] == None: federal_quota['approved_value__sum'] = 0
        quota_stat[ter_admin[1]]['approved_federal_quota'] = federal_quota['approved_value__sum']
        quota_stat[ter_admin[1]]['federal_quota'] = federal_quota['value__sum']
        
        none_federal_quota = schools_quota.filter(is_federal=False).distinct().aggregate(Sum("approved_value"), Sum("value"))
        if none_federal_quota['value__sum'] == None: none_federal_quota['value__sum'] = 0
        if none_federal_quota['approved_value__sum'] == None: none_federal_quota['approved_value__sum'] = 0
        quota_stat[ter_admin[1]]['none_federal_quota'] = none_federal_quota['value__sum']
        quota_stat[ter_admin[1]]['approved_none_federal_quota'] = none_federal_quota['approved_value__sum']
        
        full_quota = schools_quota.distinct().aggregate(Sum("approved_value"), Sum("value"))
        if full_quota['value__sum'] == None: full_quota['value__sum'] = 0
        if full_quota['approved_value__sum'] == None: full_quota['approved_value__sum'] = 0
        quota_stat[ter_admin[1]]['full_quota'] = full_quota['value__sum']
        quota_stat[ter_admin[1]]['approved_full_quota'] = full_quota['approved_value__sum']
        
        quota_stat_all['full_qouta'] += full_quota['value__sum']
        quota_stat_all['federal_quota'] += federal_quota['value__sum']
        quota_stat_all['none_federal_quota'] += none_federal_quota['value__sum']
        quota_stat_all['approved_full_qouta'] += full_quota['value__sum']
        quota_stat_all['approved_federal_quota'] += federal_quota['approved_value__sum']
        quota_stat_all['approved_none_federal_quota'] += none_federal_quota['approved_value__sum']
    full_quota = get_object_or_404(TicketFullQuota, project_year=project_year)
    quotas = TicketQuota.objects.exclude(value=0)
    ed_centers = EducationCenter.objects.exclude(ticket_quotas=None)
    schools = School.objects.exclude(ticket_quotas=None)

    return render(request, "future_ticket/quotas.html", {
        'project_year': project_year,
        'centers_project_year': centers_project_year,
        'full_quota': full_quota,
        'quota_stat': quota_stat,
        'quota_stat_all': quota_stat_all,
        'quotas': quotas,
        'ed_centers': ed_centers,
        'schools': schools
    })

@csrf_exempt
def import_ticket_professions(request):
    form = ImportDataForm()
    message = None
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.professions(form)
            message = data
    
    return render(request, "future_ticket/import_professions.html", {
        'message': message,
        'form' : ImportDataForm(),
    })

@csrf_exempt
def import_ticket_programs(request):
    form = ImportDataForm()
    message = None
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.programs(form)
            message = data
    
    return render(request, "future_ticket/import_programs.html", {
        'message': message,
        'form' : ImportDataForm(),
    })