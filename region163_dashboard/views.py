from datetime import date, datetime, timedelta

from io import BytesIO
import base64
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler

from pandas.tseries.offsets import BDay

from django.shortcuts import render

from education_centers.models import Competence, EducationCenter, EducationProgram, EducationCenterGroup
from federal_empl_program.models import  Application, CitizenCategory
from django.template.defaulttags import register
from federal_empl_program.models import Grant


def get_graphic():
    labels = []
    approved_appl = []
    started_appl = []
    
    end_date = datetime.now() - timedelta(7)
    if end_date.weekday() < 4:
        delta = timedelta(4 - end_date.weekday())
        end_date = end_date + delta
    elif end_date.weekday() > 4:
        delta = timedelta(6 - end_date.weekday() + 5)
        end_date = end_date + delta
    start_date = end_date - timedelta(7*7)
    start_week_date = start_date
    end_week_date = start_date + timedelta(7)

    while end_week_date <= end_date:
        start_week_date = start_week_date + timedelta(7)
        end_week_date = end_week_date + timedelta(7)
        labels.append(f'{(start_week_date + timedelta(1)).strftime("%d/%m")}-{end_week_date.strftime("%d/%m")}')
        approved_appl.append(Application.objects.filter(
                appl_status='ADM',
                change_status_date__lte=end_week_date,
                change_status_date__gt=start_week_date,
            ).exclude(change_status_date=None).count()
        ) 
        started_appl.append(Application.objects.filter(
                appl_status__in=['SED', 'COMP'],
                change_status_date__lte=end_week_date,
                change_status_date__gt=start_week_date,
            ).exclude(change_status_date=None).count()
        )
    
    x = np.arange(len(labels))
    width = 0.35

    mpl.rcParams['axes.prop_cycle'] = cycler(color=['#778899', '#364554'])
    fig, ax = plt.subplots(figsize=(10, 4))
    
    rects1 = ax.bar(x - width/2, approved_appl, width, label='Допущено')
    rects2 = ax.bar(x + width/2, started_appl, width, label='Приступило к обучению')

    ax.set_ylabel('Заявки')
    ax.set_xticks(x, labels)
    ax.margins(y=0.3)
    ax.legend(loc='upper right')

    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
 
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    return graphic

def ed_centers_empl(request, **kwargs):
    stat = {}
    stat_programs = {}
    
    stages_dict = {}
    stages = ['ADM', 'SED', 'COMP']
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

    delay_date = datetime.now() - BDay(8)
    delayed_appl = Application.objects.filter(appl_status='ADM', change_status_date__lte=delay_date)
    stat_delays = []
    ed_centers = EducationCenter.objects.filter(edcenter_applicants__in=Application.objects.all()).distinct()
    for education_center in ed_centers:
        if len(delayed_appl.filter(education_center=education_center)) > 0:
            stat_delays.append([
                education_center.name, 
                len(Application.objects.filter(appl_status='ADM', education_center=education_center)), 
                len(delayed_appl.filter(education_center=education_center)), 
                len(Application.objects.filter(appl_status='SED', education_center=education_center))
            ])
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

    stages_count = []
    for stage in stages:
        stages_count.append(stages_dict[stage])
     
    quote_stages = ['SED', 'COMP', 'EXAM']
    appl_count = Application.objects.filter(appl_status__in=quote_stages).distinct().count()

    #Quotes
    grant_1 = Grant.objects.get(grant_name='Грант 1')
    quote_fb_goal = grant_1.qoute_256 + grant_1.qoute_144 + grant_1.qoute_72
    categories = CitizenCategory.objects.exclude(short_name__in=['Безработные зарег. в ЦЗН', 'Безработные незарег. в ЦЗН', 'Под риском увольнения'])
    qouta_fb_ADM = Application.objects.filter(appl_status='ADM', resume=False, citizen_category__in=categories).count()
    qouta_fb_SED = Application.objects.filter(appl_status='SED', resume=False, citizen_category__in=categories).count()
    qouta_fb_COMP = Application.objects.filter(appl_status__in=['COMP','EXAM'], resume=False, citizen_category__in=categories).count()
    qouta_fb_72 = Application.objects.filter(appl_status__in=['COMP','EXAM', 'SED'], resume=False, citizen_category__in=categories, education_program__duration=72).count()
    qouta_fb_144 = Application.objects.filter(appl_status__in=['COMP','EXAM', 'SED'], resume=False, citizen_category__in=categories, education_program__duration=144).count()
    qouta_fb_256 = Application.objects.filter(appl_status__in=['COMP','EXAM', 'SED'], resume=False, citizen_category__in=categories, education_program__duration=256).count()
    quota_fb_fact = Application.objects.filter(appl_status__in=quote_stages, resume=False, citizen_category__in=categories).count()
    quota_fb_fact_p = round(quota_fb_fact / quote_fb_goal * 100)
    quota_fb = f'{quota_fb_fact}/{quote_fb_goal} ({quota_fb_fact_p}%)'
    
    grant_fby = Grant.objects.get(grant_name='Молодёжь')
    qouta_fby_goal = grant_fby.qoute_256 + grant_fby.qoute_144 + grant_fby.qoute_72
    categories = CitizenCategory.objects.filter(short_name__in=[
            'Граждане до 35 лет обратившиеся в СЗН',
            'Граждане до 35 лет находящиеся под риском увольнения', 
            'Граждане до 35 лет не занятые с получения образования', 
            'Граждане до 35 лет, обучающиеся на последних курсах',
            'Граждане до 35 лет не занятые после военной службы',
            '16-35 без ВО/СПО',
            '16-35 студенты 2022'
        ])
    qouta_fby_ADM = Application.objects.filter(appl_status='ADM', resume=False, citizen_category__in=categories).count()
    qouta_fby_SED = Application.objects.filter(appl_status='SED', resume=False, citizen_category__in=categories).count()
    qouta_fby_COMP = Application.objects.filter(appl_status__in=['COMP','EXAM'], resume=False, citizen_category__in=categories).count()
    qouta_fby_72 = Application.objects.filter(appl_status__in=['COMP','EXAM', 'SED'], resume=False, citizen_category__in=categories, education_program__duration=72).count()
    qouta_fby_144 = Application.objects.filter(appl_status__in=['COMP','EXAM', 'SED'], resume=False, citizen_category__in=categories, education_program__duration=144).count()
    qouta_fby_256 = Application.objects.filter(appl_status__in=['COMP','EXAM', 'SED'], resume=False, citizen_category__in=categories, education_program__duration=256).count()
    qouta_fby_fact = Application.objects.filter(appl_status__in=quote_stages, resume=False, citizen_category__in=categories).count()
    quota_fby_fact_p = round(qouta_fby_fact / qouta_fby_goal * 100)
    quota_fby = f'{qouta_fby_fact}/{qouta_fby_goal} ({quota_fby_fact_p}%)'
    
    grant_2 = Grant.objects.get(grant_name='Грант 2')
    qouta_rf_goal = grant_2.qoute_256 + grant_2.qoute_144 + grant_2.qoute_72
    categories = CitizenCategory.objects.filter(short_name__in=['Безработные зарег. в ЦЗН', 'Безработные незарег. в ЦЗН', 'Под риском увольнения'])
    qouta_rf_ADM = Application.objects.filter(appl_status='ADM', resume=False, citizen_category__in=categories).count()
    qouta_rf_SED = Application.objects.filter(appl_status='SED', resume=False, citizen_category__in=categories).count()
    qouta_rf_COMP = Application.objects.filter(appl_status__in=['COMP','EXAM'], resume=False, citizen_category__in=categories).count()
    qouta_rf_72 = Application.objects.filter(appl_status__in=['COMP','EXAM', 'SED'], resume=False, citizen_category__in=categories, education_program__duration=72).count()
    qouta_rf_144 = Application.objects.filter(appl_status__in=['COMP','EXAM', 'SED'], resume=False, citizen_category__in=categories, education_program__duration=144).count()
    qouta_rf_256 = Application.objects.filter(appl_status__in=['COMP','EXAM', 'SED'], resume=False, citizen_category__in=categories, education_program__duration=256).count()
    qouta_rf_fact = Application.objects.filter(appl_status__in=quote_stages, resume=False, citizen_category__in=categories).count()
    quota_rf_fact_p = round(qouta_rf_fact / qouta_rf_goal * 100)
    quota_rf = f'{qouta_rf_fact}/{qouta_rf_goal} ({quota_rf_fact_p}%)'

    all_quotas_p = round(appl_count / (quote_fb_goal+qouta_rf_goal) * 100)
    all_quotas = f'{appl_count}/{quote_fb_goal+qouta_rf_goal} ({all_quotas_p}%)'
    qouta_all_72 = qouta_fb_72 + qouta_rf_72
    qouta_all_144 = qouta_fb_144 + qouta_rf_144
    qouta_all_256 = qouta_fb_256 + qouta_rf_256

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
        'stat_delays': stat_delays,
        'graphic': get_graphic(),
        'quota_fb': quota_fb,
        'qouta_fb_ADM': qouta_fb_ADM,
        'qouta_fb_SED': qouta_fb_SED,
        'qouta_fb_COMP': qouta_fb_COMP,
        'qouta_fb_72': qouta_fb_72,
        'qouta_fb_144': qouta_fb_144,
        'qouta_fb_256': qouta_fb_256,
        'qouta_fby': quota_fby,
        'qouta_fby_ADM': qouta_fby_ADM,
        'qouta_fby_SED': qouta_fby_SED,
        'qouta_fby_COMP': qouta_fby_COMP,
        'qouta_fby_72': qouta_fby_72,
        'qouta_fby_144': qouta_fby_144,
        'qouta_fby_256': qouta_fby_256,
        'quota_rf': quota_rf,
        'qouta_rf_ADM': qouta_rf_ADM,
        'qouta_rf_SED': qouta_rf_SED,
        'qouta_rf_COMP': qouta_rf_COMP,
        'qouta_rf_72': qouta_rf_72,
        'qouta_rf_144': qouta_rf_144,
        'qouta_rf_256': qouta_rf_256,
        'all_quotas': all_quotas,
        'qouta_all_72': qouta_all_72,
        'qouta_all_144': qouta_all_144,
        'qouta_all_256': qouta_all_256,
        'grant_1': Grant.objects.get(grant_name='Грант 1'),
        'grant_2': Grant.objects.get(grant_name='Грант 2')
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


