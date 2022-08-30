import datetime 
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ForeignKey

from users.models import User, Group
from citizens.models import Citizen, School, DisabilityType
from education_centers.models import EducationCenter, Workshop, Competence

class City(models.Model):
    name = models.CharField("Название", max_length=100, blank=False, null=False)

    def __str__(self):
        return  f"{self.city_type} {self.name}"

    class Meta:
        verbose_name = "Населённый пункт"
        verbose_name_plural = "Населённые пункты"

class Address(models.Model):
    city = models.ForeignKey(
        City, 
        on_delete=CASCADE, 
        related_name="addresses", 
        verbose_name="Населённый пункт"
    )
    street = models.CharField("Улица", max_length=200, blank=False, null=False)
    building_number = models.CharField("Дом", max_length=10, blank=False, null=False)
    floor = models.IntegerField("Этаж", blank=True, null=True)
    apartment = models.CharField("Аудитория", max_length=10, blank=True, null=True)

    def __str__(self):
        if self.floor is not None and self.apartment is not None:
            return f'{self.city}, ул. {self.street}, дом №{self.building_number}, {self.floor} этаж, каб. {self.apartment}'
        if self.apartment is not None:
            return f'{self.city}, ул. {self.street}, дом {self.building_number}, каб. {self.apartment}'
        return f'{self.city}, ул. {self.street}, дом {self.building_number}'
    
    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

class VocGuidTest(models.Model):
    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", related_name="voc_guid_sessions", on_delete=CASCADE)

    name = models.CharField("Название пробы", max_length=500, default="")
    competence = models.ForeignKey(Competence, verbose_name="Компетенция", related_name="voc_guids", on_delete=CASCADE, blank=True, null=True)
    short_description = models.CharField("Краткое описание", blank=False, null=False, max_length=130)
    description = models.TextField("Описание", blank=False, null=False)
    
    participants = models.ManyToManyField(Citizen, verbose_name="Участники", related_name="voc_guid_tests", blank=True)
    attendance_limit = models.IntegerField("Лимит участников", default=8)
    participants_count = models.IntegerField("Колво участников", default=0)

    start_datetime = models.DateTimeField('Дата и время начала', blank=False, null=False, default=datetime.datetime.now())

    is_online = models.BooleanField("Онлайн", default=True)
    conference_data = models.CharField("данные для подключения", blank=True, null=True, max_length=350)
    address = models.ForeignKey(Address, verbose_name="Адресс", on_delete=CASCADE, blank=True, null=True)
        
    class Meta:
        verbose_name = "Проф. проба"
        verbose_name_plural = "Проф. пробы"

    def __str__(self):
        return  f"{self.name} ({self.id})"


class Assessment(models.Model):
    test = models.ForeignKey(VocGuidTest, verbose_name="Проба", related_name="assessment", on_delete=models.CASCADE)
    grade = models.IntegerField("Оценка", validators=[MinValueValidator(1),MaxValueValidator(3)], null=True, blank=True)
    criterion = models.CharField("Название критерия", max_length=70, blank=False, null=True)
    citizen = models.ForeignKey(Citizen, verbose_name="Ученик", related_name="assessment", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Ассессмент"
        verbose_name_plural = "Ассессмент"


class Attendance(models.Model):
    timeslot = models.ForeignKey(VocGuidTest, verbose_name="Проба",related_name="attendance", on_delete=models.CASCADE)
    is_attend = models.BooleanField("Посетил", default=False)
    citizen = models.ForeignKey(Citizen, verbose_name="Ученик", related_name="attendance", on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Посещаемость"
        verbose_name_plural = "Посещаемость"


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


    