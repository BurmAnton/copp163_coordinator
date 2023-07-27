from email.policy import default
import math
from django.db import models
from users.models import User
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.utils.translation import gettext_lazy as _
from field_history.tracker import FieldHistoryTracker
from django.utils.timezone import now

from citizens.models import Citizen
from organizations.models import Company
from education_centers.models import Competence, EducationProgram,\
                                     EducationCenter, Group, Employee


class ProjectYear(models.Model):
    year = models.IntegerField(_('year'), null=False, blank=False)
    programs = models.ManyToManyField(
        EducationProgram,
        verbose_name="Программы",
        related_name="project_years",
        blank=True
    )

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
    STAGES = [
        ('FLLNG', "заполнение"),
        ('FLLD', "на проверке"),
        ('RWRK', "отправлена на доработку"),
        ('VRFD', "проверена"),
        ('FRMD', "сформирована"),
        ('DWNLD', "подгружена"),
        ('PRVD', "принята"),
    ]
    appl_docs_link = models.TextField('Ссылка на комп. документов', default="")
    stage = models.CharField("Работа с заявкой", max_length=5, 
                             default='FLLNG', choices=STAGES)
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

    class Meta:
        verbose_name = "Данные колледжа на год"
        verbose_name_plural = "Данные колледжей на годы"


class EdCenterQuota(models.Model):
    ed_center_year = models.OneToOneField(
        EducationCenterProjectYear, 
        verbose_name="Центр обучения",
        related_name="quota",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    quota_72  = models.IntegerField('Квота 72ч', null=False, blank=False, 
                                    default=0)
    quota_144 = models.IntegerField('Квота 144ч', null=False, blank=False, 
                                    default=0)
    quota_256 = models.IntegerField('Квота 256ч', null=False, blank=False, 
                                    default=0)

    def __str__(self):
        return  f'{self.ed_center_year.ed_center.name} ({self.ed_center_year.project_year.year})'

    class Meta:
        verbose_name = "Квота ЦО на год"
        verbose_name_plural = "Квота ЦО на годы"


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
                                     max_length=500, blank=True)
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


class Application(models.Model):
    project_year = models.ForeignKey(
        ProjectYear, 
        verbose_name="Год проекта",
        related_name="applications",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    applicant = models.ForeignKey(Citizen, verbose_name="Заявитель", on_delete=CASCADE, related_name='POE_applications')
    creation_date = models.DateTimeField("Дата создания", blank=True, null=True, default=now)
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
        ('OLD', "Трехсторонний договор со старым работодателем"),
        ('NEW', "Трехсторонний договор с новым работодателем"),
        ('SELF', "Двухсторонный договор"),
        ('NOT', 'Без договора'),
        ('–', '-')
    ]
    contract_type = models.CharField("Тип контракта", max_length=4, choices=CONTR_TYPE_CHOICES, default='–')
   
    is_working = models.BooleanField("Трудоустроен", default=False)
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
        return  f"{self.applicant} ({self.get_appl_status_display()})"
    

class CitizenApplication(models.Model):
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