from users.models import User
from openpyxl import load_workbook

from datetime import datetime, tzinfo
from django.utils import timezone

from citizens.models import Citizen, School
from education_centers.models import EducationProgram, EducationCenter, Workshop, Competence
from .models import Application, Group, InteractionHistory, Questionnaire, CitizenCategory

def get_sheet(form):
    workbook = load_workbook(form.cleaned_data['import_file'])
    sheet = workbook.active
    return sheet

def express_import(form):
    try:
        sheet = get_sheet(form)
    except IndexError:
        return [False, 'IndexError']

    fields_names_set = {
        'Фамилия', 'Имя', 'Отчество', 'Пол', 'Дата рождения', 'СНИЛС', 
        'Email', 'Телефон', 'Регион для обучения', 'Город проживания', 
        'Регион проживания', 'Категория слушателя', 'Подкатегория слушателя', 
        'Компетенция','Выбранное место обучения', 
        'Адрес выбранного место обучения', 'Программа обучения в заявке', 
        'Дата создания заявки на обучение', 'Статус заявки на обучение', 'Дата последней смены статуса',
        'Группа', 'Тип договора', 'Дата начала обучения', 'Дата окончания обучения', 
    }

    cheak = cheak_col_match(sheet, fields_names_set)
    if cheak[0] == False:
        return cheak
    
    sheet_dict = load_worksheet_dict(sheet, cheak[1])
    citizens = 0
    applications = 0
    for row in range(len(sheet_dict['СНИЛС'])):
        citizen = load_citizen(sheet_dict, row)
        if citizen[1] == "Added":
            citizens += 1
        if sheet_dict["Статус заявки на обучение"][row] is not None:
            application = load_application(sheet_dict, row, citizen[0])
            if application is not None:
                if application[1] == "Added":
                    applications += 1
                application = application[0]
            if sheet_dict["Компетенция"][row] is not None:
                competence = load_Competence(sheet_dict, row, application)
                program_name = sheet_dict["Программа обучения в заявке"][row]
                if program_name is not None and program_name != 'Не указаана заявка у Группы':
                    education_program = load_EducationProgram(sheet_dict, row, competence, application)
                if sheet_dict["Выбранное место обучения"][row] is not None:
                    education_center = load_EducationCenter(sheet_dict, row, competence, application)
                    if sheet_dict["Адрес выбранного место обучения"][row] is not None:
                        workshop = load_Workshop(sheet_dict, row, competence, education_center)
                        if sheet_dict["Группа"][row] is not None:
                            load_Group(sheet_dict, row, workshop, education_program, application)
    
    return [True, citizens, applications]

def cheak_col_match(sheet, fields_names_set):
    i = 0
    col_count = sheet.max_column
    sheet_fields = []
    sheet_col = {}
    if sheet[f"A2"].value is None:
        return [False, 'EmptySheet']
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
            return [False, 'FieldError', missing_fields]
    except IndexError:
            return [False, 'IndexError']
    return [True, sheet_col]
    
def load_worksheet_dict(sheet, fields_names_set):
    row_count = sheet.max_row
    sheet_dict = {}
    for col in fields_names_set:
        sheet_dict[fields_names_set[col]] = []
        for row in range(2, row_count+1): 
            snils = sheet[f"F{row}"].value
            if snils != None:
                sheet_dict[fields_names_set[col]].append(sheet.cell(row=row,column=col).value)
    return sheet_dict

def load_citizen(sheet_dict, row):
    snils = sheet_dict["СНИЛС"][row]
    citizen = Citizen.objects.filter(snils_number=snils)
    if len(citizen) == 0:
        citizen = add_citizen(sheet_dict, row)
        return [citizen, 'Added']
    else:
        citizen = update_citizen(sheet_dict, row, citizen[0])
        return [citizen, "Updated"]

def add_citizen(sheet_dict, row):
    sex = sheet_dict["Пол"][row]
    if sheet_dict["Отчество"][row] is not None:
        middle_name = sheet_dict["Отчество"][row].capitalize()
    else:
        middle_name = None
    if sheet_dict["Город проживания"][row] == None:
        res_city = None
    else: 
        res_city = sheet_dict["Город проживания"][row].capitalize()
        if len(res_city) > 50:
            res_city = res_city[0:49]
    citizen = Citizen(
        first_name = sheet_dict["Имя"][row].capitalize(),
        last_name = sheet_dict["Фамилия"][row].capitalize(),
        phone_number = sheet_dict["Телефон"][row],
        middle_name = middle_name,
        sex = 'F' if  sex == 'ж' else 'M', 
        email=sheet_dict["Email"][row],
        snils_number=sheet_dict["СНИЛС"][row],
        res_region = sheet_dict["Регион проживания"][row].capitalize(),
        res_city = res_city
    )
    citizen.save()
    return citizen

def update_citizen(sheet_dict, row, citizen):
    first_name = sheet_dict["Имя"][row].capitalize()
    if citizen.first_name != first_name:
        citizen.first_name = first_name
    if sheet_dict["Отчество"][row] is not None:
        middle_name = sheet_dict["Отчество"][row].capitalize()
    else:
        middle_name = sheet_dict["Отчество"][row]
    if (citizen.middle_name != middle_name) and (middle_name != None):
        citizen.middle_name = middle_name
    last_name = sheet_dict["Фамилия"][row].capitalize()
    if citizen.last_name != last_name:
        citizen.last_name = last_name
    phone_number = sheet_dict["Телефон"][row]
    if citizen.phone_number != phone_number:
        citizen.phone_number = phone_number
    sex = sheet_dict["Пол"][row]
    sex = 'F' if  sex == 'ж' else 'M'
    if citizen.sex != sex:
        citizen.sex = sex
    email = sheet_dict["Email"][row]
    if citizen.email != email:
        citizen.email = email
    res_region = sheet_dict["Регион проживания"][row].capitalize()
    if citizen.res_region != res_region:
        citizen.res_region = res_region
    if sheet_dict["Город проживания"][row] == None:
        res_city = None
    else: 
        res_city = sheet_dict["Город проживания"][row].capitalize()
        if len(res_city) > 50:
            res_city = res_city[0:49]
    if citizen.res_region != res_region:
        citizen.res_region = res_region  
    citizen.save()
    return citizen

def load_application(sheet_dict, row, applicant):
    application_date = sheet_dict["Дата создания заявки на обучение"][row]
    application_date = datetime.strptime(application_date, "%Y-%m-%d %H:%M:%S")
    application_date = timezone.make_aware(application_date)
    applications = Application.objects.filter(applicant=applicant)
    if sheet_dict["Статус заявки на обучение"][row] == 'Заявка отменена':
        applications_by_date = applications.filter(creation_date=application_date)
        dublicate_applications = applications.filter(appl_status = 'NCOM')
        if len(applications_by_date) > 0:
            application = update_application(sheet_dict, row, applicant, application_date)
            return [applications[0], "Updated"]
        elif len(dublicate_applications) > 0:
            dublicate_applications[0].delete()
            application = add_application(sheet_dict, row, applicant)
            return [application, 'Added']
        else:
            application = add_application(sheet_dict, row, applicant)
            return [application, 'Added']
    else:
        applications = Application.objects.filter(applicant=applicant)
        if len(applications) == 0:
            application = add_application(sheet_dict, row, applicant)
            return [application, 'Added']
        elif len(applications.filter(creation_date=application_date)) == 0:
            for application in applications.exclude(creation_date=application_date):
                application.appl_status = 'DUPL'
                application.save()
            application = add_application(sheet_dict, row, applicant)
            return [application, 'Added']
        else:
            application = update_application(sheet_dict, row, applicant, application_date)
            return [application, "Updated"]

def add_application(sheet_dict, row, applicant):
    creation_date = datetime.strptime(sheet_dict["Дата создания заявки на обучение"][row], "%Y-%m-%d %H:%M:%S")
    creation_date = timezone.make_aware(creation_date)
    contract_type = set_contract_type(sheet_dict["Тип договора"][row])
    express_status = sheet_dict["Статус заявки на обучение"][row]
    appl_status, admit_status = set_application_status(express_status)
    change_status_date = sheet_dict["Дата последней смены статуса"][row]
    category = sheet_dict["Категория слушателя"][row]
    category = CitizenCategory.objects.filter(official_name=category)
    print(category)
    if len(category) != 0:
        category = category[0]
    else:
        category = None
    if len(Group.objects.filter(name=sheet_dict["Группа"][row])) == 0:
        group = None
        ed_ready_time = None
    else:
        ed_ready_time = 'ALR'
        group = sheet_dict["Группа"][row].partition('(')[0]
        if len(Group.objects.filter(name=sheet_dict["Группа"][row])) != 0:
            group = Group.objects.get(name=sheet_dict["Группа"][row])
        
    application = Application(
        applicant=applicant,
        creation_date=creation_date,
        admit_status=admit_status,
        appl_status=appl_status,
        change_status_date=change_status_date,
        citizen_category=category,
        group=group,
        contract_type=contract_type,
        ed_ready_time=ed_ready_time
    )
    application.save()
    application.legacy_id = application.id
    application.save()
    return application

def update_application(sheet_dict, row, applicant, application_date):
    application = Application.objects.get(applicant=applicant, creation_date=application_date)
    creation_date = datetime.strptime(sheet_dict["Дата создания заявки на обучение"][row], "%Y-%m-%d %H:%M:%S")
    creation_date = timezone.make_aware(creation_date)
    if application.creation_date != creation_date:
        application.creation_date = creation_date
    contract_type = set_contract_type(sheet_dict["Тип договора"][row])
    if application.contract_type != contract_type:
        application.contract_type = contract_type
    express_status = sheet_dict["Статус заявки на обучение"][row]
    aplication_status = update_application_status(express_status, application)
    appl_status = aplication_status[0]
    admit_status = aplication_status[1]
    application.change_status_date = sheet_dict["Дата последней смены статуса"][row]
    if application.appl_status != appl_status:
        application.appl_status = appl_status
    if application.admit_status != admit_status:
        application.admit_status = admit_status
    category = sheet_dict["Категория слушателя"][row]
    print(category)
    category = CitizenCategory.objects.filter(official_name=category)
    print(category)
    if len(category) != 0:
        category = category[0]
    else:
        category = None
    application.citizen_category = category
    application.save()
    if len(Group.objects.filter(name=sheet_dict["Группа"][row])) == 0:
        group = None
    else:
        group = Group.objects.get(name=sheet_dict["Группа"][row])
        application.ed_ready_time = 'ALR'
    if application.group != group:
        application.group = group
    application.save()
    if application.legacy_id == '':
        application.legacy_id = application.id
        application.save()
    return application

def set_application_status(express_status):
    if express_status == "Направлен в ЦО":
        admit_status = 'ADM'
        appl_status = 'ADM'
    elif express_status == 'Зачислен':
        admit_status = 'ADM'
        appl_status = 'SED'
    elif express_status == 'Направлен на экзамен':
        admit_status = 'ADM'
        appl_status = 'EXAM'      
    elif express_status == 'Завершил обучение':
        admit_status = 'ADM'
        appl_status = 'COMP'
    elif express_status == 'Отказался от обучения':
        admit_status = 'ADM'
        appl_status = 'NCOM'
    elif express_status == 'Заявка отменена':
        admit_status = 'REF'
        appl_status = 'NCOM'
    else:
        admit_status = 'RECA'
        appl_status = 'NEW'
    return [appl_status, admit_status]

def update_application_status(express_status, application):
    if express_status == "Направлен в ЦО":
        admit_status = 'ADM'
        appl_status = 'ADM'
    elif express_status == 'Зачислен':
        admit_status = 'ADM'
        appl_status = 'SED'
    elif express_status == 'Направлен на экзамен':
        admit_status = 'ADM'
        appl_status = 'EXAM'      
    elif express_status == 'Завершил обучение':
        admit_status = 'ADM'
        appl_status = 'COMP'
    elif express_status == 'Отказался от обучения':
        admit_status = 'ADM'
        appl_status = 'NCOM'
    elif express_status == 'Заявка отменена':
        admit_status = 'REF'
        appl_status = 'NADM'   
    else:
        admit_status = application.admit_status
        appl_status = application.appl_status
    return [appl_status, admit_status]

def set_contract_type(contract_type):
    if contract_type == "Трехсторонний договор":
        contract_type = 'NEW' 
    elif contract_type == "Двухстронний договор":
        contract_type = 'SELF'
    elif contract_type == 'Без договора':
        contract_type = 'NOT'
    else:
        contract_type = '–'
    return contract_type

def load_Competence(sheet_dict, row, application):
    title=sheet_dict["Компетенция"][row]
    title = title.replace('(Ворлдскиллс)', '')
    #checking competence existance in DB
    competencies = Competence.objects.filter(title=title)
    if len(competencies) == 0:
        competence = add_competence(title)
    else:
        competence = competencies[0]
    if application is not None:
        application.competence = competence
        application.save()
    return competence

def add_competence(title):
    competence = Competence(
        title=title,
        block="",
        competence_type="",
        competence_stage=""
    )
    competence.save()
    return competence

def load_EducationProgram(sheet_dict, row, competence, application):
    program_name=sheet_dict["Программа обучения в заявке"][row]
    education_program = EducationProgram.objects.filter(program_name=set_program_name(program_name))
    if len(education_program) == 0:
        education_program = add_EducationProgram(program_name, competence)
    else:
        education_program = education_program[0]

    if application is not None and application.education_program != education_program:
        application.education_program = education_program
        application.save()
    return education_program

def add_EducationProgram(program_name, competence):
    program_type = set_program_type(program_name)
    duration = set_program_duration(program_name)
    program_name = set_program_name(program_name)
    program = EducationProgram(
        program_name=program_name,
        competence=competence,
        program_type=program_type,
        duration=duration
    )
    program.save()
    return program

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

def load_EducationCenter(sheet_dict, row, competence, application):
    name = sheet_dict["Выбранное место обучения"][row]
    if len(EducationCenter.objects.filter(name=name)) == 0:
        education_center = EducationCenter(
            name=name,
        )
        education_center.save()
        education_center.competences.add(competence)
    else:
        education_center = EducationCenter.objects.get(name=name)
        education_center.competences.add(competence)
    if application is not None:
        application.education_center = education_center
        application.save()
    return education_center

def load_Workshop(sheet_dict, row, competence, education_center):
    adress = sheet_dict["Адрес выбранного место обучения"][row]
    if len(Workshop.objects.filter(adress=adress, competence=competence)) == 0:
        workshop = Workshop(
            competence=competence,
            education_center=education_center,
            adress=adress
        )
        workshop.save()
    else:
        workshop = Workshop.objects.get(adress=adress, competence=competence)
    return workshop

def load_Group(sheet_dict, row, workshop, education_program, application):
    name = (sheet_dict["Группа"][row]).partition('(')
    if len(Group.objects.filter(name=name[0])) == 0:
        group = add_Group(sheet_dict, row, name, workshop, education_program)
        application.group = group
        application.save()
    else:
        group = update_Group(sheet_dict, row, workshop, education_program, name)
    if application is not None:
        application.group = group
        application.ed_ready_time = 'ALR'
        application.save()
    return group

def add_Group(sheet_dict, row, name, workshop, education_program):
    start_date = sheet_dict["Дата начала обучения"][row]
    end_date = sheet_dict["Дата окончания обучения"][row]
    group = Group(
        name=name[0],
        workshop=workshop,
        education_program=education_program,
        start_date=start_date,
        end_date=end_date,
    )
    group.save()
    return group

def update_Group(sheet_dict, row, workshop, education_program, name):
    group = Group.objects.get(name=name[0])
    distance_education = False
    if group.distance_education != distance_education:
        group.distance_education = distance_education
    start_date = sheet_dict["Дата начала обучения"][row]
    if group.start_date != start_date:
        group.start_date = start_date
    end_date = sheet_dict["Дата окончания обучения"][row]
    if group.end_date != end_date:
        group.end_date = end_date
    if group.workshop != workshop:
        group.workshop = workshop
    if group.workshop != workshop:
        group.workshop = workshop
    group.save()
    return group

def load_worksheet_dict_st(sheet, fields_names_set):
    row_count = sheet.max_row
    sheet_dict = {}
    for col in fields_names_set:
        sheet_dict[fields_names_set[col]] = []
        for row in range(2, row_count+1): 
            email = sheet[f"A{row}"].value
            if email != None:
                sheet_dict[fields_names_set[col]].append(sheet.cell(row=row,column=col).value)
    return sheet_dict

def import_statuses(form):
    try:
        sheet = get_sheet(form)
    except IndexError:
        return [False, 'IndexError']

    fields_names_set = {
        'email',
        'Результат разговора'
    }

    cheak = cheak_col_match(sheet, fields_names_set)
    if cheak[0] == False:
        return [False, cheak[1]]

    sheet_dict = load_worksheet_dict_st(sheet, cheak[1])
    not_added = sheet_dict
    for row in range(len(sheet_dict['email'])):
        citizen = Citizen.objects.filter(email=sheet_dict["email"][row])
        if len(citizen) != 0:
            load_row_ch_st(citizen[0], sheet_dict, row)
    return [True, not_added]

def load_row_ch_st(citizen, sheet_dict, row):
    application = Application.objects.filter(applicant=citizen)
    if len(application) != 0:
        application = application[0]
        application.appl_status='VER'
        application.admit_status='CONT'
        application.save()
        comment = InteractionHistory(
            application=application,
            comunication_type='PHN',
            short_description=sheet_dict['Результат разговора'][row],
            interaction_date='2021-09-01'
        )
        comment.save()
        return application
    return citizen

#import from google sheet "База данных граждан"
def import_in_db_gd(form):
    try:
        sheet = get_sheet(form)
    except IndexError:
        return [False, 'IndexError']

    fields_names_set = {
        'ID','Статус заявки', 'Цель','Зарегистрирован на ЦП ЦОПП', 
        'Безработный', 'Фамилия', 'Имя', 'Email', 'Статус заявки на обучение', 
        'Допуск до участия', 'Уровень образования','Занятость по итогам обучения до начала обучения', 
        'Специалист по работе с клиентами', 'Курсы ИП'
    }

    cheak = cheak_col_match(sheet, fields_names_set)
    if cheak[0] == False:
        return [False, cheak[1]]

    sheet_dict = load_worksheet_dict(sheet, cheak[1])
    not_added = []
    for row in range(len(sheet_dict['ID'])): 
        citizen = Citizen.objects.filter(email=sheet_dict["Email"][row])
        if len(citizen) != 0:
            not_added.append(load_row_gd(citizen[0], sheet_dict, row))
        else:
            not_added.append(sheet_dict["Email"][row])
    return [True, not_added]

def load_row_gd(citizen, sheet_dict, row):
    if sheet_dict['Статус заявки'][row] != 'дубликат':
        if sheet_dict['Зарегистрирован на ЦП ЦОПП'][row] is not None:
            citizen.copp_registration = sheet_dict['Зарегистрирован на ЦП ЦОПП'][row]
        citizen.education_type = get_education(sheet_dict['Уровень образования'][row])
        application = Application.objects.filter(applicant=citizen)
        if len(application) != 0:
            application = application[0]

            if sheet_dict['ID'][row] is not None:
                application.legacy_id = int(sheet_dict['ID'][row])

            if sheet_dict['Цель'][row] is not None:
                purpose = get_goal(sheet_dict, row)
                questionnaire = Questionnaire(
                    applicant=application,
                    purpose = purpose
                )
                questionnaire.save()
            set_application_status_gd(sheet_dict['Статус заявки'][row], application)

            application.is_working = sheet_dict['Занятость по итогам обучения до начала обучения'][row]
            if sheet_dict['Специалист по работе с клиентами'][row] is not None:
                name = sheet_dict['Специалист по работе с клиентами'][row].split()
                try:
                    consultant = User.objects.get(first_name=name[1], last_name=name[0])
                    application.citizen_consultant = consultant
                except:
                    pass
                try:
                    consultant = User.objects.get(first_name=name[0], last_name=name[1])
                    application.citizen_consultant = consultant
                except:
                    pass

            if sheet_dict['Курсы ИП'][row] is not None:
                application.ib_course = sheet_dict['Курсы ИП'][row]

            application.save()
        citizen.save()

def get_goal(sheet_dict, row):
    goals_variants = [
        ('RECA', "самозанятый"),
        ('CONT', "сохранить работу"),
        ('RECD', "найти работу"),
        ('CONF', "просто поучиться"),
        ('CONF', "повысить квалификацию"),
    ]                    
    goal = sheet_dict["Цель"][row]
    for variant in goals_variants:
        if variant[1] == goal:
            return variant[0]
    return ""

def set_application_status_gd(gd_status, application):
    if gd_status == "заявка получена":
        admit_status = 'RECA'
        appl_status = 'NEW'
    elif gd_status == "связались":
        admit_status = 'CONT'
        appl_status = 'VER'
    elif gd_status == "прислал часть документов":
        admit_status = 'RECD'
        appl_status = 'VER'
    elif gd_status == "допущен":
        admit_status = 'ADM'
        appl_status = 'ADM'
    elif gd_status == "начал обучение":
        admit_status = 'ADM'
        appl_status = 'SED'
    elif gd_status == "завершил обучение":
        admit_status = 'CONT'
        appl_status = 'COMP'
    elif gd_status == "отчислен":
        admit_status = application.admit_status
        appl_status = 'NCOM'
    elif gd_status == "Заявка отменена":
        admit_status = application.admit_status
        appl_status = 'NADM'
    elif gd_status == "резерв":
        admit_status = application.admit_status
        appl_status = 'RES'
    elif gd_status == "дубликат":
        admit_status = application.admit_status
        appl_status = 'DUPL'
    elif gd_status == 'другой ФО':
        admit_status = application.admit_status
        appl_status = 'OTH'
    else:
        admit_status = application.admit_status
        appl_status = application.appl_status
    application.appl_status = appl_status
    application.admit_status = admit_status
    application.save()
    return application

def get_education(education):
    education_variants = Citizen.EDUCATION_CHOICES
    for variant in education_variants:
        if variant[1] == education:
            return variant[0]
    return ""

def load_worksheet_school_dict(sheet, fields_names_set):
    row_count = sheet.max_row
    sheet_dict = {}
    for col in fields_names_set:
        sheet_dict[fields_names_set[col]] = []
        for row in range(2, row_count+1): 
            school = sheet[f"A{row}"].value
            if school != None:
                sheet_dict[fields_names_set[col]].append(sheet.cell(row=row,column=col).value)
    return sheet_dict

def import_schools(form):
    try:
        sheet = get_sheet(form)
    except IndexError:
        return [False, 'IndexError']

    fields_names_set = {
        'Школа', 
        'Населенный пункт', 
        'Муниципалитет', 
        'ИНН'
    }

    cheak = cheak_col_match(sheet, fields_names_set)
    if cheak[0] == False:
        return cheak
    
    sheet_dict = load_worksheet_school_dict(sheet, cheak[1])
    for row in range(len(sheet_dict['Школа'])):
        if sheet_dict["Школа"][row] is not None:
            school = School(
                name=sheet_dict["Школа"][row],
                city=sheet_dict["Населенный пункт"][row]
            )
            if sheet_dict['Муниципалитет'][row] is not None:
                school.municipality = sheet_dict['Муниципалитет'][row]
                school.inn = sheet_dict['ИНН'][row]
                school.is_bilet = True
            school.save()
