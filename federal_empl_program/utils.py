import matplotlib.pyplot as plt
import base64
from io import BytesIO

import numpy as np

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