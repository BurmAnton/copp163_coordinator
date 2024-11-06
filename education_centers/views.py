import json
from datetime import date, datetime

from django.core.files import File
from django.db.models import Case, Count, OuterRef, Subquery, Sum, Value, When, Q
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.encoding import escape_uri_path
from django.utils.formats import date_format
from django.views.decorators.csrf import csrf_exempt

from citizens.models import School
from federal_empl_program.models import (AVAILABLE_MONTHS, Application, EdCenterEmployeePosition,
                                         EdCenterIndicator,
                                         EducationCenterProjectYear, Indicator, MonthProgramPlan, NetworkAgreement, ProgramPlan,
                                         ProjectPosition, ProjectYear)
from future_ticket.models import (AgeGroup, ContractorsDocumentTicket,
                                  DocumentTypeTicket, EdCenterTicketIndicator,
                                  EducationCenterTicketProjectYear,
                                  ProfEnviroment, ProgramAuthor,
                                  TicketEdCenterEmployeePosition,
                                  TicketFullQuota, TicketIndicator,
                                  TicketProfession, TicketProgram,
                                  TicketProjectPosition, TicketProjectYear,
                                  TicketQuota)
from future_ticket.utils import generate_document_ticket, generate_ticket_certificate
from users.models import DisabilityType

from . import exports, imports
from .contracts import (combine_all_docx, create_application, create_document,
                        create_ticket_application, generate_application_doc, generate_concent_doc, generate_net_agreement)
from .forms import (IRPOProgramForm, ImportDataForm, ImportTicketContractForm,
                    ImportTicketDataForm, SignedApplicationDataForm)
from .models import (AbilimpicsWinner, ApplicationDocEdu, BankDetails, Competence,
                     ContractorsDocument, DocumentType, EducationCenter,
                     EducationProgram, Employee, Group, Teacher, Workshop)


# Create your views here.
def index(request):
    center = EducationCenter.objects.filter(contact_person=request.user)
    if len(center) != 0:
        center = center[0].name
        return JsonResponse(center, safe=False)
    return JsonResponse(False, safe=False)

@csrf_exempt
def export_programs(request):
    return exports.programs(ed_centers=None)

@csrf_exempt
def export_ed_centers(request):
    return exports.ed_centers()

@csrf_exempt
def export_workshops(request):
    return exports.workshops()

@csrf_exempt
def application_docs(request):
    passport_series = None
    message = None
    form = "generate_application"
    if request.method == "POST":
        passport_series = request.POST['passport_series'].strip()
        passport_series = passport_series.replace(" ", "")
        if len(passport_series) >= 5:
            passport_series = passport_series[:4] + " " + passport_series[4:]
        if 'generate-application' in request.POST:
            application_docs = ApplicationDocEdu.objects.filter(passport_series=passport_series)

            if len(application_docs) == 0:
                message = "404"
            else:
                application_doc = application_docs.first()
                application_doc.index = request.POST['index']
                application_doc.address = request.POST['address']
                application_doc.status_doc = 'GEN'
                application_doc.save()
                doc = generate_application_doc(application_doc)
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename=zayavlenie.docx'
                doc.save(response)
                return response
        elif 'upload-application' in request.POST:
           form = "upload_application"
           application_docs = ApplicationDocEdu.objects.filter(passport_series=passport_series)
           if len(application_docs) == 0:
               message = "404"
           else:
                application_doc = application_docs.first()
                form = SignedApplicationDataForm(request.POST, request.FILES)
                if form.is_valid():
                    document = form.cleaned_data['import_file']
                    application_doc.signed_file = document
                    application_doc.status_doc = 'UPL'
                    application_doc.save()
                    message = "success_upload"
                    
    return render(request, "education_centers/application_docs.html", {
        'file_input': SignedApplicationDataForm,
        'form': form,
        'message': message
    })


@csrf_exempt
def applications(request):
    project = request.GET.get('p', '')
    project_year = request.GET.get('y', '')
    programs_count = None
    breakpoint()
    if 'bilet' in request.POST: project = 'bilet'
    if project_year != '': project_year = int(project_year)
    elif project == 'zan': project_year = 2023
    else: project_year = 2024
    if project == 'bilet':
        project_year = get_object_or_404(TicketProjectYear, year=project_year)
        centers_project_year = EducationCenterTicketProjectYear.objects.filter(
            project_year=project_year,).select_related('ed_center')
        stages = EducationCenterTicketProjectYear.STAGES
    else:
        project_year = get_object_or_404(ProjectYear, year=project_year)
        centers_project_year = EducationCenterProjectYear.objects.filter(
            project_year=project_year
        ).select_related('ed_center')
        project = 'zen'
        stages = EducationCenterProjectYear.STAGES  
        programs = EducationProgram.objects.exclude(new_agreements=None).count()
        filled_programs = EducationProgram.objects.exclude(new_agreements=None).exclude(
            Q(program_word='') | Q(program_pdf='') | Q(teacher_review='') | Q(employer_review='') | Q(program_word=None) | Q(program_pdf=None) | Q(teacher_review=None) | Q(employer_review=None)
        ).count()
        if filled_programs == 0: programs_count = f'{filled_programs}/{programs} (0.0%)'
        else: programs_count = f'{filled_programs}/{programs} ({round(filled_programs/programs, 2) * 100}%)'
    chosen_stages = None
    if request.method == "POST":
        if 'filter-events' in request.POST:
            chosen_stages = request.POST.getlist('stages')
            if len(chosen_stages) != 0:
                centers_project_year = centers_project_year.filter(
                    stage__in=chosen_stages)
        elif 'centers_paid' in request.POST:
            for center in centers_project_year.filter(stage='PNVC'):
                if f'center_{center.id}' in request.POST:
                    center.stage = 'NVCP'
                center.save()
            for center in centers_project_year.filter(stage='NVCP'):
                if f'center_{center.id}' not in request.POST:
                    center.stage = 'PNVC'
                center.save()
        elif 'generate-certificate' in request.POST:
            project = 'bilet'
            center_year_id = request.POST['center_year']
            center_year = get_object_or_404(
                EducationCenterTicketProjectYear, id=center_year_id)
            ed_center = center_year.ed_center
            ed_center_name = ed_center.short_name if ed_center.short_name != None else ed_center.name
            ed_center_name = ed_center_name.strip().replace("  ", " ").replace(" ", "_")
            certificate = generate_ticket_certificate(center_year)
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename=справка_{ed_center_name}.docx'
            certificate.save(response)
            return response
        else:
            data = json.loads(request.body.decode("utf-8"))
            stage = data['stage']
            centers_list = data['centers_list']
            project = data['project']
            for center_id in centers_list:
                if project == 'bilet':
                    center_year = get_object_or_404(
                        EducationCenterTicketProjectYear, id=center_id)
                else:
                    center_year = get_object_or_404(
                        EducationCenterProjectYear, id=center_id)
                center_year.stage = stage
                center_year.save()

            return JsonResponse(
                {"message": "Centers stage changed successfully."}, status=201)

    return render(request, "education_centers/applications.html", {
        'project': project,
        'project_year': project_year,
        'centers_project_year': centers_project_year,
        'stages': stages,
        'chosen_stages': chosen_stages,
        'programs_count': programs_count
    })

@csrf_exempt
def abilimpics(request):
    if 'choose-program' in request.POST:
        program_id = request.POST['program']
        program = EducationProgram.objects.get(id=program_id)
        winner_id = request.POST['winner']
        winner = AbilimpicsWinner.objects.get(id=winner_id)
        winner.program = program
        winner.ed_center = program.ed_center
        winner.save()

    winner = AbilimpicsWinner.objects.filter(email=request.user.email)
    if request.user.is_authenticated and\
    len(winner) == 1:
        winner = winner[0]
        if winner.program == None: stage = 'program'
        else: stage = 'notice'
    else:
        return HttpResponseRedirect(reverse("login"))
    programs = EducationProgram.objects.filter(is_abilimpics=True)
    template = get_object_or_404(
                DocumentType, name="Шаблон заявки (Абилимпикс)")


    return render(request, "education_centers/abilimpics.html", {
        'winner': winner,
        'programs': programs,
        'stage': stage,
        'template': template
    })


def get_qualified_programs(programs):
    programs = programs.exclude(num_teachers__lt=2, num_workshops__lt=1)
    qualified_programs = []
    for program in programs:
        if program.teachers.exclude(consent_file=None).count() >= 2:
            if program.workshops.exclude(address=None).count() >= 1:
                qualified_programs.append(program)
    return qualified_programs


def programs_plan(request):
    pass
    

@csrf_exempt
def ed_center_application(request, ed_center_id):
    project = request.GET.get('p', '')
    if 'bilet' in request.POST: project = 'bilet'
    project_year = request.GET.get('y', '')
    if project_year != '': project_year = int(project_year)
    elif project == 'zan': project_year = 2023
    else: project_year = 2024
    stage = request.GET.get('s', '')
    if stage != '': stage = int(stage)
    else: stage = 7
    ed_center = get_object_or_404(EducationCenter, id=ed_center_id)
    full_quota = None
    contract = None
    if project == 'bilet':
        project_year = get_object_or_404(TicketProjectYear, year=project_year)
        center_project_year = EducationCenterTicketProjectYear.objects.get_or_create(
                project_year=project_year,ed_center=ed_center)[0]
        full_quota = get_object_or_404(TicketFullQuota, project_year=project_year)
        if center_project_year.is_ndc:
            contract_type = get_object_or_404(
                DocumentTypeTicket, name="Договор с ЦО с НДС")
        else:
            contract_type = get_object_or_404(
                DocumentTypeTicket, name="Договор с ЦО без НДС")
        if center_project_year.stage == 'FNSHD':
            form = ImportTicketContractForm()
            contract = ContractorsDocumentTicket.objects.filter(
                doc_type=contract_type,
                contractor=ed_center
            )
            if len(contract) == 1: 
                contract = contract[0]
            else: 
                contract = generate_document_ticket(
                    center_project_year, contract_type)        
    else:
        project_year = get_object_or_404(ProjectYear, year=project_year)
        center_project_year = EducationCenterProjectYear.objects.get_or_create(
                project_year=project_year, ed_center=ed_center)[0]
        center_quota = None
    net_agreement = None
    if project != 'bilet':
        net_agreement, is_new = NetworkAgreement.objects.get_or_create(
            ed_center_year=center_project_year
        )

    if request.method == "POST":
        if 'download-contract' in request.POST:
                if contract != None:
                    register_number = contract.register_number
                else: register_number = None
                document = generate_document_ticket(center_project_year, contract_type, register_number, True)
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename=zayavka_{date.today()}.docx'
                document.save(response)
                return response
        if 'add-employee' in request.POST:
            stage=2
            last_name = request.POST['last_name'].strip().capitalize()
            first_name = request.POST['first_name'].strip().capitalize()
            if request.POST['middle_name'] != None:
                middle_name = request.POST['middle_name'].strip().capitalize()
            else: middle_name = None
            position = request.POST['position'].strip().lower()
            last_name_r = request.POST['last_name_r'].strip().capitalize()
            first_name_r = request.POST['first_name_r'].strip().capitalize()
            if request.POST['middle_name_r'] != None:
                middle_name_r = request.POST['middle_name_r'].strip().capitalize()
            else: middle_name = None
            position_r = request.POST['position_r'].strip().lower()
            try:
                if request.POST['is_head'] == 'on': is_head = True
            except: is_head = False

            employee = Employee(
                organization=ed_center,
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                position=position,
                last_name_r=last_name_r,
                first_name_r=first_name_r,
                middle_name_r=middle_name_r,
                position_r=position_r,
                is_head=is_head,
                phone=request.POST['phone'],
                email=request.POST['email']
            )
            employee.save()
        elif 'add-position' in request.POST:
            stage=2
            employee_id = request.POST['employee_id']
            employee = get_object_or_404(Employee, id=employee_id)
            if project == 'bilet':
                position_id = request.POST['position_id']
                position = get_object_or_404(TicketProjectPosition, id=position_id)
                employee_position = TicketEdCenterEmployeePosition(
                    position=position,
                    ed_center=ed_center,
                    employee=employee
                )
            else:
                position_id = request.POST['position_id']
                position = get_object_or_404(ProjectPosition, id=position_id)
                employee_position = EdCenterEmployeePosition(
                    position=position,
                    ed_center=ed_center,
                    employee=employee
                )
            if position.is_basis_needed:
                employee_position.acts_basis = request.POST['acts_basis']
            employee_position.save()
        elif 'add-org' in request.POST:
                try: bank_details = BankDetails.objects.get(organization=ed_center)
                except: 
                    bank_details = BankDetails()
                    bank_details.organization = ed_center
                bank_details.inn = request.POST['inn'].strip()
                bank_details.kpp = request.POST['kpp'].strip()
                bank_details.oktmo = request.POST['oktmo'].strip()
                bank_details.ogrn = request.POST['ogrn'].strip()
                bank_details.okpo = request.POST['okpo'].strip()
                bank_details.okved = request.POST['okved'].strip()
                bank_details.bank = request.POST['bank'].strip()
                bank_details.bank_inn = request.POST['bank_inn'].strip()
                bank_details.bank_kpp = request.POST['bank_kpp'].strip()
                bank_details.biс = request.POST['biс'].strip()
                bank_details.personal_account_number = request.POST['personal_account_number'].strip()
                bank_details.account_number = request.POST['account_number'].strip()
                bank_details.corr_account = request.POST['corr_account'].strip()
                bank_details.accountant = request.POST['accountant'].strip()
                bank_details.phone = request.POST['phone'].strip()
                bank_details.email = request.POST['email'].strip()
                bank_details.legal_address = request.POST['legal_address'].strip()
                bank_details.mail_address = request.POST['mail_address'].strip()
                bank_details.save()
                ed_center.ed_license = request.POST['ed_license'].strip()
                ed_center.license_issued_by = request.POST['license_issued_by'].strip()
                try:
                    if request.POST['is_ndc'] == 'on': is_ndc = True
                except: is_ndc = False
                if 'bilet' not in request.POST:
                    if is_ndc == False:
                        ed_center.is_ndc = False
                        ed_center.none_ndc_reason = request.POST['none_ndc_reason'].strip()
                    else:
                        ed_center.is_ndc = True
                        ed_center.none_ndc_reason = ""
                else:
                    if is_ndc == False:
                        center_project_year.is_ndc = False
                        center_project_year.none_ndc_reason = request.POST['none_ndc_reason'].strip()
                    else:
                        center_project_year.is_ndc = True
                        center_project_year.none_ndc_reason = ""
                ed_center.name = request.POST['name'].strip()
                ed_center.short_name = request.POST['short_name'].strip()
                ed_center.short_name_r = request.POST['short_name_r'].strip()
                ed_center.home_city = request.POST['home_city'].strip()
                ed_center.entity_sex = request.POST['entity_sex']
                ed_center.save()
                try:
                    if request.POST['is_federal'] == 'on': is_federal = True
                except: is_federal = False
                if 'bilet' not in request.POST:
                    center_project_year.appl_docs_link = request.POST['appl_docs_link']
                center_project_year.is_federal = is_federal
                center_project_year.save()
        elif 'add-exp-ticket' in request.POST:
            stage=8
            center_project_year.exp_ticket_events = request.POST['exp_ticket_events']
            center_project_year.exp_predprof = request.POST['exp_predprof']
            center_project_year.exp_skillsguide = request.POST['exp_skillsguide']
            center_project_year.exp_other_events = request.POST['exp_other_events']
            try: 
                if request.POST['is_disability_friendly'] == 'on': is_disability_friendly = True
            except: is_disability_friendly = False
            center_project_year.is_disability_friendly = is_disability_friendly
            center_project_year.save()
        elif 'add-program' in request.POST:
            stage=3
            if 'bilet' in request.POST:
                try:
                    if request.POST['new_profession'] == 'on': 
                        new_profession = True
                except: new_profession = False
                if new_profession:
                    profession = request.POST['profession']
                    prof_enviroment_id = request.POST['prof_enviroment_id']
                    prof_enviroment = get_object_or_404(
                        ProfEnviroment, 
                        id=prof_enviroment_id
                    )
                    profession = TicketProfession(
                        name=profession,
                        prof_enviroment=prof_enviroment,
                        is_federal=False,
                        is_centers=True
                    )
                    profession.save()
                else:
                    profession_id = request.POST['profession_id']
                    profession = get_object_or_404(
                        TicketProfession, 
                        id=profession_id
                    )
                # description = request.POST['description']
                # teacher_id =request.POST['teacher_id']
                # teacher = get_object_or_404(Teacher, id=teacher_id)
                # email = request.POST['email']
                # phone = request.POST['phone']
                # author, is_new = ProgramAuthor.objects.get_or_create(
                #     teacher=teacher,
                # )
                # author.phone=teacher.phone
                # author.email=teacher.email
                # author.save()
                teachers = request.POST.getlist('teachers')
                # age_groups = request.POST.getlist('age_groups')
                disability_types = request.POST.getlist('disability_types')
                program = TicketProgram(
                    ed_center=ed_center,
                    profession=profession,
                    # description=description,
                    # author=author,
                    # program_link=request.POST['program_link'],
                    education_form='FLL',
                )
                program.save()
                program.disability_types.add(*disability_types)
                program.teachers.add(*teachers)
                # program.age_groups.add(*age_groups)
                center_project_year.programs.add(program)
            else:
                competence_id = request.POST['competence_id']
                competence = get_object_or_404(Competence, id=competence_id)
                program_name = request.POST['program_name']
                profession = request.POST['profession']
                description = request.POST['description']
                entry_requirements = request.POST['entry_requirements']
                program_type = request.POST['program_type']
                education_form = request.POST['education_form']
                duration = int(request.POST['duration'])
                notes = request.POST['notes']
                program = EducationProgram(
                    competence=competence,
                    program_name=program_name,
                    ed_center=ed_center,
                    profession=profession,
                    description=description,
                    entry_requirements=entry_requirements,
                    program_type=program_type,
                    education_form=education_form,
                    duration=duration,
                    notes=notes
                )
                program.save()
        elif 'add-programs' in request.POST:
            stage=3
            for program in request.POST:
                if request.POST[program] == 'on':
                    center_project_year.programs.add(int(program))
            center_project_year.save()
        elif 'add-teacher' in request.POST:
            stage=4
            last_name = request.POST['last_name'].strip().capitalize()
            first_name = request.POST['first_name'].strip().capitalize()
            if request.POST['middle_name'] != None:
                middle_name = request.POST['middle_name'].strip().capitalize()
            else: middle_name = None
            experience_2024 = request.POST.getlist('experience_2024')
            teacher = Teacher(
                organization=ed_center,
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                employment_type = request.POST['employment_type'],
                # education_level = request.POST['education_level'],
                # education_major = request.POST['education_major'],
                # position = request.POST['position'],
                # experience = request.POST['experience']
                email = "test@test.ru", 
                phone = "+999", 
                is_experienced = "is_experienced" in experience_2024,
                is_certified = "is_certified" in experience_2024,
            )
            if project == 'bilet':
                pass
                # teacher.bvb_experience = request.POST['bvb_experience']
            else:
                teacher.additional_education = request.POST['additional_education']
            teacher.save()
            if 'bilet' in request.POST:
                pass
                # teacher.ticket_programs.add(*request.POST.getlist('programs'))
            else:
                teacher.programs.add(*request.POST.getlist('programs'))
            teacher.save()
        elif 'add-workshop' in request.POST:
            stage=5
            name = request.POST['name'].strip().capitalize()
            workshop = Workshop(
                name=name,
                education_center=ed_center,
                classes_type=request.POST['classes_type'],
                equipment=request.POST['equipment'],
                address=request.POST['address']
            )
            workshop.save()
            if 'bilet' in request.POST:
                workshop.ticket_programs.add(*request.POST.getlist('programs'))
            else:
                workshop.programs.add(*request.POST.getlist('programs'))
            workshop.save()
        elif 'add-indicators' in request.POST:
            stage=6
            if project == 'bilet':
                indicators = TicketIndicator.objects.filter(
                    project_year=project_year, is_free_form=False)
                for indicator in indicators:
                    center_indicator, is_new = EdCenterTicketIndicator.objects.get_or_create(
                        ed_center=ed_center,
                        indicator=indicator
                    )
                    center_indicator.value = request.POST[f'{indicator.id}'].strip()
                    center_indicator.save()
                
                try:
                    if request.POST['is_disability'] == 'on': is_disability = True
                except: is_disability = False
                center_project_year.is_disability = is_disability
                center_project_year.save()
            else:
                indicators = Indicator.objects.filter(
                    project_year=project_year, is_free_form=False)
                for indicator in indicators:
                    center_indicator, is_new = EdCenterIndicator.objects.get_or_create(
                        ed_center=ed_center,
                        indicator=indicator
                    )
                    center_indicator.value_2021 = request.POST[f'{indicator.id}_2021'].strip()
                    center_indicator.value_2022 = request.POST[f'{indicator.id}_2022'].strip()
                    center_indicator.save()
                free_indicators = Indicator.objects.filter(
                    project_year=project_year, 
                    is_free_form=True
                )
                for indicator in free_indicators:
                    center_indicator, is_new = EdCenterIndicator.objects.get_or_create(
                        ed_center=ed_center,
                        indicator=indicator
                    )
                    center_indicator.free_form_value = request.POST[f'{indicator.id}'].strip()
                    center_indicator.save()
        elif 'change-employee' in request.POST:
            stage=2
            employee_id = request.POST['employee_id']
            employee = get_object_or_404(Employee, id=employee_id)
            employee.last_name = request.POST['last_name'].strip().capitalize()
            employee.first_name = request.POST['first_name'].strip().capitalize()
            if request.POST['middle_name'] != None:
                employee. middle_name = request.POST['middle_name'].strip().capitalize()
            else: employee.middle_name = None
            employee.position = request.POST['position'].strip().lower()
            employee.last_name_r = request.POST['last_name_r'].strip().capitalize()
            employee.first_name_r = request.POST['first_name_r'].strip().capitalize()
            if request.POST['middle_name_r'] != None:
                employee.middle_name_r = request.POST['middle_name_r'].strip().capitalize()
            else: employee.middle_name = None
            employee.position_r = request.POST['position_r'].strip().lower()
            try:
                if request.POST['is_head'] == 'on': employee.is_head = True
            except: employee.is_head = False
            employee.phone=request.POST['phone']
            employee.email=request.POST['email']
            employee.save()
        elif 'change-position' in request.POST:
            stage=2
            
            employee_id = request.POST['employee_id']
            employee = get_object_or_404(Employee, id=employee_id)
            if project == 'bilet':
                position_id = request.POST['position_id']
                position = get_object_or_404(TicketProjectPosition, id=position_id)
                employee_position = TicketEdCenterEmployeePosition.objects.filter(
                    position=position,
                    ed_center=ed_center
                ).first()
            else:
                position_id = request.POST['position_id']
                position = get_object_or_404(ProjectPosition, id=position_id)
                employee_position = EdCenterEmployeePosition.objects.filter(
                    position=position,
                    ed_center=ed_center
                ).first()
            employee_position.employee = employee
            if position.is_basis_needed:
                employee_position.acts_basis = request.POST['acts_basis']
            employee_position.save()
        elif 'change-old-program' in request.POST:
            stage=3
            program_id = request.POST['program_id']
            program = get_object_or_404(TicketProgram, id=program_id)
            teachers = request.POST.getlist('teachers')
            program.teachers.remove(*teachers)
            program.teachers.add(*teachers)
            program.save()
        elif 'change-program' in request.POST:
            stage=3
            program_id = request.POST['program_id']
            if 'bilet' in request.POST:
                program = get_object_or_404(TicketProgram, id=program_id)
                profession_id = request.POST['profession_id']
                profession = get_object_or_404(
                    TicketProfession, 
                    id=profession_id
                )
                program.profession = profession
                # program.description = request.POST['description']
                # program.program_link=request.POST['program_link']
                # teacher_id =request.POST['teacher_id']
                # teacher = get_object_or_404(Teacher, id=teacher_id)
                # email = request.POST['email']
                # phone = request.POST['phone']
                # author, is_new = ProgramAuthor.objects.get_or_create(
                #     teacher=teacher,
                # )
                # author.phone=teacher.phone
                # author.email=teacher.email
                # author.save()
                # program.author = author
                # program.education_form = request.POST['education_form']
                age_groups = request.POST.getlist('age_groups')
                # program.age_groups.clear()
                # program.age_groups.add(*age_groups)
                teachers = request.POST.getlist('teachers')
                program.teachers.clear()
                program.teachers.add(*teachers)
                disability_types = request.POST.getlist('disability_types')
                program.disability_types.clear()
                program.disability_types.add(*disability_types)
            else:
                program = get_object_or_404(EducationProgram, id=program_id)
                competence_id = request.POST['competence_id']
                program.competence = get_object_or_404(Competence, id=competence_id)
                program.program_name = request.POST['program_name']
                program.profession = request.POST['profession']
                program.description = request.POST['description']
                program.entry_requirements = request.POST['entry_requirements']
                program.program_type = request.POST['program_type']
                program.education_form = request.POST['education_form']
                program.duration = int(request.POST['duration'])
                program.notes = request.POST['notes']
            program.save()
        elif 'change-teacher' in request.POST:
            stage=4
            teacher_id = request.POST['teacher_id']
            teacher = get_object_or_404(Teacher, id=teacher_id)
            teacher.last_name = request.POST['last_name'].strip().capitalize()
            teacher.first_name = request.POST['first_name'].strip().capitalize()
            if request.POST['middle_name'] != None:
                teacher.middle_name = request.POST['middle_name'].strip().capitalize()
            else: teacher.middle_name = None
            experience_2024 = request.POST.getlist('experience_2024')
            teacher.organization=ed_center
            teacher.employment_type = request.POST['employment_type']
            # teacher.email = request.POST['email']
            # teacher.phone = request.POST['phone']
            teacher.is_experienced = "is_experienced" in experience_2024
            teacher.is_certified = "is_certified" in experience_2024
            # teacher.education_level = request.POST['education_level']
            # teacher.education_major = request.POST['education_major']
            # teacher.position = request.POST['position']
            # teacher.experience = request.POST['experience']
            if project == 'bilet':
                pass
                # teacher.bvb_experience = request.POST['bvb_experience']
            else:
                teacher.additional_education = request.POST['additional_education']
            teacher.save()
            if 'bilet' in request.POST:
                pass
                # teacher.ticket_programs.clear()
                # teacher.ticket_programs.add(*request.POST.getlist('programs'))
            else:
                teacher.programs.clear()
                teacher.programs.add(*request.POST.getlist('programs'))
            teacher.save()
        elif 'change-workshop' in request.POST:
            stage=5
            workshop_id = request.POST['workshop_id']
            workshop = get_object_or_404(Workshop, id=workshop_id)
            workshop.name = request.POST['name'].strip().capitalize()
            workshop.education_center=ed_center
            workshop.classes_type = request.POST['classes_type']
            workshop.equipment = request.POST['equipment']
            workshop.address=request.POST['address']
            workshop.save()
            if 'bilet' in request.POST:
                workshop.ticket_programs.clear()
                workshop.ticket_programs.add(*request.POST.getlist('programs'))
            else:
                workshop.programs.clear()
                workshop.programs.add(*request.POST.getlist('programs'))
            workshop.save()
        elif 'delete-employee' in request.POST:
            stage=2
            employee_id = request.POST['employee_id']
            employee = get_object_or_404(Employee, id=employee_id)
            employee.delete()
        elif 'delete-program' in request.POST:
            stage=3
            program_id = request.POST['program_id']
            if project == 'bilet':
                program = get_object_or_404(TicketProgram, id=program_id)
                profession = program.profession
                TicketQuota.objects.filter(quota=full_quota, ed_center=ed_center, profession=profession).delete()
                locked_quota = TicketQuota.objects.filter(quota=full_quota, ed_center=ed_center).aggregate(quota_sum=Sum('value'))['quota_sum']
                if locked_quota is  None:
                    locked_quota = 0
                center_project_year.locked_quota = locked_quota
                center_project_year.save()
            else:
                program = get_object_or_404(EducationProgram, id=program_id)
            program.delete()
        elif 'exclude-program' in request.POST:
            stage=3
            program_id = request.POST['program_id']
            program = get_object_or_404(TicketProgram, id=program_id)
            center_project_year.programs.remove(program)
            profession = program.profession
            TicketQuota.objects.filter(quota=full_quota, ed_center=ed_center, profession=profession).delete()
            locked_quota = TicketQuota.objects.filter(quota=full_quota, ed_center=ed_center).aggregate(quota_sum=Sum('value'))['quota_sum']
            if locked_quota is None:
                locked_quota = 0
            center_project_year.locked_quota = locked_quota
            center_project_year.save()
        elif 'delete-teacher' in request.POST:
            stage=4
            teacher_id = request.POST['teacher_id']
            teacher = get_object_or_404(Teacher, id=teacher_id)
            teacher.delete()
        elif 'delete-workshop' in request.POST:
            stage=5
            workshop_id = request.POST['workshop_id']
            workshop = get_object_or_404(Workshop, id=workshop_id)
            workshop.delete()
        elif 'export-programs' in request.POST:
            return exports.programs(ed_centers=[ed_center,])
        elif 'step-comment' in request.POST:
            step = request.POST['step']
            comment = request.POST['step_commentary']
            if step == "1":
                center_project_year.step_1_commentary = comment
                center_project_year.step_1_check = False
                center_project_year.stage = 'RWRK'
                stage=1
            elif step == "2": 
                center_project_year.step_2_commentary = comment
                center_project_year.step_2_check = False
                center_project_year.stage = 'RWRK'
                stage=2
            elif step == "3": 
                center_project_year.step_3_commentary = comment
                center_project_year.step_3_check = False
                center_project_year.stage = 'RWRK'
                stage=3
            elif step == "4": 
                center_project_year.step_4_commentary = comment
                center_project_year.step_4_check = False
                center_project_year.stage = 'RWRK'
                stage=4
            elif step == "5": 
                center_project_year.step_5_commentary = comment
                center_project_year.step_5_check = False
                center_project_year.stage = 'RWRK'
                stage=5
            elif step == "6": 
                center_project_year.step_6_commentary = comment
                center_project_year.step_6_check = False
                center_project_year.stage = 'RWRK'
                stage=6
            elif step == "7": 
                center_project_year.step_7_commentary = comment
                center_project_year.step_7_check = False
                center_project_year.stage = 'RWRK'
                stage=7
            elif step == "8": 
                center_project_year.step_8_commentary = comment
                center_project_year.step_8_check = False
                center_project_year.stage = 'RWRK'
                stage=8
            center_project_year.save()
        elif 'generate-application'in request.POST:
            if center_project_year.stage != 'FNSHD':
               center_project_year.stage = 'FRMD'
               center_project_year.save()
            if 'bilet' in request.POST:
               doc_type = get_object_or_404(DocumentType, name="Заявка (БВБ)")
               old_applications = ContractorsDocument.objects.filter(
                                        doc_type=doc_type, contractor=ed_center)
               old_applications.delete()
               document = create_ticket_application(center_project_year)
            else:
                doc_type = get_object_or_404(DocumentType, name="Заявка")
                programs = request.POST.getlist('programs')
                old_applications = ContractorsDocument.objects.filter(
                                    doc_type=doc_type, contractor=ed_center)
                old_applications.delete()
                if len(programs) == 0:
                    document = create_application(center_project_year)
                else:
                    programs = EducationProgram.objects.filter(id__in=programs)
                    document = create_application(center_project_year, programs)
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename=zayavka_{date.today()}.docx'
            document.save(response)
            return response
        elif 'set-quota' in request.POST:
            stage=7
            center_quota.quota_72 = request.POST['quota_72']
            center_quota.quota_144 = request.POST['quota_144']
            center_quota.quota_256 = request.POST['quota_256']
            center_quota.save()
        elif 'add-school' in request.POST:
            stage=7
            profession_id = request.POST['profession']
            profession = get_object_or_404(TicketProfession, id=profession_id)
            is_federal = profession.is_federal
            school_id = request.POST['school_id']
            school = get_object_or_404(School, id=school_id)
            value = int(request.POST['quota'])
            quota, is_new = TicketQuota.objects.get_or_create(
                quota=full_quota,
                ed_center=ed_center,
                profession=profession,
                school=school,
                is_federal=is_federal
            )
            quota.value = value
            quota.save()
            locked_quota = TicketQuota.objects.filter(quota=full_quota, ed_center=ed_center).aggregate(quota_sum=Sum('value'))['quota_sum']
            if locked_quota is None:
                locked_quota = 0
            center_project_year.locked_quota = locked_quota
            center_project_year.save()
        elif 'delete-quota' in request.POST:
            stage=7
            quota = get_object_or_404(TicketQuota, id=request.POST['id'])
            quota.delete()
            locked_quota = TicketQuota.objects.filter(quota=full_quota, ed_center=ed_center).aggregate(quota_sum=Sum('value'))['quota_sum']
            if locked_quota is None:
                locked_quota = 0
            center_project_year.locked_quota = locked_quota
            center_project_year.save()
        elif 'approve-step' in request.POST:
            step = request.POST['step']
            if  step == "1": 
                center_project_year.step_1_check = True
                stage=1
            elif step == "2": 
                center_project_year.step_2_check = True
                stage=2
            elif step == "3": 
                center_project_year.step_3_check = True
                stage=3
            elif step == "4": 
                center_project_year.step_4_check = True
                stage=4
            elif step == "5": 
                center_project_year.step_5_check = True
                stage=5
            elif step == "6": 
                center_project_year.step_6_check = True
                stage=6
            elif step == "7": 
                center_project_year.step_7_check = True
                stage=7
            elif step == "8": 
                center_project_year.step_8_check = True
                stage=8
                center_project_year.stage = 'PRVD'
            if center_project_year.step_1_check and \
                center_project_year.step_2_check and \
                center_project_year.step_3_check and \
                center_project_year.step_4_check and \
                center_project_year.step_7_check and \
                center_project_year.step_8_check:
                center_project_year.stage = 'VRFD'
            if center_project_year.step_6_check:
                center_project_year.stage = 'VRFD'
            center_project_year.save()
        elif 'send-application' in request.POST:
            center_project_year.stage = 'FLLD'
            center_project_year.save()
        elif 'upload-application' in request.POST:
            stage = 8
            center_project_year.stage = 'DWNLD'
            center_project_year.save()
            form = ImportTicketDataForm(request.POST, request.FILES)
            if form.is_valid():
                center_project_year.application_file = request.FILES['import_file']
                center_project_year.appl_track_number = request.POST['appl_track_number']
                center_project_year.save()
        elif 'upload-contract' in request.POST:
            stage = 9
            center_project_year.save()
            form = ImportTicketDataForm(request.POST, request.FILES)
            if form.is_valid():
                contract.doc_file = request.FILES['import_file']
                contract.doc_file.name = contract.doc_file.name
                contract.save()
        elif 'import-program' in request.POST:
            stage = 3
            form = ImportTicketContractForm(request.POST, request.FILES)
            if form.is_valid():
                program_id = request.POST['program_id']
                program = EducationProgram.objects.get(id=program_id)
                program.program_file = request.FILES['import_file']
                program.save()
        elif 'generate_consent' in request.POST:
            stage = 4
            teacher_id = request.POST['teacher_id']
            teacher = Teacher.objects.get(id=teacher_id)
            document = generate_concent_doc(teacher)
            response = HttpResponse(content_type=f'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename={f"согласие_{teacher.last_name}"}.docx'
            document.save(response)
            return response
        elif 'generate-net' in request.POST:
            stage = 6
            agreement = generate_net_agreement(net_agreement)
            response = HttpResponse(content_type=f'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename={f"сетевой_договор_{net_agreement.agreement_number}"}.docx'
            agreement.save(response)
            return response
        elif 'import-consent' in request.POST:
            stage = 4
            form = ImportTicketContractForm(request.POST, request.FILES)
            if form.is_valid():
                teacher_id = request.POST['teacher_id']
                teacher = Teacher.objects.get(id=teacher_id)
                teacher.consent_file = request.FILES['import_file']
                teacher.save()
        elif 'import-net' in request.POST:
            stage = 6
            form = ImportTicketContractForm(request.POST, request.FILES)
            if form.is_valid():
                net_agreement.agreement_file = request.FILES['import_file']
                net_agreement.save()
                center_project_year.stage = 'DWNLD'
                center_project_year.save()
        elif 'irpo-program-import' in request.POST:
            stage = 6
            form = IRPOProgramForm(request.POST, request.FILES)
            if form.is_valid():
                program_id = request.POST['program_id']
                program = EducationProgram.objects.get(id=program_id)
                if form.cleaned_data['program_word'] is not None:
                    program.program_word = form.cleaned_data['program_word']
                if form.cleaned_data['program_pdf'] is not None:
                    program.program_pdf = form.cleaned_data['program_pdf']
                if form.cleaned_data['teacher_review'] is not None:
                    program.teacher_review = form.cleaned_data['teacher_review']
                if form.cleaned_data['employer_review'] is not None:
                    program.employer_review = form.cleaned_data['employer_review']
                program.save()
    approved_programs = None
    chosen_professions = None
    schools = None
    ticket_programs = None
    professions = None

    
    workshops = Workshop.objects.filter(education_center=ed_center
        ).exclude(name=None)
    teachers = ed_center.teachers.exclude(email=None).annotate(
        full_name=Concat('last_name', Value(' '), 'first_name', Value(' '), 'middle_name'))
    form = ImportTicketDataForm()
    if project == 'bilet':
        workshops = workshops.prefetch_related('ticket_programs')
        teachers = teachers.prefetch_related('ticket_programs')
        filled_positions = TicketEdCenterEmployeePosition.objects.filter(
            position__project_year=project_year,
            ed_center=ed_center,
        )
        empty_positions = project_year.positions.exclude(
            positions_employees__in=filled_positions
        )
        indicators = TicketIndicator.objects.filter(
            project_year=project_year, 
            is_free_form=False
        ).annotate(
            ed_center_indicator=Subquery(
                EdCenterTicketIndicator.objects.filter(
                    ed_center=ed_center,
                    indicator=OuterRef('pk')
                ).values('value')[:1]
            ),
        )
        free_indicators = TicketIndicator.objects.filter(
            project_year=project_year, 
            is_free_form=True
        ).annotate(
            ed_center_indicator=Subquery(
                EdCenterTicketIndicator.objects.filter(
                    ed_center=ed_center,
                    indicator=OuterRef('pk')
                ).values('free_form_value')[:1]
            )
        )
        programs = center_project_year.programs.all(
            ).prefetch_related('age_groups', 'disability_types'
            ).select_related('author', 'author__teacher', 'profession', 'ed_center', 'profession__prof_enviroment').annotate(
            author_name=Concat('author__teacher__last_name', Value(' '), 'author__teacher__first_name', Value(' '), 
                            'author__teacher__middle_name')
        )
        ticket_programs = programs.values('id', 'profession__name',)
        professions = TicketProfession.objects.filter(is_2024=True).values(
            'id', 'name', 'prof_enviroment__name')
        chosen_professions = TicketProfession.objects.filter(
            programs__in=programs).distinct().values(
            'id', 'name', 'prof_enviroment__name')
        schools = School.objects.all().values('id', 'name')
        approved_programs = TicketProgram.objects.filter(
            status='PRWD', profession__is_federal=True)
        approved_programs = approved_programs.exclude(
            id__in=center_project_year.programs.all()
        ).prefetch_related('age_groups', 'disability_types').select_related(
            'author', 'profession', 'ed_center', 'profession__prof_enviroment').annotate(
            author_name=Concat('author__teacher__last_name', Value(' '), 'author__teacher__first_name', Value(' '), 
                            'author__teacher__middle_name')
        )
        center_quota = TicketQuota.objects.filter(ed_center=ed_center)
    else:
        workshops = workshops.prefetch_related('programs')
        teachers = teachers.prefetch_related('programs')
        filled_positions = EdCenterEmployeePosition.objects.filter(
            ed_center=ed_center,
        )
        empty_positions = project_year.positions.exclude(
            positions_employees__in=filled_positions
        )

        indicators = Indicator.objects.filter(
            project_year=project_year, 
            is_free_form=False
        ).annotate(
            ed_center_indicator_2021=Subquery(
                EdCenterIndicator.objects.filter(
                    ed_center=ed_center,
                    indicator=OuterRef('pk')
                ).values('value_2021')[:1]
            ),
            ed_center_indicator_2022=Subquery(
                EdCenterIndicator.objects.filter(
                    ed_center=ed_center,
                    indicator=OuterRef('pk')
                ).values('value_2022')[:1]
            ),
        )
        free_indicators = Indicator.objects.filter(
            project_year=project_year, 
            is_free_form=True
        ).annotate(
            ed_center_indicator=Subquery(
                EdCenterIndicator.objects.filter(
                    ed_center=ed_center,
                    indicator=OuterRef('pk')
                ).values('free_form_value')[:1]
            )
        )
        programs = ed_center.programs.all().select_related(
                'competence' 
            ).annotate(
                num_teachers=Count('teachers', distinct=True),
                num_workshops=Count('workshops', distinct=True),
            )
        
    competencies = Competence.objects.filter(is_irpo=True).values('id', 'title')
    employees = ed_center.employees.all().annotate(
            full_name=Concat('last_name', Value(' '), 'first_name', Value(' '), 
                            'middle_name')
        )
    prof_enviroments = ProfEnviroment.objects.all().values('id', 'name')

    disability_types = DisabilityType.objects.all().values('id', 'name')
    age_groups = AgeGroup.objects.all()

    qualified_programs = None
    if project != 'bilet':
        qualified_programs = get_qualified_programs(programs)
    if 'add-network' in request.POST:
        net_agreement.programs.add(*request.POST.getlist('qualified_programs'))
        net_agreement.save()
        stage = 6
    elif 'change-plan' in request.POST:
        plans=[]
        stage = 7
        for program in net_agreement.programs.all():
            for monthly_plan in program.plan.monthly_plans.all():
                new_monthly_plan = int(request.POST[f'plan{ monthly_plan.id }'])
                if monthly_plan.students_count != new_monthly_plan:
                    monthly_plan.students_count = new_monthly_plan
                    plans.append(monthly_plan)
        MonthProgramPlan.objects.bulk_update(plans, ['students_count'])

    #quotas
    # for program in net_agreement.programs.all():
    #     program_plan, _ = ProgramPlan.objects.get_or_create(program=program)
    #     if program_plan.monthly_plans.all().count() != 7:
    #         for month in AVAILABLE_MONTHS:
    #             MonthProgramPlan.objects.get_or_create(plan=program_plan, month=month[0])
    
    # plans = ProgramPlan.objects.filter(program__in=programs)
    # monthly_plans = []
    # for month in AVAILABLE_MONTHS:
    #     monthly_plans.append(
    #         MonthProgramPlan.objects.filter(
    #             plan__in=plans, month=month[0]
    #         ).aggregate(month_sum=Sum('students_count'))['month_sum']
    #     )
    # try:    
    #     monthly_plans.append(sum(monthly_plans))
    # except TypeError:
    #     pass
    
    #applications
    project_year = get_object_or_404(ProjectYear, year=2024)
    applications = Application.objects.filter(
        project_year=project_year, education_center=ed_center
    ).order_by(
        'education_program',
        'rvr_status',
        'atlas_status'
    )

    
    appl_programs = EducationProgram.objects.filter(programm_applicants__in=applications).distinct()
    groups = Group.objects.filter(students__in=applications).distinct()
    if 'filter-groups' in request.POST:
        stage = 7
        applications = applications.filter(group__in=request.POST.getlist('groups'))

    free_quota = 0
    ready_to_send = True
    if project == 'bilet':
        free_quota = center_project_year.quota - center_project_year.locked_quota
        ready_to_send = False
        if free_quota == 0 and len(empty_positions) == 0:
            if programs.count() != 0:
                if programs.filter(teachers=None).count() == 0:
                    ready_to_send = True

    return render(request, "education_centers/ed_center_application.html", {
        'ed_center': ed_center,
        'employees': employees,
        'programs': programs,
        'approved_programs': approved_programs,
        'teachers': teachers,
        'workshops': workshops,
        'professions': professions,
        'chosen_professions': chosen_professions,
        'schools': schools,
        'prof_enviroments': prof_enviroments,
        'age_groups': age_groups,
        'disability_types': disability_types,
        'project_year': project_year,
        'filled_positions': filled_positions,
        'empty_positions': empty_positions,
        'center_project_year': center_project_year,
        'indicators': indicators,
        'free_indicators': free_indicators,
        'competencies': competencies,
        'center_quota': center_quota,
        'project': project,
        'stage': stage,
        'ticket_programs': ticket_programs,
        'form': form,
        'contract': contract,
        'net_agreement': net_agreement,
        'qualified_programs': qualified_programs,
        'irpo_program_form': IRPOProgramForm,
        # 'plans': plans,
        # 'monthly_plans': monthly_plans,
        # 'months': AVAILABLE_MONTHS
        'applications': applications,
        'groups': groups,
        'free_quota': free_quota,
        'ready_to_send': ready_to_send
    })

@csrf_exempt
def ed_center_groups(request, ed_center):
    ed_center = get_object_or_404(EducationCenter, id=ed_center)
    contract_doc_type = get_object_or_404(DocumentType, name="Договор")
    assig_doc_type = get_object_or_404(DocumentType, name="Задание на оказание услуг")
    act_doc_type = get_object_or_404(DocumentType, name="Акт выполненных работ")
    list_doc_type = get_object_or_404(DocumentType, name="Список лиц, завершивших обучение")
    bill_doc_type = get_object_or_404(DocumentType, name="Счет на оплату")

    if request.method == "POST":
        if 'create_contract' in request.POST:
            create_document(contract_doc_type, ed_center, date.today(), None, None)
        elif 'create_assignment' in request.POST:
            groups = request.POST.getlist("groups")
            groups = Group.objects.filter(id__in=groups)
            parent_doc_type = get_object_or_404(DocumentType, name="Договор")
            doc_parent = ContractorsDocument.objects.filter(doc_type=parent_doc_type, contractor=ed_center)
            create_document(assig_doc_type, ed_center, date.today(), doc_parent[0], groups)
        elif 'create_act' in request.POST:
            doc_parent = request.POST['doc_parent']
            groups_id = request.POST.getlist("act_groups")
            groups = Group.objects.filter(id__in=groups_id)
            doc_parent = get_object_or_404(ContractorsDocument, id=doc_parent)
            act = create_document(act_doc_type, ed_center, date.today(), doc_parent, groups)
            students_lists = []
            for group in groups:
                for student in group.students.all():
                    qual_doc = request.POST[f'student_doc{student.id}']
                    student.qual_doc = qual_doc
                    student.save()
                students_lists.append(
                    create_document(list_doc_type, ed_center, date.today(), act, group)
                    )
            combine_all_docx(act.doc_file,students_lists, act.doc_file.name)
        elif 'create_bill' in request.POST:
            doc_parent = request.POST['act_id']
            doc_parent = get_object_or_404(ContractorsDocument, id=doc_parent)
            form = ImportDataForm(request.POST, request.FILES)
            if form.is_valid():
                bill = create_document(bill_doc_type, ed_center, date.today(), doc_parent, doc_parent.groups.all())
                bill.doc_file = request.FILES['import_file']
                bill.save()
        elif 'head' in request.POST:
            if ed_center.head is None:
                #head = EducationCenterHead()
                head.organization = ed_center
            else: head = ed_center.head
            head.last_name = request.POST['last_name'].strip().capitalize()
            head.first_name = request.POST['first_name'].strip().capitalize()
            if request.POST['middle_name'] != None:
               head.middle_name = request.POST['middle_name'].strip(
                                                            ).capitalize()
            head.position = request.POST['position'].strip().lower()
            head.last_name_r = request.POST['last_name_r'].strip().capitalize()
            head.first_name_r = request.POST['first_name_r'].strip(
                                                           ).capitalize()
            if request.POST['middle_name_r'] != None:
                head.middle_name_r = request.POST['middle_name_r'].strip(
                                                                 ).capitalize()
            head.position_r = request.POST['position_r'].strip().lower()
            head.save()
        elif 'bank-details' in request.POST:
            if ed_center.bank_details is None:
                bank_details = EducationCenterHead()
                bank_details.organization = ed_center
            else: bank_details = ed_center.bank_details
            bank_details.inn = request.POST['inn'].strip()
            bank_details.kpp = request.POST['kpp'].strip()
            bank_details.oktmo = request.POST['oktmo'].strip()
            bank_details.ogrn = request.POST['ogrn'].strip()
            bank_details.okpo = request.POST['okpo'].strip()
            bank_details.okved = request.POST['okved'].strip()
            bank_details.bank = request.POST['bank'].strip()
            bank_details.biс = request.POST['biс'].strip()
            bank_details.account_number = request.POST['account_number'].strip()
            bank_details.corr_account = request.POST['corr_account'].strip()
            bank_details.accountant = request.POST['accountant'].strip()
            bank_details.phone = request.POST['phone'].strip()
            bank_details.email = request.POST['email'].strip()
            bank_details.legal_address = request.POST['legal_address'].strip()
            bank_details.mail_address = request.POST['mail_address'].strip()
            bank_details.save()

    groups = Group.objects.filter(
        workshop__education_center=ed_center
    )
    return render(request, "education_centers/ed_center_groups.html", {
        'form': ImportDataForm(),
        'groups': Group.objects.filter(workshop__education_center=ed_center),
        'free_groups': Group.objects.filter(workshop__education_center=ed_center, group_documents=None),
        "ed_center": ed_center,
        'contracts': ContractorsDocument.objects.filter(
                doc_type=contract_doc_type, 
                contractor=ed_center
            ),
    })

@csrf_exempt
def import_programs(request):
    form = ImportDataForm()
    message = None
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.programs(form)
            message = data
    
    return render(request, "education_centers/import_programs.html", {
        'message': message,
        'form' : ImportDataForm(),
    })

@csrf_exempt
def merge_centers(request):
    form = ImportDataForm()
    message = None
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.merge_ed_centers(form)
            message = data
    
    return render(request, "education_centers/merge_centers.html", {
        'message': message,
        'form' : ImportDataForm(),
    })