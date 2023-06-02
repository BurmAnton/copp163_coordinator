from datetime import date, datetime
from django.utils.formats import date_format
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django.db.models import Case, When, Value, Count, OuterRef, Subquery
from django.utils.encoding import escape_uri_path
from django.db.models.functions import Concat
from citizens.models import School

from users.models import DisabilityType

from . import imports
from . import exports
from .forms import ImportDataForm, ImportTicketDataForm
from .contracts import create_document, combine_all_docx, create_application
from .models import BankDetails, Competence, ContractorsDocument, DocumentType,\
                    EducationCenter, EducationCenterHead, EducationProgram,\
                    Employee, Group, Teacher, Workshop
from federal_empl_program.models import EdCenterEmployeePosition,\
                                        EdCenterIndicator, EdCenterQuota,\
                                        EducationCenterProjectYear, Indicator,\
                                        ProjectPosition, ProjectYear
from future_ticket.models import AgeGroup, ProfEnviroment, ProgramAuthor, TicketFullQuota, TicketProfession, TicketProgram, TicketProjectYear,TicketProjectPosition,\
                                 EducationCenterTicketProjectYear, \
                                 TicketEdCenterEmployeePosition, \
                                 TicketIndicator, EdCenterTicketIndicator, TicketQuota

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


def applications(request):
    project = request.GET.get('p', '')
    project_year = request.GET.get('y', '')
    if project_year != '': project_year = int(project_year)
    else: project_year = datetime.now().year

    if project == 'bilet':
        project_year = get_object_or_404(TicketProjectYear, year=project_year)
        centers_project_year = EducationCenterTicketProjectYear.objects.filter(
            project_year=project_year,
        )
    else:
        project_year = get_object_or_404(ProjectYear, year=project_year)
        centers_project_year = EducationCenterProjectYear.objects.filter(
            project_year=project_year
        )
        project = 'zen'

    return render(request, "education_centers/applications.html", {
        'project': project,
        'project_year': project_year,
        'centers_project_year': centers_project_year
    })

@csrf_exempt
def ed_center_application(request, ed_center_id):
    project = request.GET.get('p', '')
    if 'bilet' in request.POST: project = 'bilet'
    project_year = request.GET.get('y', '')
    if project_year != '': project_year = int(project_year)
    else: project_year = datetime.now().year
    stage = request.GET.get('s', '')
    if stage != '': stage = int(stage)
    else: stage = 1
    ed_center = get_object_or_404(EducationCenter, id=ed_center_id)
    full_quota = None
    if project == 'bilet':
        project_year = get_object_or_404(TicketProjectYear, year=project_year)
        center_project_year = EducationCenterTicketProjectYear.objects.get_or_create(
                project_year=project_year,ed_center=ed_center)[0]
        full_quota = get_object_or_404(TicketFullQuota, project_year=project_year)
    else:
        project_year = get_object_or_404(ProjectYear, year=project_year)
        center_project_year = EducationCenterProjectYear.objects.get_or_create(
                project_year=project_year, ed_center=ed_center)[0]
        center_quota, is_new = EdCenterQuota.objects.get_or_create(
            ed_center_year=center_project_year
        )
    
    if request.method == "POST":
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
                description = request.POST['description']
                teacher_id =request.POST['teacher_id']
                teacher = get_object_or_404(Teacher, id=teacher_id)
                email = request.POST['email']
                phone = request.POST['phone']
                author, is_new = ProgramAuthor.objects.get_or_create(
                    teacher=teacher,
                )
                author.phone=phone
                author.email=email
                author.save()
                
                age_groups = request.POST.getlist('age_groups')
                disability_types = request.POST.getlist('disability_types')
                program = TicketProgram(
                    ed_center=ed_center,
                    profession=profession,
                    description=description,
                    author=author,
                    program_link=request.POST['program_link'],
                    education_form='FLL',
                )
                program.save()
                program.disability_types.add(*disability_types)
                program.age_groups.add(*age_groups)
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
            teacher = Teacher(
                organization=ed_center,
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                employment_type = request.POST['employment_type'],
                education_level = request.POST['education_level'],
                education_major = request.POST['education_major'],
                position = request.POST['position'],
                experience = request.POST['experience']
            )
            if project == 'bilet':
                teacher.bvb_experience = request.POST['bvb_experience']
            else:
                teacher.additional_education = request.POST['additional_education']
            teacher.save()
            if 'bilet' in request.POST:
                teacher.ticket_programs.add(*request.POST.getlist('programs'))
            else:
                teacher.programs.add(*request.POST.getlist('programs'))
            teacher.save()
        elif 'add-workshop' in request.POST:
            stage=5
            name = request.POST['name'].strip().capitalize()
            workshop = Workshop(
                name=name,
                education_center=ed_center,
                classes_type = request.POST['classes_type'],
                equipment = request.POST['equipment'],
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
                program.description = request.POST['description']
                program.program_link=request.POST['program_link']
                teacher_id =request.POST['teacher_id']
                teacher = get_object_or_404(Teacher, id=teacher_id)
                email = request.POST['email']
                phone = request.POST['phone']
                author, is_new = ProgramAuthor.objects.get_or_create(
                    teacher=teacher,
                )
                author.phone=phone
                author.email=email
                author.save()
                program.author = author
                program.education_form = request.POST['education_form']
                age_groups = request.POST.getlist('age_groups')
                program.age_groups.clear()
                program.age_groups.add(*age_groups)
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
                program.education_form = 'FLL'
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
            teacher.organization=ed_center
            teacher.employment_type = request.POST['employment_type']
            teacher.education_level = request.POST['education_level']
            teacher.education_major = request.POST['education_major']
            teacher.position = request.POST['position']
            teacher.experience = request.POST['experience']
            if project == 'bilet':
                teacher.bvb_experience = request.POST['bvb_experience']
            else:
                teacher.additional_education = request.POST['additional_education']
            teacher.save()
            if 'bilet' in request.POST:
                teacher.ticket_programs.clear()
                teacher.ticket_programs.add(*request.POST.getlist('programs'))
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
            else:
                program = get_object_or_404(EducationProgram, id=program_id)
            program.delete()
        elif 'exclude-program' in request.POST:
            stage=3
            program_id = request.POST['program_id']
            program = get_object_or_404(TicketProgram, id=program_id)
            center_project_year.programs.remove(program)
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
            if   step == "1":
                center_project_year.step_1_commentary = comment
                center_project_year.step_1_check = False
                center_project_year.stage = 'RWRK'
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
            center_project_year.save()
        elif 'generate-application'in request.POST:
           center_project_year.stage = 'FRMD'
           center_project_year.save()
           doc_type = get_object_or_404(DocumentType, name="Заявка")
           old_applications = ContractorsDocument.objects.filter(
                                doc_type=doc_type, contractor=ed_center)
           old_applications.delete()
           document = create_application(center_project_year)
           
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
        elif 'approve-step' in request.POST:
            step = request.POST['step']
            if   step == "1": center_project_year.step_1_check = True
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
            elif step == "8": 
                center_project_year.step_8_check = True
                stage=8
                center_project_year.stage = 'PRVD'
            if center_project_year.step_1_check and \
               center_project_year.step_2_check and \
               center_project_year.step_3_check and \
               center_project_year.step_4_check and \
               center_project_year.step_5_check and \
               center_project_year.step_6_check:
                center_project_year.stage = 'VRFD'
            center_project_year.save()
        elif 'send-application' in request.POST:
            center_project_year.stage = 'FLLD'
            center_project_year.save()
        elif 'upload-application' in request.POST:
            stage = 8
            center_project_year.stage = 'FRMD'
            center_project_year.save()
            form = ImportTicketDataForm(request.POST, request.FILES)
            if form.is_valid():
                center_project_year.application_file = request.FILES['import_file']
                center_project_year.appl_track_number = request.POST['appl_track_number']
                center_project_year.save()
    approved_programs = None
    chosen_professions = None
    schools = None
    if project == 'bilet':
        filled_positions = TicketEdCenterEmployeePosition.objects.filter(
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
        programs = center_project_year.programs.all().annotate(
            num_teachers=Count('teachers'),
            num_workshops=Count('workshops'),
        )
        chosen_professions = TicketProfession.objects.filter(
            programs__in=programs).distinct()
        schools = School.objects.all()
        approved_programs = TicketProgram.objects.filter(status='PRWD')
        approved_programs= approved_programs.exclude(
            id__in=center_project_year.programs.all()
        )
        center_quota = TicketQuota.objects.filter(ed_center=ed_center)
    else:
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
        programs = ed_center.programs.all().annotate(
            num_teachers=Count('teachers'),
            num_workshops=Count('workshops'),
        )
        
    workshops = Workshop.objects.filter(
        education_center=ed_center).exclude(name=None)
    competencies = Competence.objects.filter(is_irpo=True)
    employees = ed_center.employees.all().annotate(
            full_name=Concat('last_name', Value(' '), 'first_name', Value(' '), 
                            'middle_name')
        )
    teachers = ed_center.teachers.all().annotate(
        full_name=Concat('last_name', Value(' '), 'first_name', Value(' '), 
                        'middle_name')
    )
    professions = TicketProfession.objects.all()
    prof_enviroments = ProfEnviroment.objects.all()

    disability_types = DisabilityType.objects.all()
    age_groups = AgeGroup.objects.all()

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
        'form': ImportTicketDataForm()
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
                head = EducationCenterHead()
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
def documents_fed(request):
    doc_filter = None
    if request.method == "POST":
        doc_filter = dict()
        doc_filter['ed_centers'] = request.POST.getlist("ed_centers")
        doc_filter['ed_centers'] = EducationCenter.objects.filter(
            id__in=doc_filter['ed_centers']
        )
        doc_filter['programs'] = request.POST.getlist("programs")
        doc_filter['programs'] = EducationProgram.objects.filter(
            id__in=doc_filter['programs']
        )
        doc_filter['start_date'] = request.POST['start_date']
        doc_filter['end_date'] = request.POST['end_date']
    ed_centers = EducationCenter.objects.exclude(ed_center_documents=None)
    programs = EducationProgram.objects.all()

    return render(request, "education_centers/fed-empl.html", {
        "ed_centers": ed_centers,
        "programs": programs,
        "doc_filter": doc_filter
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