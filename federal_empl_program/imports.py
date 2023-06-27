import pytz
import math

from users.models import User
from openpyxl import load_workbook

from datetime import datetime, tzinfo
from django.utils import timezone

from citizens.models import Citizen, School
from education_centers.models import EducationProgram, EducationCenter, \
                                     Workshop, Competence
from .models import Application, Group, CitizenCategory, ProjectYear

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
        return ['EmptySheet', ]
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
            return ['MissingFieldsError', missing_fields]
    except IndexError:
            return ['IndexError', ]
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


def express_import(form):
    try:
        sheet = get_sheet(form)
    except IndexError:
        return ['Import', 'IndexError']
   
    #Требуемые поля таблицы
    fields_names = [
        "Фамилия", "Имя", "Отчество", "Пол", "Дата рождения", "СНИЛС",
        "Email", "Телефон", "Категория слушателя", "Город проживания", 
        "Регион проживания", "Компетенция","Выбранное место обучения", 
        "Адрес выбранного место обучения", "Статус заявки", "Группа",
        "Дата создания заявки","Дата начала обучения", 
        "Дата окончания обучения", "Программа обучения"
    ]

    cheak_col_names = cheak_col_match(sheet, fields_names)
    if cheak_col_names[0] != True:
        return cheak_col_names
    
    sheet_dict = load_worksheet_dict(sheet, cheak_col_names[1])

    missing_fields = []
    errors = []
    added_users = 0
    added_applications = 0
    for row in range(len(sheet_dict['СНИЛС'])):
        citizen = load_citizen(sheet_dict, row)
        if citizen[0] == 'MissingField':
            missing_fields.append(citizen)
        else:
            if citizen[2] == True: added_users += 1
            citizen = citizen[1]
            application = load_application(citizen, sheet_dict, row)
            if application[0] == 'MissingField':
                missing_fields.append(citizen)
            else:
                added_applications += 1
                application = application[1]
    return ['OK', added_applications, missing_fields, errors]

def load_citizen(sheet, row):
    missing_fields = []

    snils_number = sheet["СНИЛС"][row]
    if snils_number != "": snils_number = snils_number.strip().title()
    else: missing_fields.append("СНИЛС")
    last_name = sheet["Фамилия"][row]
    if last_name != "": last_name = last_name.strip().title()
    else: missing_fields.append("Фамилия")
    first_name = sheet["Имя"][row]
    if first_name != "": first_name = first_name.strip().title()
    else: missing_fields.append("Имя")
    middle_name = sheet["Отчество"][row]
    if middle_name != "" and middle_name != None:
        middle_name = middle_name.strip().title()
    else: middle_name = None

    sex = sheet["Пол"][row]
    if sex == "м": sex = 'M'
    elif sex == "ж": sex = 'F'
    else: sex = None
    birthday = sheet["Дата рождения"][row]
    if birthday != "":
        birthday = datetime.strptime(birthday, "%Y-%m-%d")
        birthday = timezone.make_aware(birthday)
        birthday.astimezone(pytz.timezone('Europe/Samara'))
    else: birthday = None
    
    email = sheet["Email"][row]
    if email != "": email = email.strip()
    else: email = None
    phone_number = sheet["Телефон"][row]
    if phone_number != "": phone_number = phone_number.strip()
    else: phone_number = None
    res_city = sheet["Город проживания"][row]
    if res_city != "": res_city = res_city.strip()
    else: res_city = None
    res_region = sheet["Регион проживания"][row]
    if res_region != "": res_region = res_region.strip()
    else: res_region = None

    if len(missing_fields) == 0:
        citizen, is_new = Citizen.objects.get_or_create(
             snils_number=snils_number
        )
        citizen.last_name = last_name
        citizen.first_name = first_name
        citizen.middle_name = middle_name
        citizen.sex = sex
        citizen.birthday = birthday
        citizen.email = email
        citizen.phone_number = phone_number
        citizen.res_city = res_city
        citizen.res_region = res_region
        citizen.save()
        return ['OK', citizen, is_new]
    return ['MissingField', missing_fields, row + 2]

def load_application(citizen, sheet, row):
    missing_fields = []

    application_date = sheet["Дата создания заявки"][row]
    if application_date != "": 
        application_date = datetime.strptime(
            application_date, "%Y-%m-%d %H:%M:%S"
        )
        application_date = timezone.make_aware(application_date)
        application_date.astimezone(pytz.timezone('Europe/Samara'))
    else: missing_fields.append("Дата создания заявки")
    project_year, is_new = ProjectYear.objects.get_or_create(
        year=application_date.year
    )
    appl_status = None
    for status in Application.APPL_STATUS_CHOICES:
        if sheet["Статус заявки"][row] == status[1]:
            appl_status = status[0]
    if appl_status == None: missing_fields.append("Статус заявки")
    citizen_category_name = sheet["Категория слушателя"][row]
    citizen_category = CitizenCategory.objects.filter(
        official_name=citizen_category_name,
        project_year=project_year
    )
    if len(citizen_category) == 0:
        missing_fields.append("Категория слушателя")
    else: citizen_category = citizen_category[0]
    competence = sheet["Компетенция"][row]
    competence, is_new = Competence.objects.get_or_create(
        title = competence,
        is_worldskills=True
    )
    education_program = sheet["Программа обучения"][row]
    if education_program == "нет":
        education_program = None
    else:
        education_program = load_EducationProgram(sheet, row, competence)
    education_center = sheet["Выбранное место обучения"][row].strip()
    education_center, is_new = EducationCenter.objects.get_or_create(
        name=education_center
    )
    workshop, is_new = Workshop.objects.get_or_create(
        competence=competence,
        education_center=education_center,
        adress=sheet["Адрес выбранного место обучения"][row]
    )
    group, is_new = Group.objects.get_or_create(
        name=sheet["Группа"][row].strip(),
        workshop=workshop,
        education_program=education_program,
        start_date=sheet["Дата начала обучения"][row],
        end_date=sheet["Дата окончания обучения"][row],
        group_status='COMP'
    )
    application, is_new = Application.objects.get_or_create(
        project_year=project_year,
        creation_date=application_date,
        competence=competence,
        applicant=citizen,
        education_center=education_center,
        appl_status='COMP',
        citizen_category=citizen_category,
        group=group
    )
    return ['OK', application, is_new]

def load_EducationProgram(sheet_dict, row, competence):
    program_name=sheet_dict["Программа обучения"][row]
    program_type = set_program_type(program_name)
    duration = set_program_duration(program_name)
    program_name = set_program_name(program_name)
    education_program, is_new = EducationProgram.objects.get_or_create(
        program_name=program_name,
        competence=competence,
        program_type=program_type,
        duration=duration
    )
    return education_program

def set_program_type(program_name):
    program_types = (
        ('DPOPK', 'ДПО ПК', 'Дополнительная профессиональная программа повышения квалификации'),
        ('DPOPP', 'ДПО ПП', 'Дополнительная профессиональная программа профессиональной переподготовки'),
        ('POP', 'ПО П', '(профессиональная подготовка)'),
        ('POPP', 'ПО ПП', '(переподготовка)'),
        ('POPK', 'ПО ПК', '(повышение квалификации)'),
    )
    program_type = 'DPOPK'
    for prog_type in program_types:
        if prog_type[2] in program_name:
            program_type = prog_type[0]
    return program_type

def set_program_duration(program_name):
    duration = 144
    durations =  EducationProgram.PROGRAM_DURATIONS
    for dur in durations:
        if dur[1] in program_name:
            duration = dur[0]
    return duration

def set_program_name(program_name):
    program_name = program_name.split('"', 1)[1]
    program_name = program_name.split('(', 1)[0]
    program_name = program_name.replace('" ', '')
    return program_name