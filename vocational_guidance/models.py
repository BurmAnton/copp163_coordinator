import datetime
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ForeignKey

from users.models import User, Group
from citizens.models import Citizen, School, DisabilityType
from education_centers.models import EducationCenter, EducationProgram, Workshop

class VocGuidTest(models.Model):
    name = models.CharField("Название пробы", max_length=300, default="")
    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", related_name="voc_guid_sessions", on_delete=CASCADE)
    education_program_link = models.URLField("Программа обучения (ссылка)", max_length=200, blank=True, null=True)
    AGE_GROUP_CHOICES = [
        ('6-7', "6-7 класс"),
        ('8-9',"8-9 класс"),
        ('10-11', "10-11 класс"),
        ('ALL', "Единая")
    ]
    age_group = models.CharField("Возрастная группа", max_length=5, choices=AGE_GROUP_CHOICES, blank=True, null=True)
    participants = models.ManyToManyField(Citizen, verbose_name="Участники", related_name="voc_guid_tests", blank=True)
    THEMES_CHOICES = [
        ('HLTH', "Здоровая среда"),
        ('CMFRT',"Комфортная сред"),
        ('SAFE', "Безопасная среда"),
        ('SMRT', "Умная среда"),
        ('CRTV', "Креативная среда"),
        ('SCL', "Социальная среда"),
        ('BSNSS', "Деловая среда"),
        ('INDST', "Индустриальная среда")
    ]
    thematic_env = models.CharField("Проф. среда", max_length=5, choices=THEMES_CHOICES, blank=True, null=True)
    description = models.TextField("Описание", blank=True, null=True, default="")
    img_link = models.CharField("Ссылка на изображение", max_length=250, blank=True, null=True, default="")
    attendance_limit = models.IntegerField("Максимальное кол-во участников", default=8)
    workshop = models.ForeignKey(Workshop, verbose_name="Место проведения", on_delete=CASCADE, blank=True, null=True)
    
    TYPE_CHOICES = [
        ('SPO', "На площадке исторический парк «Россия – Моя история»"),
        ('VO', "В онлайн формате"),
        ('EC', "На базе ЦО")
    ]
    guid_type = models.CharField("Тип проб", max_length=4, choices=TYPE_CHOICES, default="VO")
    disability_types = models.ManyToManyField(DisabilityType, verbose_name="ОВЗ", blank=True)
    
    class Meta:
        verbose_name = "Проф. проба"
        verbose_name_plural = "Проф. пробы"

    def __str__(self):
        return  f"{self.name} ({self.id})"


class TestContact(models.Model):
    test = models.OneToOneField(VocGuidTest, verbose_name="Проф. проба", related_name="contact", on_delete=models.CASCADE)
    full_name = models.CharField("ФИО преподователя", max_length=300, null=True, blank=True)
    email = models.EmailField("Email преподователя", max_length=300, null=True, blank=True)
    phone = models.CharField("Телефон преподователя", max_length=300, null=True, blank=True)

    class Meta:
        verbose_name = "Контакты преподавателя"
        verbose_name_plural = "Контакты преподователей"

    def __str__(self):
        return  f"{self.test} ({self.full_name})"


class VocGuidGroup(models.Model):
    participants = models.ManyToManyField(Citizen, verbose_name="Участники", related_name='voc_guid_groups')
    AGE_GROUP_CHOICES = [
        ('6-7', "6-7 класс"),
        ('8-9',"8-9 класс"),
        ('10-11', "10-11 класс"),
    ]
    age_group = models.CharField("Возрастная группа", max_length=5, choices=AGE_GROUP_CHOICES, blank=True, null=True)
    attendance_limit = models.IntegerField("Максимальное кол-во участников", default=8)
    school = models.ForeignKey(School, verbose_name="Школа", related_name="guid_groups", on_delete=CASCADE, blank=True, null=True)
    bundle = models.ForeignKey(VocGuidTest, verbose_name="Бандл", related_name="groups", on_delete=CASCADE, blank=True, null=True)
    city = models.CharField("Населённый пункт", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Группа по проф. ориентации"
        verbose_name_plural = "Группы по проф. ориентации"

    def __str__(self):
        return  f"{self.bundle} {self.school} {self.age_group} класс (ID: {self.id})"


class TimeSlot(models.Model):
    date = models.DateField("Дата")
    SLOT_CHOICES = [
        ("MRN", "с 10:00 до 11:30"),
        ("MID", "с 15:00 до 16:30"),
        ("EVN", "с 16:30 до 18:00"),
    ]
    slot = models.CharField("Временной промежуток", max_length=5, choices=SLOT_CHOICES)
    group = models.ManyToManyField(VocGuidGroup, related_name="slots", verbose_name="Группы", blank=True)
    participants_count = models.IntegerField("Колво участников", default=0, validators=[MaxValueValidator(8),MinValueValidator(0)])
    test = models.ForeignKey(VocGuidTest, verbose_name="Пробы", related_name="slots", blank=True, null=True, on_delete=CASCADE)
    zoom_link = models.URLField("Ссылка на конференцию (zoom)", max_length=400, blank=True, null=True)
    report_link = models.URLField("Отчетная ссылка", max_length=400, blank=True, null=True)

    class Meta:
        verbose_name = "Слот"
        verbose_name_plural = "Слоты"

    def __str__(self):
        return  f"{self.id} {self.test} – {self.date} {self.slot}"


class VocGuidAssessment(models.Model):
    participant = models.ForeignKey(
        Citizen, related_name="voc_guid_assessment", 
        verbose_name="Участник", on_delete=CASCADE
    )
    test = models.ForeignKey(
        VocGuidTest, related_name="assessments", 
        verbose_name="Проба", on_delete=CASCADE
    )
    slot = models.ForeignKey(
        TimeSlot, related_name="assessments", 
        verbose_name="Слот", on_delete=CASCADE
    )
    attendance = models.BooleanField("Посещаемость", default=False)

    class Meta:
        verbose_name = "Ассесмент"
        verbose_name_plural = "Ассесмент"

    def __str__(self):
        cl_group = Group.objects.filter(name='Координатор')
        if len(cl_group) != 0:
            cl_group = cl_group[0]
            school = self.participant.school
            teacher = User.objects.filter(coordinated_schools=school, groups=cl_group)
            if len(teacher) !=0:
                teacher = teacher[0]
                if teacher.phone_number is None:
                    return f"{self.participant.school} {teacher} (–; {teacher.email})"
                return f"{self.participant.school} {teacher} ({teacher.phone_number}; {teacher.email})"
        return  f"{self.participant.school}"
