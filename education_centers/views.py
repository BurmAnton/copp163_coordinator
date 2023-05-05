from datetime import date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django.db.models import Case, When, Value

from . import imports
from .forms import ImportDataForm
from .contracts import create_document, combine_all_docx
from .models import BankDetails, Competence, ContractorsDocument, DocumentType, EducationCenter, \
                    EducationCenterHead, EducationProgram, Employee, Group, Teacher, Workshop
from federal_empl_program.models import EdCenterEmployeePosition, ProjectPosition, ProjectYear

# Create your views here.
def index(request):
    center = EducationCenter.objects.filter(contact_person=request.user)
    if len(center) != 0:
        center = center[0].name
        return JsonResponse(center, safe=False)
    return JsonResponse(False, safe=False)

@csrf_exempt
def ed_center_application(request, ed_center_id):
    ed_center = get_object_or_404(EducationCenter, id=ed_center_id)
    project_year = get_object_or_404(ProjectYear, year=2023)
    if request.method == "POST" and 'add-employee' in request.POST:
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
    elif request.method == "POST" and 'add-position' in request.POST:
        position_id = request.POST['position_id']
        position = get_object_or_404(ProjectPosition, id=position_id)
        employee_id = request.POST['employee_id']
        employee = get_object_or_404(Employee, id=employee_id)
        employee_position = EdCenterEmployeePosition(
            position=position,
            ed_center=ed_center,
            employee=employee
        )
        if position.is_basis_needed:
            employee_position.acts_basis = request.POST['acts_basis']
        employee_position.save()
    elif request.method == "POST" and 'add-org' in request.POST:
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
            bank_details.biс = request.POST['biс'].strip()
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
            if is_ndc:
                ed_center.is_ndc = True
                ed_center.none_ndc_reason = request.POST['none_ndc_reason'].strip()
            ed_center.name = request.POST['name'].strip()
            ed_center.short_name = request.POST['short_name'].strip()
            ed_center.short_name_r = request.POST['short_name_r'].strip()
            ed_center.home_city = request.POST['home_city'].strip()
            ed_center.entity_sex = request.POST['entity_sex']
            ed_center.save()
    elif request.method == "POST" and 'add-program' in request.POST:
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
    elif request.method == "POST" and 'add-teacher' in request.POST:
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
            experience = request.POST['experience'],
            additional_education = request.POST['additional_education']
        )
        teacher.save()
        teacher.programs.add(*request.POST.getlist('programs'))
        teacher.save()
    elif request.method == "POST" and 'add-workshop' in request.POST:
        name = request.POST['name'].strip().capitalize()
        workshop = Workshop(
            name=name,
            education_center=ed_center,
            classes_type = request.POST['classes_type'],
            equipment = request.POST['equipment'],
        )
        workshop.save()
        workshop.programs.add(*request.POST.getlist('programs'))
        workshop.save()

    return render(request, "education_centers/ed_center_application.html", {
        'ed_center': ed_center,
        'project_year': project_year,
        'workshops': Workshop.objects.filter(education_center=ed_center).exclude(name=None),
        'competencies': Competence.objects.filter(is_irpo=True)
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
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.programs(form)
            message = data
    
    return render(request, "education_centers/import_programs.html", {
        'message': message,
        'form' : ImportDataForm(),
    })