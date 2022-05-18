from django.contrib.admin.filters import SimpleListFilter
from users.models import User
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import TextInput
from django.db import models

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import  RelatedDropdownFilter, ChoiceDropdownFilter, RelatedOnlyDropdownFilter
from field_history.models import FieldHistory

from .models import Application, Questionnaire, InteractionHistory, CitizenCategory
from education_centers.models import EducationCenter, EducationProgram
from users.models import Group

from datetime import datetime, timedelta


QuestionnaireForm = select2_modelform(Questionnaire, attrs={'width': '400px'})

class QuestionnaireInline(admin.StackedInline):
    form = QuestionnaireForm
    model = Questionnaire

InteractionHistoryForm = select2_modelform(InteractionHistory, attrs={'width': '400px'})

class InteractionHistoryInLine(admin.TabularInline):
    model = InteractionHistory
    form = InteractionHistoryForm
    classes = ['collapse']
    ordering = ("-id",)
    fields = ['interaction_date', 'comunication_type', 'short_description']
    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra

@admin.register(CitizenCategory)
class CitizenCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "short_name",
        "official_name"
    )

ApplicationForm = select2_modelform(Application, attrs={'width': '400px'})

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationForm
    inlines = [InteractionHistoryInLine, QuestionnaireInline]

    readonly_fields = ['get_applicant', 'get_history', 'id', 'get_phone', 'get_email']

    fieldsets = (
        (None, {
            'fields': ('get_applicant', 'id', 'get_phone', 'get_email')
        }),
        ('Работа с заявкой', {
            'fields': ('citizen_consultant', 'admit_status', 'appl_status', 
            'citizen_category', 'competence', 'education_program', 'education_center', 'ed_ready_time',
            'ed_center_group', 'group', 'is_enrolled', 'is_deducted'),
        }),
        ('Работа по трудоустройству', {
            'classes': ('collapse',),
            'fields': ('empoyment_specialist', 'contract_type', 'is_working', 'find_work', 'get_history', 'employer'),
        }),
    )

    def get_applicant(self, application):
        applicant_url = reverse("admin:citizens_citizen_change", args=[application.applicant.id])
        applicant_name = application.applicant
        applicant_link = f'<a href="{applicant_url}">{applicant_name}</a>'
        return mark_safe(applicant_link)
    get_applicant.short_description = 'Заявитель'
    get_applicant.admin_order_field = 'applicant__last_name'

    def get_phone(self, application):
        phone = application.applicant.phone_number
        return phone
    get_phone.short_description='Телефон'

    def get_email(self, application):
        email = application.applicant.email
        return email
    get_email.short_description='Email'

    def get_comment(self, application):
        comment = InteractionHistory.objects.filter(application=application).latest().short_description
        return comment
    get_comment.short_description='Последний комментарий'
        
    def get_comment_date(self, application):
        comment = InteractionHistory.objects.filter(application=application).latest().interaction_date
        return comment
    get_comment_date.short_description='Дата комментария'

    def get_history(self, application):
        history = application.field_history.latest('date_created').date_created + timedelta(hours=4)
        return history.strftime('%d/%m/%y %H:%M') 
    get_history.short_description='Дата последнего изменения'

    search_fields = ['applicant__phone_number','applicant__email','applicant__snils_number',
    'applicant__first_name','applicant__middle_name','applicant__last_name', 'id']
    actions = ['allow_applications']

    list_display = (
        'id',
        'applicant', 
        'appl_status', 
        'citizen_category',
        'creation_date',
        'contract_type',
        'competence',
        'get_phone',
        'get_comment',
        'get_comment_date'
    )
    def get_form(self, request, obj=None, **kwargs):
        form = super(ApplicationAdmin, self).get_form(request, obj, **kwargs)
        cl_group = Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) == 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) == 0:
                form.base_fields['citizen_category'].widget.attrs['style'] = 'width: 55em;'
                form.base_fields['education_program'].widget.attrs['style'] = 'width: 75em;'
                form.base_fields['education_center'].widget.attrs['style'] = 'width: 75em;'
        return form

    list_filter = (
        ('citizen_consultant', RelatedOnlyDropdownFilter),
        ('admit_status', ChoiceDropdownFilter), 
        ('appl_status', ChoiceDropdownFilter),
        ('competence', RelatedOnlyDropdownFilter),
        ('education_program', RelatedOnlyDropdownFilter),
        ('education_center', RelatedOnlyDropdownFilter),
        ('citizen_category', ChoiceDropdownFilter),
        ('ed_ready_time',ChoiceDropdownFilter),
        ('group', RelatedOnlyDropdownFilter),
        ('contract_type', ChoiceDropdownFilter),
        ('ed_center_group', ChoiceDropdownFilter),
    )

    def allow_applications(self, request, queryset):
        queryset.update(appl_status='ADM')
        queryset.update(admit_status='ADM')
    allow_applications.short_description='Изменить статус на допущен к обучению'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        cl_group = Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                education_centers = EducationCenter.objects.filter(contact_person=request.user)
                return queryset.filter(education_center__in=education_centers)
        return queryset
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        group = Group.objects.filter(name='Специалист по работе с клиентами')
        if (db_field.name == "citizen_consultant") and (len(group) != 0):
            kwargs["queryset"] = User.objects.filter(groups=group[0])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
           
    def get_readonly_fields(self, request, obj=None):
        cl_group = Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                return self.readonly_fields + [
                    'citizen_consultant','admit_status', 'appl_status', 
                    'citizen_category', 'competence', 'education_program', 'education_center',
                    'group', 'is_enrolled', 'is_deducted', 'education_document', 'pasport', 'resume', 'worksearcher_certificate',
                    'consent_pers_data', 'workbook', 'unemployed_certificate', 'senior_certificate',
                    'parental_leave_confirm','birth_certificate', 'birth_certificate_undr_seven', 
                    'notIP_certificate', 'empoyment_specialist', 'contract_type', 'is_working', 'find_work', 'get_history', 'employer',
                    'ed_ready_time'
                ]
        return self.readonly_fields