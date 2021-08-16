from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.utils.safestring import mark_safe
from django.urls import reverse

from django_admin_listfilter_dropdown.filters import  RelatedOnlyDropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter

from .models import Workshop, EducationCenter, EducationProgram, Competence, Group, EducationCenterGroup
from federal_empl_program.models import Application
from users.models import User
import users

# Register your models here.
class WorkshopInline(admin.TabularInline):
    model = Workshop

@admin.register(EducationCenter)
class EducationCentersAdmin(admin.ModelAdmin):
    filter_horizontal = ('competences',)
    inlines = [
        WorkshopInline,
    ]
    search_fields = ['name',]
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        cl_group = users.models.Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                queryset = EducationCenter.objects.filter(contact_person=request.user)
                return queryset
        return queryset

class EducationProgramInline(admin.TabularInline):
    model = EducationProgram
    
@admin.register(Competence)
class CompetencesAdmin(admin.ModelAdmin):
    list_filter = ('block', 'competence_stage', 'competence_type')
    search_fields = ['title']
    list_display = ['title', 'block', 'competence_stage', 'competence_type']
    inlines = [
        EducationProgramInline,
    ]

@admin.register(EducationProgram)
class EducationProgramAdmin(admin.ModelAdmin):
    list_display = ['program_name', 'program_type', 'duration', 'competence']

    list_filter = (
        ('program_type'),
        ('duration'),
        ('competence', RelatedOnlyDropdownFilter)
    )
    search_fields = ['program_name',]


class StudentsInline(admin.StackedInline):
    model = Application
    fields = ('applicant',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    inlines = [
        StudentsInline, 
    ]
    list_filter = (
        ('education_program__competence', RelatedOnlyDropdownFilter),
        ('education_program', RelatedOnlyDropdownFilter),
        ('workshop__education_center', RelatedOnlyDropdownFilter),
        ('workshop', RelatedOnlyDropdownFilter)
    )
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
        cl_group = users.models.Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                education_centers = EducationCenter.objects.filter(contact_person=request.user)
                if len(education_centers) != 0:  
                    workshops = Workshop.objects.filter(education_center=education_centers[0])        
                    queryset = Group.objects.filter(workshop__in=workshops)
                    return queryset
        return queryset
    
    @admin.register(EducationCenterGroup)
    class EducationCenterGroupAdmin(admin.ModelAdmin):
        list_filter = (
            ('education_center', RelatedOnlyDropdownFilter),
            ('competence', RelatedOnlyDropdownFilter),
            ('program', RelatedOnlyDropdownFilter),
            ('start_date'),
            ('end_date')
        )
        search_fields = ['education_center', 'competence', 'program', 'start_date', 'end_date']
        list_display = ('education_center', 'competence', 'program', 'education_period')
        fieldsets = (
            (None, {
                'fields': ('education_center', 'competence', 'program')
            }),
            ('Размер группы', {
                'fields': ('min_group_size', 'max_group_size')
            }),
            ('Период', {
                'fields': ('start_date', 'end_date', 'study_period', 'study_days_count', 'ed_schedule_link'),
            }),
            ('Express', {
                'fields': ('group',),
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