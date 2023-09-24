from datetime import date, datetime, timedelta
from django.forms import IntegerField
import pandas
from transliterate import translit

from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from citizens.models import School
from django.db.models import Sum, Count, Case, When
from education_centers.forms import ImportSchoolOrderDataForm, ImportTicketDataForm
from education_centers.models import EducationCenter
from django.http import HttpResponseRedirect
from django.urls import reverse


from future_ticket.models import DocumentTypeTicket, EducationCenterTicketProjectYear, EventsCycle, QuotaEvent, SchoolProjectYear, TicketEvent,\
                                 TicketFullQuota, TicketProfession, TicketProjectYear, TicketQuota

from .forms import ImportDataForm
from . import imports, exports

def equalize_quotas(request):
    quotas = TicketQuota.objects.all()
    for quota in quotas:
        quota.approved_value = quota.value
        quota.save()

    return HttpResponseRedirect(reverse("quotas"))

@csrf_exempt
def quotas(request):
    if 'save-quotas' in request.POST:
        for quota in TicketQuota.objects.exclude(value=0):
            approved_value = request.POST[f'{quota.id}']
            if int(approved_value) != quota.approved_value:
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
        quota_stat_all['approved_full_qouta'] += full_quota['approved_value__sum']
        quota_stat_all['approved_federal_quota'] += federal_quota['approved_value__sum']
        quota_stat_all['approved_none_federal_quota'] += none_federal_quota['approved_value__sum']
    full_quota = get_object_or_404(TicketFullQuota, project_year=project_year)
    quotas = TicketQuota.objects.exclude(value=0).select_related(
        'quota', 'ed_center', 'school', 'profession'
    )
    if 'export-quotas' in request.POST:
           return exports.qoutas(quotas)
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

@csrf_exempt
def import_schools_address(request):
    form = ImportDataForm()
    message = None
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.schools_address(form)
            message = data
    
    return render(request, "future_ticket/import_schools_address.html", {
        'message': message,
        'form' : ImportDataForm(),
    })

@csrf_exempt
def merge_ticket_professions(request):
    form = ImportDataForm()
    message = None
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.change_professions(form)
            message = data
    
    return render(request, "future_ticket/merge_professions.html", {
        'message': message,
        'form' : ImportDataForm(),
    })


@csrf_exempt
def export_professions(request):
    return exports.professions()

@csrf_exempt
def export_ticket_programs(request):
    return exports.programs()

def schools_application(request):
    message = None
    if request.method == 'POST':
        project_year = datetime.now().year
        project_year = get_object_or_404(TicketProjectYear, year=project_year)
        form = ImportTicketDataForm(request.POST, request.FILES)
        if form.is_valid():
            resp_full_name = request.POST['resp_full_name']
            resp_position = request.POST['resp_position']
            email = request.POST['email']
            phone = request.POST['phone']
            school_id = request.POST['school']
            school = School.objects.get(id=school_id)
            school_project = SchoolProjectYear(
                project_year=project_year,
                school=school,
                resp_full_name=resp_full_name,
                resp_position=resp_position,
                email=email,
                phone=phone
            )
            school_project.save()
            resp_order = request.FILES['import_file']
            school_project.resp_order = resp_order
            school_project.save()
            message = "OK"
        else:
            message = "Error"
    schools = School.objects.filter(
        ticket_project_years=None
    )

    return render(request, "future_ticket/schools_application.html", {
        'schools': schools,
        'form': ImportSchoolOrderDataForm(),
        'message': message
    })

@csrf_exempt
def schools_applications(request):     
    schools = SchoolProjectYear.objects.all()
    if request.method == 'POST':
        return exports.schools_applications(schools)

    return render(request, "future_ticket/schools_applications.html", {
        'schools': schools
    })


def events(request):
    pass

@csrf_exempt
def center_events(request, ed_center_id):
    project_year = datetime.now().year
    project_year = get_object_or_404(TicketProjectYear, year=project_year)
    center_year = get_object_or_404(
        EducationCenterTicketProjectYear, 
        ed_center=ed_center_id, project_year=project_year
    )
    if request.method == 'POST':
        if 'add-event' in request.POST:
            cycle = EventsCycle.objects.get(id=request.POST["cycle_id"])
            profession = TicketProfession.objects.get(id=request.POST["profession_id"])
            event_date = request.POST["event_date"]
            TicketEvent.objects.create(
                ed_center=center_year,
                cycle=cycle,
                profession=profession,
                event_date=datetime.strptime(event_date, "%d.%m.%Y"),
                status="CRTD"
            )
        if 'delete-event' in request.POST:
            event = TicketEvent.objects.get(id=request.POST["event_id"])
            event.delete()
        if 'assign-quota' in request.POST:
            event = TicketEvent.objects.get(id=request.POST["event_id"])
            quota = TicketQuota.objects.get(id=request.POST["quota_id"])
            reserved_quota = int(request.POST["reserved_quota"])
            event_quota = QuotaEvent.objects.create(
                event=event,
                quota=quota,
                reserved_quota=reserved_quota
            )
            quota.reserved_quota += reserved_quota
            quota.save()
            double_quotas = QuotaEvent.objects.filter(
                event=event,
                quota=quota,
            ).exclude(id=event_quota.id)
            if len(double_quotas) != 0:
                reserved_quota = 0
                for double_quota in double_quotas:
                    reserved_quota += double_quota.reserved_quota
                event_quota.reserved_quota += reserved_quota
                quota.reserved_quota += reserved_quota
                quota.save()
                event_quota.save()
                double_quota.delete()
        return HttpResponseRedirect(reverse(
            "ticket_center_events", args=[ed_center_id]))
    cycles = EventsCycle.objects.filter(project_year=project_year).annotate(
            center_events_count=Count(
                Case(When(events__ed_center=center_year, then=1),
                    output_field=IntegerField()),)
    ).prefetch_related('events')
    quotas = TicketQuota.objects.filter(ed_center=center_year.ed_center).exclude(
        approved_value=0
    )
    professions = TicketProfession.objects.filter(
        quotas__in=quotas
    ).distinct()

    return render(request, "future_ticket/center_events.html", {
        'center_year': center_year,
        'cycles': cycles,
        'quotas': quotas,
        'professions': professions,
    })

