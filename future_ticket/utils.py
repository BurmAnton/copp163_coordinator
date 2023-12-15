import os
from datetime import date, timedelta, datetime

from django.db.models import Sum
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.formats import date_format
from docx import Document as Document_compose
from docxcompose.composer import Composer
from docxtpl import DocxTemplate
from number_to_string import get_string_by_number

from .models import (ContractorsDocumentTicket, DocumentTypeTicket,
                     EdCenterTicketIndicator, EventsCycle,
                     TicketEdCenterEmployeePosition, TicketEvent,
                     TicketProfession, TicketProjectPosition, TicketQuota)


def get_document_number(doc_type, contractor=None, parent_doc=None):
    previous_docs = ContractorsDocumentTicket.objects.all()
    return len(previous_docs) + 1

def generate_document_ticket(center_year, doc_type, register_number=None, download=False):
    
    project_year = center_year.project_year
    ed_center = center_year.ed_center
    sign_position = TicketProjectPosition.objects.get(
        position="Должностное лицо, подписывающее договор")
    sign_employee = TicketEdCenterEmployeePosition.objects.get(
        ed_center=ed_center, position=sign_position)
    if register_number == None:
        register_number = get_document_number(doc_type)
    context = {
        'register_number': register_number,
        'ed_center': ed_center,
        'center_year': center_year,
        'sign_employee': sign_employee,
    }
    doc_type = get_object_or_404(DocumentTypeTicket, name=doc_type)

    document = DocxTemplate(doc_type.template)
    document.render(context)

    path = f'media/documents/ticket/{center_year.id}/{1}/'
    if not os.path.exists(path): os.makedirs(path)

    contract_path = f'{path}/contract_bvb_№{register_number}.docx'
    
    if download:
        return document
    document.save(contract_path)

    contract, is_new = ContractorsDocumentTicket.objects.get_or_create(
        contractor=ed_center,
        doc_type=doc_type,
        register_number=register_number,
        parent_doc=None
    )
    contract.doc_file.name=contract_path
    contract.save()

    return contract

def generate_ticket_act(ed_center_year):
    is_ndc = ed_center_year.is_ndc
    ed_center = ed_center_year.ed_center
    
    sign_position = TicketProjectPosition.objects.get(
        position="Должностное лицо, подписывающее договор")
    sign_employee = TicketEdCenterEmployeePosition.objects.get(
        ed_center=ed_center, position=sign_position)
    events = TicketEvent.objects.filter(ed_center=ed_center_year
                                        ).exclude(participants_limit=0)
    quota = TicketQuota.objects.filter(ed_center=ed_center).aggregate(
        quota_count=Sum('completed_quota'))['quota_count']
    
    participant_all_count = quota
    
    if is_ndc: 
        doc_type = "Акт с НДС"
        contract_type="Договор с ЦО с НДС"
        full_amount = quota * 1300
        ndc = str(round((full_amount / 1.2 - full_amount) * -1, 2)).split('.')
        if ndc[1] == "0": ndc[1] = "00"
        elif len(ndc[1]) == 1: ndc[1] = f"{ndc[1]}0"
        full_amount_spelled = f'{full_amount} ({get_string_by_number(full_amount).replace(" 00 копеек", "")}) 00 коп. (включая НДС {ndc[0]} руб. {ndc[1]} коп.)'
        full_amount = f'{full_amount} руб. 00 коп. (включая НДС {ndc[0]} руб. {ndc[1]} коп.)'
    else: 
        doc_type = "Акт без НДС"
        contract_type="Договор с ЦО без НДС"
        full_amount = str(round(quota * 1083.33, 2)).split('.')
        if full_amount[1] == "0": full_amount[1] = "00"
        elif len(full_amount[1]) == 1: full_amount[1] = f"{full_amount[1]}0"
        full_amount_spelled = f'{full_amount[0]} ({get_string_by_number(int(full_amount[0])).replace(" 00 копеек", "")}) {full_amount[1]} коп.'.replace(" рублей)", ") рублей").replace(" рубля)", ") руб.")
        full_amount = f'{full_amount[0]} руб. {full_amount[1]} коп.'
    doc_type = get_object_or_404(DocumentTypeTicket, name=doc_type)
    contract_type = get_object_or_404(DocumentTypeTicket, name=contract_type)
    contract = get_object_or_404(
        ContractorsDocumentTicket, doc_type=contract_type, contractor=ed_center
    )
    register_number = contract.register_number
    
    events_list = []
    for event in events:
        events_list.append([
            event.profession, 
            str(event.event_date.strftime('%d.%m.%Y')), 
            event.start_time, 
            event.participants_limit, 
            event.photo_link,
            event.event_date
        ])
    
    context = {
        'events': events_list,
        'register_number': register_number,
        'ed_center': ed_center,
        'sign_employee': sign_employee,
        'full_amount': full_amount,
        'full_amount_spelled': full_amount_spelled,
        'participant_all_count': participant_all_count,
        'none_ndc_reason': ed_center_year.none_ndc_reason
    }

    document = DocxTemplate(doc_type.template)
    document.render(context)

    path = f'media/documents/ticket/{ed_center_year.id}/acts/'
    if not os.path.exists(path): os.makedirs(path)

    act_path = f'{path}act_bvb_№{register_number} ({datetime.now().strftime("%d.%m.%y %H:%M:%S")}).docx'

    document.save(act_path)

    act, is_new = ContractorsDocumentTicket.objects.get_or_create(
        contractor=ed_center,
        doc_type=doc_type,
        register_number=register_number,
        parent_doc=contract
    )
    act.doc_file.name=act_path
    act.save()


def fix_reserved_quota():
    from .models import QuotaEvent, TicketQuota
    for quota in TicketQuota.objects.all():
        reserved_quota = QuotaEvent.objects.filter(quota=quota).aggregate(
                reserved_quota_sum=Sum('reserved_quota'))['reserved_quota_sum']
        if reserved_quota == None:
            quota.reserved_quota = 0
        else:
            quota.reserved_quota = reserved_quota
        quota.save()