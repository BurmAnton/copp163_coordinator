from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager

class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
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
