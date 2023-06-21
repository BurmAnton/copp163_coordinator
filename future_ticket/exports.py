from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from django.db.models import Sum

from datetime import datetime
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from .models import TicketProfession, TicketQuota

def professions():
    professions = TicketProfession.objects.all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Программы"
    col_titles = [
        "ID", 
        "Название", 
        "Среда",
        "Федеральная?",
        "Колво программ",
        "Колво заявок"
    ]
    for col_number, col_title in enumerate(col_titles, start=1):
        ws.cell(row=1, column=col_number, value=col_title)

    row_number = 2
    for profession in professions:
        if profession.is_federal: is_federal = "Да"
        else: is_federal = "Нет"
        quota_sum = TicketQuota.objects.filter(profession=profession).distinct(
                            ).aggregate(Sum('quota'))['quota__sum']
        if quota_sum == None: quota_sum = 0
        ws.cell(row=row_number, column=1, value=profession.id)
        ws.cell(row=row_number, column=2, value=profession.name)
        ws.cell(row=row_number, column=3, value=profession.prof_enviroment.name)
        ws.cell(row=row_number, column=4, value=is_federal)
        ws.cell(row=row_number, column=5, value=len(profession.programs.all()))
        ws.cell(row=row_number, column=6, value=quota_sum)
        row_number += 1
    
    wb.template = False
    response = HttpResponse(
        content=save_virtual_workbook(wb), 
        content_type='application/vnd.openxmlformats-\
        officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = "attachment; filename=" + \
        escape_uri_path(
            f'professions_{datetime.now().strftime("%d/%m/%y %H:%M")}.xlsx'
        )
    return response