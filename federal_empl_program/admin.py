from pickle import TRUE
from django.contrib.admin.filters import SimpleListFilter
from users.models import User
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import TextInput
from django.db import models

from django.db.models import Sum, Avg
from django.db.models.functions import Coalesce
from djaa_list_filter.admin import (
    AjaxAutocompleteListFilterModelAdmin,
)
from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import  RelatedDropdownFilter, ChoiceDropdownFilter, RelatedOnlyDropdownFilter, DropdownFilter
from field_history.models import FieldHistory

from .models import Application, Questionnaire, InteractionHistory, CitizenCategory, CategoryInstruction, Grant
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


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = ['grant_name', 'qoute_72', 'qoute_144', 'qoute_256']

@admin.register(Application)
class ApplicationAdmin(AjaxAutocompleteListFilterModelAdmin):
    form = ApplicationForm
    inlines = [InteractionHistoryInLine, QuestionnaireInline]
    
    readonly_fields = ['get_applicant', 'get_history', 'id', 'get_phone', 'get_email', 'get_city']

    fieldsets = (
        (None, {
            'fields': ('get_applicant', 'id', 'get_phone', 'get_email', 'get_city')
        }),
        ('Работа с заявкой', {
            'fields': ('resume', 'admit_status', 'appl_status', 'change_status_date', 
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

    def get_city(self, application):
        city = application.applicant.res_city
        return city
    get_city.short_description='Город'

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
    

    list_display = [
        'applicant',
        'is_working',
        'payment',
        'payment_amount',
        'education_program',
        'grant'
    ]
    list_totals = ['payment_amount',]
    def get_form(self, request, obj=None, **kwargs):
        form = super(ApplicationAdmin, self).get_form(request, obj, **kwargs)
        cl_group = Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) == 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) == 0:
                form.base_fields['citizen_category'].widget.attrs['style'] = 'width: 55em;'
                form.base_fields['education_program'].widget.attrs['style'] = 'width: 75em;'
                form.base_fields['education_center'].widget.attrs['style'] = 'width: 75em;'
        return form
    autocomplete_list_filter = ('education_center', 'education_program', 'group', 'competence')
    list_filter = (
        ('group__start_date', DropdownFilter),
        ('group__end_date', DropdownFilter),
        ('citizen_consultant', RelatedOnlyDropdownFilter),
        ('appl_status', ChoiceDropdownFilter),
        ('citizen_category', RelatedOnlyDropdownFilter)
    )
    
    actions = ['allow_applications', 'get_job', 'get_jobless', 'get_paid', 'get_paid_part', 'cancel_payment']
    def allow_applications(self, request, queryset):
        queryset.update(appl_status='ADM')
        queryset.update(admit_status='ADM')
    allow_applications.short_description='Изменить статус на допущен к обучению'

    def get_job(self, request, queryset):
        queryset.update(is_working=True)
    get_job.short_description='Трудоустроить'

    def get_jobless(self, request, queryset):
        queryset.update(is_working=False)
    get_jobless.short_description='Уволить'

    def get_paid(self, request, queryset):
        full_payment = queryset.filter(is_working=True, group__is_new_price=False)
        full_payment.update(payment="PF")
        full_payment_72 = full_payment.filter(education_program__duration=72)
        full_payment_72.update(payment_amount=23000)
        full_payment_144 = full_payment.filter(education_program__duration=144)
        full_payment_144.update(payment_amount=46000)
        full_payment_256 = full_payment.filter(education_program__duration=256)
        full_payment_256.update(payment_amount=92000)
        full_payment = queryset.filter(is_working=True, group__is_new_price=True)
        full_payment.update(payment="PFN")
        full_payment_72 = full_payment.filter(education_program__duration=72)
        full_payment_72.update(payment_amount=16100)
        full_payment_144 = full_payment.filter(education_program__duration=144)
        full_payment_144.update(payment_amount=32200)
        full_payment_256 = full_payment.filter(education_program__duration=256)
        full_payment_256.update(payment_amount=64400)
        part_payment = queryset.filter(is_working=False, group__is_new_price=False)
        part_payment.update(payment="PP")
        part_payment_72 = part_payment.filter(education_program__duration=72)
        part_payment_72.update(payment_amount=16100)
        part_payment_144 = part_payment.filter(education_program__duration=144)
        part_payment_144.update(payment_amount=32200)
        part_payment_256 = part_payment.filter(education_program__duration=256)
        part_payment_256.update(payment_amount=64400)
        part_payment = queryset.filter(is_working=False, group__is_new_price=True)
        part_payment.update(payment="PPN")
        part_payment_72 = part_payment.filter(education_program__duration=72)
        part_payment_72.update(payment_amount=11270)
        part_payment_144 = part_payment.filter(education_program__duration=144)
        part_payment_144.update(payment_amount=22540)
        part_payment_256 = part_payment.filter(education_program__duration=256)
        part_payment_256.update(payment_amount=45080)
    get_paid.short_description='Оплатить'

    def cancel_payment(self, request, queryset):
        queryset.update(payment="DP")
        queryset.update(payment_amount=0)
    cancel_payment.short_description='Отменить оплату'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        cl_group = Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                education_centers = EducationCenter.objects.filter(contact_person=request.user)
                return queryset.filter(education_center__in=education_centers)
        return queryset.exclude(appl_status='NCOM')
    
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

    def changelist_view(self, request, extra_context=None):
        request_get = request.GET
        total = Application.objects.all()
        for query in request_get.dict():
            try:
                query = f'{query}={request_get[query]}'
                total = total.filter(query)
            except:
                print(query)
        total = total.aggregate(total=Sum('payment_amount'))['total']
        context = {
            'total': total,
        }
        return super(ApplicationAdmin, self).changelist_view(request, extra_context=context)


@admin.register(CategoryInstruction)
class CategoryInstructionAdmin(admin.ModelAdmin):
    pass