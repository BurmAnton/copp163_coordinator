from datetime import date
from django.shortcuts import get_object_or_404
from django.utils.formats import date_format
from django.db.models.query import QuerySet
from django.db.models import Sum
import os

from docxcompose.composer import Composer
from docx import Document as Document_compose
from docxtpl import DocxTemplate
from number_to_string import get_string_by_number

from .models import EdCenterTicketIndicator, EventsCycle,\
            TicketEdCenterEmployeePosition, TicketEvent, TicketProfession,\
            TicketProjectPosition,DocumentTypeTicket, \
            ContractorsDocumentTicket, TicketQuota


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
        ndc = str((full_amount / 1.2 - full_amount) * -1).split('.')
        if ndc[1] == "0": ndc[1] = "00"
        full_amount_spelled = f'{full_amount} ({get_string_by_number(full_amount).replace(" рублей 00 копеек", "")}) рублей 00 копеек (включая НДС {ndc[0]} руб. {ndc[1]} копеек)'
        full_amount = f'{full_amount} руб. 00 копеек (включая НДС {ndc[0]} руб. {ndc[1]} копеек)'
    else: 
        doc_type = "Акт без НДС"
        contract_type="Договор с ЦО без НДС"
        full_amount = str(quota * 1083.33).split('.')
        full_amount_spelled = f'{full_amount[0]} ({get_string_by_number(int(full_amount[0]))}'.replace(" рублей", ") рублей")
        full_amount = f'{full_amount[0]} руб. {full_amount[1]} копеек'
    doc_type = get_object_or_404(DocumentTypeTicket, name=doc_type)
    contract_type = get_object_or_404(DocumentTypeTicket, name=contract_type)
    contract = get_object_or_404(
        ContractorsDocumentTicket, doc_type=contract_type, contractor=ed_center
    )
    register_number = contract.register_number

    context = {
        'events': events,
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

    act_path = f'{path}act_bvb_№{register_number}.docx'

    document.save(act_path)

    act, is_new = ContractorsDocumentTicket.objects.get_or_create(
        contractor=ed_center,
        doc_type=doc_type,
        register_number=register_number,
        parent_doc=contract
    )
    act.doc_file.name=act_path
    act.save()