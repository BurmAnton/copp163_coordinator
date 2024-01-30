from django.db import models
from django.db.models.deletion import CASCADE


class Region(models.Model):
    name = models.CharField(
        "Название субъекта", max_length=100, 
        blank=False, null=False
    )
    
    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = "Субъект РФ"
        verbose_name_plural = "Субъекты РФ"


class TerAdministration(models.Model):
    name = models.CharField(
        "Тер. управление", max_length=100, 
        blank=False, null=False
    )
    region = models.ForeignKey(
        Region, on_delete=CASCADE, 
        related_name="ter_administrations", 
        verbose_name="Субъект Российской Федерации"
    )
    
    def __str__(self):
        return  self.name
        
    class Meta:
        verbose_name = "Тер. управление"
        verbose_name_plural = "Тер. управления"


class CityType(models.Model):
    name = models.CharField(
        "Название", max_length=100, 
        blank=False, null=False
    )
    short_name = models.CharField(
        "Сокращение", max_length=15, blank=False, null=False
    )

    def __str__(self):
        return  self.short_name

    class Meta:
        verbose_name = "Тип населённого пункта"
        verbose_name_plural = "Типы населённых пунктов"


class City(models.Model):
    name = models.CharField(
        "Название", max_length=100, blank=False, null=False
    )
    city_type = models.ForeignKey(
        CityType, on_delete=CASCADE, 
        related_name="cities", 
        verbose_name="Тип населённого пункта"
    ) 
    region = models.ForeignKey(
        Region, on_delete=CASCADE, 
        related_name="cities", 
        verbose_name="Субъект Российской Федерации"
    )

    def __str__(self):
        return  f"{self.name}"

    class Meta:
        verbose_name = "Населённый пункт"
        verbose_name_plural = "Населённые пункты"