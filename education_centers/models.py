from email.policy import default
from email.quoprimime import quote

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


from users.managers import CustomUserManager
from users.models import DisabilityType, User


class Competence(models.Model):
    title = models.CharField("Название компетенции", max_length=500)
    is_irpo = models.BooleanField("ИРПО?", default=True)
    is_worldskills = models.BooleanField("ВС?", default=True)

    class Meta:
        verbose_name = "Компетенция"
        verbose_name_plural = "Компетенции"

    def __str__(self):
        return self.title
    

class EducationCenter(models.Model):
    name = models.CharField("Название организации", max_length=500)
    short_name = models.CharField("Краткое название организации", max_length=500, null=True, blank=True, default="")
    short_name_r = models.CharField("Краткое название организации (род.)", max_length=500, null=True, blank=True, default="")
    flow_name = models.CharField("Название на flow", max_length=500, null=True, blank=True, default="")

    contact_person = models.ForeignKey(User, verbose_name="Контактное лицо", related_name="education_centers", on_delete=DO_NOTHING, blank=True, null=True)
    home_city = models.CharField("Город", max_length=150, null=True, blank=True, default="")
    ENTITY_SEXES = (
        ('ML', 'Мужской'),
        ('M', 'Женский'),
        ('N', 'Средний')
    )
    entity_sex = models.CharField(max_length=4, choices=ENTITY_SEXES, verbose_name='Род для юр. лица', blank=True, null=True)

    competences = models.ManyToManyField(Competence, related_name="educationCenters", verbose_name="Компетенции", blank=True)
    
    org_document = models.TextField(
        "Действует на основаннии:", null=True, blank=True
    )
    legal_address = models.TextField(
        "Адрес места нахождения", null=True, blank=True
    )
    is_license = models.BooleanField("Есть обр. лизенция?", default=False)
    ed_license = models.TextField(
        "Образовательная лизенция (серия, номер, дата, срок действия)", 
        null=True, blank=True, default=""
    )
    license_issued_by = models.TextField(
        "Кем выдана обр. лизенция (творический падеж)", null=True, blank=True, default=""
    )
    is_ndc = models.BooleanField("Платит НДС?", default=False)
    none_ndc_reason = models.CharField(
        "Основание работы без НДС", max_length=500, null=True, blank=True, default=""
    )

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
        return self.short_name
    

class EducationProgram(models.Model):
    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения", 
        related_name='programs',
        on_delete=CASCADE, 
        null=True,
        blank=True
    )
    program_name = models.CharField("Название программы", max_length=500)
    flow_id = models.IntegerField('Идентификатор flow', null=True, blank=True) 
    
    competence = models.ForeignKey(Competence, verbose_name="Компетенция", on_delete=CASCADE, related_name='programs')
    PROGRAM_TYPES = (
        ('DPOPK', 'ДПО ПК'),
        ('DPOPP', 'ДПО ПП'),
        ('POP', 'ПО П'),
        ('POPP', 'ПО ПП'),
        ('POPK', 'ПО ПК'),
    )
    program_type = models.CharField(max_length=5, choices=PROGRAM_TYPES, verbose_name='Тип программы', blank=True, null=True)
    duration = models.IntegerField("Длительность (ак. часов)", blank=True)
    EDUCATION_FORMS = (
        ('PRTLN', 'Очно-заочная с применением ДОТ'),
        ('FLLLN', 'Очная с применением ДОТ '),
        ('PRT', 'Очно-заочная'),
        ('FLL', 'Очная'),
    )
    education_form = models.CharField(max_length=5, choices=EDUCATION_FORMS, verbose_name='Форма обучения', blank=True, null=True)
    EDUCATION_CHOICES = [
        ('NDC', "Без образования"),
        ('SPO', "Среднее профессиональное образование"),
    ]
    entry_requirements = models.CharField("Входные требования", max_length=4, choices=EDUCATION_CHOICES, blank=True, null=True)
    program_link = models.CharField("Ссылка на программу", max_length=200, blank=True, null=True)

    profession = models.CharField(
        "Профессия", max_length=200, blank=True, null=True
    )
    description = models.TextField(
        "Описание программы", null=True, blank=True
    )
    notes = models.TextField("Примечания", null=True, blank=True)

    is_abilimpics = models.BooleanField("Абилимпикс?", default=False)
    is_atlas = models.BooleanField("Атлас?", default=False)
    period = models.CharField("Период обучения", max_length=500, blank=True, null=True)
    disability_types = models.ManyToManyField(
        DisabilityType, 
        verbose_name="ОВЗ", 
        blank=True
    )

    def doc_directory_path(instance, filename):
        return 'media/programs/{0}/{1}'.format(
            instance.ed_center.id, filename
        )
    
    program_file = models.FileField(
        "Программа (документ)", 
        upload_to=doc_directory_path,
        null=True, blank=True
    )

    def irpo_directory_path(instance, filename):
        folder = f'{instance.program_name} {instance.get_program_type_display()} {instance.duration}'
        if len(instance.program_name) > 100:
                folder = f'{instance.program_name[:97]} {instance.get_program_type_display()} {instance.duration}'
        return 'media/programs/irpo/{0}/{1}/{2}'.format(
            instance.ed_center.short_name, 
            folder,
            filename
    )
    program_word = models.FileField(
        "Программа по шаблону ИРПО (word)", 
        upload_to=irpo_directory_path,
        max_length=500,
        null=True, blank=True
    )
    program_pdf = models.FileField(
        "Программа, подписанная работодателем (pdf)", 
        upload_to=irpo_directory_path,
        max_length=500,
        null=True, blank=True
    )
    teacher_review = models.FileField(
        "Рецензии преподавателя (pdf)", 
        upload_to=irpo_directory_path,
        max_length=500,
        null=True, blank=True
    )
    employer_review = models.FileField(
        "Рецензии работодателя (pdf)", 
        upload_to=irpo_directory_path,
        max_length=500,
        null=True, blank=True
    )

    class Meta:
        verbose_name = "Программа"
        verbose_name_plural = "Программы"

    def __str__(self):
        program_type = 'ДПО ПК'
        for prog_type in self.PROGRAM_TYPES:
            if prog_type[0] == self.program_type:
                program_type = prog_type[1]
                break
        return f"{self.program_name} ({program_type}, {self.duration}ч.)"


class Teacher(models.Model):
    organization = models.ForeignKey(
        EducationCenter,
        verbose_name="Организация",
        related_name="teachers",
        null=False,
        blank=False,
        on_delete=CASCADE
    )
    programs = models.ManyToManyField(
        EducationProgram,
        verbose_name='программы', 
        related_name='teachers',
        blank=False
    )
    first_name = models.CharField("Имя", max_length=30, blank=False, 
                                  null=False)
    middle_name = models.CharField("Отчество", max_length=30, blank=True, 
                                   null=True)
    last_name = models.CharField("Фамилия", max_length=30, blank=False, 
                                 null=False)
    position = models.CharField("Ученая степень/должность", max_length=150, 
                                blank=True, null=True)
    EMPLOYMENT_TYPES = (
        ('STFF', 'Штатный педагогический сотрудник'),
        ('TTRC', 'Привлеченный педагогический работник')
    )
    employment_type = models.CharField(
        max_length=4, choices=EMPLOYMENT_TYPES, 
        verbose_name='Тип трудоустройства', blank=True, null=True
    )
    EDUCATION_LEVELS = (
        ('VO', 'Высшее образование'),
        ('SPO', 'Среднее профессиональное образование')
    )
    education_level = models.CharField(
        max_length=4, choices=EDUCATION_LEVELS, 
        verbose_name='Уровень образования', blank=True, null=True
    )
    education_major = models.CharField("Специальность", max_length=150, 
                                blank=True, null=True)
    experience = models.TextField("Наличие опыта", null=True, blank=True)
    bvb_experience = models.TextField(
        "Наличие профессиональных сертификаций", null=True, blank=True)
    additional_education = models.TextField(
        "Наличие доп. проф. образования по профилю программы за последние 3 года", 
        null=True, blank=True
    )
    def doc_directory_path(instance, filename):
        return 'media/consents/{0}/{1}/{2}'.format(
            instance.organization.id, 
            instance.id, 
            filename
        )
    consent_file = models.FileField(
        "Согласие",
        null=True, 
        blank=True,
        upload_to=doc_directory_path
    )

    class Meta:
        verbose_name = "Педагог"
        verbose_name_plural = "Педагоги"

    def get_name(self):
        if self.middle_name == None or self.middle_name == "":
            return f'{self.first_name} {self.last_name}'
        return f'{self.first_name} {self.middle_name} {self.last_name}'

    def get_short_name(self):
        if self.middle_name == None or self.middle_name == "":
            return f'{self.last_name} {self.first_name[0]}.'
        return f'{self.last_name} {self.first_name[0]}.{self.middle_name[0]}.'

    def __str__(self):
        return f'{self.last_name} ({self.organization})'


class Employee(models.Model):
    organization = models.ForeignKey(
        EducationCenter,
        verbose_name="Организация",
        related_name="employees",
        null=False,
        blank=False,
        on_delete=CASCADE
    )
    first_name = models.CharField("Имя", max_length=30, blank=False, 
                                  null=False)
    middle_name = models.CharField("Отчество", max_length=30, blank=True, 
                                   null=True)
    last_name = models.CharField("Фамилия", max_length=30, blank=False, 
                                 null=False)
    position = models.CharField("Должность", max_length=150, blank=False, 
                                null=False)
    is_head = models.BooleanField("Руководитель организации?", default=False)
    first_name_r= models.CharField("Имя (род)", max_length=30, blank=False, 
                                   null=False)
    middle_name_r = models.CharField("Отчество (род)", max_length=30, 
                                     blank=True, null=True)
    last_name_r = models.CharField("Фамилия (род)", max_length=30, 
                                   blank=False, null=False)
    position_r = models.CharField("Должность (род)", max_length=150, 
                                  blank=False, null=False)

    phone = models.CharField("Телефон(-ы)", max_length=120, blank=False, 
                             null=False)
    email = models.EmailField(_('email address'), blank=False, null=False)

    class Meta:
        verbose_name = "Сотрудник (контрагента)"
        verbose_name_plural = "Сотрудники (контрагента)"

    def get_name(self, is_r=False):
        if is_r:
                return f'{self.last_name_r} {self.first_name_r} {self.middle_name_r}'
        return f'{self.last_name} {self.first_name} {self.middle_name}'

    def get_short_name(self, is_r=False):
        if is_r:
            if self.middle_name == None or self.middle_name == "":
                return f'{self.last_name_r} {self.first_name_r[0]}.'
            return f'{self.last_name_r} {self.first_name_r[0]}.{self.middle_name_r[0]}.'
        if self.middle_name == None or self.middle_name == "":
            return f'{self.last_name} {self.first_name[0]}.'
        return f'{self.last_name} {self.first_name[0]}.{self.middle_name[0]}.'
    
    def __str__(self):
        return f'{self.last_name} ({self.position})'


class BankDetails(models.Model):
    organization = models.OneToOneField(
        EducationCenter,
        verbose_name="Организация",
        related_name="bank_details",
        null=False,
        blank=False,
        on_delete=CASCADE
    )
    inn = models.CharField("ИНН", max_length=25, null=False, blank=False)
    kpp = models.CharField("КПП", max_length=25, null=False, blank=False)
    ogrn = models.CharField("ОГРН", max_length=25, null=False, blank=False)
    okpo = models.CharField("ОКПО", max_length=25, null=False, blank=False)
    okved = models.CharField("ОКВЭД", max_length=250, null=False, blank=False)
    oktmo = models.CharField("ОКТМО", max_length=25, null=False, blank=False) 

    bank = models.CharField("Банк", max_length=250, null=False, blank=False)
    bank_inn = models.CharField("Банк ИНН", max_length=25, null=True, blank=True)
    bank_kpp = models.CharField("Банк КПП", max_length=25, null=True, blank=True)
    biс = models.CharField("БИК", max_length=25, null=False, blank=False) 
    account_number = models.CharField("Расчётный счёт", max_length=25, null=False, blank=False)
    personal_account_number = models.CharField("Лицевой счёт", max_length=25, null=True, blank=True) 
    corr_account = models.CharField("К/сч", max_length=25, null=False, blank=False)

    legal_address = models.CharField("Юридический адрес", max_length=500, null=False, blank=False)
    mail_address = models.CharField("Почтовый адрес", max_length=500, null=False, blank=False)
    bank = models.CharField("Банк", max_length=250, null=False, blank=False)
    accountant = models.CharField("Главный бухгалтер", max_length=250, null=True, blank=True)
    phone = models.CharField("Телефон(-ы)", max_length=120, blank=False, null=False)
    email = models.EmailField(_('email address'), unique=True)

    other = models.TextField("Другие реквизиты", null=True, blank=True)
    
    class Meta:
        verbose_name = "Реквизиты организации"
        verbose_name_plural = "Реквизиты организаций"

    def __str__(self):
        return self.organization.name


class Workshop(models.Model):
    name = models.CharField("Название мастерской", max_length=500, null=True, blank=True)
    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", on_delete=CASCADE, related_name='workshops')
    competence = models.ForeignKey(Competence, verbose_name="Компетенция", on_delete=CASCADE, null=True, blank=True, related_name='workshops')
    address = models.CharField("Адрес", max_length=500, null=True, blank=True)
    
    programs = models.ManyToManyField(
        EducationProgram,
        verbose_name='программы', 
        related_name='workshops',
        blank=True
    )
    CLASSES_TYPES = (
        ('T', 'Теоретические занятия'),
        ('P', 'Практические занятия'),
        ('TP', 'Практические и теоретические занятия'),
    )
    classes_type = models.CharField(max_length=4, choices=CLASSES_TYPES, verbose_name='Вид занятий', blank=True, null=True)
    equipment = models.TextField("Оборудование", null=True, blank=True)

    class Meta:
        verbose_name = "Мастерская"
        verbose_name_plural = "Мастерские"

    def __str__(self):
        return f"{self.education_center} ({self.address})"


class Group(models.Model):   
    name = models.CharField("Программа", max_length=750)
    flow_id = models.IntegerField('Идентификатор flow', null=True, blank=True) 
    workshop = models.ForeignKey(Workshop, verbose_name="мастерская", on_delete=CASCADE, related_name='groups', blank=True, null=True)
    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", on_delete=CASCADE, related_name='groups', blank=True, null=True)
    education_program = models.ForeignKey(EducationProgram, verbose_name="Программа обучения", on_delete=CASCADE, related_name='groups', blank=True, null=True)
    start_date = models.DateField("Дата начала обучения", blank=True, null=True)
    end_date = models.DateField("Дата окончания обучения", blank=True, null=True)
    distance_education = models.BooleanField("Дистанционное обучение", default=False)
    mixed_education = models.BooleanField("Смешанное обучение", default=False)
    PAY_STATUSES = [
        ('WFB', "Проверка"),
        ('UPB', "На оплату"),
        ('PDB', "Оплачен"),
    ]
    pay_status = models.CharField(
        "Статус оплаты", max_length=4, default='WFB', choices=PAY_STATUSES)
    GROUP_STATUS_CHOICES = [
        ('NEW', "Создана"),
        ('SED',"В процессе обучения"),
        ('COMP', "Завершила обучение"),
        ('NCOM', "Отменена"),
    ]
    group_status = models.CharField("Статус заявки", max_length=4, default='NEW', choices=GROUP_STATUS_CHOICES)
    group_link = models.CharField("Цифровой след", max_length=500, null=True, blank=True)
    group_commentary = models.TextField(
        "Комментарий", null=True, blank=True, default=""
    )
    is_new_price = models.BooleanField("Новая цена", default=False)
    is_atlas = models.BooleanField("Атлас?", default=False)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
    
    def get_price(self):
        group_price = 0
        for student in self.students.all():
            group_price += student.get_full_price()
        return group_price

    def __str__(self):
        return  f"{self.name}"


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
        return 'media/doc_templates/{0}'.format(filename)
    
    template = models.FileField("Документ", upload_to=template_directory_path)

    class Meta:
        verbose_name = "Шаблон документов"
        verbose_name_plural = "Шаблоны документов"

    def __str__(self):
        return f'{self.name}'


class ContractorsDocument(models.Model):
    creation_date = models.DateTimeField("Дата создания", blank=True, null=True, default=now)
    contractor = models.ForeignKey(
        EducationCenter, 
        verbose_name='подрядчик', 
        related_name='ed_center_documents',
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
        DocumentType, 
        verbose_name="Тип документа",
        null=True,
        blank=False,
        on_delete=CASCADE
    )

    def doc_directory_path(instance, filename):
        return 'media/documents/{0}/{1}'.format(
            instance.contractor.id, filename
        )
    
    doc_file = models.FileField("Документ", upload_to=doc_directory_path)

    class Meta:
        verbose_name = "Документ с подрядчиком"
        verbose_name_plural = "Документы с подрядчиками"

    def __str__(self):
        return f'{self.doc_type} №{self.register_number} ({self.contractor.name})'
    

class AbilimpicsWinner(User):
    is_send = models.BooleanField("Сертификат отправлен", default=False)
    is_received = models.BooleanField("Сертификат получен", default=False)
    competence = models.ForeignKey(
        Competence,
        verbose_name="Компетенция",
        related_name="abilimpics_winners",
        on_delete=DO_NOTHING,
        null=True,
        blank=False
    )
    ed_center = models.ForeignKey(
        EducationCenter,
        verbose_name="Центр обучения",
        related_name="abilimpics_winners",
        on_delete=DO_NOTHING,
        null=True,
        blank=True
    )
    program = models.ForeignKey(
        EducationProgram,
        verbose_name="Программа",
        related_name="abilimpics_winners",
        on_delete=DO_NOTHING,
        null=True,
        blank=True
    )

    objects = CustomUserManager()

    def __str__(self):
        if self.first_name == "":
            return f'{self.email}'
        return f'{self.first_name} {self.last_name}'
    
    class Meta:
        verbose_name = "Участник Абилимпикс"
        verbose_name_plural = "Участники Абилимпикс"
