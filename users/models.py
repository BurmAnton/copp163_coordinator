from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager

class User(AbstractUser):
    username = None
    middle_name = models.CharField("Отчество", max_length=30, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField("Номер телефона", max_length=20, blank=True, null=True)
    code = models.CharField("Код подтверждения", max_length=10, blank=True, null=True, default=None)

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
