from datetime import datetime, timedelta
import math
from pickle import TRUE

from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.db import models
from django.db.models import Avg, Sum
from django.db.models.functions import Coalesce
from django.forms import TextInput
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_admin_listfilter_dropdown.filters import (
    ChoiceDropdownFilter, DropdownFilter, RelatedDropdownFilter,
    RelatedOnlyDropdownFilter)
from easy_select2 import select2_modelform
from field_history.models import FieldHistory

from education_centers.models import EducationCenter, EducationProgram
from federal_empl_program import exports
from users.models import Group, User

from .models import (Application, CitizenApplication, CitizenCategory, ClosingDocument, Contract,
                     EdCenterEmployeePosition, EdCenterQuotaRequest,
                     EducationCenterProjectYear, EmploymentInvoice, FlowStatus, Grant, Indicator, NetworkAgreement,
                     ProgramQuotaRequest, ProjectPosition, ProjectYear,
                     QuotaRequest)


check_wrk_status = FlowStatus.objects.get(off_name='Ожидаем трудоустройства')
find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')

@admin.register(ClosingDocument)
class ClosingDocumentAdmin(admin.ModelAdmin):
    list_filter = [
        'doc_type',
        'is_paid'
    ]

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = [
        'number',
        'get_name',
        'get_applications_count'
    ]

    def get_name(self, contract):
        return contract.ed_center.ed_center.flow_name
    get_name.short_description='ЦО'

    def get_applications_count(self, contract):
        return Application.objects.filter(
            flow_status__in=[find_wrk_status, check_wrk_status],
            contract=contract).count()
    get_applications_count.short_description='Колво слушателей'


#@admin.register(ProgramQuotaRequest)
class ProgramQuotaRequestAdmin(admin.ModelAdmin):
    pass

@admin.register(CitizenApplication)
class CitizenApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'last_name', 
        'first_name',
        'middle_name',
        'consultation',
        'email',
        'phone_number',
        'competence',
        'education_type',
        'employment_status',
        'planned_employment',
        'practice_time'
    ]
    search_field = [
        'last_name', 
        'first_name',
        'middle_name',
        'email',
        'phone_number',
        'competence',
    ]

#@admin.register(EdCenterEmployeePosition)
class EdCenterEmployeePositionnAdmin(admin.ModelAdmin):
    list_display = ['position', 'ed_center']
    search_fields = ['ed_center__name']

#@admin.register(ProjectPosition)
class ProjectPositionAdmin(admin.ModelAdmin):
    pass

@admin.register(FlowStatus)
class FlowStatusAdmin(admin.ModelAdmin):
    list_display = ['off_name', 'is_rejected']


@admin.register(ProjectYear)
class ProjectYearAdmin(admin.ModelAdmin):
    pass

@admin.register(EducationCenterProjectYear)
class EducationCenterProjectYearAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'count_pay', 'is_federal']
    search_fields = ['ed_center__name', 'ed_center__flow_name', 'ed_center__short_name']

    def get_name(self, center_year):
        if center_year.ed_center.flow_name == "":
             return center_year.ed_center.name
        return center_year.ed_center.flow_name
    get_name.short_description='ЦО'

    def count_pay(self, center_year):
        education_sum = ClosingDocument.objects.filter(
            group__education_program__ed_center=center_year.ed_center
        ).aggregate(sum_ammount=Sum('bill_sum'))['sum_ammount']
        if education_sum == None:
            education_sum = 0
        employment_sum = EmploymentInvoice.objects.filter(contract__ed_center=center_year).aggregate(sum_ammount=Sum('amount'))['sum_ammount'] 
        if employment_sum == None:
            employment_sum = 0
        return round(education_sum + employment_sum, 2)
    count_pay.short_description='Оплачено'

    actions = ['scratch_steps_check',]

    def scratch_steps_check(self, request, queryset):
        queryset.update(
            step_1_check=False,
            step_2_check=False,
            step_3_check=False,
            step_4_check=False,
            step_5_check=False,
            step_6_check=False
        )
    scratch_steps_check.short_description='Снять проверку этапов'


@admin.register(NetworkAgreement)
class NetworkAgreementAdmin(admin.ModelAdmin):
    list_display = ['get_ed_center', 'get_number', 'is_agreement_file_upload']
    search_fields = [
        'ed_center_year__ed_center__name', 
        'ed_center_year__ed_center__flow_name',
        'ed_center_year__ed_center__short_name',
        'agreement_number'
    ]


    def get_ed_center(self, agreement):
        if agreement.ed_center_year.ed_center.flow_name == "":
            return agreement.ed_center_year.ed_center.name
        return agreement.ed_center_year.ed_center.flow_name
    get_ed_center.short_description='ЦО'

    def get_number(self, agreement):
        if agreement.suffix is None:
            return f'{agreement.agreement_number}/СЗ'
        return f'{agreement.agreement_number}/СЗ{agreement.suffix}'
    get_number.short_description='Номер'
    get_number.admin_order_field = 'agreement_number'

    def is_agreement_file_upload(self, agreement):
        if agreement.agreement_file.name == "":
            return "Нет"
        return "Да"
    is_agreement_file_upload.short_description='Договор подгружен?'

    actions = [
        'download_archive', 
        'get_programs_list',
        'get_programs_w_people_list'
    ]
    def download_archive(self, request, queryset):
        return exports.net_agreements(queryset)
    download_archive.short_description='Скачать архив договоров'

    def get_programs_list(self, request, queryset):
        return exports.programs(queryset)
    get_programs_list.short_description='Скачать перечень программ'

    def get_programs_w_people_list(self, request, queryset):
        return exports.programs_w_people(queryset)
    get_programs_w_people_list.short_description='Скачать кадровое обеспечение'
    



#@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    pass


@admin.register(EmploymentInvoice)
class EmploymentInvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(CitizenCategory)
class CitizenCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "short_name",
        "official_name"
    )
    list_filter = (
        ('project_year', RelatedOnlyDropdownFilter),
    )

ApplicationForm = select2_modelform(Application, attrs={'width': '400px'})


#@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = [
        'project_year', 
        'grant_name', 
        'qouta_72', 
        'qouta_144', 
        'qouta_256'
    ]

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationForm
    
    readonly_fields = ['get_applicant', 'id', 'get_phone', 'get_email', 'get_city']

    fieldsets = (
        (None, {
            'fields': ('get_applicant', 'id', 'project_year', 'get_phone', 'get_email', 'get_city')
        }),
        ('Работа с заявкой', {
            'fields': ('flow_status', 'citizen_category',
                        'competence', 'education_program', 'education_center',
                        'group', 'price'
                    ),
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

    def get_empl(self, application):
        amount = round(application.price * 0.3, 2)
        return amount
    get_empl.short_description='30%'

    def get_center(self, application):
        if application.education_center == None:
            return "-"
        center_url = reverse("admin:education_centers_educationcenter_change",
                              args=[application.education_center.id])
        flow_name = application.education_center.flow_name
        enter_link = f'<a href="{center_url}">{flow_name}</a>'
        return mark_safe(enter_link)
    get_center.short_description = 'ЦО'
    get_center.admin_order_field = 'education_center__flow_name'

    search_fields = ['applicant__phone_number','applicant__email','applicant__snils_number',
    'applicant__first_name','applicant__middle_name','applicant__last_name', 'id', 'education_center__flow_name', 'flow_id']
    

    list_display = [
        'applicant',
        'csn_prv_date',
        'flow_status',
        'get_center',
        'citizen_category',
        'group',
        'added_to_act',
        'get_empl'
        
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
        ('project_year', RelatedOnlyDropdownFilter),
        ('flow_status', RelatedOnlyDropdownFilter),
        ('citizen_category', RelatedOnlyDropdownFilter),
        'added_to_act'
    )
    
    #actions = ['allow_applications', 'get_job', 'get_jobless', 'get_paid', 'get_paid_part', 'cancel_payment']
    def allow_applications(self, request, queryset):
        queryset.update(appl_status='ADM')
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
                    'citizen_consultant', 'appl_status', 'citizen_category',
                    'competence', 'education_program', 'education_center',
                    'group', 'education_document','pasport', 'worksearcher_certificate',
                    'consent_pers_data', 'workbook', 'unemployed_certificate',
                    'senior_certificate', 'parental_leave_confirm',
                    'birth_certificate', 'birth_certificate_undr_seven',
                    'contract_type', 'is_working', 'find_work',
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