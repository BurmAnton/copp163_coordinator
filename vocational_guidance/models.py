from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.core.exceptions import ValidationError

from citizens.models import Citizen
from education_centers.models import EducationCenter, EducationProgram, Workshop

class VocGuidGroup(models.Model):
    participants = models.ManyToManyField(
        Citizen, 
        verbose_name="Участники", 
        related_name='voc_guid_groups'
    )
    AGE_GROUP_CHOICES = [
        ('6-7', "6-7 класс"),
        ('8-9',"8-9 класс"),
        ('10-11', "10-11 класс"),
    ]
    age_group = models.CharField("Возрастная группа", max_length=5, choices=AGE_GROUP_CHOICES)

    class Meta:
        verbose_name = "Группа по проф. ориентации"
        verbose_name_plural = "Группы по проф. ориентации"

    def __str__(self):
        return  f"Группа №{self.id}"

class VocGuidBundle(models.Model):
    name = models.CharField("Название пакета", max_length=100, blank=True, null=True, default="")
    description = models.TextField("Описание", blank=True, null=True, default="")
    img_link = models.CharField("Ссылка на изображение", max_length=250, blank=True, null=True, default="")
    programs = models.ManyToManyField(EducationProgram, verbose_name="Список проб")
    education_center = models.ForeignKey(EducationCenter, verbose_name="Организатор", on_delete=CASCADE, blank=True, null=True)
    workshop = models.ForeignKey(Workshop, verbose_name="Место проведения", on_delete=CASCADE, blank=True, null=True)
    participants = models.ManyToManyField(
        Citizen, 
        verbose_name="Участники", 
        related_name='voc_guid_bundles',
        blank=True, 
        null=True
    )
    TYPE_CHOICES = [
        ('SPO', "Моя Россия"),
        ('VO', "Онлайн")
    ]
    guid_type = models.CharField("Тип проб", max_length=4, choices=TYPE_CHOICES, blank=True, null=True)
    
    class Meta:
        verbose_name = "Бандл"
        verbose_name_plural = "Бандлы"

    def __str__(self):
        return  f"Набор №{self.id}"

class TimeSlot(models.Model):
    date = models.DateField("Дата")
    start_time = models.TimeField("Время начала")
    end_time = models.TimeField("Время завершения")
    groups = models.ManyToManyField(VocGuidGroup, verbose_name="Группы")
    bundle = models.ForeignKey(VocGuidBundle, verbose_name="Пробы", blank=True, null=True, on_delete=DO_NOTHING)
    education_center = models.ForeignKey(EducationCenter, verbose_name="Организатор проб", blank=True, null=True, on_delete=DO_NOTHING)

    def clean(self, *args, **kwargs):
        if self.groups.count() > 3:
            raise ValidationError("You can't assign more than three groups")

    class Meta:
        verbose_name = "Слот"
        verbose_name_plural = "Слоты"

    def __str__(self):
        return  f"{self.start_time}-{self.end_time} {self.date} ({self.education_center})"