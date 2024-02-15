from django import forms
from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_admin_listfilter_dropdown.filters import (
    ChoiceDropdownFilter, DropdownFilter, RelatedOnlyDropdownFilter)
from easy_select2 import select2_modelform
from education_centers import exports

import users
from citizens.models import Citizen, School
from education_centers.forms import (AbilimpicsWinnerChangeForm,
                                     AbilimpicsWinnerCreationForm)
from federal_empl_program.models import (Application,
                                         EducationCenterProjectYear,
                                         ProjectYear)
from users.models import User

from .models import (AbilimpicsWinner, BankDetails, Competence,
                     ContractorsDocument, DocumentType, EducationCenter,
                     EducationProgram, Group, Teacher, Workshop)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'middle_name', 'organization', 'is_consent_file_upload']
    search_fields = [
        'organization__name', 
        'organization__flow_name', 
        'organization__short_name',
        'last_name', 
        'first_name', 
        'middle_name'
    ]

    def is_consent_file_upload(self, teacner):
        if teacner.consent_file.name == None:
            return "Нет"
        return "Да"
    is_consent_file_upload.short_description='Согласие подгружено?'

    actions = ['download_archive']
    def download_archive(self, request, queryset):
        return exports.consent_teachers(queryset)
    download_archive.short_description='Скачать архив согласий'

@admin.register(BankDetails)
class BankDetailsAdmin(admin.ModelAdmin):
    pass

@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'stage']

@admin.register(ContractorsDocument)
class ContractorsDocumentAdmin(admin.ModelAdmin):
    search_fields = ['contractor__name',]
    list_display = [
        'doc_type',
        'contractor', 
        'parent_doc',
        'register_number',
        'doc_stage',

    ]
    list_filter = (
        ('doc_type', RelatedOnlyDropdownFilter),
        ('contractor', RelatedOnlyDropdownFilter),
        ('doc_stage', ChoiceDropdownFilter)
    )

    filter_horizontal = ('groups',)

@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    pass

WorkshopForm = select2_modelform(Workshop, attrs={'width': '400px'})
class WorkshopInline(admin.TabularInline):
    model = Workshop
    form = WorkshopForm


EducationCentersForm = select2_modelform(EducationCenter, attrs={'width': '400px'})


@admin.register(EducationCenter)
class EducationCentersAdmin(admin.ModelAdmin):
    form = EducationCentersForm
    
    list_display = ['name', 'short_name', 'get_status', 'contact_person']

    search_fields = ['name', 'short_name', 'contact_person__last_name']

    fieldsets = (
        (None, {
            "fields": (
                'name', 'short_name', 'flow_name', 'contact_person'
            ),
        }),
    )

    def get_status(self, center):
        application_url = reverse("ed_center_application", args=[center.id])
        project_year = get_object_or_404(ProjectYear, year=2023)
        center_project_year, is_new = EducationCenterProjectYear.objects.get_or_create(
            project_year=project_year,
            ed_center=center
        )
        application_link = f'<a href="{application_url}" target="_blank">{center_project_year.get_stage_display()}</a>'
        return mark_safe(application_link)
    get_status.short_description='Статус заявки'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        cl_group = users.models.Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                queryset = EducationCenter.objects.filter(contact_person=request.user)
                return queryset
        return queryset

EducationProgramForm = select2_modelform(EducationProgram, attrs={'width': '400px'})


CompetenceForm = select2_modelform(Competence, attrs={'width': '400px'})

@admin.register(Competence)
class CompetencesAdmin(admin.ModelAdmin):
    form = CompetenceForm
    search_fields = ['title']
    list_display = ['title']


EducationProgramForm = select2_modelform(EducationProgram, attrs={'width': '400px'})

@admin.register(EducationProgram)
class EducationProgramAdmin(admin.ModelAdmin):
    form = EducationProgramForm
    list_display = ['program_name', 'flow_id', 'program_type', 'duration', 'flow_name', 'competence']
    filter_horizontal = ('teachers', 'workshops')
    list_filter = (
        ('program_type'),
        ('duration'),
        ('competence', RelatedOnlyDropdownFilter)
    )
    search_fields = ['program_name', 'ed_center__short_name', 'ed_center__name', 'ed_center__flow_name']

    def flow_name(self, program):
        if program.ed_center == None:
            return "-"
        if program.ed_center.flow_name == "":
            return program.ed_center.short_name
        return program.ed_center.flow_name
    flow_name.short_description = 'ЦО'
    flow_name.admin_order_field = 'ed_center__id'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(ed_center=None)

ApplicationForm = select2_modelform(Application, attrs={'width': '400px'})

class StudentsInline(admin.StackedInline):
    model = Application
    form = ApplicationForm
    fields = ('applicant',)

GroupForm = select2_modelform(Group, attrs={'width': '400px'})



AbilimpicsWinnerForm = select2_modelform(AbilimpicsWinner, attrs={'width': '400px'})

@admin.register(AbilimpicsWinner)
class AbilimpicsWinnerAdmin(UserAdmin):
    add_form = AbilimpicsWinnerCreationForm
    form = AbilimpicsWinnerChangeForm
    list_filter = []
    list_display = ('last_name', 'first_name', 'middle_name', 'email', 'competence', 'ed_center', 'program', 'is_received', 'is_send')
    fieldsets = (
        (None,
            {'fields': (
                'email', 'password', 'first_name', 'last_name', 'middle_name',
                'competence', 'ed_center', 'program', 'is_received', 'is_send'
            )}),
        ('Важные даты', 
            {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',

            )}
        ),
    )
    ordering = ('email',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    form = GroupForm
    inlines = [
        StudentsInline, 
    ]
    list_filter = (
        ('education_program__competence', RelatedOnlyDropdownFilter),
        ('education_program', RelatedOnlyDropdownFilter),
        ('workshop__education_center', RelatedOnlyDropdownFilter),
        ('workshop', RelatedOnlyDropdownFilter),
    )
    search_fields = ['flow_id', 'start_date', 'end_date']
    list_display = ('flow_id', 'education_period', 'pay_status')

    def education_period(self, group):
        start_date = group.start_date.strftime('%d/%m/%y')
        end_date = group.end_date.strftime('%d/%m/%y')
        period = f"{start_date}\xa0–\xa0{end_date}"
        return period
    education_period.short_description = 'Период обучения'
    education_period.admin_order_field = 'start_date'

    actions = ['change_to_pay_statys', ]

    def change_to_pay_statys(self, request, queryset):
        queryset.update(pay_status='PDB')
    change_to_pay_statys.short_description='Изменить статус на оплачен'


CitizenForm = select2_modelform(Application, attrs={'width': '400px'})

class CitizensInline(admin.TabularInline):
    model = Citizen
    form = CitizenForm
    fields = ('last_name', 'first_name', 'middle_name', 'phone_number', 'email')

    def get_readonly_fields(self, request, obj=None):
        cl_group = users.models.Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                return self.readonly_fields + ('last_name', 'first_name', 'middle_name', 'phone_number', 'email')
        return self.readonly_fields
