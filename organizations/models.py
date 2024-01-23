from django.db import models



class Organization(models.Model):
    name = models.CharField("Название организации", max_length=250)


    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return  f"{self.name}"

