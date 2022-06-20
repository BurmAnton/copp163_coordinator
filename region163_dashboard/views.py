from datetime import datetime, timedelta
from email.mime import application

from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from django.views.decorators.csrf import csrf_exempt
from citizens.models import Citizen

from education_centers.models import Competence, EducationCenter, EducationProgram, EducationCenterGroup
from federal_empl_program.models import  Application
from django.template.defaulttags import register



def ed_centers_empl(request, **kwargs):
    stat = {}
    stat_programs = {}
    
    stages_dict = {}
    stages = ['ADM', 'SED', 'COMP', 'NCOM', 'RES', 'NADM'] 
    program_types = {
        'DPOPK': 'ДПО ПК',
        'DPOPP': 'ДПО ПП',
        'POP': 'ПО П',
        'POPP': 'ПО ПП',
        'POPK': 'ПО ПК',
    }

    applications = Application.objects.all()
    competencies = [competence for competence in Competence.objects.filter(competence_applicants__in=applications).distinct().values('title')]
    education_centers = [education_center for education_center in EducationCenter.objects.filter(edcenter_applicants__in=applications).distinct().values('name')]
    education_programs = [education_program for education_program in EducationProgram.objects.filter(programm_applicants__in=applications).distinct().values('program_name', 'duration', 'program_type')]
    applications = [application for application in Application.objects.all().values('competence__title', 'education_center__name', 'appl_status', 'education_program__program_name')]

    delay_date = datetime.now() - timedelta(days=9)
    delayed_appl = Application.objects.filter(appl_status='ADM', change_status_date__lte=delay_date)
    stat_delays = []
    ed_centers = EducationCenter.objects.filter(edcenter_applicants__in=Application.objects.all()).distinct()
    for education_center in ed_centers:
        if len(delayed_appl.filter(education_center=education_center)) > 0:
            stat_delays.append([education_center.name, len(Application.objects.filter(appl_status='ADM', education_center=education_center)), len(delayed_appl.filter(education_center=education_center))])
    def takeDelays(elem):
        return elem[2]
    stat_delays.sort(key=takeDelays, reverse=True)
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
    stages = ['ADM', 'SED', 'COMP', 'NCOM', 'RES', 'EXAM', 'NADM']
    
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

    stages = ['ADM', 'SED', 'COMP', 'NCOM', 'RES', 'NADM']
    stages_count = []
    for stage in stages:
        stages_count.append(stages_dict[stage])
        if stage not in ['RES', 'NCOM', 'NADM']:
            appl_count += stages_dict[stage]

    return render(request, 'region163_dashboard/ed_centers_empl.html', {
        'stat': stat,
        'stat_programs': stat_programs,
        'stages': stages,
        'appl_count': appl_count,
        'education_centers_count': len(education_centers),
        'competencies_count': len(competencies),
        'education_programs_count': len(education_programs),
        'stages_count': stages_count,
        'competencies': competencies,
        'stat_delays': stat_delays
    })

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def groups_suggestions(request):
    applications = [application for application in Application.objects.filter(appl_status__in=['VER','ADM'])]
    group_applications = [application for application in EducationCenterGroup.objects.filter(group=None)]
    competencies = [competence for competence in Competence.objects.all().values('title')]
    education_centers = [education_center for education_center in EducationCenter.objects.all().values('name', 'id')]
    education_programs = [education_program for education_program in EducationProgram.objects.all().values('program_name', 'duration', 'program_type')]
    
    competencies_dict = {}
    for competence in competencies:
        competence = competence['title']
        competencies_dict[competence] = {}
        competencies_dict[competence]['Programs'] = {}
        competencies_dict[competence]['Empty'] = True
        competencies_dict[competence]['Count'] = 0
        competencies_dict[competence]['Programs']['Нет'] = {}
        competencies_dict[competence]['Programs']['Нет']['Education_centers'] = {}
        competencies_dict[competence]['Programs']['Нет']['Empty'] = True
        competencies_dict[competence]['Programs']['Нет']['Count'] = 0
        for program in education_programs:
            program = program['program_name']
            competencies_dict[competence]['Programs'][program] = {}
            competencies_dict[competence]['Programs'][program]['Education_centers'] = {}
            competencies_dict[competence]['Programs'][program]['Empty'] = True
            competencies_dict[competence]['Programs'][program]['Count'] = 0
            for education_center in education_centers:
                education_center = education_center['name']
                competencies_dict[competence]['Programs'][program]['Education_centers'][education_center] = {}
                competencies_dict[competence]['Programs'][program]['Education_centers'][education_center]['Empty'] = True
                competencies_dict[competence]['Programs'][program]['Education_centers'][education_center]['Count'] = 0
                competencies_dict[competence]['Programs']['Нет']['Education_centers'][education_center] = {}
                competencies_dict[competence]['Programs']['Нет']['Education_centers'][education_center]['Empty'] = True
                competencies_dict[competence]['Programs']['Нет']['Education_centers'][education_center]['Count'] = 0

    for application in applications:
        competencies_dict[application.competence.title]['Count'] += 1
        competencies_dict[application.competence.title]['Empty'] = False
        if application.education_program != None:
            competencies_dict[application.competence.title]['Programs'][application.education_program.program_name]['Count'] += 1
            competencies_dict[application.competence.title]['Programs'][application.education_program.program_name]['Empty'] = False
            if application.education_center != None:
                competencies_dict[application.competence.title]['Programs'][application.education_program.program_name]['Education_centers'][application.education_center.name]['Count'] += 1
                competencies_dict[application.competence.title]['Programs'][application.education_program.program_name]['Education_centers'][application.education_center.name]['Empty'] = False
        else:
            competencies_dict[application.competence.title]['Programs']['Нет']['Empty'] = False
            competencies_dict[application.competence.title]['Programs']['Нет']['Count'] += 1
            if application.education_center != None:
                competencies_dict[application.competence.title]['Programs']['Нет']['Education_centers'][application.education_center.name]['Count'] += 1
                competencies_dict[application.competence.title]['Programs']['Нет']['Education_centers'][application.education_center.name]['Empty'] = False
    
    empty_comp = []
    empty_programs = []
    empty_ed_ceters = []
    for competence in competencies_dict:
        if competencies_dict[competence]['Empty']:
            empty_comp.append(competence)
        else:
            for program in competencies_dict[competence]['Programs']:
                if competencies_dict[competence]['Programs'][program]['Empty']:
                    empty_programs.append([competence, program])
                elif program != 'Нет':
                    for center in competencies_dict[competence]['Programs'][program]['Education_centers']:
                        if competencies_dict[competence]['Programs'][program]['Education_centers'][center]['Empty']:
                            empty_ed_ceters.append([competence, program, center])

    matches = []
    match_number = 1
    for group_appl in group_applications:
        competence = group_appl.competence.title
        program = group_appl.program.program_name
        education_center = group_appl.education_center.name
        min_group_size = group_appl.min_group_size
        comp_count = competencies_dict[competence]['Count']
        program_count = competencies_dict[competence]['Programs'][program]['Count']
        program_none_count = competencies_dict[competence]['Programs']['Нет']['Count']
        ed_center_count = competencies_dict[competence]['Programs'][program]['Education_centers'][education_center]['Count']
        ed_center_none_count = competencies_dict[competence]['Programs']['Нет']['Education_centers'][education_center]['Count']
        ed_centers = competencies_dict[competence]['Programs'][program]['Education_centers']
        url = 'http://127.0.0.1:8000/federal_empl_program/application/'
        match = []
        if comp_count >= min_group_size:
            if program_count >= min_group_size:
                if ed_center_count  >= min_group_size:
                    appl_count = competencies_dict[competence]['Programs'][program]['Education_centers'][education_center]['Count']
                    url_adress = f'{url}?competence__id__exact={group_appl.competence.id}&education_center__id__exact={group_appl.education_center.id}&education_program__id__exact={group_appl.program.id}'
                    match.append([match_number, appl_count, 'Группа', 'Отсутствует','Создать группу', url_adress])
                    match_number += 1
                else:
                    for ed_center in ed_centers:
                        if (ed_centers[ed_center]['Empty'] == False) and (ed_center != education_center):
                            appl_count = ed_centers[ed_center]['Count']
                            ed_id = EducationCenter.objects.get(name=ed_center).id
                            url_adress = f'{url}?competence__id__exact={group_appl.competence.id}&education_center__id__exact={ed_id}&education_program__id__exact={group_appl.program.id}'
                            match.append([match_number, appl_count, 'ЦО', ed_center,f'Сменить ЦО на {education_center}', url_adress])
                            match_number += 1
            elif program_count + program_none_count >= min_group_size:
                if ed_center_none_count + ed_center_count >= min_group_size:
                    appl_count = competencies_dict[competence]['Programs'][program]['Education_centers'][education_center]['Count']
                    url_adress = f'{url}?competence__id__exact={group_appl.competence.id}&education_center__id__exact={group_appl.education_center.id}&education_program__isnull=True'
                    match.append([match_number, appl_count, 'Программа подготовки', 'Отсутствует',f'Добавить {program}', url_adress])
                    match_number += 1
        appl_count = competencies_dict[competence]['Programs'][program]['Education_centers'][education_center]['Count']
        matches.append([group_appl, competence, appl_count, match])

                    

    return render(request, 'region163_dashboard/groups_suggestions.html', {
        'competencies_dict': competencies_dict,
        'matches': matches
    })


