from django.shortcuts import render

from education_centers.models import Competence, EducationCenter, EducationProgram
from federal_empl_program.models import Group, Application
from django.template.defaulttags import register

def ed_centers_empl(request):
    stat = {}
    stat_programs = {}
    stages_dict = {}
    stages = ['NEW', 'VER', 'ADM', 'SED', 'COMP', 'NCOM', 'RES'] 
    program_types = {
        'DPOPK': 'ДПО ПК',
        'DPOPP': 'ДПО ПП',
        'POP': 'ПО П',
        'POPP': 'ПО ПП',
        'POPK': 'ПО ПК',
    }
    
    applications = [application for application in Application.objects.all().values('competence__title', 'education_center__name', 'appl_status', 'education_program__program_name')]
    competencies = [competence for competence in Competence.objects.all().values('title')]
    education_centers = [education_center for education_center in EducationCenter.objects.all().values('name')]
    education_programs = [education_program for education_program in EducationProgram.objects.all().values('program_name', 'duration', 'program_type')]

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

    for education_program in education_programs:
        duration = education_program['duration']
        program_type = education_program['program_type']
        education_program = education_program['program_name']
        stat_programs[education_program] = {}
        stat_programs[education_program]['duration'] = duration
        stat_programs[education_program]['program_type'] = program_types[program_type]
        stat_programs[education_program]['Empty'] = True
        for education_center in education_centers:
            education_center = education_center['name']
            stat_programs[education_program][education_center] = {}
            stat_programs[education_program][education_center]['Empty'] = True
            for stage in stages:
                stat_programs[education_program][education_center][stage] = 0

    for stage in stages:
        stages_dict[stage] = 0
    stages = ['NEW', 'VER', 'ADM', 'SED', 'COMP', 'NCOM', 'RES', 'EXAM']
    
    for application in applications:
        if application['appl_status'] in stages:
            if application['appl_status'] == 'EXAM':
                stat[application['competence__title']][application['education_center__name']]['SED'] += 1
                stages_dict['SED'] += 1     
                if application['education_program__program_name'] is not None:
                    stat_programs[application['education_program__program_name']][application['education_center__name']]['SED'] += 1
                    stat_programs[application['education_program__program_name']]['Empty'] = False
                    stat_programs[application['education_program__program_name']][application['education_center__name']]['Empty'] = False         
            else:
                stat[application['competence__title']][application['education_center__name']][application['appl_status']] += 1
                stages_dict[application['appl_status']] += 1
                if application['education_program__program_name'] is not None:
                    stat_programs[application['education_program__program_name']][application['education_center__name']][application['appl_status']] += 1
                    stat_programs[application['education_program__program_name']]['Empty'] = False
                    stat_programs[application['education_program__program_name']][application['education_center__name']]['Empty'] = False
            stat[application['competence__title']]['Empty'] = False
            stat[application['competence__title']][application['education_center__name']]['Empty'] = False

    stages = ['NEW', 'VER', 'ADM', 'SED', 'COMP', 'NCOM', 'RES'] 
    stages_count = []
    for stage in stages:
        stages_count.append(stages_dict[stage])
            
    return render(request, 'region163_dashboard/ed_centers_empl.html', {
        'stat': stat,
        'stat_programs': stat_programs,
        'stages': stages,
        'appl_count': len(applications),
        'education_centers_count': len(education_centers),
        'competencies_count': len(competencies),
        'education_programs_count': len(education_programs),
        'stages_count': stages_count
    })

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)