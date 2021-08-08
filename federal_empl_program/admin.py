from django.contrib.admin.filters import SimpleListFilter
from users.models import User
import django.contrib.auth.models
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import Application, Questionnaire, InteractionHistory
from education_centers.models import EducationCenter
from users.models import Group

from django_admin_listfilter_dropdown.filters import  DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter
from field_history.models import FieldHistory
from datetime import datetime, timedelta

@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    pass

class QuestionnaireInline(admin.StackedInline):
    model = Questionnaire

class InteractionHistoryInLine(admin.TabularInline):
    model = InteractionHistory
    classes = ['collapse']
    ordering = ("-id",)
    fields = ['interaction_date', 'comunication_type', 'short_description']
    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    inlines = [InteractionHistoryInLine, QuestionnaireInline]

    readonly_fields = ['get_applicant', 'get_history', 'legacy_id', 'get_phone', 'get_email']
    fieldsets = (
        (None, {
            'fields': ('get_applicant', 'legacy_id', 'get_phone', 'get_email')
        }),
        ('Работа с заявкой', {
            'fields': ('citizen_consultant', 'admit_status', 'appl_status', 
            'category', 'competence', 'education_program', 'education_center',
            'group', 'is_enrolled', 'is_deducted'),
        }),
        ('Документы', {
            'fields': ('education_document', 'pasport', 'resume', 'worksearcher_certificate',
            'consent_pers_data', 'workbook', 'unemployed_certificate', 'senior_certificate',
            'parental_leave_confirm','birth_certificate', 'birth_certificate_undr_seven', 
            'notIP_certificate'),
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

    def get_history(self, application):
        history = application.field_history.latest('date_created').date_created + timedelta(hours=4)
        return history.strftime('%d/%m/%y %H:%M') 
    get_history.short_description='Дата последнего изменения'

    search_fields = ['applicant__phone_number','applicant__email','applicant__snils_number',
    'applicant__first_name','applicant__middle_name','applicant__last_name', 'legacy_id']
    actions = ['allow_applications']

    list_display = (
        'legacy_id',
        'applicant', 
        'appl_status', 
        'category',
        'creation_date'
    )

    list_filter = (
        ('citizen_consultant', RelatedDropdownFilter),
        ('admit_status', ChoiceDropdownFilter), 
        ('appl_status', ChoiceDropdownFilter),
        ('competence', RelatedDropdownFilter),
        ('education_program', RelatedDropdownFilter),
        ('education_center', RelatedDropdownFilter),
        ('category', ChoiceDropdownFilter),
        ('group', RelatedDropdownFilter),
        ('contract_type', ChoiceDropdownFilter), 
    )

    def allow_applications(self, request, queryset):
        queryset.update(appl_status='ADM')
        queryset.update(admit_status='ADM')
    allow_applications.short_description='Изменить статус на допущен к обучению'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        cl_group = Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], username=request.user.username)) != 0:
                education_centers = EducationCenter.objects.filter(contact_person=request.user)
                return queryset.filter(education_center__in=education_centers)
        return queryset
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        group = Group.objects.filter(name='Специалист по работе с клиентами')
        if (db_field.name == "citizen_consultant") and (len(group) != 0):
            kwargs["queryset"] = User.objects.filter(groups=group[0])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class CustomFilter(SimpleListFilter):
        template = 'django_admin_listfilter_dropdown/dropdown_filter.html'

        def queryset(self, request, queryset):
            group = Group.objects.filter(name='Специалист по работе с клиентами')
            users = User.objects.filter(groups=group[0])
            return queryset(citizen_consultant__in = users)
