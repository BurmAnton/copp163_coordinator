from django import template
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter

from education_centers.models import ContractorsDocument, DocumentType

register = template.Library()

@register.filter
def get_name_r(head):
    return head.get_name(is_r=True)

@register.filter
def get_groups_wo_act(groups):
    act_doc_type = get_object_or_404(DocumentType, name="Акт выполненных работ")
    groups_wo_act = []
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