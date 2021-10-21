from openpyxl import load_workbook

from datetime import datetime, tzinfo
from django.utils import timezone

from citizens.models import Citizen, School
from education_centers.models import EducationProgram, EducationCenter, Workshop, Competence
from users.models import User, Group

def get_sheet(form):
    workbook = load_workbook(form.cleaned_data['import_file'])
    sheet = workbook.active
    return sheet

def bvb_teachers(form):
    try:
        sheet = get_sheet(form)
    except IndexError:
        return [False, 'IndexError']

    fields_names_set = {
        'ТУ', 
        'Школа', 
        'Населенный пункт', 
        'Логин', 
        'Пароль'
    }

    cheak = cheak_col_match(sheet, fields_names_set)
    if cheak[0] == False:
        return cheak
    
    sheet_dict = load_worksheet_dict(sheet, cheak[1])
    teachers = 0
    for row in range(len(sheet_dict['Логин'])):
        teacher = load_teacher(sheet_dict, row)
        if teacher[1] == "Added":
            teachers += 1
    return [True, teachers]

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
            login = sheet[f"D{row}"].value
            if login != None:
                sheet_dict[fields_names_set[col]].append(sheet.cell(row=row,column=col).value)
    return sheet_dict

def load_teacher(sheet_dict, row):
    email = sheet_dict["Логин"][row]
    teacher = Citizen.objects.filter(email=email, social_status='SCHT')
    if len(teacher) == 0:
        teacher = add_teacher(sheet_dict, row)
        return [teacher, 'Added']
    else:
        teacher = update_teacher(sheet_dict, row, teacher[0])
        return [teacher, "Updated"]

def add_teacher(sheet_dict, row):
    school = sheet_dict["Школа"][row]
    email=sheet_dict["Логин"][row]
    password=sheet_dict["Пароль"][row]

    school = School.objects.filter(name=school)
    if len(school) > 0:
        school = school[0]
    else:
        school = School(
            name=sheet_dict["Школа"][row],
            city=sheet_dict["Населенный пункт"][row],
        )
        school.save()

    teacher = Citizen(
        phone_number = "–",
        email = email,
        social_status='SCHT'
    )

    user = User(email=email, password=password)
    user.save()
    group = Group.objects.get(name="Координатор")
    user.groups.add(group)
    school.school_coordinators.add(user)

    teacher.save()
    user.save()
    school.save()
    return teacher

def update_teacher(sheet_dict, row, teacher):
    school = sheet_dict["Школа"][row]
    email = sheet_dict["Логин"][row]
    user = User.objects.get(email=teacher.email)
    school = School.objects.filter(name=school)
    if len(school) > 0:
        school = school[0]
    else:
        school = School(
            name=sheet_dict["Школа"][row],
            city=sheet_dict["Населенный пункт"][row],
        )
        school.save()
        user.coordinated_schools.clear()
        school.school_coordinators.add(user)

    if teacher.email != email:
        teacher.email = email
        teacher.save()

    if user.email != email:
        user.email = email

    user.save()
    school.save()
    return teacher

