from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.encoding import escape_uri_path
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook


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