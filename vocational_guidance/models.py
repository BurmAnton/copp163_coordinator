import datetime

from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ForeignKey

from users.models import User
from citizens.models import Citizen, School
from education_centers.models import EducationCenter, EducationProgram, Workshop

class EducatorNavigator(User):
    school = models.ForeignKey(School, verbose_name="Школа", related_name="ed_navs", on_delete=CASCADE)
        
    class Meta:
        verbose_name = "Педагог-навигатор"
        verbose_name_plural = "Педагоги-навигаторы"

class VocGuidTest(models.Model):
    name = models.CharField("Название пробы", max_length=100, default="")
    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", related_name="voc_guid_sessions", on_delete=CASCADE)
    education_program_link = models.URLField("Программа обучения (ссылка)", max_length=200)
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

    class Meta:
        verbose_name = "Проф. проба"
        verbose_name_plural = "Проф. пробы"

    def __str__(self):
        return  f"{self.name}"


class VocGuidGroup(models.Model):
    participants = models.ManyToManyField(Citizen, verbose_name="Участники", related_name='voc_guid_groups')
    AGE_GROUP_CHOICES = [
        ('6-7', "6-7 класс"),
        ('8-9',"8-9 класс"),
        ('10-11', "10-11 класс"),
    ]
    age_group = models.CharField("Возрастная группа", max_length=5, choices=AGE_GROUP_CHOICES, blank=True, null=True)
    attendance_limit = models.IntegerField("Максимальное кол-во участников", default=50)
    school = models.ForeignKey(School, verbose_name="Школа", related_name="guid_groups", on_delete=CASCADE, blank=True, null=True)
    bundle = models.ForeignKey(VocGuidTest, verbose_name="Бандл", related_name="groups", on_delete=CASCADE, blank=True, null=True)
    city = models.CharField("Населённый пункт", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Группа по проф. ориентации"
        verbose_name_plural = "Группы по проф. ориентации"

    def __str__(self):
        return  f"{self.id}"

class TimeSlot(models.Model):
    date = models.DateField("Дата")
    start_time = models.TimeField("Время начала")
    end_time = models.TimeField("Время завершения")
    groups = models.ManyToManyField(VocGuidGroup, verbose_name="Группы")
    bundle = models.ForeignKey(VocGuidTest, verbose_name="Пробы", blank=True, null=True, on_delete=DO_NOTHING)
    education_center = models.ForeignKey(EducationCenter, verbose_name="Организатор проб", blank=True, null=True, on_delete=DO_NOTHING)

    def clean(self, *args, **kwargs):
        if self.groups.count() > 3:
            raise ValidationError("You can't assign more than three groups")

    class Meta:
        verbose_name = "Слот"
        verbose_name_plural = "Слоты"

    def __str__(self):
        return  f"{self.start_time}-{self.end_time} {self.date} ({self.education_center})"
