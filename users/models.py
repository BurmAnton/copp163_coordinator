from datetime import datetime

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class DisabilityType(models.Model):
    name = models.CharField("ОВЗ", max_length=100)
    description = models.CharField("Описание", max_length=300, blank=True, 
                                   null=True)

    def __str__(self):
        return  f"{self.name}"

    class Meta:
        verbose_name = "Инвалидность"
        verbose_name_plural = "Инвалидности"

class User(AbstractUser):
    username = None
    middle_name = models.CharField("Отчество", max_length=30, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField("Номер телефона", max_length=20, blank=True, null=True)
    code = models.CharField("Код подтверждения", max_length=10, blank=True, null=True, default=None)

    ROLES = (
        ('CTZ', 'Гражданин'),
        ('CO', 'Представитель ЦО'),
        ('COR', 'Координатор'),
        ('BLM', 'Участник Абилимпикса'),
        ('CNT', 'Бухгалтер')
    )
    role = models.CharField(max_length=3, choices=ROLES, verbose_name='Роль', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        if self.first_name == "":
            return f'{self.email}'
        return f'{self.first_name} {self.last_name}'
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Group(Group):
    
    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Permission(Permission):
    pass


class Organization(models.Model):
    name = models.CharField("Название организации", max_length=250)


    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return  f"{self.name}"