from datetime import date
from django.shortcuts import get_object_or_404
from django.utils.formats import date_format
from django.db.models.query import QuerySet
import os

from docxcompose.composer import Composer
from docx import Document as Document_compose
from docxtpl import DocxTemplate

from .models import EdCenterTicketIndicator, EventsCycle, TicketEdCenterEmployeePosition, \
      TicketProfession, TicketProjectPosition,ContractorsDocumentTicket, \
      DocumentTypeTicket


def get_document_number(doc_type, contractor=None, parent_doc=None):
    previous_docs = ContractorsDocumentTicket.objects.all()
    #if contractor is not None:
        #previous_docs = previous_docs.filter(contractor=contractor)
    #if parent_doc is not None:
        #previous_docs = previous_docs.filter(parent_doc=parent_doc)
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

def number_cycles():
    cycles = EventsCycle.objects.all().order_by('end_reg_date')
    for cycle_number, cycle in enumerate(cycles, start=1):
        cycle.cycle_number = cycle_number
        cycle.save()