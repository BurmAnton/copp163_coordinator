import math

from django.core.cache import cache
from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from field_history.tracker import FieldHistoryTracker
from django.db.models import Max, Sum

from citizens.models import Citizen
from education_centers.models import (Competence, EducationCenter,
                                      EducationProgram, Employee, Group, Teacher)
from users.models import User


class ProjectYear(models.Model):
    year = models.IntegerField(_('year'), null=False, blank=False)
    programs = models.ManyToManyField(
        EducationProgram,
        verbose_name="Программы",
        related_name="project_years",
        blank=True
    )
    price_72 = models.IntegerField("Стоимость 72", default=27435)
    price_144 = models.IntegerField("Стоимость 144", default=40920)
    price_256 = models.IntegerField("Стоимость 256", default=61380)
    full_budget = models.IntegerField("Бюджет", default=49850840)
    appls_last_update = models.DateTimeField(
        "Дата последнего обновления заявок", blank=True, null=True)

    def __str__(self):
        return  str(self.year)

    class Meta:
        verbose_name = "Год проекта"
        verbose_name_plural = "Годы проекта"


class EducationCenterProjectYear(models.Model):
    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения",
        related_name="project_years",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    project_year = models.ForeignKey(
        ProjectYear, 
        verbose_name="Год проекта",
        related_name="ed_centers",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    quota_72 = models.IntegerField("Квота 72", default=0)
    quota_144 = models.IntegerField("Квота 144", default=0)
    quota_256 = models.IntegerField("Квота 256", default=0)
    STAGES = [
        ('FLLNG', "заполнение"),
        ('FLLD', "на проверке"),
        ('RWRK', "отправлен на доработку"),
        ('VRFD', "проверен"),
        ('FRMD', "договор сформирован"),
        ('DWNLD', "договор подгружен"),
        ('PRVD', "договор подписан"),
        ('FNSHD', "ПКО пройден"),
    ]
    stage = models.CharField("Работа с заявкой", max_length=5, 
                             default='FLLNG', choices=STAGES)
    appl_docs_link = models.TextField('Ссылка на комп. документов', default="")
    step_1_check = models.BooleanField("Шаг 1. Проверка", default=False)
    step_1_commentary = models.TextField(
        "Шаг 1. Комментарий", null=True, blank=True, default=""
    )
    step_2_check = models.BooleanField("Шаг 2. Проверка", default=False)
    step_2_commentary = models.TextField(
        "Шаг 2. Комментарий", null=True, blank=True, default=""
    )
    step_3_check = models.BooleanField("Шаг 3. Проверка", default=False)
    step_3_commentary = models.TextField(
        "Шаг 3. Комментарий", null=True, blank=True, default=""
    )
    step_4_check = models.BooleanField("Шаг 4. Проверка", default=False)
    step_4_commentary = models.TextField(
        "Шаг 4. Комментарий", null=True, blank=True, default=""
    )
    step_5_check = models.BooleanField("Шаг 5. Проверка", default=False)
    step_5_commentary = models.TextField(
        "Шаг 5. Комментарий", null=True, blank=True, default=""
    )
    step_6_check = models.BooleanField("Шаг 6. Проверка", default=False)
    step_6_commentary = models.TextField(
        "Шаг 6. Комментарий", null=True, blank=True, default=""
    )
    is_federal = models.BooleanField("Федеральный центр", default=False)

    def __str__(self):
        return  f'{self.ed_center} ({self.project_year.year} г.)'
   
    def save(self, *args, **kwargs):
        super(EducationCenterProjectYear, self).save(*args, **kwargs)
        #cache.clear()

    class Meta:
        verbose_name = "Данные колледжа на год"
        verbose_name_plural = "Данные колледжей на годы"


def number_agreement(agreement):
    agreements_count = NetworkAgreement.objects.all().aggregate(max_number=Max('agreement_number'))
    if agreement.agreement_number == 0:
        agreement.agreement_number = agreements_count['max_number'] + 1
        agreement.save(agreement_number=True)

class NetworkAgreement(models.Model):
    agreement_number = models.IntegerField("№ цикла", default=0)
    suffix = models.CharField(
        "Доп. номер", max_length=10, null=True, blank=True
    )
    ed_center_year = models.ForeignKey(
        EducationCenterProjectYear, 
        verbose_name="Центра обучения (год проекта)",
        related_name="net_agreements",
        null=True, 
        blank=True,
        on_delete=models.CASCADE
    )
    programs = models.ManyToManyField(
        EducationProgram,
        verbose_name="Программы",
        related_name="new_agreements",
        blank=True
    )
    STAGES = [
        ('FLLNG', "заполнение"),
        ('DWNLD', "договор подгружен"),
        ('PRVD', "договор подписан"),
    ]
    stage = models.CharField(
        "Статус договора", max_length=5, 
        default='FLLNG', choices=STAGES
    )
    def agreement_path(instance, filename):
        return f'media/federal_empl/net_agreements/{filename}'
    agreement_file = models.FileField("Договор", null=True, blank=True,  upload_to=agreement_path)

    def __str__(self):
        return f'Договор №{self.agreement_number}'

    class Meta:
        verbose_name = "Сетевой договор"
        verbose_name_plural = "Сетевые договоры"    

    def save(self, agreement_number=False, *args, **kwargs):
        super(NetworkAgreement, self).save(*args, **kwargs)
        if agreement_number == False:
            number_agreement(self)


class QuotaRequest(models.Model):
    project_year = models.ForeignKey(
        ProjectYear, 
        verbose_name="Год проекта",
        related_name="quota_requests",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    request_number = models.IntegerField(
        'Номер запроса', null=False, blank=False)
    STATUS = [
        ('DRFT', "заполнение"),
        ('SND', "отправлена"),
        ('PRVD', "согласована"),
    ]
    status = models.CharField("Работа с запросом", max_length=5, 
                             default='DRFT', choices=STATUS)
    send_date = models.DateField("Дата отправки", null=True, blank=True)
    approval_date = models.DateField(
        "Дата согласования", null=True, blank=True)
    
    def __str__(self):
        return f'Запрос №{self.request_number} ({self.get_status_display()})'

    class Meta:
        verbose_name = "Запрос квоты"
        verbose_name_plural = "Запрос квоты"


class EdCenterQuotaRequest(models.Model):
    request = models.ForeignKey(
        QuotaRequest, 
        verbose_name="Запрос квоты",
        related_name="centers_requests",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    ed_center_year = models.ForeignKey(
        EducationCenterProjectYear, 
        verbose_name="Центра обучения (год проекта)",
        related_name="quota_requests",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    STATUS = [
        ('DRFT', "заполнение"),
        ('LCK', "на проверке"),
        ('SND', "отправлена"),
        ('PRVD', "согласована"),
    ]
    status = models.CharField("Работа с запросом", max_length=5, 
                             default='DRFT', choices=STATUS)
    request_number = models.IntegerField(
        'Номер запроса', null=False, blank=False)
    
    def __str__(self):
        return f'Запрос {self.ed_center_year.ed_center.short_name} №{self.request_number} ({self.get_status_display()})'

    class Meta:
        verbose_name = "Запрос квоты (ЦО)"
        verbose_name_plural = "Запрос квоты (ЦО)"


class ProgramQuotaRequest(models.Model):
    ed_center_request = models.ForeignKey(
        EdCenterQuotaRequest, 
        verbose_name="Запрос квоты (ЦО)",
        related_name="quota_requests",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    program = models.ForeignKey(
        EducationProgram, 
        verbose_name="Программа",
        related_name="quota_requests",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    price = models.IntegerField(
        'Стоимость программы', null=False, blank=False, default=0)
    req_quota = models.IntegerField(
        'Запращиваемая квота', null=False, blank=False, default=0)
    ro_quota = models.IntegerField(
        'Квота (коррекция РО)', null=False, blank=False, default=0)
    approved_quota = models.IntegerField(
        'Квота (согласованная)', null=False, blank=False, default=0)
    
    def __str__(self):
        return f'{self.program.program_name} ({self.ed_center_request.ed_center_year})'

    class Meta:
        verbose_name = "Запрос квоты (программа)"
        verbose_name_plural = "Запрос квоты (программы)"


class Indicator(models.Model):
    project_year = models.ForeignKey(
        ProjectYear, 
        verbose_name="Год проекта",
        related_name="indicators",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    name = models.CharField("Показатель эффективности", max_length=500, 
                            blank=False,null=False)
    is_free_form = models.BooleanField("Свободная форма?", default=False)
    
    def __str__(self):
        return  f'{self.name}'

    class Meta:
        verbose_name = "Показатель эффективности"
        verbose_name_plural = "Показатели эффективности"


class EdCenterIndicator(models.Model):
    indicator = models.ForeignKey(
        Indicator, 
        verbose_name="Показатель",
        related_name="ed_centers",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения",
        related_name="indicators",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    value_2021 = models.CharField("Значение показателя (2021)", max_length=25, 
                            blank=False,null=False)
    value_2022 = models.CharField("Значение показателя (2022)", max_length=25, 
                            blank=False,null=False)
    free_form_value = models.TextField("Значение (свободная форма)", 
                                       null=True, blank=True, default="")

    def __str__(self):
        return  f'{self.indicator} ({self.ed_center})'
    
    class Meta:
        verbose_name = "Показатель эффективности (ЦО)"
        verbose_name_plural = "Показатели эффективности (ЦО)"


class ProjectPosition(models.Model):
    project_year = models.ForeignKey(
        ProjectYear, 
        verbose_name="Год проекта",
        related_name="positions",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    position = models.CharField("Название позиции", max_length=50, blank=False, 
                                null=False)
    is_basis_needed = models.BooleanField("Нужно основание?", default=False)

    def __str__(self):
        return  f'{self.position} ({self.project_year.year} г.)'

    class Meta:
        verbose_name = "Позиция в проекте"
        verbose_name_plural = "Позиции в проекте"


class EdCenterEmployeePosition(models.Model):
    position = models.ForeignKey(
        ProjectPosition, 
        verbose_name="Позиция",
        related_name="positions_employees",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения",
        related_name="positions_employees",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        Employee, 
        verbose_name="Сотрудник",
        related_name="positions",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    acts_basis = models.CharField(
        "Действует на основании", max_length=500, null=True, blank=True
    )
    
    def __str__(self):
        return  f'{self.employee} ({self.position})'

    class Meta:
        verbose_name = "Роль сотрудника"
        verbose_name_plural = "Роли сотрудников"



class CitizenCategory(models.Model):
    short_name = models.CharField("Название", max_length=100, blank=False)
    official_name = models.CharField("Офицальное наименованние", 
                                     max_length=600, blank=True)
    project_year = models.ForeignKey(
        ProjectYear, 
        verbose_name="Год проекта",
        related_name="categories",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    
    def __str__(self):
        return  self.short_name

    class Meta:
        verbose_name = "Категория граждан"
        verbose_name_plural = "Категории граждан"
        

class Grant(models.Model):
    project_year = models.ForeignKey(ProjectYear, verbose_name="Год проекта",
        null=False, blank=False, on_delete=CASCADE)
    grant_name = models.CharField("Название", max_length=100, null=False, 
                                  blank=False)
    qouta_72 = models.IntegerField('Квота 72', null=False, blank=False, 
                                   default=0)
    qouta_144 = models.IntegerField('Квота 144', null=False, blank=False, 
                                   default=0)
    qouta_256 = models.IntegerField('Квота 256', null=False, blank=False, 
                                   default=0)
    
    def __str__(self):
        return f'{self.grant_name} ({self.project_year.year} г.)'

    class Meta:
        verbose_name = "Грант"
        verbose_name_plural = "Гранты"


class FlowStatus(models.Model):
    off_name = models.CharField("Название с flow", max_length=700, null=False)
    name = models.CharField("Название", max_length=700, null=False)
    action = models.TextField("Что делать?", null=False, blank=False)
    is_parent = models.BooleanField("Верхнеуровневый статус", default=False)
    is_rejected = models.BooleanField("Отказной статус", default=False)
    parent_status = models.ForeignKey(
        "self", 
        verbose_name="Родительский статус",
        related_name="children_statuses",
        null=True, 
        blank=True,
        on_delete=CASCADE
    )

    def __str__(self):
        return f'{self.name} ({self.off_name})'

    class Meta:
        verbose_name = "Статус flow"
        verbose_name_plural = "Статусы flow"


class Contract(models.Model):
    number = models.CharField(
        "Номер договора", max_length=100,
        null=False, blank=False
    )
    project_year = models.ForeignKey(
        ProjectYear, 
        verbose_name="Год проекта",
        related_name="contracts",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    ed_center = models.ForeignKey(
        EducationCenterProjectYear,
        verbose_name="ЦО",
        related_name="contracts",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Договор на организацию обучения"
        verbose_name_plural = "Договоры на организацию обучения"
    
    def __str__(self):
        return  f"{self.number} ({self.ed_center.ed_center}, {self.project_year})"


class EmploymentInvoice(models.Model):
    invoice_number = models.CharField("Номер счёта", blank=True, null=True, max_length=50)
    contract = models.ForeignKey(
        Contract,
        verbose_name="договор",
        related_name="empl_invoices",
        null=False,
        blank=False,
        on_delete=CASCADE
    )
    amount = models.FloatField("Сумма оплаты", default=0)
    STAGES = [
        ('GNRT', 'Сгенерирован'),
        ('NVC', 'Подгружен счёт'),
        ('SPD', 'На оплату'),
        ('PD', 'Оплачен')
    ]
    stage = models.CharField("Стадии", max_length=4, choices=STAGES, blank=True, null=True, default="GNRT")
    is_requisted = models.BooleanField("Запросили счёт", default=False)
    def invoice_path(instance, filename):
        return 'media/federal_empl/docs/invoices/employeement/{0}'.format(filename)
    invoice_file = models.FileField("Счёт", blank=True, upload_to=invoice_path)

    class Meta:
        verbose_name = "Счёт (30%)"
        verbose_name_plural = "Счёта (30%)"
    
    def __str__(self):
        return f"№{self.invoice_number} ({self.contract.number})"    


class ApplStatus(models.Model):
    short_name = models.CharField(max_length=50, null=False, blank=False)
    name = models.CharField("Название", max_length=250, null=False, blank=False)
    order = models.IntegerField('Очередь', null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Статус заявки"
        verbose_name_plural = "Статусы заявки"

    def __str__(self):
        return self.name 


class Application(models.Model):
    project_year = models.ForeignKey(
        ProjectYear, 
        verbose_name="Год проекта",
        related_name="applications",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    flow_id = models.IntegerField('Номер заявки', null=True, blank=True)
    atlas_id = models.CharField('Номер заявления на РР', max_length=100, blank=True, null=True)
    flow_status = models.ForeignKey(
        FlowStatus,
        verbose_name="Статус (2023)",
        related_name="applications",
        null=True,
        blank=True,
        on_delete=CASCADE
    )
    added_to_act = models.BooleanField("Актирован", default=False)
    contract = models.ForeignKey(
        Contract, 
        verbose_name="Договор",
        related_name="applications",
        null=True, 
        blank=True,
        on_delete=SET_NULL
    )
    employment_invoice = models.ForeignKey(
        EmploymentInvoice, 
        verbose_name="Счёт (30%)",
        related_name="applications",
        null=True, 
        blank=True,
        on_delete=SET_NULL
    )
    applicant = models.ForeignKey(Citizen, verbose_name="Заявитель", on_delete=CASCADE, related_name='POE_applications')
    creation_date = models.DateTimeField("Дата создания", blank=True, null=True, default=now)
    expiration_date = models.DateField("Дата истечения заявки", blank=True, null=True)
    csn_prv_date = models.DateField("Дата одобрения ЦЗН", blank=True, null=True)
    price = models.IntegerField('Стоимость обучения', default=0)
    APPL_STATUS_CHOICES = [
        ('NEW', "Новая заявка"),
        ('ADM', "Допущен"),
        ('SED',"Начал обучение"),
        ('COMP', "Завершил обучение"),
        ('NCOM', "Заявка отменена"),
        ('DUPL', "Дубликат")
    ]
    appl_status = models.CharField("Статус заявки", max_length=4, default='NEW', choices=APPL_STATUS_CHOICES)
    change_status_date = models.DateTimeField("Дата последней смены статуса", null=True, blank=False)
    
    citizen_category = models.ForeignKey(CitizenCategory, verbose_name="категория", related_name="application", on_delete=CASCADE, blank=True, null=True)
    competence = models.ForeignKey(Competence, verbose_name="Компетенция", on_delete=CASCADE, related_name='competence_applicants', blank=True, null=True)
    education_program = models.ForeignKey(EducationProgram, verbose_name="Програма обучения", on_delete=CASCADE, related_name='programm_applicants', blank=True, null=True)
    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", on_delete=CASCADE, related_name='edcenter_applicants', blank=True, null=True)
    group = models.ForeignKey(Group, verbose_name="Группа", on_delete=CASCADE, related_name='students', blank=True, null=True)
    CONTR_TYPE_CHOICES = [
        ('OLD', "Трёхсторонний со старым работодателем"),
        ('NEW', "Трёхсторонний с новым работодателем"),
        ('THR', "Трёхсторонний"),
        ('CZN', "Трёхсторонний с ЦЗН"),
        ('SELF', "Двусторонний"),
        ('NOT', 'Без договора'),
        ('–', '-')
    ]
    contract_type = models.CharField("Тип контракта", max_length=4, choices=CONTR_TYPE_CHOICES, default='–')
    contract_date = models.DateTimeField("Дата последней смены статуса", null=True, blank=False)
    #В 2023 используется для тех кто не потверждён на платформе
    is_working = models.BooleanField("Трудоустроен (не подтверждено)", default=False)
    PAYMENT_OPTIONS = [
        ('DP', 'Не оплачен'),
        ('PF', 'Оплачен (100%)'),
        ('PP', 'Оплачен (70%)'),
        ('PFN', 'Оплачен (100%), НЦ'),
        ('PPN', 'Оплачен (70%), НЦ'),
    ]
    payment = models.CharField("Статус оплаты", max_length=3, choices=PAYMENT_OPTIONS, blank=True, null=True, default="DP")
    payment_amount = models.IntegerField("Оплата", default=0)
    GRANTS = [
        ('1', 'Грант 1'),
        ('2', 'Грант 2')
    ]
    grant = models.CharField("Грант", max_length=2, choices=GRANTS, blank=True, null=True, default="1")
    WORK_SEARCH_STAGES = [
        ('CONT', 'Заключил договор'),
        ('CERT', 'Предоставил справку о самозанятости'),
        ('VACS', 'Подобраны вакансии'),
        ('DFI', 'Направлен на собеседование'),
        ('INTD', 'Прошел собеседование'),
        ('GAJ', 'Трудоустроился'),
        ('SWRK', 'Сохранил работу'),
        ('CRIP', 'Предоставил справку ИП')
    ]
    find_work = models.CharField("Трудоустройство", max_length=4, choices=WORK_SEARCH_STAGES, blank=True, null=True)

    atlas_status = models.CharField("Статус в Атлас", max_length=100, blank=True, null=True)
    rvr_status = models.CharField("Статус в РвР", max_length=100, blank=True, null=True)
    status = models.ForeignKey(ApplStatus, verbose_name="Статус", related_name="application", on_delete=CASCADE, blank=True, null=True)
    
        
    class Meta:
        verbose_name = "Заявка (Содействие занятости)"
        verbose_name_plural = "Заявки (Содействие занятости)"

    def get_ed_price(self):
        if self.education_program.duration == 72: full_price = 23000
        if self.education_program.duration == 144: full_price = 46000
        if self.education_program.duration == 256: full_price = 92000
        return math.ceil(full_price * 0.7)

    def get_empl_price(self):
        if self.education_program.duration == 72: full_price = 23000
        if self.education_program.duration == 144: full_price = 46000
        if self.education_program.duration == 256: full_price = 92000
        if self.is_working:
            return math.ceil(full_price * 0.3)
        return 0

    def get_full_price(self):
        if self.education_program.duration == 72: full_price = 23000
        if self.education_program.duration == 144: full_price = 46000
        if self.education_program.duration == 256: full_price = 92000
        if self.is_working:
            return full_price
        return math.ceil(full_price * 0.7)
    
    def __str__(self):
        return  f"{self.applicant} ({self.status})"


class ClosingDocument(models.Model):
    group = models.ForeignKey(
        Group, 
        verbose_name="Поток",
        related_name="closing_documents",
        null=False, blank=False, on_delete=CASCADE
    )
    DOC_TYPES = [
        ('ACT', 'Акт'),
        ('RPRT', 'Отчёт об трудоустройсте')
    ]
    doc_type = models.CharField(
        "Тип документа", max_length=4, 
        choices=DOC_TYPES, blank=False, null=False
    )
    bill_sum = models.FloatField("Сумма оплаты", default=0)
    is_paid = models.BooleanField("Оплаченно?", default=False)
    
    def doc_path(instance, filename):
        return 'media/federal_empl/docs/{0}'.format(filename)
    doc_file = models.FileField("Акт/Отчёт", upload_to=doc_path)

    def bill_path(instance, filename):
        return 'media/federal_empl/docs/{0}'.format(filename)
    bill_file = models.FileField("Счёт", upload_to=bill_path)
    bill_id = models.CharField("Номер счёта", blank=True, null=True, max_length=50)
    
    class Meta:
        verbose_name = "Закрывающий документ"
        verbose_name_plural = "Закрывающие документы"
    
    def __str__(self):
        return  f"{self.group.id} ({self.get_doc_type_display()})"
    


class CitizenApplication(models.Model):
    created_at = models.DateField(auto_now_add=True)

    first_name = models.CharField("Имя", max_length=30, null=True)
    last_name = models.CharField("Фамилия", max_length=50, null=True)
    middle_name = models.CharField("Отчество", max_length=60, blank=True, null=True)

    SEX_CHOICES = [
        ('M', "Мужской"),
        ('F', "Женский")
    ]
    sex = models.CharField("Пол", max_length=1, choices=SEX_CHOICES, blank=True, null=True)
    birthday = models.DateField("Дата рождения", blank=True, null=True)

    email = models.EmailField("Email", max_length=320, blank=True, null=True)
    phone_number = models.CharField("Номер телефона", max_length=40, blank=True, null=True)

    competence = models.CharField("Компетенция", max_length=250, null=True)
    EDUCATION_CHOICES = [
        ('SPVO', "Имею диплом о среднем профессиональном или высшем образовании (например, колледжа или вуза)"),
        ('SCHL', 'Имею среднее образование (школа), в том числе неоконченное'),
        ('STDN', "Cтудент"),
    ]
    education_type = models.CharField(
        "Образование", 
        max_length=4, 
        choices=EDUCATION_CHOICES, 
        blank=True, 
        null=True
    )
    EMPLOYMENT_STATUSES = [
        ('MPL', "Трудоустроен"),
        ('SMPL', "Cамозанятый или индивидуальный предприниматель"),
        ('NMPL', 'Не работаю'),
    ]
    employment_status = models.CharField(
        "Трудоустройство", 
        max_length=4, 
        choices=EMPLOYMENT_STATUSES, 
        blank=True, 
        null=True
    )
    PLANNED_EMPLOYMENT_STATUSES = [
        ('SVMPL', "Cохранение рабочего места"),
        ('CMPL', "Трудоустройство на новую работу"),
        ('SMPL', 'Открытие или сохранение самозанятости/ИП'),
    ]
    planned_employment = models.CharField(
        "Цель обучения", 
        max_length=5, 
        choices=PLANNED_EMPLOYMENT_STATUSES, 
        blank=True, 
        null=True
    )
    PRACTICE_TIME_SLOTS = [
        ('MRNG', "9:00-13:00"),
        ('DAYT', "13:00-17:00"),
        ('EVNG', '17:00-21:00'),
    ]
    practice_time = models.CharField(
        "Удобное время", 
        max_length=4, 
        choices=PRACTICE_TIME_SLOTS, 
        blank=True, 
        null=True
    )
    consultation = models.BooleanField("консультация?", default=False)

    class Meta:
        verbose_name = "Предварительная заявка"
        verbose_name_plural = "Предварительные заявки"

    def __str__(self):
        if self.middle_name is not None:
            return  f'{self.last_name} {self.first_name} {self.middle_name}'
        return f'{self.last_name} {self.first_name}'
    



class RegulatoryDocument(models.Model):
    name = models.CharField("Наименование программы", max_length=350, null=False, blank=False)
    ed_center = models.ForeignKey(
        EducationCenterProjectYear,
        verbose_name="ЦО",
        related_name="reg_docs",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Нормативно-правовой документ"
        verbose_name_plural = "Нормативно-правовые документы"

    def __str__(self):
        return self.name


class ProfField(models.Model):
    code = models.CharField("Код", max_length=5, null=False, blank=False, unique=True)
    name = models.CharField("Наименование области профессиональной деятельности",  max_length=250, null=False, blank=False)
    
    class Meta:
        verbose_name = "область проф. деятельности"
        verbose_name_plural = "Области проф. деятельности"

    def __str__(self):
        return f'{self.code} {self.name}'


class Profstandart(models.Model):
    prof_field = models.ForeignKey(
        ProfField,
        verbose_name="Область профессиональной деятельности",
        related_name="irpo_programs",
        on_delete=CASCADE,
        blank=True,
        null=True
    )
    code = models.CharField("Код ПС", max_length=20, null=False, blank=False)
    name = models.CharField("Наименование стандарта",  max_length=500, null=False, blank=False)
    prof_activity_type = models.CharField("Вид профессиональной деятельности", null=True, blank=True, max_length=600)

    mintrud_order_date = models.CharField("Приказ Минтруда России (дата)",  max_length=10, null=True, blank=True)
    mintrud_order_number = models.CharField("Приказ Минтруда России	(номер)",  max_length=5, null=True, blank=True)
    minust_order_date = models.CharField("Приказ Минюста России (дата)",  max_length=10, null=True, blank=True)
    minust_order_number = models.CharField("Приказ Минюста России	(номер)",  max_length=10, null=True, blank=True)

    class Meta:
        verbose_name = "Профстандарт"
        verbose_name_plural = "Профстандарты"

    def __str__(self):
        return f'{self.prof_field.code}.{self.code} {self.name}'


STANDARTS_TYPES = (
    ('VO', 'ФГОС ВО'),
    ('SPO', 'ФГОС СПО')
)

class FgosStandart(models.Model):
    code = models.CharField("Код ПС", max_length=20, null=False, blank=False)
    name = models.CharField("Наименование стандарта", max_length=350, null=False, blank=False)
    standart_type = models.CharField(
        max_length=4, choices=STANDARTS_TYPES, 
        verbose_name='Тип стандарта', blank=True, null=True
    )

    class Meta:
        verbose_name = "ФГОС Стандарт"
        verbose_name_plural = "ФГОС Стандарты"

    def __str__(self):
        return f'{self.code} {self.name}'


class Author(models.Model):
    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения", 
        related_name='authors',
        on_delete=CASCADE, 
        null=True,
        blank=True
    )
    name = models.CharField("ФИО", max_length=600, null=False, blank=False)
    degree = models.CharField("Учёная степень", max_length=250, null=True, blank=True)
    position = models.CharField("Должность", max_length=250, null=False, blank=False)
    place_of_work = models.CharField("Место работы", max_length=600, null=False, blank=False)

    class Meta:
        verbose_name = "Разработчик программы"
        verbose_name_plural = "Разработчики программы"

    def __str__(self):
        return f'{self.name}'


PROGRAM_TYPES = (
    ('DPOPK', 'ДПО ПК'),
    ('DPOPP', 'ДПО ПП'),
    ('POP', 'ПО П'),
    ('POPP', 'ПО ПП'),
    ('POPK', 'ПО ПК'),
)
EDUCATION_FORMS = (
    ('FLL', 'очная'),
    ('PRT', 'очно-заочная'),
    ('PRTF', 'Заочная'),
    ('PRTLN', 'очно-заочная'),
    ('FLLLN', 'очная'),
)
PROGRAM_STATUSES = (
    ("1", 'Шаг 1. Общие сведения о программе'),
    ("2", 'Шаг 2. Планируемые результаты обучения'),
    ("3", 'Шаг 3. Разработчики (составители)'),
    ("4", 'Шаг 4. Учебно-тематический план'),
    ("5", 'Шаг 5. Календарный учебный график'),
    ("6", 'Шаг 5. Информационное и учебно-методическое обеспечение'),
)


class IrpoProgram(models.Model):
    name = models.CharField("Наименование программы", null=False, blank=False, max_length=250)
    assigned_qualif = models.CharField("Присваиваемая квалификация", null=True, blank=True, max_length=250)
    duration = models.IntegerField("Длительность (ак. часов)", blank=True)
    duration_days = models.IntegerField("Период освоения", null=True, blank=True)

    program_type = models.CharField(
        max_length=5, choices=PROGRAM_TYPES, 
        verbose_name='Тип программы', 
        blank=True, null=True
    )
    education_form = models.CharField(
        max_length=5, choices=EDUCATION_FORMS, 
        verbose_name='Форма обучения', 
        blank=True, null=True
    )
    status = models.CharField(
        max_length=5, choices=PROGRAM_STATUSES, 
        verbose_name='Статус', 
        blank=True, null=True, default="1"
    )
    gen_functions = models.TextField('Обобщенные (конкретные) трудовые функции', null=True, blank=True)
    
    current_control = models.TextField('Описание требований к проведению текущей аттестации', null=True, blank=True)
    middle_control = models.TextField('Описание требований к выполнению заданий промежуточной аттестации', null=True, blank=True)
    final_control = models.TextField('Описание процедуры проведения итоговой аттестации', null=True, blank=True)
    final_control_matereils = models.TextField('Характеристика материалов итоговой аттестации', null=True, blank=True)
    final_control_criteria = models.TextField('Критерии оценивания', null=True, blank=True)
    min_score = models.CharField("Минимальный балл", null=True, blank=True, max_length=50)

    qual_level = models.CharField(
        "Уровень квалификации в соответствии с профессиональным стандартом", 
        null=True, blank=True, max_length=20
    )

    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения", 
        related_name='irpo_programs',
        on_delete=CASCADE, 
        null=True,
        blank=True
    )
    profstandart = models.ForeignKey(
        Profstandart,
        verbose_name="Профстандарт",
        related_name="irpo_programs",
        on_delete=CASCADE,
        blank=True,
        null=True
    )
    standart = models.ForeignKey(
        FgosStandart,
        verbose_name="Стандарт (СПО/ВО)",
        related_name="irpo_programs",
        on_delete=CASCADE,
        blank=True,
        null=True
    )
    ed_program = models.ForeignKey(
        EducationProgram,
        verbose_name="Программа",
        related_name="irpo_programs",
        on_delete=CASCADE,
        blank=True,
        null=True
    )

    authors = models.ManyToManyField(
        Author,
        verbose_name="Разработчики",
        related_name="irpo_programs",
        blank=True
    )
    
    exam_duration = models.IntegerField("длительность ИА", default=0)
    exam_attest_form = models.CharField("Форма итоговой аттестации", null=True, blank=True, max_length=100)
    

    class Meta:
        verbose_name = "Программа (ИРПО)"
        verbose_name_plural = "Программы (ИРПО)"

    def get_lections_duration(self):
        sum_duration = 0
        for module in self.modules.all():
            if module.get_lection_duration() is not None:
                sum_duration += module.get_lection_duration()
        return sum_duration
    
    def get_practice_duration(self):
        sum_duration = 0
        for module in self.modules.all():
            if module.get_practice_duration() is not None:
                sum_duration += module.get_practice_duration()
        return sum_duration
    
    def get_consultations_duration(self):
        sum_duration = 0
        for module in self.modules.all():
            if module.get_consultations_duration() is not None:
                sum_duration += module.get_consultations_duration()
        return sum_duration
    
    def get_independent_duration(self):
        sum_duration = 0
        for module in self.modules.all():
            if module.get_independent_duration() is not None:
                sum_duration += module.get_independent_duration()
        return sum_duration
    
    def get_full_duration(self):
        sum_duration = self.exam_duration
        for module in self.modules.all():
            if module.get_full_duration() is not None:
                sum_duration += module.get_full_duration()
        return sum_duration

    def __str__(self):
        return self.name


class ActivityType(models.Model):
    program = models.ForeignKey(
        IrpoProgram,
        verbose_name="Программа",
        related_name="activities",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    index = models.IntegerField("Номер", null=False, blank=False)
    name = models.CharField("вид деятельности", max_length=350, null=False, blank=False)

    class Meta:
        verbose_name = "Вид деятельности"
        verbose_name_plural = "Виды деятельности"

    def __str__(self):
        return f'ВД {self.index} {self.name}'


class ActivityCompetence(models.Model):
    code = models.CharField("Код", max_length=20, null=False, blank=False)
    name = models.CharField("Наименование", null=False, blank=False, max_length=350)
    activity = models.ForeignKey(
        ActivityType,
        verbose_name="Вид деятельности",
        related_name="competencies",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    function_code = models.CharField("Код", max_length=20, null=False, blank=False)
    function_name = models.CharField("Наименование", null=False, blank=False, max_length=350)

    class Meta:
        verbose_name = "Компетенция (Вид деятельности)"
        verbose_name_plural = "Компетенции (Виды деятельности)"

    def __str__(self):
        return f'ПК {self.activity.index}.{self.code} {self.name}'


class ActivityCompetenceIndicators(models.Model):
    index = models.IntegerField("Номер", null=False, blank=False)
    knowledge = models.CharField("Знание", null=False, blank=False, max_length=350)
    skill  = models.CharField("Умение", null=False, blank=False, max_length=350)
    practice = models.CharField("Практический опыт", null=True, blank=True, max_length=350)
    competence = models.ForeignKey(
        ActivityCompetence,
        verbose_name="Профстандарты",
        related_name="indicators",
        on_delete=CASCADE,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = "Показатель (компетенция)"
        verbose_name_plural = "Показатели (компетенции)"

    def __str__(self):
        return f'{self.index}'


class ActivityCompetenceEquipment(models.Model):
    name = models.TextField("Наименование", null=False, blank=False)
    competencies = models.ManyToManyField(
        ActivityCompetence,
        verbose_name="Профстандарты",
        related_name="equipments",
        blank=False
    )

    class Meta:
        verbose_name = "МТБ"
        verbose_name_plural = "МТБ"

    def __str__(self):
        return f'{self.name}'


class ProgramModule(models.Model):
    index = models.IntegerField("Номер", null=False, blank=False)
    name = models.CharField("Наименование", null=False, blank=False, max_length=350)
    program = models.ForeignKey(
        IrpoProgram,
        verbose_name="Программа",
        related_name="modules",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    lections_duration = models.IntegerField("Лекции (ак. часы)", default=0)
    practice_duration = models.IntegerField("Практика (ак. часы)", default=0)
    consultations_duration = models.IntegerField("Консультации (ак. часы)", default=0)
    independent_duration = models.IntegerField("Самостоятельная работа (ак. часы)", default=0)

    attest_form = models.CharField("Форма аттестации", null=True, blank=True, max_length=100)
    exam_lections = models.TextField("Лекции (ПА)", null=True, blank=True)
    exam_practice = models.TextField("Практика (ПА)", null=True, blank=True)
    exam_consultations = models.TextField("Консультации (ПА)", null=True, blank=True)
    exam_independent = models.TextField("Самостоятельная работа (ПА)", null=True, blank=True)

    class Meta:
        verbose_name = "Учебный модуль"
        verbose_name_plural = "Учебные модули"
    
    def get_int_ex_duration(self):
        return self.lections_duration + self.practice_duration + self.consultations_duration + self.independent_duration

    def get_ex_duration(self):
        return self.lections_duration + self.practice_duration + self.consultations_duration + self.independent_duration

    def get_lection_duration(self):
        duration = self.subjects.all().aggregate(sum_duration=Sum('lections_duration'))['sum_duration']
        if duration == None:
            return self.lections_duration
        return duration + self.lections_duration
    
    def get_practice_duration(self):
        duration = self.subjects.all().aggregate(sum_duration=Sum('practice_duration'))['sum_duration']
        if duration == None:
            return self.practice_duration
        return duration + self.practice_duration
    
    def get_consultations_duration(self):
        duration = self.subjects.all().aggregate(sum_duration=Sum('consultations_duration'))['sum_duration']
        if duration == None:
            return self.consultations_duration
        return duration + self.consultations_duration

    def get_independent_duration(self):
        duration = self.subjects.all().aggregate(sum_duration=Sum('independent_duration'))['sum_duration']
        if duration == None:
            return self.independent_duration
        return duration + self.independent_duration


    def get_full_duration(self):
        durations = self.subjects.all().aggregate(
            lections_duration=Sum('lections_duration'),
            practice_duration=Sum('practice_duration'),
            consultations_duration=Sum('consultations_duration'),
            independent_duration=Sum('independent_duration')
        )
        try:
            durations = sum(durations.values())
            return durations + self.get_int_ex_duration()
        except TypeError:
            return 0 + self.get_int_ex_duration()
    
    def __str__(self):
        return f'Модуль (Раздел) {self.index}. {self.name}'
    
class Subject(models.Model):
    index = models.IntegerField("Номер", null=False, blank=False)
    name = models.CharField("Наименование", null=False, blank=False, max_length=350)
    module = models.ForeignKey(
        ProgramModule,
        verbose_name="Программа",
        related_name="subjects",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    lections_duration = models.IntegerField("Лекции (ак. часы)", default=0)
    practice_duration = models.IntegerField("Практика (ак. часы)", default=0)
    consultations_duration = models.IntegerField("Консультации (ак. часы)", default=0)
    independent_duration = models.IntegerField("Самостоятельная работа (ак. часы)", default=0)
    lections = models.TextField(
        "Лекции (содержание)", null=True, blank=True)
    practice = models.TextField(
        "Практика (содержание)", default=0, null=True, blank=True)
    consultations = models.TextField(
        "Консультации (содержание)", default=0, null=True, blank=True)
    independent = models.TextField(
        "Самостоятельная работа (содержание)", default=0, null=True, blank=True)
    attest_form = models.CharField("Форма аттестации", null=True, blank=True, max_length=100)

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

    def get_full_duration(self):
        return self.lections_duration + self.practice_duration + self.consultations_duration + self.independent_duration

    def __str__(self):
        return f'Тема {self.module.index}.{self.index} {self.name}'
    

DOCUMENTATION_TYPES = (
    ('LAW', 'Нормативные правовые акты, иная документация'),
    ('MAIN', 'Основная литература'),
    ('ADD', 'Дополнительная литература'),
    ('INT', 'Интернет-ресурсы'),
    ('LIB', 'Электронно-библиотечная система'),
)

class ProgramDocumentation(models.Model):
    name = models.CharField("Наименование", null=False, blank=False, max_length=350)
    program = models.ForeignKey(
        IrpoProgram,
        verbose_name="Программа",
        related_name="documentation",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    doc_type = models.CharField(
        max_length=5, choices=DOCUMENTATION_TYPES, 
        verbose_name='Тип документации', 
        blank=True, null=True
    )

    class Meta:
        verbose_name = "Документация"
        verbose_name_plural = "Документация"

    def __str__(self):
        return f'{self.name} ({self.program})'


AVAILABLE_MONTHS = (
    ('5', 'Май'),
    ('6', 'Июнь'),
    ('7', 'Июль'),
    ('8', 'Август'),
    ('9', 'Сентябрь'),
    ('10', 'Октябрь'),
    ('11', 'Ноябрь'),
)


class ProgramPlan(models.Model):
    program = models.OneToOneField(
        EducationProgram,
        verbose_name="Программа",
        related_name="plan",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    students_count = models.IntegerField("Планируется обучить", default=0)

    class Meta:
        verbose_name = "План обучения по программе"
        verbose_name_plural = "Планы обучения по программам"

    @property
    def months_sum(self):
        queryset = self.monthly_plans.all().aggregate(
            months_sum=models.Sum('students_count'))
        return queryset["months_sum"]

    def __str__(self):
        return f'План по {self.program}'
    

class MonthProgramPlan(models.Model):
    plan = models.ForeignKey(
        ProgramPlan,
        verbose_name="Программа",
        related_name="monthly_plans",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    month = models.CharField(
        max_length=5, choices=AVAILABLE_MONTHS, 
        verbose_name='Месяц', 
        blank=False, null=False
    )
    students_count = models.IntegerField("Планируется обучить", default=0)

    class Meta:
        verbose_name = "План обучения на месяц"
        verbose_name_plural = "Планы обучения на месяц"

    def __str__(self):
        return f'План по {self.plan} ({self.month})'