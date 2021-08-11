from django.shortcuts import render

from education_centers.models import Competence, EducationCenter, EducationProgram
from federal_empl_program.models import Group, Application
from django.template.defaulttags import register

# Create your views here.
def ed_centers_empl(request):
    stat = {}
    stages = ['NEW', 'VER', 'ADM', 'SED', 'COMP', 'NCOM', 'RES']
    applications = [application for application in Application.objects.filter(appl_status__in = stages).values('competence__title', 'education_center__name', 'appl_status')]
    competencies = [competence for competence in Competence.objects.all().values('title')]
    education_centers = [education_center for education_center in EducationCenter.objects.all().values('name')]

    for competence in competencies:
        competence = competence['title']
        stat[competence] = {}
        stat[competence]['Empty'] = True
        for education_center in education_centers:
            education_center = education_center['name']
            stat[competence][education_center] = {}
            stat[competence][education_center]['Empty'] = True
            for stage in stages:
                stat[competence][education_center][stage] = 0

    for application in applications:
        stat[application['competence__title']][application['education_center__name']][application['appl_status']] += 1
        if stat[application['competence__title']][application['education_center__name']][application['appl_status']] > 0:
            stat[application['competence__title']]['Empty'] = False
            stat[application['competence__title']][application['education_center__name']]['Empty'] = False
            
    return render(request, 'region163_dashboard/ed_centers_empl.html', {
        'stat': stat,
        'stages': stages
    })

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)