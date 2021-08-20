from django.db import models
from field_history.tracker import FieldHistoryTracker
from django.db.models.deletion import DO_NOTHING, CASCADE

from organizations.models import Company

class Citizen(models.Model):
    first_name = models.CharField("Имя", max_length=30)
    last_name = models.CharField("Фамилия", max_length=50)
    middle_name = models.CharField("Отчество", max_length=30, blank=True, null=True)

    SEX_CHOICES = [
        ('M', "Мужской"),
        ('F', "Женский")
    ]
    sex = models.CharField("Пол", max_length=1, choices=SEX_CHOICES, blank=True, null=True)

    email = models.EmailField("Email", max_length=320, blank=True, null=True)
    phone_number = models.CharField("Номер телефона", max_length=16, blank=True, null=True)

    snils_number = models.CharField("Номер СНИЛС", max_length=11, blank=True, null=True)
    inn_number = models.CharField("ИНН", max_length=30, blank=True, null=True)

    res_region = models.CharField("Регион проживания", max_length=50, blank=True, null=True)
    res_city = models.CharField("Населённый пункт", max_length=50, blank=True, null=True)
    res_disctrict = models.CharField("Населённый пункт", max_length=50, blank=True, null=True)

    STATUS_CHOICES = [
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
