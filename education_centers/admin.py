from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import RelatedOnlyDropdownFilter,\
      DropdownFilter, ChoiceDropdownFilter

from .models import Workshop, EducationCenter, EducationProgram, Competence, \
      Group, EducationCenterGroup, ContractorsDocument, DocumentType, \
      BankDetails, EducationCenterHead
from federal_empl_program.models import Application, EducationCenterProjectYear, ProjectYear
from citizens.models import Citizen, School, SchoolClass
from users.models import User
import users

@admin.register(BankDetails)
class BankDetailsAdmin(admin.ModelAdmin):
    pass

@admin.register(EducationCenterHead)
class EducationCenterHeadAdmin(admin.ModelAdmin):
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
    filter_horizontal = ('competences',)
    inlines = [
        WorkshopInline
    ]
    search_fields = ['name', 'short_name', 'contact_person__last_name']

    def reg_link(self, group):
        reg_link = f"https://copp63-coordinator.ru/registration/1?c={group.id}"
        return reg_link
    reg_link.short_description = 'Ссылка на рег.'


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

class EducationProgramInline(admin.TabularInline):
    model = EducationProgram
    form = EducationProgramForm

CompetenceForm = select2_modelform(Competence, attrs={'width': '400px'})

@admin.register(Competence)
class CompetencesAdmin(admin.ModelAdmin):
    form = CompetenceForm
    list_filter = ('block', 'competence_stage', 'competence_type')
    search_fields = ['title']
    list_display = ['title', 'block', 'competence_stage', 'competence_type']
    inlines = [
        EducationProgramInline,
    ]

EducationProgramForm = select2_modelform(EducationProgram, attrs={'width': '400px'})

@admin.register(EducationProgram)
class EducationProgramAdmin(admin.ModelAdmin):
    form = EducationProgramForm
    list_display = ['program_name', 'program_type', 'duration', 'competence']

    list_filter = (
        ('program_type'),
        ('duration'),
        ('competence', RelatedOnlyDropdownFilter)
    )
    search_fields = ['program_name',]

ApplicationForm = select2_modelform(Application, attrs={'width': '400px'})

class StudentsInline(admin.StackedInline):
    model = Application
    form = ApplicationForm
    fields = ('applicant',)

GroupForm = select2_modelform(Group, attrs={'width': '400px'})

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
        'is_new_price'
    )
    search_fields = ['name', 'start_date', 'end_date']
    list_display = ('name', 'education_period', 'is_new_price', 'workshop_link', 'competence')
    
    def competence(self, group):
        url = reverse("admin:education_centers_competence_change", args=[group.education_program.competence.id])
        link = f'<a href="%s"> %s </a>' % (url, group.education_program.competence)
        return mark_safe(link)
    competence.short_description = 'Компетенция'

    def workshop_link(self, group):
        url = reverse("admin:education_centers_educationcenter_change", args=[group.workshop.education_center.id])
        link = f'<a href="%s"> %s </a>' % (url, group.workshop)
        return mark_safe(link)
    workshop_link.short_description = 'Место обучения (адрес)'

    def education_period(self, group):
        start_date = group.start_date.strftime('%d/%m/%y')
        end_date = group.end_date.strftime('%d/%m/%y')
        period = f"{start_date}\xa0–\xa0{end_date}"
        return period
    education_period.short_description = 'Период обучения'
    education_period.admin_order_field = 'start_date'

    actions = ['set_new_price', 'set_old_price']

    def set_new_price(self, request, queryset):
        queryset.update(is_new_price=True)
    set_new_price.short_description='Установить новую цену'

    def set_old_price(self, request, queryset):
        queryset.update(is_new_price=False)
    set_old_price.short_description='Вернуть старую цену'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        cl_group = users.models.Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                education_centers = EducationCenter.objects.filter(contact_person=request.user)
                if len(education_centers) != 0:  
                    workshops = Workshop.objects.filter(education_center=education_centers[0])        
                    queryset = Group.objects.filter(workshop__in=workshops)
                    return queryset
        return queryset


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

EducationCenterForm = select2_modelform(EducationCenterGroup, attrs={'width': '400px'})

#@admin.register(EducationCenterGroup)
class EducationCenterGroupAdmin(admin.ModelAdmin):
    form = EducationCenterForm
    inlines = [
        CitizensInline, 
    ]
    list_filter = (
        ('education_center', RelatedOnlyDropdownFilter),
        ('competence', RelatedOnlyDropdownFilter),
        ('city', DropdownFilter),
        ('start_date'),
        ('end_date')
    )

    search_fields = ['education_center', 'get_id', 'competence', 'program', 'start_date', 'end_date']
    list_display = ('get_id', 'competence', 'program', 'education_center', 'city', 'education_period')
    fieldsets = (
        (None, {
            'fields': ('education_center', 'competence', 'program', 'program_link', 'educational_requirements', 'duration', 'description', 'is_visible')
        }),
        ('Формат и место проведения', {
            'fields': ('is_online', 'ed_city')
        }),
        ('Размер группы', {
            'fields': ('min_group_size', 'max_group_size')
        }),
        ('Период', {
            'fields': ('start_date', 'end_date', 'study_period', 'study_days_count', 'ed_schedule_link'),
        }),
    )

    def education_period(self, ed_group):
        start_date = ed_group.start_date.strftime('%d/%m/%y')
        end_date = ed_group.end_date
        if end_date is not None:
            end_date = end_date.strftime('%d/%m/%y')
            period = f"{start_date}\xa0–\xa0{end_date}"
        else:
            period = f"с {start_date}"
        return period
    education_period.short_description = 'Период обучения'
    education_period.admin_order_field = 'start_date'

    def get_id(self, group):
        id = f'ЦО-{group.id}'
        return id
    get_id.short_description = 'ID'
    get_id.admin_order_field = 'id'
    
    
    def get_readonly_fields(self, request, obj=None):
        cl_group = users.models.Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                return self.readonly_fields + ('is_visible',)
        return self.readonly_fields

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        cl_group = users.models.Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                education_centers = EducationCenter.objects.filter(contact_person=request.user)
                return queryset.filter(education_center__in=education_centers)
        return queryset
