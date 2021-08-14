from django.contrib import admin
from django.contrib.auth.models import User
import django.contrib.auth.models
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import Workshop, EducationCenter, EducationProgram, Competence, Group
from federal_empl_program.models import Application

# Register your models here.
class WorkshopInline(admin.TabularInline):
    model = Workshop

@admin.register(EducationCenter)
class EducationCentersAdmin(admin.ModelAdmin):
    filter_horizontal = ('competences',)
    inlines = [
        WorkshopInline,
    ]

class EducationProgramInline(admin.TabularInline):
    model = EducationProgram
    
@admin.register(Competence)
class CompetencesAdmin(admin.ModelAdmin):
    inlines = [
        EducationProgramInline,
    ]

@admin.register(EducationProgram)
class EducationProgramAdmin(admin.ModelAdmin):
    list_display = ['program_name', 'program_type', 'duration', 'competence']
    list_filter = ['program_type', 'duration', 'competence']

class StudentsInline(admin.StackedInline):
    model = Application
    fields = ('applicant',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    inlines = [
        StudentsInline, 
    ]
    list_filter = ('education_program__competence',)
    search_fields = ['name', 'start_date', 'end_date']
    list_display = ('name', 'education_period', 'workshop_link', 'competence')
    
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        sp_group = django.contrib.auth.models.Group.objects.filter(name='Специалист по работе с клиентами')
        cl_group = django.contrib.auth.models.Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], username=request.user.username)) != 0:
                education_centers = EducationCenter.objects.filter(contact_person=request.user)
                if len(education_centers) != 0:  
                    workshops = Workshop.objects.filter(education_center=education_centers[0])        
                    queryset = Group.objects.filter(workshop__in=workshops)
                    return queryset
        return queryset