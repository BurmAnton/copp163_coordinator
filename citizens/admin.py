from datetime import timedelta

import django.contrib.auth.models
from django.contrib import admin
from django.db.models import Q
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, RelatedOnlyDropdownFilter)
from easy_select2 import select2_modelform

from education_centers.models import EducationCenter
from federal_empl_program.models import Application
from users.models import User

from .models import Citizen, DisabilityType, School

ApplicationForm = select2_modelform(Application, attrs={'width': '400px'})

class ApplicationInline(admin.StackedInline):
    model = Application
    form = ApplicationForm
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

@admin.register(DisabilityType)
class DisabilityTypeAdmin(admin.ModelAdmin):
    pass

CitizenForm = select2_modelform(Citizen, attrs={'width': '400px'})

@admin.register(Citizen)
class CitizensAdmin(admin.ModelAdmin):
    form = CitizenForm
    search_fields = ['phone_number','email','snils_number','first_name','middle_name','last_name']
    list_filter = ('social_status', 'is_verified')
    list_display = ('__str__', 'snils_number', 'email')
    readonly_fields = ['get_is_employed_history', 'get_self_employed_history']
    inlines = [
        ApplicationInline, 
    ]
    fieldsets = (
        (None, {
            'fields': ('last_name', 'first_name', 'middle_name', 'user','birthday', 'sex', 'snils_number', 'inn_number')
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
                queryset = Citizen.objects.filter(Q(POE_applications__in=applications) | Q(social_status='SCHS'))
                
                return queryset
        return queryset



SchoolForm = select2_modelform(School, attrs={'width': '400px'})

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    form = SchoolForm
    search_fields = ['name', 'inn', 'city', 'adress', 'specialty', 'school_coordinators__email']
    list_filter = (
        ('city', DropdownFilter),
        ('school_coordinators', RelatedOnlyDropdownFilter)
    )
    list_display = ('name', 'inn', 'adress', 'territorial_administration', 'municipality')
    filter_horizontal = ("school_coordinators",)
    fieldsets = (
        (None, {
            'fields': (
                "name",
                "specialty"
            ),
        }),
        ("Местоположение",{
            'fields': (
                "territorial_administration",
                "city",
                "adress",
                "inn"
            ),
        }),
        ("Билет в будущее", {
            'fields': (
                "school_coordinators",
            )
        }),
    )

CitizenForm = select2_modelform(Citizen, attrs={'width': '400px'})

class CitizenInline(admin.TabularInline):
    model = Citizen
    form = CitizenForm
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