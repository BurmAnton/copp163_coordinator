from datetime import datetime
import os
from zipfile import ZipFile

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.encoding import escape_uri_path
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from education_centers.models import EducationProgram


def quota_request(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Центры обучения"
    col_titles = [
        "Наименование Центра обучения",
        "Количество академических часов",
        "Стоимость программы",
        "Запрашиваемая квота",
        "Сумма, руб."
    ]
    
    for col_number, col_title in enumerate(col_titles, start=1):
        ws.cell(row=1, column=col_number, value=col_title)

    row_number = 2
    for center_request in request.centers_requests.all():
        for center_request in request.centers_requests.all():
            ed_center = center_request.ed_center_year.ed_center
            for program_request in center_request.quota_requests.all().order_by('program__duration'):
                quota_price = round((program_request.price / 0.93*100),0) / 100
                quota_amount = program_request.ro_quota
                quota_sum = quota_price * quota_amount
                if quota_sum != 0:
                    ws.cell(row=row_number, column=1, value=ed_center.name)
                    ws.cell(row=row_number, column=2, value=program_request.program.duration)
                    ws.cell(row=row_number, column=3, value=quota_price)
                    ws.cell(row=row_number, column=4, value=quota_amount)
                    ws.cell(row=row_number, column=5, value=quota_sum)
                    row_number += 1
    
    wb.template = False
    response = HttpResponse(
        content=save_virtual_workbook(wb), 
        content_type='application/vnd.openxmlformats-\
        officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = "attachment; filename=" + \
        escape_uri_path(f'kvota_{request.send_date}.xlsx')
    return response



def net_agreements(agreements):
    path_to_archive = "media/archive/network_agreements.zip"
    with ZipFile(path_to_archive, 'w') as aggr_archive:
        agreements_w_file = agreements.exclude(agreement_file='')
        for agreement in agreements_w_file:
            file_name, file_extension = os.path.splitext(agreement.agreement_file.name)
            if agreement.suffix is None:
                number = f'{agreement.agreement_number}СЗ'
            else:
                number = f'{agreement.agreement_number}СЗ{agreement.suffix}'
            destination = f'сетевое_соглашение_№{number}{file_extension}'
            aggr_archive.write(agreement.agreement_file.name, destination)

    zip_file = open(path_to_archive, 'rb')
    response = HttpResponse(content=zip_file, content_type='application/force-download')
    time_now = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    response['Content-Disposition'] = f'attachment; filename=network_agreements ({time_now}).zip'
    return response


def programs(agreements):
    wb = Workbook()
    ws = wb.active
    ws.title = "Учебные программы"
    col_titles = [
        "№ п/п",
        "Наименование программы",
        "Наименование профессии",
        "Вид программы (подвид для ДПО)",
        "Количество часов",
        "Форма обучения",
        "Сетевая форма реализации (да/нет)",
        "Номер договора о сетевом взаимодействии",
        "Субъект(ы) РФ, в которых планируется реализация образовательной программы"
    ]
    
    for col_number, col_title in enumerate(col_titles, start=1):
        ws.cell(row=1, column=col_number, value=col_title)
        ws.cell(row=2, column=col_number, value=col_number)

    row_number = 3
    programs = EducationProgram.objects.filter(new_agreements__in=agreements)
    for program in programs:
        if program.program_type == 'DPOPK':
            program_type = "Дополнительное профессиональное образование (повышение квалификации)"
        elif program.program_type == 'DPOPP':
            program_type = "Дополнительное профессиональное образование (профессиональная переподготовка)"
        elif program.program_type == 'POPP':
            program_type = "Профессиональное обучение (переподготовка)"
        elif program.program_type == 'POP':
            program_type = "Профессиональное обучение (профессиональная подготовка)" 
        elif program.program_type == 'POPK':
            program_type ="Профессиональное обучение (повышение квалификации)"
        agreement = program.new_agreements.first()
        if agreement.suffix == None:
            number = f'{agreement.agreement_number}/СЗ' 
        else: number = f'{agreement.agreement_number}/СЗ{agreement.suffix}'
        ws.cell(row=row_number, column=1, value=row_number - 2)
        ws.cell(row=row_number, column=2, value=program.program_name)
        ws.cell(row=row_number, column=3, value=program.profession)
        ws.cell(row=row_number, column=4, value=program_type)
        ws.cell(row=row_number, column=5, value=program.duration)
        ws.cell(row=row_number, column=6, value=program.get_education_form_display())
        ws.cell(row=row_number, column=7, value="да")
        ws.cell(row=row_number, column=8, value=number)
        ws.cell(row=row_number, column=9, value="Самарская область")
        row_number += 1

    wb.template = False
    response = HttpResponse(
        content=save_virtual_workbook(wb), 
        content_type='application/vnd.openxmlformats-\
        officedocument.spreadsheetml.sheet'
    )
    time_now = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    response['Content-Disposition'] = "attachment; filename=" + \
        escape_uri_path(f'programs_list ({time_now}).xlsx')
    return response