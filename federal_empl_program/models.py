from django.db import models
from users.models import User
from django.db.models.deletion import DO_NOTHING, CASCADE
from field_history.tracker import FieldHistoryTracker

from django.db.models.fields.related import OneToOneField
from django.utils.timezone import now

from citizens.models import Citizen
from organizations.models import Company
from education_centers.models import Competence, EducationCenterGroup, EducationProgram, EducationCenter, Group

class CitizenCategory(models.Model):
    short_name = models.CharField("Название", max_length=100, blank=False)
    official_name = models.CharField("Офицальное наименованние", max_length=500, blank=True)
    
    def __str__(self):
        return  self.short_name

    class Meta:
        verbose_name = "Категория граждан"
        verbose_name_plural = "Категории граждан"
        

class Application(models.Model):
    legacy_id = models.IntegerField('ID', blank=True, null=True)
    applicant = models.ForeignKey(Citizen, verbose_name="Заявитель", on_delete=CASCADE, related_name='POE_applications')
    creation_date = models.DateTimeField("Дата создания", blank=True, null=True, default=now)
    ADM_STATUS_CHOICES = [
        ('RECA', "Заявка получена"),
        ('CONT', "Связались/Ждём документы"),
        ('RECD', "Получили часть документов"),
        ('CONF', "Подтвердили статус"),
        ('ADM', "Допустили на платформе"),
        ('REF', "Отказали")
    ]
    admit_status = models.CharField("Работа с заявкой", max_length=4, default='RECA', choices=ADM_STATUS_CHOICES)
    APPL_STATUS_CHOICES = [
        ('NEW', "Новая заявка"),
        ('VER', "Верификация"),
        ('ADM', "Допущен"),
        ('SED',"Начал обучение"),
        ('EXAM', "Направлен на экзамен"),
        ('COMP', "Завершил обучение"),
        ('NCOM', "Отказался от обучения"),
        ('NADM', "Отклонено"),
        ('RES', "Резерв"),
        ('OTH', "Другой ФО"),
        ('DUPL', "Дубликат")
    ]
    appl_status = models.CharField("Статус заявки", max_length=4, default='NEW', choices=APPL_STATUS_CHOICES)
    change_status_date = models.DateTimeField("Дата последней смены статуса",null=True, blank=False)

    #Устарело (2021 год), использовать CitizenCategory
    CATEGORY_CHOICES = [
        ('EMPS', "Граждане, ищущие работу и обратившиеся в органы службы занятости, включая безработных граждан"),
        ('JOBS', 'Ищущий работу'),
        ('UEMP', 'Безработный'),
        ('VACK', "Женщины, находящиеся в отпуске по уходу за ребенком в возрасте до трех лет"),
        ('SCHK', "Женщины, имеющие детей дошкольного возраста и не состоящие в трудовых отношениях"),
        ('50+',"Граждане в возрасте 50-ти лет и старше"),
        ('SC', "Граждане предпенсионного возраста")
    ]
    category = models.CharField("Категория слушателя", max_length=50, choices=CATEGORY_CHOICES, default="EMPS")
    
    citizen_category = models.ForeignKey(CitizenCategory, verbose_name="категория", related_name="application", on_delete=DO_NOTHING, blank=True, null=True)
    distance_education = models.BooleanField("Дистанционное обучение", default=False)
    competence = models.ForeignKey(Competence, verbose_name="Компетенция", on_delete=DO_NOTHING, related_name='competence_applicants', blank=True, null=True)
    education_program = models.ForeignKey(EducationProgram, verbose_name="Програма обучения", on_delete=DO_NOTHING, related_name='programm_applicants', blank=True, null=True)
    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", on_delete=DO_NOTHING, related_name='edcenter_applicants', blank=True, null=True)
    ed_center_group = models.ForeignKey(EducationCenterGroup, verbose_name="Предварительная заявка", on_delete=DO_NOTHING, related_name="applications", blank=True, null=True)
    group = models.ForeignKey(Group, verbose_name="Группа", on_delete=DO_NOTHING, related_name='students', blank=True, null=True)
    CONTR_TYPE_CHOICES = [
        ('OLD', "Трехсторонний договор со старым работодателем"),
        ('NEW', "Трехсторонний договор с новым работодателем"),
        ('SELF', "Двухсторонный договор"),
        ('NOT', 'Без договора'),
        ('–', '-')
    ]
    contract_type = models.CharField("Тип контракта", max_length=4, choices=CONTR_TYPE_CHOICES, default='–')
    citizen_consultant = models.ForeignKey(User, verbose_name='Специалист по работе с клиентами', related_name='consulted_applicants', on_delete=models.SET_NULL, blank=True, null=True)
    employer = models.ForeignKey(Company, verbose_name='Работодатель', on_delete=DO_NOTHING, blank=True, null=True)
    empoyment_specialist = models.ForeignKey(User, verbose_name='Специалист по трудоустройству', related_name='consulted_citizens', on_delete=models.SET_NULL, blank=True, null=True)
    ED_TIMELINE_CHOICES = [
        ('CG', "В планируемой группе"),
        ('NG', "В следующей группе"),
        ('OCT', "В октябре"),
        ('NOV', "В ноябре"),
        ('NY', "В следующем году"),
        ('ALR', "Уже зачислен"),
        ('ltr_month', "Позднее чем через месяц"),
        ('month', "В течение месяца"),
        ('week', "В течение 1 недели"),
    ]
    ed_ready_time = models.CharField("Хочет начать учиться", max_length=10, choices=ED_TIMELINE_CHOICES, blank=True, null=True)
    
    #Общее
    consent_pers_data = models.BooleanField("Согласие на обработку перс. данных", default=False)
    pasport = models.BooleanField("Копия паспорт", default=False)
    education_document = models.BooleanField("Копия документа об образ./справка об обучении", default=False)
    resume = models.BooleanField("Резюме", default=False)

    #Граждане, ищущие работу
    worksearcher_certificate = models.BooleanField("Справка о регистрации в качестве лица, ищущего работу", default=False)
    
    #Безработные граждане
    workbook = models.BooleanField("Копия трудовой книжки", default=False)
    unemployed_certificate = models.BooleanField("Выписка о регистрации в качестве безработного", default=False)

    #Граждане предпенсионного возраста
    senior_certificate = models.BooleanField("Справка об отнесении к категории пред пенсионера", default=False)

    #Женщины, находящиеся в отпуске по уходу за ребенком
    parental_leave_confirm = models.BooleanField("Копия документа, подтверждающего нахождение в отпуске по уходу за ребенком", default=False)
    birth_certificate = models.BooleanField("Копия свидетельства о рождении ребенка", default=False)

    #Женщины, не состоящие в трудовых отношениях и имеющие детей дошкольного возраста
    birth_certificate_undr_seven = models.BooleanField("Копия свидетельства о рождении ребенка (младше 7 лет)", default=False)
    notIP_certificate = models.BooleanField("Cправка об отсутствии статуса ИП", default=False)

    ib_course = models.BooleanField("Курсы ИП", default=False)
    is_enrolled = models.BooleanField("Приказ о зачисл.", default=False)
    is_deducted = models.BooleanField("Приказ об отчисл.", default=False)
    is_working = models.BooleanField("Трудоустроен до начала обучения", default=False)
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
    field_history = FieldHistoryTracker(['find_work'])

    @property
    def _field_history_user(self):
        return self.updated_by
        
    class Meta:
        verbose_name = "Заявка (Содействие занятости)"
        verbose_name_plural = "Заявки (Содействие занятости)"
    
    def __str__(self):
        appl_status = ""
        for appl_status_type in self.APPL_STATUS_CHOICES:
            if appl_status_type[0] == self.appl_status:
                appl_status = appl_status_type[1]
        return  f"{self.applicant} ({appl_status})"

class InteractionHistory(models.Model):
    application = models.ForeignKey(Application, verbose_name='История взаимодействия', related_name="interactions", on_delete=CASCADE)
    creation_time = models.DateTimeField("Дата",default=now)
    interaction_date = models.DateField("Дата",default=now)
    COMMUNICATION_TYPES = [
        ('PHN','Телефон'),
        ('EML','Email'),
        ('OFF','Оффлайн')
    ]
    comunication_type = models.CharField('Канал связи', max_length=3, choices=COMMUNICATION_TYPES)
    short_description = models.TextField('Краткое описание', max_length=2000)

    class Meta:
        verbose_name = "Взаимодействие с гражданином"
        verbose_name_plural = "История взаимодействия"
        get_latest_by = "interaction_date"

class Questionnaire(models.Model):
    applicant = OneToOneField(Application, on_delete=CASCADE, primary_key=True, related_name='anketa')
    TIME_SLOTS = [
        ('MRNG', "09.00-13.00"),
        ('DAYT', "13.00-17.00"),
        ('EVNG', "17.00-21.00")
    ]
    convenient_study_periods = models.CharField("Удобное время занятий", max_length=4, blank=True, null=True, choices=TIME_SLOTS)
    PURPOSE_CHOICES = [
        ('RECA', "Открытие своего дела (ИП или самозанятость)"),
        ('CONT', "Сохранение текущего места работы"),
        ('RECD', "Трудоустройство на новую работу"),
        ('CONF', "Саморазвитие"),
    ]
        
    purpose = models.CharField("Цель", max_length=4, blank=True, null=True, choices=PURPOSE_CHOICES)
    need_consultation = models.BooleanField("Нужна ли консультация по самозаятости", default=False)
    CONTR_TYPE_CHOICES = [
        ('OLD', "Трехсторонний договор со старым работодателем"),
        ('NEW', "Трехсторонний договор с новым работодателем"),
        ('SELF', "Двухсторонный договор"),
        ('NOT', 'Без договора')
    ]
    pref_contract_type = models.CharField("Предпочитаемый тип контракта", max_length=4, choices=CONTR_TYPE_CHOICES, blank=True, null=True)
    
    class Meta:
        verbose_name = "Анкета"
        verbose_name_plural = "Анкета"
        
    
    def __str__(self):
        return  f"{self.applicant} (анкета)"


class CategoryInstruction(models.Model):
    category = models.ForeignKey(CitizenCategory, verbose_name="категория", related_name="instructions", on_delete=DO_NOTHING, blank=True, null=True)
    subject = models.CharField("Тема письма", max_length=150)
    text = models.TextField("Текст")
    html = models.TextField("HTML")

    class Meta:
        verbose_name = "Инструкция"
        verbose_name_plural = "Инструкции"
        
    
    def __str__(self):
        return self.category.short_name