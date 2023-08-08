from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from django.utils.encoding import escape_uri_path


def quota_request(request):
    

    wb = Workbook()
    ws = wb.active
    ws.title = "Центры обучения"
    col_titles = [
        "№ п/п",
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
        ws.cell(row=row_number, column=1, value=ed_center.id)
        ws.cell(row=row_number, column=2, value=ed_center.name)
        ws.cell(row=row_number, column=3, value=ed_center.short_name)
        row_number += 1
    
    wb.template = False
    response = HttpResponse(
        content=save_virtual_workbook(wb), 
        content_type='application/vnd.openxmlformats-\
        officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = "attachment; filename=" + \
        escape_uri_path(f'ed_centers_{datetime.now().strftime("%d/%m/%y")}.xlsx')
    return response