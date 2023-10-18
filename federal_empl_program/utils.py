import os
import matplotlib.pyplot as plt
import base64
from io import BytesIO

import numpy as np
from openpyxl import Workbook, load_workbook

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i,y[i]-45,y[i], ha = 'center', color='white', fontsize=12, fontweight=500)

def get_applications_plot(month, applications):
    plt.switch_backend('AGG')

    x = np.arange(len(month)) # the label locations
    width = 0.45 # the width of the bars
    multiplier = 0.5

    fig, ax = plt.subplots(layout='constrained')
    for attribute, measurement in applications.items():
        offset = width * multiplier
        if attribute == 'Подали заявку':
            color = '#426cf8'
        else:
            color = '#394959'
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=color)
        ax.bar_label(rects, padding=2)
        multiplier += 1

    fig.set_figwidth(10)
    fig.set_figheight(5)
    fig.set_facecolor('#e9ecf7')
    ax.set_facecolor('#e9ecf7')
    ax.spines[['right', 'top']].set_visible(False)
    bar_labels = month
    

    #ax.bar(applications, month, label=bar_labels, color=bar_colors)
    #addlabels(applications, month)
    ax.set_ylabel('Количество заявок')
    ax.set_title('')

    ax.set_ylabel('Заявки')
    ax.set_xticks(x + width, month)
    ax.legend(loc='upper left', ncols=2)
    plt.tight_layout()
    graph = get_graph()
    return graph

def get_flow_applications_plot(weeks, weeks_stat):
    plt.switch_backend('AGG')

    x = np.arange(len(weeks))
    width = 0.3 # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')
    for attribute, measurement in weeks_stat.items():
        offset = width * multiplier
        if attribute == 'Новые':
            color = '#426cf8'
        elif attribute == 'Одобрены ЦЗН':
            color = '#02509e'
        else:
            color = '#394959'
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=color)
        ax.bar_label(rects, padding=2)
        multiplier += 1
    
    fig.set_figwidth(15)
    fig.set_figheight(5)
    fig.set_facecolor('#F2F2F2')
    ax.set_facecolor('#F2F2F2')
    ax.spines[['right', 'top']].set_visible(False)
    bar_labels = weeks

    ax.set_ylabel('Количество заявок')
    ax.set_title('')

    ax.set_ylabel('Заявки')
    ax.set_xticks(x + width, weeks)
    ax.legend(loc='upper left', ncols=4)
    ax.legend(ncols=4, bbox_to_anchor=(0, 1),
              loc='lower left')
    plt.tight_layout()
    graph = get_graph()
    return graph

def count_levels(directory_path):
    levels_values = []
    for filename in os.listdir(directory_path):
        f = os.path.join(directory_path, filename)
        if '.xlsx' not in filename:
            print(filename)
        elif os.path.isfile(f):
            workbook = load_workbook(f)
            sheet = workbook.active
            sheet_values = []
            sheet_values.append(sheet.cell(row = 5, column = 3).value)
            sheet_values.append(sheet.cell(row = 7, column = 3).value)
            sheet_values.append(sheet.cell(row = 8, column = 3).value)
            sheet_values.append(sheet.cell(row = 9, column = 3).value)
            sheet_values.append(filename)
            levels_values.append(sheet_values)
            
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Сводная уровней школ"
    ws.cell(row=1, column=1, value="Название школы")
    ws.cell(row=1, column=2, value="Базовый")
    ws.cell(row=1, column=3, value="Основной")
    ws.cell(row=1, column=4, value="Продвинутый")
    ws.cell(row=1, column=5, value="Название файла")
    for row_number, sheet in enumerate(levels_values, start=2):
        for col_number, value in enumerate(sheet, start=1):
            ws.cell(row=row_number, column=col_number, value=value)
    wb.save('Сводная уровней школ.xlsx')