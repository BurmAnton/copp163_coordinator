from datetime import datetime

from django.db.models import Case, Count, F, Sum, When
from django.forms import IntegerField
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from citizens.models import School
from education_centers.forms import (ImportSchoolOrderDataForm,
                                     ImportTicketDataForm)
from education_centers.models import EducationCenter
from future_ticket.models import (EducationCenterTicketProjectYear,
                                  EventsCycle, PartnerEvent, QuotaEvent, SchoolProjectYear,
                                  StudentBVB, TicketEvent, TicketFullQuota,
                                  TicketProfession, TicketProjectYear,
                                  TicketQuota)
from regions.models import City
from users.models import Organization

from . import exports, imports
from .forms import ImportDataForm, ImportDocumentForm, ImportParticipantsForm
from .utils import generate_ticket_act


def equalize_quotas(request):
    quotas = TicketQuota.objects.all()
    for quota in quotas:
        quota.approved_value = quota.value
        quota.save()

    return HttpResponseRedirect(reverse("quotas"))

@csrf_exempt
def quotas(request):
    if not(request.user.is_superuser):
        return HttpResponseRedirect(reverse("login"))
    if 'save-quotas' in request.POST:
        for quota in TicketQuota.objects.exclude(
            value=0, approved_value=0, reserved_quota=0, completed_quota=0):
            approved_value = request.POST[f'{quota.id}']
            if int(approved_value) != quota.approved_value:
                quota.approved_value = int(approved_value)
                quota.save()
    project_year = get_object_or_404(TicketProjectYear, year=2024)
    centers_project_year = EducationCenterTicketProjectYear.objects.filter(
        project_year=project_year
    )
    ffull_quota = get_object_or_404(TicketFullQuota, project_year=project_year)
    
    quota_stat = dict()
    quota_stat_all = dict()
    quota_stat_all['full_qouta'] = 0
    quota_stat_all['federal_quota'] = 0
    quota_stat_all['none_federal_quota'] = 0
    quota_stat_all['approved_full_qouta'] = 0
    quota_stat_all['approved_federal_quota'] = 0
    quota_stat_all['approved_none_federal_quota'] = 0
    quota_stat_all['partic_full_qouta'] = 0
    quota_stat_all['partic_federal_quota'] = 0
    quota_stat_all['partic_none_federal_quota'] = 0
    quota_stat_all['reserved_full_qouta'] = 0
    quota_stat_all['reserved_federal_quota'] = 0
    quota_stat_all['reserved_none_federal_quota'] = 0
    quota_stat_all['completed_full_qouta'] = 0
    quota_stat_all['completed_federal_quota'] = 0
    quota_stat_all['completed_none_federal_quota'] = 0
    for ter_admin in School.TER_CHOICES:
        quota_stat[ter_admin[1]] = dict()
        ter_admin_schools = School.objects.filter(territorial_administration=ter_admin[0])
        schools_quota = TicketQuota.objects.filter(school__in=ter_admin_schools, quota=ffull_quota).distinct()
        
        federal_quota = schools_quota.filter(is_federal=True).distinct().aggregate(Sum("approved_value"), Sum("value"), Sum("reserved_quota"), Sum("completed_quota"))
        quota_event = QuotaEvent.objects.filter(quota__in=schools_quota.filter(is_federal=True))
        events = TicketEvent.objects.filter(quotas__in=quota_event)
        if federal_quota['value__sum'] == None: federal_quota['value__sum'] = 0
        if federal_quota['approved_value__sum'] == None: federal_quota['approved_value__sum'] = 0
        if federal_quota['reserved_quota__sum'] == None: federal_quota['reserved_quota__sum'] = 0
        if federal_quota['completed_quota__sum'] == None: federal_quota['completed_quota__sum'] = 0
        quota_stat[ter_admin[1]]['federal_quota'] = federal_quota['value__sum']
        quota_stat[ter_admin[1]]['approved_federal_quota'] = federal_quota['approved_value__sum']
        quota_stat[ter_admin[1]]['partic_federal_quota'] = StudentBVB.objects.filter(
            event__in=events, school__in=ter_admin_schools, is_double=False, is_attend=True
        ).count()
        quota_stat[ter_admin[1]]['reserved_federal_quota'] = federal_quota['reserved_quota__sum']
        quota_stat[ter_admin[1]]['completed_federal_quota'] = federal_quota['completed_quota__sum']
        
        none_federal_quota = schools_quota.filter(is_federal=False).distinct().aggregate(Sum("approved_value"), Sum("value"), Sum("reserved_quota"), Sum("completed_quota"))
        quota_event = QuotaEvent.objects.filter(quota__in=schools_quota.filter(is_federal=False))
        events = TicketEvent.objects.filter(quotas__in=quota_event)
        if none_federal_quota['value__sum'] == None: none_federal_quota['value__sum'] = 0
        if none_federal_quota['approved_value__sum'] == None: none_federal_quota['approved_value__sum'] = 0
        if none_federal_quota['reserved_quota__sum'] == None: none_federal_quota['reserved_quota__sum'] = 0
        if none_federal_quota['completed_quota__sum'] == None: none_federal_quota['completed_quota__sum'] = 0
        quota_stat[ter_admin[1]]['none_federal_quota'] = none_federal_quota['value__sum']
        quota_stat[ter_admin[1]]['approved_none_federal_quota'] = none_federal_quota['approved_value__sum']
        quota_stat[ter_admin[1]]['partic_none_federal_quota'] = StudentBVB.objects.filter(
            event__in=events, school__in=ter_admin_schools, is_double=False, is_attend=True
        ).count()
        quota_stat[ter_admin[1]]['reserved_none_federal_quota'] = none_federal_quota['reserved_quota__sum']
        quota_stat[ter_admin[1]]['completed_none_federal_quota'] = none_federal_quota['completed_quota__sum']
        
        full_quota = schools_quota.distinct().aggregate(Sum("approved_value"), Sum("value"), Sum("reserved_quota"), Sum("completed_quota"))
        quota_event = QuotaEvent.objects.filter(quota__in=schools_quota)
        events = TicketEvent.objects.filter(quotas__in=quota_event)
        if full_quota['value__sum'] == None: full_quota['value__sum'] = 0
        if full_quota['approved_value__sum'] == None: full_quota['approved_value__sum'] = 0
        if full_quota['reserved_quota__sum'] == None: full_quota['reserved_quota__sum'] = 0
        if full_quota['completed_quota__sum'] == None: full_quota['completed_quota__sum'] = 0
        quota_stat[ter_admin[1]]['full_quota'] = full_quota['value__sum']
        quota_stat[ter_admin[1]]['approved_full_quota'] = full_quota['approved_value__sum']
        quota_stat[ter_admin[1]]['partic_full_quota'] = StudentBVB.objects.filter(
            event__in=events, school__in=ter_admin_schools, is_double=False, is_attend=True
        ).count()
        quota_stat[ter_admin[1]]['reserved_full_quota'] = full_quota['reserved_quota__sum']
        quota_stat[ter_admin[1]]['completed_full_quota'] = full_quota['completed_quota__sum']
        
        quota_stat_all['full_qouta'] += full_quota['value__sum']
        quota_stat_all['federal_quota'] += federal_quota['value__sum']
        quota_stat_all['none_federal_quota'] += none_federal_quota['value__sum']
        quota_stat_all['approved_full_qouta'] += full_quota['approved_value__sum']
        quota_stat_all['approved_federal_quota'] += federal_quota['approved_value__sum']
        quota_stat_all['approved_none_federal_quota'] += none_federal_quota['approved_value__sum']
        quota_stat_all['partic_full_qouta'] += quota_stat[ter_admin[1]]['partic_full_quota']
        quota_stat_all['partic_federal_quota'] += quota_stat[ter_admin[1]]['partic_federal_quota']
        quota_stat_all['partic_none_federal_quota'] += quota_stat[ter_admin[1]]['partic_none_federal_quota']
        quota_stat_all['reserved_full_qouta'] += full_quota['reserved_quota__sum']
        quota_stat_all['reserved_federal_quota'] += federal_quota['reserved_quota__sum']
        quota_stat_all['reserved_none_federal_quota'] += none_federal_quota['reserved_quota__sum']
        quota_stat_all['completed_full_qouta'] += full_quota['completed_quota__sum']
        quota_stat_all['completed_federal_quota'] += federal_quota['completed_quota__sum']
        quota_stat_all['completed_none_federal_quota'] += none_federal_quota['completed_quota__sum']
    
    quotas = TicketQuota.objects.filter(quota=ffull_quota).exclude(
        value=0, approved_value=0, reserved_quota=0, completed_quota=0
        ).select_related('quota', 'ed_center', 'school', 'profession')
    if 'export-quotas' in request.POST:
           return exports.qoutas(quotas)
    ed_centers = EducationCenter.objects.exclude(ticket_quotas=None)
    schools = School.objects.exclude(ticket_quotas=None)

    return render(request, "future_ticket/quotas.html", {
        'project_year': project_year,
        'centers_project_year': centers_project_year,
        'full_quota': ffull_quota,
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
def import_quotas_2024(request):
    form = ImportDataForm()
    message = None
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.quotas(form)
            message = data
    
    return render(request, "future_ticket/import_quotas_2024.html", {
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
def export_events(request):
    return exports.events()

@csrf_exempt
def export_ticket_programs(request):
    return exports.programs()

def schools_application(request):
    message = None
    if request.method == 'POST':
        project_year = 2023
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


@csrf_exempt
def center_events(request, ed_center_id):
    project_year = 2024
    project_year = get_object_or_404(TicketProjectYear, year=project_year)
    full_quota = get_object_or_404(TicketFullQuota, project_year=project_year)
    center_year = get_object_or_404(
        EducationCenterTicketProjectYear, 
        ed_center=ed_center_id, project_year=project_year
    )
    contact_person = center_year.ed_center.contact_person
    if not(request.user.is_superuser) and request.user != contact_person:
        return HttpResponseRedirect(reverse("login"))
    import_output = None
    if request.method == 'POST':
        if 'add-event' in request.POST:
            cycle = EventsCycle.objects.get(id=request.POST["cycle_id"])
            profession = TicketProfession.objects.get(id=request.POST["profession_id"])
            event_date = request.POST["event_date"]
            start_time = request.POST["start_time"]
            TicketEvent.objects.create(
                ed_center=center_year,
                cycle=cycle,
                profession=profession,
                event_date=datetime.strptime(event_date, "%d.%m.%Y"),
                start_time=start_time,
                status="CRTD"
            )
        elif 'change-event' in request.POST:
            event_id = request.POST["event_id"]
            event = TicketEvent.objects.get(id=event_id)
            event.profession = TicketProfession.objects.get(
                id=request.POST["profession_id"])
            event.event_date = datetime.strptime(request.POST["event_date"], "%d.%m.%Y")
            event.start_time = request.POST["start_time"]
            photo_link = request.POST["photo_link"]
            if photo_link == "":
                event.photo_link = None
            else: 
                event.photo_link = photo_link
                quota_events = QuotaEvent.objects.filter(event=event)      
                for quota_event in quota_events:
                    if quota_event.completed_quota == 0:
                        quota_event.completed_quota = quota_event.reserved_quota
                        quota_event.quota.completed_quota += QuotaEvent.objects.filter(event=event).aggregate(completed_quota=Sum("completed_quota"))['completed_quota']
                        quota_event.quota.save()
            event.save()
        elif 'delete-event' in request.POST:
            event = TicketEvent.objects.get(id=request.POST["event_id"])
            event.delete()
        elif 'assign-quota' in request.POST:
            event = TicketEvent.objects.get(id=request.POST["event_id"])
            quota = TicketQuota.objects.get(id=request.POST["quota_id"])
            reserved_quota = int(request.POST["reserved_quota"])
            if quota.free_quota >= reserved_quota:
                event_quota = QuotaEvent.objects.create(
                    event=event,
                    quota=quota,
                    completed_quota=0,
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
            reserved_quota = QuotaEvent.objects.filter(
                quota=quota
            ).aggregate(reserved_quota_sum=Sum('reserved_quota'))['reserved_quota_sum']
            quota.reserved_quota = reserved_quota
            quota.save()
        elif 'delete-quota' in request.POST:
            quota = TicketQuota.objects.get(id=request.POST["quota_id"])
            quota.delete()
        elif 'change-quota' in request.POST:
            quota = TicketQuota.objects.get(id=request.POST["quota_id"])
            school = School.objects.get(id=request.POST["school_id"])
            if quota.school != school:
                transfered_quota = int(request.POST["transfered_quota"])
                new_quota, is_new = TicketQuota.objects.get_or_create(
                    quota=quota.quota,
                    ed_center=quota.ed_center,
                    school=school,
                    profession=quota.profession,
                    is_federal=quota.is_federal
                )
                if is_new:
                    new_quota.value = transfered_quota
                    new_quota.approved_value = transfered_quota
                else:
                    new_quota.value = new_quota.value + transfered_quota
                    new_quota.approved_value = new_quota.approved_value\
                                                + transfered_quota
                new_quota.save()
                if transfered_quota == quota.approved_value and\
                quota.reserved_quota == 0 and quota.completed_quota == 0:
                    quota.delete()
                else:
                    quota.value = quota.value - transfered_quota
                    quota.approved_value = quota.approved_value \
                                           - transfered_quota
                    quota.save()
        elif 'delete-participant' in request.POST:
            participant = StudentBVB.objects.get(
                                        id=request.POST["participant_id"])
            participant.delete()
        elif 'change-event-quota' in request.POST:
            quota_event = QuotaEvent.objects.get(
                                        id=request.POST["event_quota_id"])
            minus_quota = int(request.POST["minus_quota"])
            if minus_quota < quota_event.reserved_quota:
                new_quota_event = QuotaEvent.objects.create(
                    quota = quota_event.quota,
                    event = quota_event.event,
                    completed_quota = quota_event.completed_quota,
                    reserved_quota = quota_event.reserved_quota - minus_quota
                )
            quota_event.delete()
            reserved_quota = QuotaEvent.objects.filter(
                quota=quota_event.quota
            ).aggregate(reserved_quota_sum=Sum('reserved_quota'))['reserved_quota_sum']
            quota_event.quota.reserved_quota = reserved_quota
            quota_event.quota.save()
        elif 'create-act' in request.POST:
           generate_ticket_act(center_year)
           center_year.stage = 'ACT'
           center_year.save()
        elif 'upload-bill' in request.POST:
            form = ImportDocumentForm(request.POST, request.FILES)
            if form.is_valid():
                center_year.bill_file = request.FILES['import_file']
                if bool(center_year.act_file) and\
                bool(center_year.bill_file):
                    if center_year.is_ndc == False:
                        center_year.stage = 'NVC'
                    elif bool(center_year.ndc_bill_file):
                        center_year.stage = 'NVC'
                center_year.save()
        elif 'upload-ndc-bill'in request.POST:
            form = ImportDocumentForm(request.POST, request.FILES)
            if form.is_valid():
                center_year.ndc_bill_file = request.FILES['import_file']
                if bool(center_year.act_file) and\
                bool(center_year.bill_file):
                    if center_year.is_ndc == False:
                        center_year.stage = 'NVC'
                    elif bool(center_year.ndc_bill_file):
                        center_year.stage = 'NVC'
                center_year.save()
        elif 'upload-act' in request.POST:
            form = ImportDocumentForm(request.POST, request.FILES)
            if form.is_valid():
                center_year.act_file = request.FILES['import_file']
                if bool(center_year.act_file) and\
                bool(center_year.bill_file):
                    if center_year.is_ndc == False:
                        center_year.stage = 'NVC'
                    elif bool(center_year.ndc_bill_file):
                        center_year.stage = 'NVC'
                center_year.save()

        if 'import-participants' in request.POST:
            form = ImportParticipantsForm(request.POST, request.FILES)
            if form.is_valid():
                event = TicketEvent.objects.get(id=request.POST["event_id"])
                import_output = imports.import_participants(form, event)
            else: import_output = "FormError"
        else:
            return HttpResponseRedirect(reverse(
                "ticket_center_events", args=[ed_center_id]))
    cycles = EventsCycle.objects.filter(project_year=project_year).order_by(
        'cycle_number').annotate(
            center_events_count=Count(
                Case(When(events__ed_center=center_year, then=1),
                    output_field=IntegerField()),)
    ).prefetch_related('events')
    quotas = TicketQuota.objects.filter(ed_center=ed_center_id, quota=full_quota)

    professions = TicketProfession.objects.filter(
        quotas__in=quotas
    ).distinct()

    events_wo_links = TicketEvent.objects.filter(
        ed_center=center_year, photo_link=None).count()
    events_wo_time = TicketEvent.objects.filter(
        ed_center=center_year, start_time=None).count()
    act_ready = False
    if quotas.exclude(approved_value=F('completed_quota')).count() == 0\
    and events_wo_links == 0 and events_wo_time == 0:
        act_ready = True

    return render(request, "future_ticket/center_events.html", {
        'center_year': center_year,
        'cycles': cycles,
        'quotas': quotas,
        'professions': professions,
        'schools': School.objects.all(),
        'participants_form': ImportParticipantsForm(),
        'import_output': import_output,
        'act_ready': act_ready,
        'form': ImportDocumentForm()
    })


@csrf_exempt
def partners_events(request):
    message = None
    if 'add-event' in request.POST:
        partner, is_new = Organization.objects.get_or_create(
            name=request.POST["partner"].strip()
        )
        status = "PRV" if request.user.is_superuser else "CRT"
            
        event, is_new = PartnerEvent.objects.get_or_create(
            name=request.POST["name"].strip(),
            partner=partner,
            status=status,
            period=request.POST["period"].strip(),
            signup_link=request.POST["signup_link"].strip(),
            contact=request.POST["contact"].strip(),
            contact_email=request.POST["contact_email"].strip(),
            contact_phone=request.POST["contact_phone"].strip(),
            description=request.POST["description"],
            instruction=request.POST["instruction"]
        )
        event.cities.add(*request.POST.getlist('cities'))
        event.save()
        if is_new == False:
            return HttpResponseRedirect(reverse("partners_events"))
        message = "EventAddedSuccessfully"
    events = PartnerEvent.objects.filter(status='PRV')
    cities = City.objects.all()
    filter_cities = cities.exclude(partner_events=None)

    chosen_cities = None
    if 'filter-events' in request.POST:
        chosen_cities = request.POST.getlist('cities')
        if len(chosen_cities) != 0:
            events = events.filter(cities__name__in=chosen_cities).distinct()
        else:
            chosen_cities = None

    return render(request, "future_ticket/partners_events.html", {
        'events': events,
        'message': message,
        'cities': cities,
        'filter_cities': filter_cities,
        'chosen_cities': chosen_cities
    })