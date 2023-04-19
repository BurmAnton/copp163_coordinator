from django import template
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter

from education_centers.models import ContractorsDocument, DocumentType

register = template.Library()

@register.filter
def get_name_r(head):
    return head.get_name(is_r=True)

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