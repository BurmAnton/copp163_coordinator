from openpyxl import load_workbook

from datetime import datetime, tzinfo
from django.utils import timezone

from citizens.models import Citizen, DisabilityType, School
from users.models import User, Group
from .models import VocGuidTest, TimeSlot
from education_centers.models import EducationCenter

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
    updated = 0
    for row in range(len(sheet_dict['Логин'])):
        teacher = load_teacher(sheet_dict, row)
        if teacher[1] == "Added":
            teachers += 1
        elif teacher[1] == "Updated":
            updated += 1
    return [True, teachers, updated]

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
    teacher = User.objects.filter(email=email)
    if len(teacher) == 0:
        teacher = add_teacher(sheet_dict, row)
        return [teacher, 'Added']
    else:
        teacher = update_teacher(sheet_dict, row, teacher[0])
        if teacher[1]:
            return [teacher[0], "Updated"]
        else:
            return [teacher[0], "Unchange"]

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

    user = User.objects.create_user(email=email, password=password)
    user.save()
    group = Group.objects.get(name="Координатор")
    user.groups.add(group)
    school.school_coordinators.add(user)

    user.save()
    school.save()
    return user

def update_teacher(sheet_dict, row, teacher):
    is_changed = False
    school = sheet_dict["Школа"][row]
    email = sheet_dict["Логин"][row]
    password = sheet_dict["Пароль"][row]

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
    if not school.school_coordinators.filter(id=user.id).exists():
        user.coordinated_schools.clear()
        school.school_coordinators.add(user)
        school.save()
        is_changed = True

    if teacher.email != email:
        teacher.email = email
        teacher.save()
        is_changed = True

    if user.email != email:
        user.email = email
        is_changed = True

    user.save()
    school.save()
    return [teacher, is_changed]


def slots_import(form):
    try:
        sheet = get_sheet(form)
    except IndexError:
        return [False, 'IndexError']

    fields_names_set = {
        'ЦО', 'Программа', 
        'Тип', 'Возрастная категория', 
        'Описание', 'Дата',
        'Время', 'ОВЗ'
    }

    cheak = cheak_col_match(sheet, fields_names_set)
    if cheak[0] == False:
        return cheak
    
    sheet_dict = load_worksheet_dict_slots(sheet, cheak[1])
    slots = 0
    nf_ed_centers = set()
    for row in range(len(sheet_dict['Программа'])):
        test = load_slot(sheet_dict, row)
        if test[0] == "OK":
            slots += test[2]
        else:
            nf_ed_centers.add(test[1])
    return [slots, nf_ed_centers]
    
def load_worksheet_dict_slots(sheet, fields_names_set):
    row_count = sheet.max_row
    sheet_dict = {}
    for col in fields_names_set:
        sheet_dict[fields_names_set[col]] = []
        for row in range(2, row_count+1): 
            login = sheet[f"B{row}"].value
            if login != None:
                sheet_dict[fields_names_set[col]].append(sheet.cell(row=row,column=col).value)
    return sheet_dict

def load_slot(sheet_dict, row):
    ed_center = sheet_dict["ЦО"][row]
    program = sheet_dict["Программа"][row]
    time_slots = sheet_dict["Время"][row]
    date = sheet_dict["Дата"][row]
    test_type = ""

    test = load_test(sheet_dict, row)
    if test[0] == "OK":
        test = test[1]
    else:
        return ["NOT_FOUND_ED_CNTR", test[1]]

    time_slots = time_slots.split(",")
    slots_count = 0
    for slot in time_slots:
        if "с 15:00 до 16:30" in slot:
            slot = 'MID'
        elif "с 16:30 до 18:00" in slot:
            slot = 'EVN'
        elif 'с 10:00 до 11:30' in slot:
            slot = 'MRN'
        else: 
            return ["OK", test, slots_count]
        time_slot = TimeSlot.objects.filter(test=test, date=date, slot=slot)
        if len(time_slot) == 0:
            slot = TimeSlot(
                test=test, 
                date=date, 
                slot=slot
            )
            slot.save()
            slots_count += 1
    return ["OK", test, slots_count]

def load_test(sheet_dict, row):
    name = sheet_dict["Программа"][row]
    description = sheet_dict["Описание"][row]
    disabilities = sheet_dict["ОВЗ"][row]
    education_center = sheet_dict["ЦО"][row]
    age_group = sheet_dict["Возрастная категория"][row]
    education_center = EducationCenter.objects.filter(name=education_center)

    if len(education_center) > 0:
        education_center = education_center[0]
        if age_group == "6-7 класс":
            age_group = '6-7'
        elif age_group == "8-9 класс":
            age_group = '8-9'
        elif age_group == "10-11 класс":
            age_group = '10-11'
        else:
            age_group = 'ALL'

        test = VocGuidTest.objects.filter(
            name=name, 
            education_center=education_center, 
            age_group=age_group
        )

        if len(test) == 0:
            test = VocGuidTest(
                name = name,
                education_center = education_center,
                description = description,
                age_group = age_group,
                guid_type = 'VO'
            )
            test.save()
        else:
            test = test[0]

        if disabilities is not None:
            disabilities = disabilities.split(",")
            for disability in disabilities:
                disability = DisabilityType.objects.filter(name=disability)
                if len(disability) > 0:
                    test.disability_types.add(disability[0])

        test.save()
        return ["OK", test]

    return ["NOT_FOUND_ED_CNTR", sheet_dict["ЦО"][row]]
