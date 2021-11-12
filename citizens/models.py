from django.db import models
from django.db.models.enums import Choices
from field_history.tracker import FieldHistoryTracker
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User
from organizations.models import Company

class School(models.Model):
    name = models.CharField("Название школы", max_length=100)
    specialty = models.CharField("Уклон школы", max_length=50, blank=True, null=True)

    TER_CHOICES = [
        ('TADM', "Тольяттинское управление министерства образования и науки Самарской области"),
        ('NWADM', "Северо-Западное управление"),
        ('WADM', "Западное управление"),
        ('SWADM', "Юго-Западное управление"),
        ('POVADM', "Поволжское управление"),
        ('SADM', "Южное управление"),
        ('DEPSAM', "Департамент образования Администрации городского округа Самара"),
        ('SEADM', "Юго-Восточное управление"),
        ('OTRADM', "Отрадненское управление"),
        ('CENTADM', "Центральное управление"),
        ('NEADM', "Северо-Восточное управление"),
        ('DEPTOL', "Департамент образования Администрации городского округа Тольятти"),
        ('NADM', "Северное управление"),
        ('KINADM', "Кинельское управление"),
        ('SAMADM', "Самарское управление"),
    ]
    territorial_administration = models.CharField("Тер. управление", choices=TER_CHOICES, max_length=20, blank=True, null=True)

    city = models.CharField("Населённый пункт", max_length=100, blank=True, null=True)
    adress = models.CharField("Адрес", max_length=250, blank=True, null=True)
    school_coordinators = models.ManyToManyField(User, verbose_name="Педагоги-навигаторы", related_name="coordinated_schools", blank=True)
    is_bilet = models.BooleanField('Есть педагог-навигатор', default=False)
    inn = models.CharField("ИНН", max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Школа"
        verbose_name_plural = "Школы"

    def __str__(self):
        return  f"{self.name}({self.city})"
    
class SchoolClass(models.Model):
    school = models.ForeignKey(School, verbose_name="Школа", related_name="classes", on_delete=CASCADE)
    grade_number = models.IntegerField("Номер класса", validators=[MaxValueValidator(11),MinValueValidator(1)])
    grade_letter = models.CharField("Буква класса", max_length=4)
    specialty = models.CharField("Уклон класса", max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"

    def __str__(self):
        return  f"{self.grade_number}{self.grade_letter} – {self.school}"


class DisabilityType(models.Model):
    name = models.CharField("ОВЗ", max_length=100)
    description = models.CharField("Описание", max_length=300, blank=True, null=True)

    class Meta:
        verbose_name = "Инвалидность"
        verbose_name_plural = "Инвалидности"

    def __str__(self):
        return  f"{self.name}"


class Citizen(models.Model):
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

    snils_number = models.CharField("Номер СНИЛС", max_length=11, blank=True, null=True)
    inn_number = models.CharField("ИНН", max_length=30, blank=True, null=True)

    res_region = models.CharField("Регион проживания", max_length=150, blank=True, null=True)
    res_city = models.CharField("Населённый пункт", max_length=150, blank=True, null=True)
    res_disctrict = models.CharField("Населённый пункт", max_length=50, blank=True, null=True)

    STATUS_CHOICES = [
        ('SCHT', "Учитель в школе"),
        ('SCHS', "Обучающиеся общеообразовательных организаций"),
        ('SSPO',"студент СПО"),
        ('SVO', "студент ВО"),
        ('EMP', "Cотрудник предприятия"),
        ('SC', "Гражданин предпенсионного возраста"),
        ('50+', "Гражданин старше 50-ти лет"),
        ('UEMP', "Безработный гражданин (статус ЦЗН)"),
        ('EMPS', "Гражданин, ищущий работу (статус ЦЗН)"),
        ('OTHR', "Другой")
    ]
    social_status = models.CharField("Социальный статус", max_length=4, choices=STATUS_CHOICES, blank=True, null=True)
    school = models.ForeignKey(School, verbose_name="Школа", related_name="students", blank=True, null=True, on_delete=DO_NOTHING)
    school_class = models.ForeignKey(SchoolClass, verbose_name="Школный класс", related_name="students", blank=True, null=True, on_delete=DO_NOTHING)
    EDUCATION_CHOICES = [
        ('SPO', "СПО"),
        ('VO', "ВО"),
        ('SSPO', "Cтудент ВО"),
        ('SVO', "Cтудент СПО"),
        ('11', '11 классов'),
        ('9', '9 классов'),
        ('OTHR', "Другой")
    ]
    education_type = models.CharField("Образование", max_length=4, choices=EDUCATION_CHOICES, blank=True, null=True)
    self_employed = models.BooleanField("Самозанятый", default=False)
    is_employed = models.BooleanField("Трудоустроен", default=False)
    is_verified = models.BooleanField("Верифицирован", default=False)
    copp_registration = models.BooleanField("Зарегистрирован на copp63.ru", default=False)
    disability_type = models.ForeignKey(DisabilityType, verbose_name="ОВЗ", on_delete=DO_NOTHING, blank=True, null=True)

    field_history = FieldHistoryTracker(['is_employed', 'self_employed', 'is_verified'])

    class Meta:
        verbose_name = "Гражданин"
        verbose_name_plural = "Граждане"

    def __str__(self):
        if self.middle_name is not None:
            return  f'{self.last_name} {self.first_name} {self.middle_name}'
        return f'{self.last_name} {self.first_name}'

class Job(models.Model):
    worker = models.ForeignKey(Citizen, on_delete=CASCADE, related_name='jobs')

    place_of_work = models.ForeignKey(Company, verbose_name="Место работы", on_delete=DO_NOTHING, related_name='employees')
    position = models.CharField("Должность", max_length=50)

    start_date = models.DateField("Дата начала работы")
    end_date = models.DateField("Дата окончания работы")
    
    class Meta:
        verbose_name = "Работа"
        verbose_name_plural = "Работы"

    def __str__(self):
        if self.end_date is not None:
            return  f"{self.position}, {self.place_of_work} ({self.start_date} – {self.end_date})"
        else:
            return  f"{self.position}, {self.place_of_work} (c {self.start_date})"
