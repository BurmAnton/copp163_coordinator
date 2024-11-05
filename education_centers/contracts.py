import os
from datetime import date

from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.formats import date_format
from docx import Document as Document_compose
from docxcompose.composer import Composer
from docxtpl import DocxTemplate

from federal_empl_program.models import (EdCenterEmployeePosition,
                                         EdCenterIndicator, NetworkAgreement, ProjectPosition)
from future_ticket.models import (EdCenterTicketIndicator,
                                  TicketEdCenterEmployeePosition,
                                  TicketProfession, TicketProjectPosition)

from .models import (ApplicationDocEdu, ContractorsDocument, DocumentType, EducationProgram,
                     Teacher, Workshop)


def generate_application_doc(application_doc: ApplicationDocEdu):
    doc_type = get_object_or_404(DocumentType, name="Заявление на отправку документа о квалификации")
    document = DocxTemplate(doc_type.template)
    context = {
        'application_doc': application_doc,
        'citizen': application_doc.citizen,
        'creation_date': date_format(date.today(), 'd «E» Y г.'),
        'passport_issued_date': date_format(application_doc.passport_issued_date, 'd.m.Y г.')
    }
    document.render(context)
    path = f'media/application_docs/{application_doc.id}'
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    document_name = f"заявление_{application_doc.full_name}"
    path_to_doc = f'{path}/{document_name}.docx'
    document.save(path_to_doc)
    
    application_doc.file.name = path_to_doc
    application_doc.save()
    
    return document


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

def generate_net_agreement(agreement: NetworkAgreement) -> DocxTemplate:
    doc_type = get_object_or_404(DocumentType, name="Сетевой договор (2024)")
    ed_center = agreement.ed_center_year.ed_center
    sign_position = ProjectPosition.objects.get(
        position="Должностное лицо, подписывающее договор")
    context = {
        'number' : agreement.agreement_number,
        'programs': agreement.programs.all(),
        'ed_center': ed_center,
        'sign_employee': EdCenterEmployeePosition.objects.filter(
            ed_center=ed_center, position=sign_position).first(),

    }
    document = DocxTemplate(doc_type.template)
    document.render(context)

    path = f'media/federal_empl/net_agreements_new/{ed_center.id}' 
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    doc_name = f"стетевой_договор_{agreement.agreement_number}"
    path_to_doc = f'{path}/{doc_name}.docx'
    document.save(path_to_doc)

    return document

def generate_concent_doc(teacher: Teacher) -> DocxTemplate:
    doc_type = get_object_or_404(DocumentType, name="Согласие (2024)")
    
    context = {
        'teacher' : teacher,
    }
    
    document = DocxTemplate(doc_type.template)
    document.render(context)

    path = f'media/consents/generate/{teacher.id}' 
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    doc_name = f"согласие_{teacher.last_name}"
    path_to_doc = f'{path}/{doc_name}.docx'
    document.save(path_to_doc)

    return document


def combine_all_docx(filename_master,files_list, file_name):
    number_of_sections=len(files_list)
    master = Document_compose(filename_master)
    composer = Composer(master)
    for i in range(0, number_of_sections):
        doc_temp = Document_compose(files_list[i].doc_file)
        composer.append(doc_temp)
    composer.save(file_name)

def create_application(center_project_year, programs=None):
    ed_center = center_project_year.ed_center
    contact_position = ProjectPosition.objects.get(
        position="Контактное лицо и администратор ЦО")
    sign_position = ProjectPosition.objects.get(
        position="Должностное лицо, подписывающее договор")
    resp_position = ProjectPosition.objects.get(
        position="Контакт, ответственный за заключение договора")
    citizens_position = ProjectPosition.objects.get(
        position="Лицо, подписывающее договоры с гражданами")
    programs_position =ProjectPosition.objects.get(
        position="Ответственный за формирование каталога программ")
    if programs == None:
        programs = EducationProgram.objects.filter(ed_center=ed_center)
    
    context = {
        'creation_date' : date_format(date.today(), 'd «E» Y г.'),
        'ed_center': ed_center,
        'is_federal': center_project_year.is_federal,
        'programs': programs,
        'teachers': Teacher.objects.filter(
            organization=ed_center, programs__in=programs),
        'contact_employee': EdCenterEmployeePosition.objects.get(
            ed_center=ed_center, position=contact_position),
        'sign_employee': EdCenterEmployeePosition.objects.filter(
            ed_center=ed_center, position=sign_position).first(),
        'resp_employee': EdCenterEmployeePosition.objects.get(
            ed_center=ed_center, position=resp_position),
        'citizens_employee': EdCenterEmployeePosition.objects.get(
            ed_center=ed_center, position=citizens_position),
        'programs_employee': EdCenterEmployeePosition.objects.filter(
            ed_center=ed_center, position=programs_position).first(),
        'k1': EdCenterIndicator.objects.get(
            indicator__name="Общая численность лиц, прошедших обучение по программам ПО и/или ДПО, чел.", ed_center=ed_center),
        'k2': EdCenterIndicator.objects.get(
            indicator__name="Из них численность лиц, занятых по виду деятельности и полученным трудовым функциям (профессиональным компетенциям) по завершению обучения, %.", ed_center=ed_center),
        'k3': EdCenterIndicator.objects.filter(
            indicator__name="Количество реализованных программ ПО и/или ДПО организацией, осуществляющей образовательную деятельность, шт.", ed_center=ed_center).first(),
        'k4': EdCenterIndicator.objects.get(
            indicator__name="Объем привлеченных средств, полученных от реализации программ ПО и/или ДПО, руб.", ed_center=ed_center),
        'k5': EdCenterIndicator.objects.get(
            indicator__name="Опыт участия организации, осуществляющей образовательную деятельность в рамках Проекта, чел.", ed_center=ed_center),
        'k6': EdCenterIndicator.objects.get(
            indicator__name="Опыт участия организации, осуществляющей образовательную деятельность в реализации мероприятий в федеральных, региональных проектах по профилю ПО и/или ДПО, в том числе в рамках Проекта, чел.", ed_center=ed_center),
        'k7': EdCenterIndicator.objects.filter(
            indicator__name="Общая численность лиц, прошедших обучение с применением дистанционных образовательных технологий, чел.", ed_center=ed_center).first(),
        'students': EdCenterIndicator.objects.get(
            indicator__name="Общая численность лиц, прошедших обучение по программам ПО и/или ДПО, чел.", ed_center=ed_center),
        'count_programs': EdCenterIndicator.objects.filter(
            indicator__name="Количество реализованных программ ПО и/или ДПО организацией, осуществляющей образовательную деятельность, шт.", ed_center=ed_center).first(),
        'distant': EdCenterIndicator.objects.filter(
            indicator__name="Общая численность лиц, прошедших обучение с применением дистанционных образовательных технологий, чел.", ed_center=ed_center).first(),
        'partners': EdCenterIndicator.objects.get(
            indicator__name="Имеются соглашения о сотрудничестве с работодателями в рамках реализации программ профессионального обучения и дополнительного профессионального образования (укажите перечень индустриальных и(или) социальных партнёров):", ed_center=ed_center),
        'experience_feds': EdCenterIndicator.objects.get(
            indicator__name="Имеется опыт участия организации в федеральных, региональных проектах по профилю профессионального обучения и дополнительного профессионального образования (укажите крупные проекты за 2021-2022 гг.):", ed_center=ed_center),
        'experience_programs': EdCenterIndicator.objects.get(
            indicator__name="Имеется опыт участия организации в реализации программ профессионального обучения и дополнительного профессионального образования в сетевой форме (укажите перечень программ):", ed_center=ed_center),
        'experience_other': EdCenterIndicator.objects.get(
            indicator__name="Укажите иную информацию по профилю профессионального обучения и дополнительного профессионального образования", ed_center=ed_center),
    }

    if programs == None:
        doc_type = get_object_or_404(DocumentType, name="Заявка")
        document_name = "заявка_ПКО_СЗ"
    else:
        doc_type = get_object_or_404(DocumentType, name="Заявка на доп. программы")
        document_name = "заявка_ПКО_СЗ_доп"
    document = DocxTemplate(doc_type.template)
    document.render(context)

    path = f'media/documents/{ed_center.id}' 
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    
    path_to_contract = f'{path}/{document_name}.docx'
    document.save(path_to_contract)
    contract = ContractorsDocument(
        contractor=ed_center,
        doc_type=doc_type,
        register_number=get_document_number(doc_type, ed_center),
        parent_doc=None
    )
    contract.doc_file.name=path_to_contract
    contract.save()

    return document

def create_ticket_application(center_project_year):
    ed_center = center_project_year.ed_center
    contact_position = TicketProjectPosition.objects.get(position="Контактное лицо и администратор ЦО", project_year=center_project_year.project_year)
    sign_position = TicketProjectPosition.objects.get(position="Должностное лицо, подписывающее договор", project_year=center_project_year.project_year)
    programs = center_project_year.programs.all()
    professions = TicketProfession.objects.filter(
        programs__in=programs).distinct()
    professions_dict = dict()
    for profession in professions:
        professions_dict[f'{profession.name}'] = dict()
        profession_programs = programs.filter(profession=profession)
        professions_dict[f'{profession.name}']['teachers'] = Teacher.objects.filter(
            organization=ed_center,
            ticket_programs__in=profession_programs
        ).distinct()
        professions_dict[f'{profession.name}']['workshops'] = Workshop.objects.filter(
            education_center=ed_center,
            ticket_programs__in=profession_programs
        ).distinct()
    
    context = {
        'creation_date' : date_format(date.today(), 'd «E» Y г.'),
        'ed_center': ed_center,
        'center_project_year': center_project_year,
        'contact_employee': TicketEdCenterEmployeePosition.objects.get(ed_center=ed_center, position=contact_position),
        'sign_employee': TicketEdCenterEmployeePosition.objects.get(ed_center=ed_center, position=sign_position),
        'programs': programs,
        'professions': professions,
        'professions_dict': professions_dict,
        # 'events': EdCenterTicketIndicator.objects.get(indicator__name="Мероприятия по профессиональной ориентации учащихся 6–11-х классов общеобразовательных организаций в рамках проекта «Билет в будущее»", ed_center=ed_center).value,
        # 'training': EdCenterTicketIndicator.objects.get(indicator__name="Профессиональные пробы в рамках регионального проекта «Мой выбор»", ed_center=ed_center).value,
        # 'courses': EdCenterTicketIndicator.objects.get(indicator__name="Предпрофильные курсы для учащихся 9-х классов, проведение дней открытых дверей с мастер-классами", ed_center=ed_center).value,
        # 'nti': EdCenterTicketIndicator.objects.get(indicator__name="Прочие профориентационные мероприятия, включая Олимпиады НТИ (всероссийские многопрофильные командные инженерные соревнования для школьников 8-11 классов), фестивали и т.д.", ed_center=ed_center).value
    }
    doc_type = get_object_or_404(DocumentType, name="Заявка (БВБ)")

    document = DocxTemplate(doc_type.template)
    document.render(context)

    path = f'media/applications/{center_project_year.id}'
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    document_name = "заявка_ПКО_СЗ"
    path_to_contract = f'{path}/{document_name}.docx'
    document.save(path_to_contract)
    contract, is_new = ContractorsDocument.objects.get_or_create(
        contractor=ed_center,
        doc_type=doc_type,
        register_number=get_document_number(doc_type, ed_center),
        parent_doc=None
    )
    contract.doc_file.name=path_to_contract
    contract.save()

    return document
