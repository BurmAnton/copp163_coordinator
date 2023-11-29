import datetime
from datetime import date

import unidecode
from django.db import models
from django.db.models import Sum
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from transliterate import translit

from citizens.models import School
from copp163_coordinator import settings
from education_centers.models import (Competence, EducationCenter,
                                      EducationProgram, Employee, Group,
                                      Teacher, Workshop)
from future_ticket.tasks import (find_participants_dublicates,
                                 update_completed_quota)
from users.models import DisabilityType


# Create your models here.
class ProfEnviroment(models.Model):
    name = models.CharField("Название среды", max_length=100)

    class Meta:
        verbose_name = "Профессиональная среда"
        verbose_name_plural = "Профессиональные среды"

    def __str__(self):
        return self.name
    

class TicketProfession(models.Model):
    name = models.CharField("Название профессии", max_length=250)
    prof_enviroment = models.ForeignKey(
        ProfEnviroment, 
        verbose_name="Среда",
        related_name="profession",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    is_federal = models.BooleanField("Федеральная?", default=False)
    is_centers = models.BooleanField("Создана ЦО?", default=False)

    class Meta:
        verbose_name = "Профессия"
        verbose_name_plural = "Профессии"

    def __str__(self):
        return self.name


class ProgramAuthor(models.Model):
    teacher = models.OneToOneField(
        Teacher,
        verbose_name="Педагог",
        related_name="author",
        null=False,
        blank=False,
        on_delete=CASCADE
    )
    phone = models.CharField("Телефон", max_length=120, blank=False, 
                             null=False)
    email = models.EmailField(_('email address'), blank=False, null=False)

    class Meta:
        verbose_name = "Автор программы"
        verbose_name_plural = "Авторы программ"

    def __str__(self):
        return self.teacher.get_name()


class AgeGroup(models.Model):
    name = models.CharField("Название профессии", max_length=250)

    class Meta:
        verbose_name = "Возрастная группа"
        verbose_name_plural = "Возрастные группы"

    def __str__(self):
        return self.name


class TicketProgram(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения", 
        related_name='ticket_programs',
        on_delete=CASCADE, 
        null=True,
        blank=True
    )
    author = models.ForeignKey(
        ProgramAuthor, 
        verbose_name="Автор программы", 
        related_name='programs',
        on_delete=CASCADE, 
        null=True,
        blank=True
    )
    profession = models.ForeignKey(
        TicketProfession,
        verbose_name="Профессия",
        related_name="programs",
        null=False,
        blank=False,
        on_delete=DO_NOTHING
    )
    PROGRAM_STATUSES = (
        ('NEW', 'Новая'),
        ('PRWD', 'Подтверждённая'),
    )
    status = models.CharField(
        max_length=5, 
        choices=PROGRAM_STATUSES, 
        verbose_name='Статус программы', 
        blank=False, 
        null=False,
        default='NEW'
    )
    EDUCATION_FORMS = (
        ('FLL', 'Очный'),
        ('FLLLN', 'Очный с применением ДОТ'),
    )
    education_form = models.CharField(
        max_length=5, 
        choices=EDUCATION_FORMS, 
        verbose_name='Формат обучения', 
        blank=False, 
        null=False
    )
    description = models.TextField(
        "Краткое описание задания", null=True, blank=True
    )
    program_link = models.CharField("Ссылка на программу", max_length=500, 
                                    blank=True, null=True)
    age_groups = models.ManyToManyField(
        AgeGroup,
        verbose_name='Возрастные категории',
        related_name='programs',
        blank=False
    )
    disability_types = models.ManyToManyField(
        DisabilityType, 
        verbose_name="ОВЗ", 
        blank=True
    )
    teachers = models.ManyToManyField(
        Teacher,
        verbose_name='педагоги', 
        related_name='ticket_programs',
        blank=True
    )
    workshops = models.ManyToManyField(
        Workshop,
        verbose_name='аудитории', 
        related_name='ticket_programs',
        blank=True
    )

    class Meta:
        verbose_name = "Программа"
        verbose_name_plural = "Программы"

    def __str__(self):
        return f'{self.profession} ({self.get_education_form_display()})'


class TicketProjectYear(models.Model):
    year = models.IntegerField('год', null=False, blank=False)
    programs = models.ManyToManyField(
        TicketProgram,
        verbose_name="Программы",
        related_name="ticket_project_years",
        blank=True
    )

    def __str__(self):
        return  str(self.year)

    class Meta:
        verbose_name = "Год проекта"
        verbose_name_plural = "Годы проекта"


class EducationCenterTicketProjectYear(models.Model):
    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения",
        related_name="ticket_project_years",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    project_year = models.ForeignKey(
        TicketProjectYear, 
        verbose_name="Год проекта (БВБ)",
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
        ('FNSHD', "ПКО пройден"),
        ('ACT', "Акт сформирован"),
        ('ACTS', "Акт подписан"),
        ('NVC', "Счёт и акт подгружены"),
        ('PNVC', "Счёт и акт проверены"),
        ('NVCP', "Счёт оплачен"),
    ]
    stage = models.CharField("Работа с заявкой", max_length=5, 
                             default='FLLNG', choices=STAGES)
    programs = models.ManyToManyField(
        TicketProgram,
        verbose_name="Программы",
        related_name="ticket_centers_project_years",
        blank=True
    )
    is_disability = models.BooleanField("ОВЗ?", default=False)
    appl_docs_link = models.TextField('Ссылка на комп. документов', 
                                      default="", null=True, blank=True)
    is_ndc = models.BooleanField("Платит НДС?", default=False)
    none_ndc_reason = models.CharField(
        "Основание работы без НДС", max_length=500, null=True, blank=True, default=""
    )
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
    step_8_check = models.BooleanField("Шаг 8. Проверка", default=False)
    step_8_commentary = models.TextField(
        "Шаг 8. Комментарий", null=True, blank=True, default=""
    )

    def doc_directory_path(instance, filename):
        return 'media/applications/{0}/{1}'.format(
            instance.id, f'zayavka_scan.pdf'
        )
    application_file = models.FileField(
        "Скан заявки",
        null=True, 
        blank=True,
        upload_to=doc_directory_path
    )
    appl_track_number = models.CharField(
        "Трек номер", max_length=150, blank=True, null=True)
    
    def doc_dir_path(instance, filename):
        return 'media/applications/{0}/{1}'.format(
            instance.id, unidecode.unidecode(filename)
        )
    act_file = models.FileField(
        "Подписанный акт",
        null=True, 
        blank=True,
        upload_to=doc_dir_path
    )
    bill_file = models.FileField(
        "Счёт",
        null=True, 
        blank=True,
        upload_to=doc_dir_path
    )

    def __str__(self):
        return  f'{self.ed_center} ({self.project_year.year} г.)'

    class Meta:
        verbose_name = "Данные колледжа на год"
        verbose_name_plural = "Данные колледжей на годы"


class TicketProjectPosition(models.Model):
    project_year = models.ForeignKey(
        TicketProjectYear, 
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


class TicketEdCenterEmployeePosition(models.Model):
    position = models.ForeignKey(
        TicketProjectPosition, 
        verbose_name="Позиция",
        related_name="positions_employees",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения",
        related_name="ticket_positions_employees",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        Employee, 
        verbose_name="Сотрудник",
        related_name="ticket_positions",
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


class TicketIndicator(models.Model):
    project_year = models.ForeignKey(
        TicketProjectYear, 
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


class EdCenterTicketIndicator(models.Model):
    indicator = models.ForeignKey(
        TicketIndicator, 
        verbose_name="Показатель",
        related_name="ed_centers",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения",
        related_name="ticket_indicators",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    value = models.CharField("Значение показателя", max_length=25, 
                            blank=False,null=False)
    free_form_value = models.TextField("Значение (свободная форма)", 
                                       null=True, blank=True, default="")

    def __str__(self):
        return  f'{self.indicator} ({self.ed_center})'
    
    class Meta:
        verbose_name = "Показатель эффективности (ЦО)"
        verbose_name_plural = "Показатели эффективности (ЦО)"


class TicketFullQuota(models.Model):
    project_year = models.OneToOneField(
        TicketProjectYear, 
        verbose_name="Год проекта",
        related_name="quota",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    full_quota = models.IntegerField("Полная квота", default=0)
    federal_quota = models.IntegerField("Федеральная квота", default=0)

    def __str__(self):
        return  f'Квота за {self.project_year.year} г.'
    
    class Meta:
        verbose_name = "Квота региона"
        verbose_name_plural = "Квоты региона"


class TicketQuota(models.Model):
    quota = models.ForeignKey(
        TicketFullQuota, 
        verbose_name="Квота",
        related_name="quotas",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения",
        related_name="ticket_quotas",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    school = models.ForeignKey(
        School, 
        verbose_name="Школа",
        related_name="ticket_quotas",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    profession = models.ForeignKey(
        TicketProfession,
        verbose_name="Профессия",
        related_name="quotas",
        null=False,
        blank=False,
        on_delete=CASCADE
    )
    is_federal = models.BooleanField("Федеральная?", default=False)
    value = models.IntegerField("Квота", default=0)
    approved_value = models.IntegerField("Одобренная квота", default=0)
    reserved_quota = models.IntegerField("Зарезервированая квота", default=0)
    completed_quota = models.IntegerField("Выполненная квота", default=0)
    free_quota = models.IntegerField("Свободная квота", null=False, blank=True)

    def __init__(self, *args, **kwargs):
        super(TicketQuota, self).__init__(*args, **kwargs)
        self.free_quota = self.approved_value - self.reserved_quota

    def save(self, *args, **kwargs):
        self.free_quota = int(self.approved_value) - self.reserved_quota
        if self.reserved_quota > self.approved_value:
            self.reserved_quota = self.approved_value
        self.free_quota = int(self.approved_value) - self.reserved_quota
        super(TicketQuota, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.profession} ({self.ed_center}, {self.school})'
     
    class Meta:
        verbose_name = "Квота"
        verbose_name_plural = "Квоты"


class SchoolProjectYear(models.Model):
    project_year = models.ForeignKey(
        TicketProjectYear, 
        verbose_name="Год проекта (БВБ)",
        related_name="schools",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    school = models.ForeignKey(
        School, 
        verbose_name="Школа",
        related_name="ticket_project_years",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    resp_full_name = models.CharField(
        "ФИО ответственного", max_length=250, blank=False, null=False)
    resp_position = models.CharField(
        "Должность", max_length=100, blank=False, null=False)
    phone = models.CharField("Телефон", max_length=120, blank=False, 
                             null=False)
    email = models.EmailField(_('email address'), blank=False, null=False)
    
    def template_directory_path(instance, filename):
        try:
            return 'media/documents/{0}'.format(translit(filename, reversed=True))
        except:
            return 'media/documents/{0}'.format(filename)
    resp_order = models.FileField("Приказ", upload_to=template_directory_path)
    
    def __str__(self):
        return f'{self.resp_full_name} ({self.school})'
     
    class Meta:
        verbose_name = "Школа (ответственный)"
        verbose_name_plural = "Школы (ответственные)"


class DocumentTypeTicket(models.Model):
    project_year = models.ForeignKey(
        TicketProjectYear, 
        verbose_name="Год проекта (БВБ)",
        related_name="docs_templates",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        "Тип документа", 
        max_length=150, 
        null=True, 
        blank=True
    )
    STAGES = [
        ("GRMNT", "Договорные"),
        ("CLS", "Закрывающие"),
        ("PRV", "Подтверждающие"),
    ]
    stage = models.CharField(
        "Этап", 
        max_length=6, 
        choices=STAGES,
        null=False,
        blank=False
    )
    def template_directory_path(instance, filename):
        return 'media/doc_templates/ticket/{0}'.format(filename)
    
    template = models.FileField("Документ", upload_to=template_directory_path)

    class Meta:
        verbose_name = "Шаблон документов (БВБ)"
        verbose_name_plural = "Шаблоны документов (БВБ)"

    def __str__(self):
        return f'{self.name}'
    

class ContractorsDocumentTicket(models.Model):
    creation_date = models.DateTimeField("Дата создания", blank=True,
                                          null=True, default=now)
    contractor = models.ForeignKey(
        EducationCenter, 
        verbose_name='подрядчик', 
        related_name='ticket_docs',
        null=False,
        blank=False,
        on_delete=CASCADE
    )
    register_number = models.IntegerField(
        'Номер в реестре',
        null=False,
        blank=False
        )
    parent_doc = models.ForeignKey(
        "self", 
        verbose_name="Родительский документ",
        related_name="children_docs",
        null=True, 
        blank=True,
        on_delete=CASCADE
    )
    STAGES = [
        ("CRTD", "Создан"),
        ("CHCKD", "Проверен"),
        ("SGND", "Подписан"),
        ("SGNDAP", "Подписан и проверен"),
    ]
    doc_stage = models.CharField(
        "Стадия", 
        max_length=6, 
        choices=STAGES,
        null=False,
        blank=False,
        default="CRTD"
    )
    doc_type = models.ForeignKey(
        DocumentTypeTicket, 
        verbose_name="Тип документа",
        null=True,
        blank=False,
        on_delete=CASCADE
    )

    def doc_directory_path(instance, filename):
        return 'media/documents/ticket/{0}/{1}'.format(
            instance.contractor.id, filename
        )
    
    doc_file = models.FileField("Документ", upload_to=doc_directory_path)

    class Meta:
        verbose_name = "Документ с подрядчиком (БВБ)"
        verbose_name_plural = "Документы с подрядчиками (БВБ)"

    def __str__(self):
        return f'{self.doc_type} №{self.register_number} ({self.contractor.name})'


def number_cycles():
    from .models import EventsCycle
    cycles = EventsCycle.objects.all().order_by(
            'end_reg_date', 'start_period_date', 'end_period_date'
        )
    for cycle_number, cycle in enumerate(cycles, start=1):
        if cycle_number != cycle.cycle_number:
            cycle.cycle_number = cycle_number
            cycle.save(cycle_number=True)


class EventsCycle(models.Model):
    cycle_number = models.IntegerField("№ цикла", default=1)
    project_year = models.ForeignKey(
        TicketProjectYear, 
        verbose_name="Год проекта (БВБ)",
        related_name="events_cycles",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    end_reg_date = models.DateField(
        "Дата окончания регистрации", blank=False, null=False
    )
    start_period_date = models.DateField(
        "Старт проведения мероприятий", blank=False, null=False
    )
    end_period_date = models.DateField(
        "Конец проведения мероприятий", blank=False, null=False
    )
    STATUSES = [
        ("REG", "Регистрация"),
        ("CHCK", "Проверка и коррекция"),
        ("HSTNG", "В процессе"),
        ("END", "Завершено"),
    ]
    status = models.CharField(
        "Статус", 
        max_length=6, 
        choices=STATUSES,
        null=False,
        blank=False,
        default="REG"
    )
    def save(self, *args, **kwargs):
        today = date.today()
        if self.end_reg_date >= today: self.status = 'REG'
        elif self.end_reg_date < today and self.start_period_date > today:
            self.status = 'CHCK'
        elif self.start_period_date <= today and self.end_period_date >= today:
            self.status = 'HSTNG'
        elif self.end_period_date < today: self.status='END'
        super(EventsCycle, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Цикл проб"
        verbose_name_plural = "Циклы проб"

    def __str__(self):
        return f'Цикл №{self.cycle_number}'
    
    def save(self, cycle_number=False, *args, **kwargs):
        super(EventsCycle, self).save(*args, **kwargs)
        if cycle_number == False:
            number_cycles()

@receiver(post_delete, sender=EventsCycle, dispatch_uid='EventsCycle_delete_signal')
def change_number_cycles(sender, instance, using, **kwargs):
    number_cycles()

class TicketEvent(models.Model):
    ed_center = models.ForeignKey(
        EducationCenterTicketProjectYear,
        verbose_name="Центр обучения",
        related_name="events",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    profession = models.ForeignKey(
        TicketProfession,
        verbose_name="Профессия",
        related_name="events",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    cycle = models.ForeignKey(
        EventsCycle,
        verbose_name="Цикл",
        related_name="events",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    event_date = models.DateTimeField(
        "Дата проведения", blank=False, null=False
    )
    start_time = models.CharField(
        "Время начала", max_length=20, blank=True, null=True
    )
    participants_limit = models.IntegerField(
        "Колво участников", blank=False, null=False, default=0
    )
    photo_link = models.CharField(
        "Фото с профпробы", max_length=500, null=True, blank=True
    )
    
    STATUSES = [
        ("CRTD", "Создана"),
        ("LOAD", "Фото и видеоматериалы загружены"),
    ]
    status = models.CharField(
        "Статус", 
        max_length=6, 
        choices=STATUSES,
        null=False,
        blank=False,
        default="CRTD"
    )

    class Meta:
        verbose_name = "Профпроба"
        verbose_name_plural = "Профпробы"

    def __str__(self):
        return f'{self.ed_center} ({self.profession}, {self.event_date})'


class StudentBVB(models.Model):
    bvb_id = models.IntegerField(
        "ID БВБ", blank=False, null=False, db_index=True)
    is_double = models.BooleanField("Дубликат?", default=False)
    is_hidden = models.BooleanField("Скрыт?", default=False)
    is_attend = models.BooleanField("Присутствовал?", default=True)

    full_name = models.CharField(
        "Имя", max_length=200, blank=False, null=False)
    grade = models.CharField(
        "Класс", max_length=50, blank=False, null=False)
    school = models.ForeignKey(
        School,
        verbose_name="Школа", 
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    event = models.ForeignKey(
        TicketEvent,
        verbose_name="Мероприятие",
        related_name="participants",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    
    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return f'{self.bvb_id}'


class QuotaEvent(models.Model):
    quota = models.ForeignKey(
        TicketQuota,
        verbose_name="Квота",
        related_name="events",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    event = models.ForeignKey(
        TicketEvent,
        verbose_name="Квота",
        related_name="quotas",
        on_delete=CASCADE,
        blank=False,
        null=False
    )
    reserved_quota = models.IntegerField(
        "Колво участников", blank=False, null=False
    )

    def save(self, *args, **kwargs):
        super(QuotaEvent, self).save(*args, **kwargs)

        participants_limit = QuotaEvent.objects.filter(event=self.event
            ).aggregate(participants_limit=Sum("reserved_quota")
            )['participants_limit']
        self.event.participants_limit = participants_limit
        self.event.save()
        update_completed_quota.delay()

@receiver(pre_delete, sender=QuotaEvent, dispatch_uid='quotaEvent_delete_signal')
def change_quota(sender, instance, using, **kwargs):
    quota = instance.quota
    quota.reserved_quota -= instance.reserved_quota
    quota.save()
    event = instance.event
    event.participants_limit -= instance.reserved_quota
    event.save()