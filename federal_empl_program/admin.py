from django.contrib import admin

from django.db.models import Sum

from django.urls import reverse
from django.utils.safestring import mark_safe
from django_admin_listfilter_dropdown.filters import RelatedOnlyDropdownFilter, DropdownFilter
from easy_select2 import select2_modelform
from rangefilter.filters import DateRangeFilterBuilder

from education_centers.models import EducationCenter, EducationProgram
from federal_empl_program import exports
from users.models import Group, User

from .models import (
    Application, CitizenApplication, 
    CitizenCategory, ClosingDocument, 
    EmploymentInvoice, FlowStatus, ProjectYear, ApplStatus
)


@admin.register(ApplStatus)
class ApplStatusAdmin(admin.ModelAdmin):
    pass

#@admin.register(Profstandart)
class ClosingDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'mintrud_order_date',
        'mintrud_order_number',
        'minust_order_date',
        'minust_order_number'
    ]


#@admin.register(Contract)
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
        check_wrk_status = FlowStatus.objects.get(off_name='Ожидаем трудоустройства')
        find_wrk_status = FlowStatus.objects.get(off_name='Трудоустроен')
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
        'created_at',
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
    list_filter = (

        ("created_at", DateRangeFilterBuilder()),
    )

#@admin.register(EdCenterEmployeePosition)
class EdCenterEmployeePositionnAdmin(admin.ModelAdmin):
    list_display = ['position', 'ed_center']
    search_fields = ['ed_center__name']

#@admin.register(ProjectPosition)
class ProjectPositionAdmin(admin.ModelAdmin):
    pass

#@admin.register(FlowStatus)
class FlowStatusAdmin(admin.ModelAdmin):
    list_display = ['off_name', 'is_rejected']


#@admin.register(ProfField)
class ProfFieldAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']



@admin.register(ProjectYear)
class ProjectYearAdmin(admin.ModelAdmin):
    pass

#@admin.register(EducationCenterProjectYear)
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


#@admin.register(NetworkAgreement)
class NetworkAgreementAdmin(admin.ModelAdmin):
    list_display = ['get_ed_center', 'get_number', 'is_agreement_file_upload']
    search_fields = [
        'ed_center_year__ed_center__name', 
        'ed_center_year__ed_center__flow_name',
        'ed_center_year__ed_center__short_name',
        'agreement_number'
    ]


    def get_ed_center(self, agreement):
        if agreement.ed_center_year.ed_center.flow_name == "" or agreement.ed_center_year.ed_center.flow_name is None:
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
        'get_programs_archive',
        'get_irpo_programs_archive',
        'get_programs_list',
        'get_programs_w_people_list',
        'get_programs_w_workshops_list'
    ]
    def download_archive(self, request, queryset):
        return exports.net_agreements_archives(queryset)
    download_archive.short_description='Скачать архив договоров'

    def get_programs_archive(self, request, queryset):
        return exports.net_agreements_archives(queryset, 'programs')
    get_programs_archive.short_description='Скачать архив программ'

    def get_irpo_programs_archive(self, request, queryset):
        return exports.net_agreements_archives(queryset, 'irpo_programs')
    get_irpo_programs_archive.short_description='Скачать архив документов для ИРПО'

    def get_programs_list(self, request, queryset):
        return exports.programs(queryset)
    get_programs_list.short_description='Скачать перечень программ'


    def get_programs_w_people_list(self, request, queryset):
        return exports.programs_w_people(queryset)
    get_programs_w_people_list.short_description='Скачать кадровое обеспечение'
    
    def get_programs_w_workshops_list(self, request, queryset):
        return exports.programs_w_workshops(queryset)
    get_programs_w_workshops_list.short_description='Скачать обеспечение МТО'



#@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    pass


#@admin.register(EmploymentInvoice)
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
    
    readonly_fields = ['get_applicant', 'get_phone', 'get_email']

    fieldsets = (
        (None, {
            'fields': ('get_applicant', 'atlas_id', 'project_year', 'get_phone', 'get_email')
        }),
        ('Работа с заявкой', {
            'fields': ('citizen_category','education_program', 
                       'education_center', 'group', 'status', 'atlas_status', 'rvr_status'
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

    def get_empl(self, application):
        amount = round(application.price * 0.3, 2)
        return amount
    get_empl.short_description='30%'


    search_fields = ['applicant__phone_number','applicant__email','applicant__snils_number',
    'applicant__first_name','applicant__middle_name','applicant__last_name', 'id']
    

    list_display = [
        'applicant',
        'status',
        'group',       
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
    #autocomplete_list_filter = ('education_center', 'education_program', 'group', 'competence')
    list_filter = (
        ('status', RelatedOnlyDropdownFilter),
        ('atlas_status', DropdownFilter),
        ('rvr_status', DropdownFilter),
        ('education_program', RelatedOnlyDropdownFilter),
        ('group', RelatedOnlyDropdownFilter)
    )

    def get_queryset(self, request):
        project_year = ProjectYear.objects.get(year=2024)
        queryset = super().get_queryset(request).filter(project_year=project_year)
        return queryset
