from django.shortcuts import render

from education_centers.models import Competence, EducationCenter, EducationProgram
from federal_empl_program.models import Group, Application
from django.template.defaulttags import register
...

# Create your views here.
def ed_centers_empl(request):
    stat = {}
    compentencies = Competence.objects.all()
    education_centers = EducationCenter.objects.all()
    statuses = Application.ADM_STATUS_CHOICES
    statuses_dict = {
        'RECA': "Заявка получена",
        'CONT': "Связались/Ждём документы",
        'RECD': "Получили часть документов",
        'CONF': "Подтвердили статус",
        'ADM': "Допустили на платформе",
        'REF': "Отказали"
    }

    for competence in compentencies:
        stat[competence] = {}
        stat[competence]['Empty'] = True
        for ed_center in education_centers:
            stat[competence][ed_center] = {}
            stat[competence][ed_center]['Empty'] = True
            applications = Application.objects.filter(education_center=ed_center, competence=competence)
            if len(applications) > 0:
                stat[competence][ed_center]['Empty'] = False
                stat[competence]['Empty'] = False
                for status in statuses:
                    stat[competence][ed_center][status[0]] = len(applications.filter(admit_status=status[0]))

    return render(request, 'region163_dashboard/ed_centers_empl.html', {
        'ed_centers': stat,
        'stages': statuses_dict
    })

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)