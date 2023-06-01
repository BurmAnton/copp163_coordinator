from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.utils.translation import gettext_lazy as _
from citizens.models import School

from education_centers.models import Competence, EducationProgram, \
                                     EducationCenter, Group, Employee, Workshop
from users.models import DisabilityType
from education_centers.models import Teacher

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
        verbose_name='Возрастная категория',
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
        blank=False
    )
    workshops = models.ManyToManyField(
        Workshop,
        verbose_name='аудитории', 
        related_name='ticket_programs',
        blank=False
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
        ('RWRK', "отправленна на доработку"),
        ('VRFD', "проверена"),
        ('FRMD', "сформирована"),
        ('DWNLD', "подгружена"),
        ('PRVD', "принята"),
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
    step_8_check = models.BooleanField("Шаг 8. Проверка", default=False)
    step_8_commentary = models.TextField(
        "Шаг 8. Комментарий", null=True, blank=True, default=""
    )
    quota = models.IntegerField('Квота', null=False, blank=False, default=0)

    def doc_directory_path(instance, filename):
        return 'media/applications/{0}/{1}'.format(
            instance.id, filename
        )
    application_file = models.FileField(
        "Скан заявки",
        null=True, 
        blank=True,
        upload_to=doc_directory_path
    )
    appl_track_number = models.CharField(
        "Трек номер", max_length=150, blank=True, null=True)

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

    def __str__(self):
        return f'{self.profession} ({self.ed_center}, {self.school})'
     
    class Meta:
        verbose_name = "Квота"
        verbose_name_plural = "Квоты"
