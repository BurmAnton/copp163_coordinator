from django.contrib import admin
from django_admin_listfilter_dropdown.filters import (
    ChoiceDropdownFilter, DropdownFilter, RelatedOnlyDropdownFilter)
from easy_select2 import select2_modelform

from .models import (AgeGroup, ContractorsDocumentTicket, DocumentTypeTicket,
                     EdCenterTicketIndicator, EducationCenterTicketProjectYear,
                     EventsCycle, PartnerEvent, ProfEnviroment, ProgramAuthor,
                     SchoolProjectYear, StudentBVB,
                     TicketEdCenterEmployeePosition, TicketEvent,
                     TicketFullQuota, TicketIndicator, TicketProfession,
                     TicketProgram, TicketProjectPosition, TicketProjectYear,
                     TicketQuota)


@admin.register(StudentBVB)
class StudentBVBAdmin(admin.ModelAdmin):
    search_fields = [ 'bvb_id', 'full_name', 'school__name', 'event__id']
    list_display = [
        'bvb_id', 'full_name', 'is_double', 'is_attend', 'school', 'event'
    ]

#@admin.register(TicketProjectYear)
class TicketProjectYearAdmin(admin.ModelAdmin):
    list_display = ['year']


@admin.register(EducationCenterTicketProjectYear)
class EducationCenterTicketProjectYearAdmin(admin.ModelAdmin):
    list_display = ['ed_center', 'project_year']


#@admin.register(TicketProjectPosition)
class TicketProjectPositionAdmin(admin.ModelAdmin):
    search_fields = ['position',]
    list_display = ['position', 'is_basis_needed', 'project_year']


#@admin.register(TicketEdCenterEmployeePosition)
class TicketEdCenterEmployeePositionAdmin(admin.ModelAdmin):
    search_fields = [
        'position__position', 
        'ed_center__name',
        'ed_center__short_name'
    ]
    list_display = ['employee', 'position', 'ed_center']


#@admin.register(TicketIndicator)
class TicketIndicatorAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    list_display = ['name', 'project_year', 'is_free_form']


#@admin.register(EdCenterTicketIndicator)
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


#@admin.register(ProgramAuthor)
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
    list_display = [
        'cycle_number', 
        'end_reg_date',
        'start_period_date',
        'end_period_date', 
        'status', 
        
    ]


@admin.register(PartnerEvent)
class PartnerEventAdmin(admin.ModelAdmin):
    search_fields = ['name', 'partner__name', 'contact', 'contact_phone', 'contact_email']
    list_filter = ['status']
    list_display = [
        'name', 
        'get_partner',
        'city',
        'contact', 
        'contact_phone', 
        'contact_email',
        'description',
        'instruction',
    ]

    def get_partner(self, event):
        return event.partner
    get_partner.short_description = 'Партнёр'
    
    actions = ['approve_event',]
    def approve_event(self, request, queryset):
        queryset.update(status='PRV')
    approve_event.short_description='Одобрить мероприятия'



@admin.register(TicketEvent)
class TicketEventAdmin(admin.ModelAdmin):
    list_display = [
        'profession', 
        'get_short_name', 
        'cycle', 
        'event_date', 
        'participants_count'
    ]

    list_filter = (
        ('cycle', RelatedOnlyDropdownFilter),
        ('profession', RelatedOnlyDropdownFilter),
        ('ed_center', RelatedOnlyDropdownFilter)
    )

    def participants_count(self, event):
        return event.participants.filter(
            is_double=False, is_attend=True).count()
    participants_count.short_description = 'Колво участников'
    
    def get_short_name(self, event):
        return event.ed_center.ed_center.short_name
    get_short_name.short_description = 'ЦО'
    get_short_name.admin_order_field = 'ed_center__ed_center__short_name'
