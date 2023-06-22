from django.contrib import admin

from .models import AgeGroup, ProfEnviroment, ProgramAuthor, TicketFullQuota, TicketProfession, TicketProgram, TicketProjectYear, EducationCenterTicketProjectYear,\
                    TicketProjectPosition, TicketEdCenterEmployeePosition,\
                    TicketIndicator, EdCenterTicketIndicator, TicketQuota
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
        'ed_center', 
        'education_form',
    ]

    
@admin.register(TicketFullQuota)
class TicketFullQuotaAdmin(admin.ModelAdmin):
    list_display = ['project_year', 'full_quota', 'federal_quota']


@admin.register(TicketQuota)
class TicketQuotaAdmin(admin.ModelAdmin):
    list_display = [
        'ed_center', 
        'school', 
        'profession', 
        'is_federal',
        'value',
        'quota'
    ]