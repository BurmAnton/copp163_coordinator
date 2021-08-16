from django.shortcuts import render

from education_centers.models import Competence, EducationCenter, EducationProgram, EducationCenterGroup, Workshop
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
    
    appl_count = 0
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
        if stage != 'RES' and stage != 'NCOM':
            appl_count += stages_dict[stage]
            
    return render(request, 'region163_dashboard/ed_centers_empl.html', {
        'stat': stat,
        'stat_programs': stat_programs,
        'stages': stages,
        'appl_count': appl_count,
        'education_centers_count': len(education_centers),
        'competencies_count': len(competencies),
        'education_programs_count': len(education_programs),
        'stages_count': stages_count
    })

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def groups_suggestions(request):
    ed_center_groups = [EducationCenterGroup.objects.filter(group=None).values(
        'education_center',
        'education_center__name',
        'program',
        'program__program_name',
        'min_group_size',
        'max_group_size',
        'start_date',
        'end_date'
    )]
    groups = {}
    suggestions = []
    for ed_center_group in ed_center_groups[0]:
        education_center = ed_center_group['education_center']
        education_center__name = ed_center_group['education_center__name']
        education_program = ed_center_group['program']
        program__program_name = ed_center_group['program__program_name']
        max_students = ed_center_group['max_group_size']
        min_students = ed_center_group['min_group_size']
        start_date = ed_center_group['start_date']
        end_date = ed_center_group['end_date']
        ed_center_group = f"{ed_center_group['education_center__name']} {ed_center_group['program__program_name']}"
        workshops = Workshop.objects.filter(education_center=education_center)
        group = [Group.objects.filter(workshop__in=workshops, education_program=education_program).values(
            'workshop__education_center__name',
            'education_program__program_name',
            'students'
        )]
        if len(group[0]) > 0:
            groups[ed_center_group] = {}
            groups[ed_center_group]['education_center'] = group[0][0]['workshop__education_center__name']
            groups[ed_center_group]['program'] = group[0][0]['education_program__program_name']
            groups[ed_center_group]['students'] = len(group[0])
            students_count = groups[ed_center_group]['students']
            if max_students >= students_count >= min_students:
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%y')
                suggestions.append([
                    education_center__name, 
                    program__program_name,
                    min_students,
                    max_students,
                    start_date.strftime('%d/%m/%y'),
                    end_date,
                    'add', 
                    groups[ed_center_group]['education_center'],
                    groups[ed_center_group]['program'],
                    groups[ed_center_group]['students']
            ])

    return render(request, 'region163_dashboard/groups_suggestions.html', {
        'ed_center_group': ed_center_groups,
        'groups': groups,
        'suggestions': suggestions
    })

    