from django import template
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter
from django.db.models import Sum

from education_centers.models import ContractorsDocument, DocumentType, EducationCenter
from federal_empl_program.models import EdCenterEmployeePosition, EdCenterIndicator
from future_ticket.models import ContractorsDocumentTicket,\
        DocumentTypeTicket, EducationCenterTicketProjectYear, TicketQuota

register = template.Library()

@register.filter
def count_people(ndc_type, pay_status):
    centers = EducationCenterTicketProjectYear.objects.all()
    if ndc_type == "NDC":
        centers = centers.filter(is_ndc=True)
    elif ndc_type == "NNDC":
        centers = centers.filter(is_ndc=False)
    
    if pay_status == "quoted":
        centers = centers.filter(stage__in=('ACT', 'ACTS', 'NVC', 'PNVC'))
    elif pay_status == "paid":
        centers = centers.filter(stage="NVCP")
    
    centers = EducationCenter.objects.filter(
            ticket_project_years__in=centers,
        ).distinct()
    people_count = TicketQuota.objects.filter(
        ed_center__in=centers).aggregate(
        quota_count=Sum('completed_quota'))['quota_count']
    if people_count == None:
        return 0
    return people_count

@register.filter
def count_pay_wo_ndc(ndc_type, pay_status):
    people_count = count_people(ndc_type, pay_status)
    if people_count == 0:
        return "0.00 ₽"
    if ndc_type == "NDC":
        sum = people_count * 1300
        ndc = round((sum / 1.2 - sum) * -1, 2)
        pay_wo_ndc = sum - ndc
    else: 
        pay_wo_ndc = people_count * 1083.33
    return "{:,.2f} ₽".format(pay_wo_ndc).replace(',', ' ')

@register.filter
def count_ndc(ndc_type, pay_status):
    people_count = count_people(ndc_type, pay_status)
    if people_count == 0:
        return "0.00 ₽"
    full_amount = people_count * 1300
    ndc = round((full_amount / 1.2 - full_amount) * -1, 2)
    return "{:,.2f} ₽".format(ndc).replace(',', ' ')

@register.filter
def count_full_price(ndc_type, pay_status):
    people_count = count_people(ndc_type, pay_status)
    if people_count == 0:
        return "0.00 ₽"
    if ndc_type == "NNDC":
        full_amount = people_count * 1083.33
    elif ndc_type == "NDC":
        full_amount = people_count * 1300
    else:
        people_count_w_ndc = count_people("NDC", pay_status)
        full_amount_w_ndc = people_count_w_ndc * 1300
        people_count_wo_ndc = count_people("NNDC", pay_status)
        full_amount_wo_ndc = people_count_wo_ndc * 1083.33
        full_amount = full_amount_w_ndc + full_amount_wo_ndc
    return "{:,.2f} ₽".format(full_amount).replace(',', ' ')

@register.filter
def count_full_price_w_ndc(ndc_type, pay_status):
    people_count = count_people(ndc_type, pay_status)
    if people_count == 0:
        return "0.00 ₽"
    if ndc_type == "NNDC":
        full_amount = people_count * 1083.33
    elif ndc_type == "NDC":
        full_amount = people_count * 1300
    else:
        people_count_w_ndc = count_people("NDC", pay_status)
        full_amount_w_ndc = people_count_w_ndc * 1300
        people_count_wo_ndc = count_people("NNDC", pay_status)
        full_amount_wo_ndc = people_count_wo_ndc * 1300
        full_amount = full_amount_w_ndc + full_amount_wo_ndc
    return "{:,.2f} ₽".format(full_amount).replace(',', ' ')
        
@register.filter
def ndc_sum(center):
    ed_center = center.ed_center
    quota = TicketQuota.objects.filter(ed_center=ed_center).aggregate(
        quota_count=Sum('completed_quota'))['quota_count']
    full_amount = quota * 1300
    ndc = round((full_amount / 1.2 - full_amount) * -1, 2)
    if quota is None or quota == 0:
        return "-"
    return "{:,.2f} ₽".format(ndc).replace(',', ' ')

@register.filter
def act_sum(center):
    ed_center = center.ed_center
    quota = TicketQuota.objects.filter(ed_center=ed_center).aggregate(
        quota_count=Sum('completed_quota'))['quota_count']
    if quota is None or quota == 0:
        return "-"
    if center.is_ndc:
        sum = quota * 1300
        ndc = round((sum / 1.2 - sum) * -1, 2)
        sum = sum - ndc
    else:
        sum = quota * 1083.33
    return "{:,.2f} ₽".format(sum).replace(',', ' ')

@register.filter
def get_act(center):
    if center.is_ndc: doc_type = "Акт с НДС"
    else: doc_type = "Акт без НДС"
    doc_type = get_object_or_404(DocumentTypeTicket, name=doc_type)
    act = ContractorsDocumentTicket.objects.filter(
        contractor=center.ed_center,
        doc_type=doc_type
    )
    if len(act) == 0:
        return "#"
    return act[0].doc_file.url

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