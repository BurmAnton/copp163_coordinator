import pytz
import math

from users.models import User
from openpyxl import load_workbook

from datetime import datetime, tzinfo
from django.utils import timezone

from citizens.models import Citizen, School
from education_centers.models import EducationProgram, EducationCenter, \
                                     Workshop, Competence
from .models import Application, FlowStatus, Group, CitizenCategory, ProjectYear


CONTR_TYPE_CHOICES = {
     "Трёхсторонний с работодателем": 'THR',
     "Трёхсторонний с ЦЗН": 'CZN',
     "Двусторонний": 'SELF'
}
EDUCATION_CHOICES = {
    "Высшее образование – бакалавриат": 'SPVO',
    "Среднее профессиональное образование - техникум, колледж": 'SPVO',
    "Высшее образование – специалитет, магистратура": 'SPVO',
    "Высшее образование – подготовка кадров высшей квалификации": 'SPVO',
    "Среднее общее образование - 11 классов": 'SCHL',
    "Основное общее образование - 9 классов": 'SCHL',
}

def get_sheet(form):
    workbook = load_workbook(form.cleaned_data['import_file'])
    sheet = workbook.active
    return sheet

def cheak_col_match(sheet, fields_names_set):
    i = 0
    col_count = sheet.max_column
    sheet_fields = []
    sheet_col = {}
    if sheet[f"A2"].value is None:
        return ['Import', 'EmptySheet']
    try:
        for col_header in range(1, col_count+1):
            if sheet.cell(row=1,column=col_header).value is not None:
                sheet_fields.append(sheet.cell(row=1,column=col_header).value)
                sheet_col[col_header] = sheet.cell(row=1,column=col_header).value
        missing_fields = []
        for field in fields_names_set:
            if field not in sheet_fields:
                missing_fields.append(field)
        if len(missing_fields) != 0:
            return ['Error', 'MissingFieldsError', missing_fields]
    except IndexError:
            return ['Error', 'IndexError']
    return [True, sheet_col]

def load_worksheet_dict(sheet, fields_names_set):
    row_count = sheet.max_row
    sheet_dict = {}
    for col in fields_names_set:
        sheet_dict[fields_names_set[col]] = []
        for row in range(2, row_count+1): 
            snils = sheet[f"A{row}"].value
            if snils != None:
                cell_value = sheet.cell(row=row,column=col).value
                try: cell_value = str(math.floor(cell_value))
                except (ValueError, TypeError): pass
                sheet_dict[fields_names_set[col]].append(cell_value)
    return sheet_dict


def import_applications(form, year):
    try: sheet = get_sheet(form)
    except IndexError: return ['Error', 'IndexError']
    
    #Требуемые поля таблицы
    fields_names = {
        "Номер заявки", "Фамилия", "Имя", "Отчество", "СНИЛС", "Телефон",
        "Пол гражданина","Уровень образования с портала РР", "Email",
        "Регион", "Статус заявки", "Дата одобрения ЦЗН", "Категория",
        "Тип договора", "Образовательный партнёр", "Начало обучения",
        "Окончание обучения", "Дата создания заявки", "Идентификатор потока",
        "Программа", "Идентификатор образовательной программы", 
        "Дата рождения гражданина", "Срок истечения заявки",
        "Дата заключения договора со слушателем"
    }
    cheak_col_names = cheak_col_match(sheet, fields_names)
    if cheak_col_names[0] != True:
        return cheak_col_names
    
    sheet = load_worksheet_dict(sheet, cheak_col_names[1])
    missing_fields = []
    citizen_added = 0
    citizen_updated = 0
    application_added = 0
    application_updated = 0
    group_added = 0
    group_updated = 0
    project_year = ProjectYear.objects.get(year=year)

    for row in range(len(sheet['Номер заявки'])):
        citizen_input = create_citizen(sheet, row)
        if citizen_input[0] != True:
            missing_fields.append(citizen_input)
        else:
            citizen = citizen_input[1]
            if citizen_input[2]: citizen_added += 1
            else: citizen_updated += 1
            application_input = create_application(sheet, row, citizen, project_year)
            if application_input[0] != True:
                missing_fields.append(application_input)
            else:
                application = application_input[1]
                if application_input[2]: application_added += 1
                else: application_updated += 1
                if sheet["Идентификатор потока"][row] != "" \
                    and sheet["Идентификатор потока"][row] != None:
                    group_input = create_group(sheet, row, application)
                    if group_input[0] != True:
                        missing_fields.append(group_input)
                    else:
                        if group_input[2]: group_added += 1
                        else: group_updated += 1
    return ['OK', missing_fields, citizen_added, citizen_updated,
             application_added, application_updated, group_added, group_updated]

def create_citizen(sheet, row):
    snils_number = sheet["СНИЛС"][row]
    if snils_number == "" or None:
        return ["SnilsMissing", "СНИЛС", row+2]
    citizen, is_new = Citizen.objects.get_or_create(
        snils_number=snils_number
    )
    citizen.last_name = sheet["Фамилия"][row]
    citizen.first_name = sheet["Имя"][row]
    citizen.middle_name = sheet["Отчество"][row]
    citizen.phone_number = sheet["Телефон"][row]
    citizen.email = sheet["Email"][row]
    citizen.res_region = sheet["Регион"][row]
    citizen.birthday = datetime.strptime(sheet["Дата рождения гражданина"][row], "%d.%m.%Y")
    if sheet["Пол гражданина"][row] == "Мужской": citizen.sex = 'M'
    elif sheet["Пол гражданина"][row] == "Женский": citizen.sex = 'F'
    education_type = sheet["Уровень образования с портала РР"][row]
    if education_type in EDUCATION_CHOICES:
        citizen.education_type = EDUCATION_CHOICES[education_type]
    citizen.save()

    return [True, citizen, is_new]

def create_application(sheet, row, citizen, project_year):
    flow_id = sheet["Номер заявки"][row].replace('=HYPERLINK("https://flow.firpo.info/Requests/Card/', '')
    flow_id = sheet["Номер заявки"][row].replace(')', '')
    flow_id = int(flow_id.split()[1])
    application, is_new = Application.objects.get_or_create(
        flow_id=flow_id,
        project_year=project_year,
        applicant=citizen
    )
    flow_status = sheet["Статус заявки"][row]
    application.flow_status = FlowStatus.objects.get(off_name=flow_status)
    application.creation_date = datetime.strptime(sheet["Дата создания заявки"][row], "%d.%m.%Y")
    if sheet["Срок истечения заявки"][row] != None:
        application.expiration_date = datetime.strptime(sheet["Срок истечения заявки"][row], "%d.%m.%Y")
    if sheet["Дата одобрения ЦЗН"][row] != None:
        csn_prv_date = datetime.strptime(sheet["Дата одобрения ЦЗН"][row], "%d.%m.%Y")
        if csn_prv_date == "": csn_prv_date = None
        application.csn_prv_date = csn_prv_date
    citizen_category = sheet["Категория"][row]
    application.citizen_category = CitizenCategory.objects.get(
            official_name=citizen_category, project_year=project_year)
    contract_type = sheet["Тип договора"][row]
    if contract_type in CONTR_TYPE_CHOICES:
        application.contract_type = CONTR_TYPE_CHOICES[contract_type]
        if sheet["Дата заключения договора со слушателем"][row] != None:
            application.contract_date = datetime.strptime(sheet[
                "Дата заключения договора со слушателем"][row], "%d.%m.%Y")
    else: application.contract_type = "–"

    flow_name = sheet["Образовательный партнёр"][row]
    education_center = EducationCenter.objects.filter(
        flow_name=flow_name
    )
    if len(education_center) == 0:
        return ["EdCenterMissing", flow_name, row+2]
    application.education_center = education_center[0]
    application.save()
    return [True, application, is_new]

def create_group(sheet, row, application):
    flow_id = sheet["Идентификатор потока"][row]
    group, is_new = Group.objects.get_or_create(flow_id=flow_id)
    if sheet["Начало обучения"][row] != None:
        group.start_date = datetime.strptime(sheet["Начало обучения"][row], "%d.%m.%Y")
    if sheet["Окончание обучения"][row] != None:
        group.end_date = datetime.strptime(sheet["Окончание обучения"][row], "%d.%m.%Y")
    
    program_name = sheet["Программа"][row]
    program_flow_id = sheet["Идентификатор образовательной программы"][row]
    group.education_program = get_education_program(
        program_name, program_flow_id, application.education_center
    )
    if group.education_program == None:
        return ["EdProgramMissing", program_flow_id, row+2]
    group.save()
    return [True, group, is_new]
    
def get_education_program(program_name, program_flow_id, education_center):
    education_program = EducationProgram.objects.filter(
        flow_id=program_flow_id)
    if len(education_program) != 0: return education_program[0]
    education_program = EducationProgram.objects.filter(
        program_name=program_name, ed_center=education_center)
    if len(education_program) != 0: 
        education_program[0].flow_id = program_flow_id
        education_program[0].save()
        return education_program[0]
    
    return None