from django.contrib import admin
import django.contrib.auth.models
from django.utils.safestring import mark_safe
from django.urls import reverse
from field_history.models import FieldHistory
from datetime import datetime, timedelta

from .models import Citizen, Job, School, SchoolClass
from federal_empl_program.models import Application
from education_centers.models import EducationCenter
from users.models import User

class JobInline(admin.TabularInline):
    model = Job
    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra + obj.jobs.count()
        return extra

class ApplicationInline(admin.StackedInline):
    model = Application
    readonly_fields = ['get_workshop',]
    fields = ('competence', 'education_program', 'education_center',
    'group', 'appl_status', 'creation_date', 'find_work')
    exclude = ('contract_type', 'category', 'admit_status')
    def get_workshop(self, obj):
        return obj.group.workshop.education_center
    get_workshop.short_description = 'Центр обучения'
    def get_extra(self, request, obj=None, **kwargs):
        extra = -1
        if obj:
            return extra + obj.POE_applications.count()
        return extra

@admin.register(Citizen)
class CitizensAdmin(admin.ModelAdmin):
    search_fields = ['phone_number','email','snils_number','first_name','middle_name','last_name']
    list_filter = ('social_status', 'is_verified')
    list_display = ('__str__', 'snils_number', 'email')
    readonly_fields = ['get_is_employed_history', 'get_self_employed_history']
    inlines = [
        ApplicationInline, JobInline 
    ]
    fieldsets = (
        (None, {
            'fields': ('last_name', 'first_name', 'middle_name', 'sex', 'snils_number', 'inn_number')
        }),
        ('Контактная информация', {
            'fields': ('email', 'phone_number', 'res_region', 'res_city', "copp_registration"),
        }),
        ('Статус', {
            'fields': ('social_status', 'education_type', 'school', 'is_employed',
            'get_is_employed_history', 'self_employed', 'get_self_employed_history','is_verified'),
        })
    )
    def get_is_employed_history(self, application):
        is_employed_history = application.field_history.filter(field_name='is_employed').latest('date_created').date_created + timedelta(hours=4)
        return is_employed_history.strftime('%d/%m/%y %H:%M')
    get_is_employed_history.short_description='Дата последнего изменения'

    def get_self_employed_history(self, application):
        self_employed_history = application.field_history.filter(field_name='self_employed').latest('date_created').date_created + timedelta(hours=4)
        return self_employed_history.strftime('%d/%m/%y %H:%M')
    get_self_employed_history.short_description='Дата последнего изменения'


    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        cl_group = django.contrib.auth.models.Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                education_centers = EducationCenter.objects.filter(contact_person=request.user)
                applications = Application.objects.filter(education_center__in=education_centers)     
                queryset = Citizen.objects.filter(POE_applications__in=applications)
                return queryset
        return queryset

class SchoolClassInline(admin.TabularInline):
    model = SchoolClass

@admin.register(School)
class SchoolsAdmin(admin.ModelAdmin):
    search_fields = ['name', 'city', 'adress', 'specialty']
    list_filter = ('city', 'specialty')
    list_display = ('name', 'city', 'adress', 'specialty')
    filter_horizontal = ("school_coordinators",)
    inlines = [
        SchoolClassInline
    ]
    fieldsets = (
        (None, {
            'fields': (
                "name",
                "specialty"
            ),
        }),
        ("Местоположение",{
            'fields': (
                "city",
                "adress"
            ),
        }),
        ("Координаторы", {
            'classes': ('collapse',),
            'fields': (
                "school_coordinators",
            )
        }),
    )

class CitizenInline(admin.TabularInline):
    model = Citizen
    fieldsets = (
        (None, {
            "fields": (
                "first_name",
                "last_name",
                "middle_name",
                "email"
            ),
        }),
    )
    short_description='Студенты'
    

@admin.register(SchoolClass)
class SchoolClassesAdmin(admin.ModelAdmin):
    inlines = [
        CitizenInline
    ]
