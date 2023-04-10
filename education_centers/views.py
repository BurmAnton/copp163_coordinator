from datetime import date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File

from .models import ContractorsDocument, DocumentType, EducationCenter, Group
from .contracts import create_document

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
            doc_parent = request.POST['assignment']
            doc_parent = get_object_or_404(ContractorsDocument, id=doc_parent)
            create_document(act_doc_type, ed_center, date.today(), doc_parent, doc_parent.groups.all())
        elif 'create_students_list' in request.POST:
            doc_parent = request.POST['act']
            doc_parent = get_object_or_404(ContractorsDocument, id=doc_parent)
            for group in doc_parent.groups.all():
                create_document(list_doc_type, ed_center, date.today(), doc_parent, group)

    groups = Group.objects.filter(
        workshop__education_center=ed_center
    )
    return render(request, "education_centers/ed_center_groups.html", {
        "ed_center": ed_center,
        "groups": groups,
        'contracts': ContractorsDocument.objects.filter(
                doc_type=contract_doc_type, 
                contractor=ed_center
            ),
        'assigments': ContractorsDocument.objects.filter(
                doc_type=assig_doc_type, 
                contractor=ed_center
            ),
        'acts': ContractorsDocument.objects.filter(
                doc_type=act_doc_type, 
                contractor=ed_center
            ),
        'students_lists': ContractorsDocument.objects.filter(
                doc_type=list_doc_type, 
                contractor=ed_center
            ),
    })
