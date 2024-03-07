import base64
import os
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
from openpyxl import Workbook, load_workbook

from federal_empl_program.models import FgosStandart, Profstandart


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
    

    ax.bar(applications, month, label=bar_labels, color=bar_colors)
    addlabels(applications, month)
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
    width = 0.2 # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')
    for attribute, measurement in weeks_stat.items():
        offset = width * multiplier
        if attribute == 'Начали обучение':
            color = '#426cf8'
        elif attribute == 'Завершили обучение':
            color = '#02509e'
        else:
            color = '#394959'
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=color)
        ax.bar_label(rects, padding=2)
        multiplier += 1
    
    fig.set_figwidth(12)
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


def save_program_stage(form, program):
    stage = form['save-stage']
    if stage == "1":

        program.standart = FgosStandart.objects.get(id=form['standart'])
        program.profstandart = Profstandart.objects.get(id=form['profstandart'])
        program.assigned_qualif = form['assigned_qualif']
        program.gen_functions = form['gen_functions']
        program.duration_days = form['duration_days']
        program.current_control = form['current_control']
        program.middle_control = form['middle_control']
        program.final_control = form['final_control']
        program.final_control_matereils = form['final_control_matereils']
        program.final_control_criteria = form['final_control_criteria']
        program.min_score = form['min_score']

        if program.status == "0" or program.status == "1":
            program.status = "2"
            stage = 2
        else:
            stage = 1
    elif stage == "2":
        if program.status == "2":
            program.status = "3"
            stage = 3
        else:
            stage = 2
    elif stage == "3":
        if program.status == "3":
            program.status = "4"
            stage = 4
        else:
            stage = 3
    elif stage == "4" or stage == "5":
        if program.status == "4" or program.status == "5":
            program.status = "6"
            stage = 6
        else:
            stage = 4
    elif stage == "6":
        if program.status == "6":
            program.status = "7"
            stage = 7
        else:
            stage = 6
    program.save()
    return int(stage)
        
        