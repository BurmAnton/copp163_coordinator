from django.contrib import admin
from django_admin_listfilter_dropdown.filters import RelatedOnlyDropdownFilter,\
      DropdownFilter, ChoiceDropdownFilter
from easy_select2 import select2_modelform

from .models import AgeGroup, ContractorsDocumentTicket, DocumentTypeTicket, EventsCycle, \
    ProfEnviroment, ProgramAuthor, SchoolProjectYear, TicketFullQuota, \
    TicketProfession, TicketProgram, TicketProjectYear, \
    EducationCenterTicketProjectYear, TicketProjectPosition, \
    TicketEdCenterEmployeePosition, TicketIndicator, EdCenterTicketIndicator, \
    TicketQuota
# Register your models here.


@admin.register(TicketProjectYear)
class TicketProjectYearAdmin(admin.ModelAdmin):
    list_display = ['year']


@admin.register(EducationCenterTicketProjectYear)
class EducationCenterTicketProjectYearAdmin(admin.ModelAdmin):
    list_display = ['ed_center', 'project_year']


@admin.register(TicketProjectPosition)
class TicketProjectPositionAdmin(admin.ModelAdmin):
    search_fields = ['position',]
    list_display = ['position', 'is_basis_needed', 'project_year']


@admin.register(TicketEdCenterEmployeePosition)
class TicketEdCenterEmployeePositionAdmin(admin.ModelAdmin):
    search_fields = [
        'position__position', 
        'ed_center__name',
        'ed_center__short_name'
    ]
    list_display = ['employee', 'position', 'ed_center']


@admin.register(TicketIndicator)
class TicketIndicatorAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    list_display = ['name', 'project_year', 'is_free_form']


@admin.register(EdCenterTicketIndicator)
class EdCenterTicketIndicatorAdmin(admin.ModelAdmin):
    search_fields = [
        'indicator_name',
        'ed_center__name',
        'ed_center__short_name'
    ]
    list_display = [
        'indicator', 
        'ed_center', 
        'value', 
        'free_form_value'
    ]


@admin.register(ProfEnviroment)
class ProfEnviromentAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(TicketProfession)
class TicketProfessionAdmin(admin.ModelAdmin):
    search_fields = [
        'name', 
        'prof_enviroment__name'
    ]
    list_display = ['name', 'prof_enviroment', 'is_federal']


@admin.register(ProgramAuthor)
class ProgramAuthorAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'phone', 'email']


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(TicketProgram)
class TicketProgramAdmin(admin.ModelAdmin):
    search_fields = [
        'profession__name',
        'ed_center__name',
        'ed_center__short_name'
    ]
    list_display = [
        'profession',
        'updated_at', 
        'ed_center', 
        'education_form',
        'created_at'
    ]
    list_filter = (
        ('status', ChoiceDropdownFilter),
    )

    
@admin.register(TicketFullQuota)
class TicketFullQuotaAdmin(admin.ModelAdmin):
    list_display = ['project_year', 'full_quota', 'federal_quota']


@admin.register(SchoolProjectYear)
class SchoolProjectYearAdmin(admin.ModelAdmin):
    search_fields = [
        'school__name',
        'resp_full_name',
        'resp_position',
        'phone',
        'email',
    ]
    list_display = [
        'school', 
        'resp_full_name', 
        'resp_position',
        'phone',
        'email',
        'project_year'
    ]


TicketQuotaForm = select2_modelform(TicketQuota, attrs={'width': '600px'})

@admin.register(TicketQuota)
class TicketQuotaAdmin(admin.ModelAdmin):
    form = TicketQuotaForm
    list_display = [
        'ed_center', 
        'school', 
        'profession', 
        'is_federal',
        'value',
        'approved_value',
        'free_quota',
        'quota',
        
    ]

@admin.register(DocumentTypeTicket)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'stage']


@admin.register(ContractorsDocumentTicket)
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


@admin.register(EventsCycle)
class EventsCycleAdmin(admin.ModelAdmin):
    list_display = ['start_period_date', 'end_period_date', 'status', 'end_reg_date']

    