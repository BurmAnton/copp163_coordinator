from datetime import date
from django.utils.formats import date_format
from django.db.models.query import QuerySet
import os

from docxcompose.composer import Composer
from docx import Document as Document_compose
from docxtpl import DocxTemplate
from .models import ContractorsDocument

from docxcompose.composer import Composer

def get_document_number(doc_type, contractor, parent_doc=None):
    previous_docs = ContractorsDocument.objects.filter(
        doc_type=doc_type,
        contractor=contractor
    )
    if parent_doc is not None:
        previous_docs = previous_docs.filter(parent_doc=parent_doc)
    return len(previous_docs) + 1

def get_doc_name(doc_type, doc_number, parent_doc):
    doc_name = f'{doc_type} №{doc_number}'
    if parent_doc is not None:
        doc_name = f'{doc_name} ({parent_doc.doc_type} №{parent_doc.register_number})'
    return doc_name

def create_document(doc_type, contractor, doc_date, parent_doc, groups):
    head = contractor.head
    doc_number = get_document_number(doc_type, contractor, parent_doc)
    contract = ContractorsDocument(
        contractor=contractor,
        doc_type=doc_type,
        register_number=doc_number,
        parent_doc=parent_doc
    )
    if parent_doc is None:
        contract_date = doc_date
    else:
        contract_date = date.today()
    context = {
        'contract_date' : date_format(contract_date, 'd «E» Y г.'),
        'contract_number': doc_number,
        'contractor': contractor,
        'parent_doc': parent_doc,
        'doc_date': date_format(contract_date, 'd «E» Y г.')
    }
    if groups is not None:
        if isinstance(groups, QuerySet):
            context['groups'] = groups
            context['groups_sum_price'] = 0
            context['groups_start_date'] = groups.earliest('start_date').start_date
            context['groups_end_date'] = groups.latest('end_date').end_date
            for group in groups:
                context['groups_sum_price'] += group.get_price()
        else:
            context['group'] = groups
        
    document = DocxTemplate(doc_type.template)
    
    document.render(context)
    path = f'media/documents/{contractor.id}' 
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    document_name = get_doc_name(doc_type, doc_number, parent_doc)
    path_to_contract = f'{path}/{document_name}.docx'
    document.save(path_to_contract)
    contract.doc_file.name=path_to_contract
    contract.save()
    if isinstance(groups, QuerySet): contract.groups.add(*groups)
    else: contract.groups.add(groups)

    return contract

def combine_all_docx(filename_master,files_list, file_name):
    number_of_sections=len(files_list)
    master = Document_compose(filename_master)
    composer = Composer(master)
    for i in range(0, number_of_sections):
        doc_temp = Document_compose(files_list[i].doc_file)
        composer.append(doc_temp)
    composer.save(file_name)