from django import template
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter

from education_centers.models import ContractorsDocument, DocumentType
from federal_empl_program.models import EdCenterEmployeePosition, EdCenterIndicator

register = template.Library()

@register.filter
def count_teachers(program, ed_center):
    return len(program.teachers.filter(organization=ed_center))

@register.filter
def count_workshops(program, ed_center):
    return len(program.workshops.filter(education_center=ed_center))

@register.filter
def get_profession_quota(quota, profession):
    return quota.filter(profession=profession['id'])

@register.filter
def exclude_programs(programs, workshop_programs):
    return programs.exclude(id__in=workshop_programs)

@register.filter
def exclude_groups(age_groups, program_age_groups):
    return age_groups.exclude(id__in=program_age_groups)

@register.filter
def exclude_disabilities(disabilities, program_disabilities):
    return disabilities.exclude(id__in=program_disabilities)

@register.filter
def get_groups_wo_act(groups, group_status=None):
    act_doc_type = get_object_or_404(DocumentType, name="Акт выполненных работ")
    groups_wo_act = []
    if group_status != None:
        groups = groups.filter(group_status='COMP')
    for group in groups:
        acts = group.group_documents.filter(doc_type=act_doc_type)
        if len(acts) == 0:
            groups_wo_act.append(group)
    return groups_wo_act

@register.filter
def is_group_wo_act(group):
    act_doc_type = get_object_or_404(DocumentType, name="Акт выполненных работ")
    acts = group.group_documents.filter(doc_type=act_doc_type)
    if len(acts) == 0:
        return True
    return False

@register.filter
def get_list(group):
    list_doc_type = get_object_or_404(DocumentType, name="Список лиц, завершивших обучение")
    students_list = group.group_documents.filter(doc_type=list_doc_type)
    if len(students_list) == 0:
        return None
    return students_list[0]

@register.filter
def get_bill(act):
    bill_doc_type = get_object_or_404(DocumentType, name="Счет на оплату")
    bill = act.children_docs.filter(doc_type=bill_doc_type)
    if len(bill) == 0:
        return None
    return bill[0]

@register.filter
def get_contracts(docs):
    contract_doc_type = get_object_or_404(DocumentType, name="Договор")
    contracts = docs.filter(doc_type=contract_doc_type)
    return contracts

@register.filter
def filter_centers(ed_centers, filter):
    if filter == None or len(filter['ed_centers']) == 0:
        return ed_centers
    return ed_centers.filter(id__in=filter['ed_centers'])

@register.filter
def filter_groups(groups, filter):
    if filter != None:
        if filter['programs'] != 0 and len(filter['programs']) != 0:
            groups = groups.filter(education_program__in=filter['programs'])
        if filter['start_date'] != "":
            groups = groups.filter(start_date__gte=filter['start_date'])
        if filter['end_date'] != "":
            groups = groups.filter(start_date__lte=filter['end_date'])
    return groups