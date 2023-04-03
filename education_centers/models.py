from email.policy import default
from email.quoprimime import quote
from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User

class Competence(models.Model):
    title = models.CharField("Название компетенции", max_length=200)
    
    СOMPETENCE_BLOCKS = (
        ('IT', 'Информационные и коммуникационные технологии'),
        ('SR', 'Сфера услуг'),
        ('BD', 'Строительство и строительные технологии'),
        ('MF', 'Производство и инженерные технологии'),
        ('DS', 'Творчество и дизайн'),
        ('TR', 'Транспорт и логистика'),
        ('ED', 'Образование')
    )
    block = models.CharField(max_length=2, choices=СOMPETENCE_BLOCKS, verbose_name='Блок', blank=True, null=True)
    СOMPETENCE_STAGES = (
        ('MN', 'Основная'),
        ('PR', 'Презентационная')
    )
    competence_stage = models.CharField(max_length=2, choices=СOMPETENCE_STAGES, verbose_name='Стадия', blank=True, null=True)
    СOMPETENCE_TYPES = (
        ('RU', 'WorldSkills Russia'),
        ('WSI', 'WorldSkills International'),
        ('WSE', 'WorldSkills Eurasia')
    )
    competence_type = models.CharField(max_length=3, choices=СOMPETENCE_TYPES, verbose_name='Тип', blank=True, null=True)

    class Meta:
        verbose_name = "Компетенция"
        verbose_name_plural = "Компетенции"

    def __str__(self):
        return self.title


class EducationProgram(models.Model):
    program_name = models.CharField("Название программы", max_length=500)
    competence = models.ForeignKey(Competence, verbose_name="Компетенция", on_delete=CASCADE, related_name='programs')
    PROGRAM_TYPES = (
        ('DPOPK', 'ДПО ПК'),
        ('DPOPP', 'ДПО ПП'),
        ('POP', 'ПО П'),
        ('POPP', 'ПО ПП'),
        ('POPK', 'ПО ПК'),
    )
    program_type = models.CharField(max_length=5, choices=PROGRAM_TYPES, verbose_name='Тип программы', blank=True, null=True)
    PROGRAM_DURATIONS = (
        (72, '72 ч.'),
        (144, '144 ч.'),
        (256, '256 ч.')
    )
    duration = models.IntegerField("Длительность (ак. часов)", choices=PROGRAM_DURATIONS, blank=True)
    program_link =  models.CharField("Ссылка на программу", max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "Программа"
        verbose_name_plural = "Программы"

    def __str__(self):
        program_type = 'ДПО ПК'
        for prog_type in self.PROGRAM_TYPES:
            if prog_type[0] == self.program_type:
                program_type = prog_type[1]
                break
        return f"{self.program_name} ({program_type}, {self.duration} ч.)"

class EducationCenter(models.Model):
    name = models.CharField("Название организации", max_length=500)
    contact_person = models.ForeignKey(User, verbose_name="Контактное лицо", related_name="education_centers", on_delete=DO_NOTHING, blank=True, null=True)
    competences = models.ManyToManyField(Competence, related_name="educationCenters", verbose_name="Компетенции", blank=True)
    quota_1_72 = models.IntegerField("Квота 72ч (Грант 1)", default=0)
    quota_1_144 = models.IntegerField("Квота 144ч (Грант 1)", default=0)
    quota_1_256 = models.IntegerField("Квота 256ч (Грант 1)", default=0)
    quota_2_72 = models.IntegerField("Квота 72ч (Грант 2)", default=0)
    quota_2_144 = models.IntegerField("Квота 144ч (Грант 2)", default=0)
    quota_2_256 = models.IntegerField("Квота 256ч (Грант 2)", default=0)


    class Meta:
        verbose_name = "Центр обучения"
        verbose_name_plural = "Центры обучения"

    def __str__(self):
        return self.name

class Workshop(models.Model):
    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", on_delete=CASCADE, related_name='workshops')
    competence = models.ForeignKey(Competence, verbose_name="Компетенция",  on_delete=CASCADE, related_name='workshops')
    adress = models.CharField("Адрес", max_length=200)

    class Meta:
        verbose_name = "Мастерская"
        verbose_name_plural = "Мастерские"

    def __str__(self):
        return f"{self.education_center} ({self.adress})"

class Group(models.Model):
    name = models.CharField("Номер группы", max_length=50)
    workshop = models.ForeignKey(Workshop, verbose_name="мастерская", on_delete=CASCADE, related_name='groups', blank=True, null=True)
    education_program = models.ForeignKey(EducationProgram, verbose_name="Программа обучения", on_delete=CASCADE, related_name='groups', blank=True, null=True)
    start_date = models.DateField("Дата начала обучения", blank=True, null=True)
    end_date = models.DateField("Дата окончания обучения", blank=True, null=True)
    distance_education = models.BooleanField("Дистанционное обучение", default=False)
    mixed_education = models.BooleanField("Смешанное обучение", default=False)
    EDUCATION_PROJECTS = (
        ('COMM', 'Комерция'),
        ('PoE', 'Содействие занятости'),
        ('OTHR', 'Другое')
    )
    education_project = models.CharField(max_length=4, choices=EDUCATION_PROJECTS, verbose_name='Федеральная программа', blank=True, null=True)

    is_new_price = models.BooleanField("Новая цена", default=False)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return  f"{self.name}"

class EducationCenterGroup(models.Model):
    education_center = models.ForeignKey(EducationCenter, verbose_name='Центр обучения', on_delete=CASCADE, related_name='ed_center_groups', null=True, blank=True)
    competence = models.ForeignKey(Competence, verbose_name='Компетенция', on_delete=CASCADE, related_name='ed_center_groups')
    program = models.CharField("Название программы", max_length=500, null=True, blank=False)
    program_link = models.CharField("Ссылка на программу", max_length=200, null=True, blank=False)
    reg_link = models.CharField("Ссылка на программу на сайте работа в россии", max_length=300, null=True, blank=False)
    description = models.TextField("Описание", max_length=120, null=True, blank=True)
    PROGRAM_DURATIONS = (
        ('72', '72 ч.'),
        ('144', '144 ч.'),
        ('256', '256 ч.')
    )
    duration = models.CharField("Длительность (ак. часов)", max_length=3, choices=PROGRAM_DURATIONS, blank=True)
    ED_REQ = [   
        ("scl","Не требуется"),
        ("pro", "Свидетельство о профессии"),
        ("clg","Среднее специальное/Высшее")
    ]
    educational_requirements = models.CharField("Требования к образованию", max_length=4, choices=ED_REQ)
    is_visible = models.BooleanField("Показывать в списке планируемого обучения", default=False)

    FORMATS = [   
        ("on","Онлайн"),
        ("off","Очный")
    ]
    is_online = models.CharField("Формат проведения", max_length=4, choices=FORMATS, default='off')
    city = models.CharField("Город проведения", max_length=100, blank=True, null=True, default="")

    min_group_size = models.IntegerField('Минимальный размер')
    max_group_size = models.IntegerField('Максимальный размер')
    
    start_date = models.DateField('Дата старта')
    end_date = models.DateField('Дата окончания', blank=True, null=True)

    study_period = models.CharField("Период проведения занятий", max_length=128, blank=True, null=True)
    study_days_count = models.IntegerField("Занятий в неделю", validators=[MaxValueValidator(7),MinValueValidator(1)], blank=True, null=True)
    ed_schedule_link = models.URLField("Ссылка на график обучения", max_length=256, blank=True, null=True)

    group = models.OneToOneField(Group, verbose_name='Группа Express', on_delete=CASCADE, related_name='ed_center_group', blank=True, null=True)

    class Meta:
        verbose_name = "ЦО группа"
        verbose_name_plural = "ЦО группы"
        
    def __str__(self):
        if self.end_date == None:
            return  f"{self.education_center} {self.program} (с {self.start_date})"            
        else:
            return  f"{self.education_center} {self.program} ({self.start_date}–{self.end_date})"    

class DocumentType(models.Model):
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
        return 'documents/{0}'.format(filename)
    
    template = models.FileField("Документ", upload_to=template_directory_path)

    class Meta:
        verbose_name = "Шаблон документов"
        verbose_name_plural = "Шаблоны документов"

    def __str__(self):
        return f'{self.name}'

class ContractorsDocument(models.Model):
    contractor = models.ForeignKey(
        EducationCenter, 
        verbose_name='подрядчик', 
        related_name='ed_center_documents',
        null=False,
        blank=False,
        on_delete=CASCADE
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='группы', 
        related_name='group_documents',
        blank=False
    )
    STAGES = [
        ("CRTD", "Создан"),
        ("CHCKD", "Проверен"),
        ("SGND", "Подписан"),
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
        DocumentType, 
        verbose_name="Тип документа",
        null=True,
        blank=False,
        on_delete=CASCADE
    )

    def doc_directory_path(instance, filename):
        return 'documents/{0}/{1}'.format(
            instance.contractor.id, filename
        )
    
    doc_file = models.FileField("Документ", upload_to=doc_directory_path)

    class Meta:
        verbose_name = "Документ с подрядчиком"
        verbose_name_plural = "Документы с подрядчиками"

    def __str__(self):
        return f'{self.get_doc_type_display()} ({self.contractor.name})'