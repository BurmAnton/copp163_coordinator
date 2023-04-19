from datetime import date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django.db.models import Case, When, Value

from .forms import ImportDataForm
from .models import ContractorsDocument, DocumentType, EducationCenter, EducationProgram, Group
from .contracts import create_document, combine_all_docx

# Create your views here.
def index(request):
    center = EducationCenter.objects.filter(contact_person=request.user)
    if len(center) != 0:
        center = center[0].name
        return JsonResponse(center, safe=False)
    return JsonResponse(False, safe=False)

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