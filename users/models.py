from datetime import datetime
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.deletion import DO_NOTHING, CASCADE

from .managers import CustomUserManager

class User(AbstractUser):
    username = None
    middle_name = models.CharField("Отчество", max_length=30, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField("Номер телефона", max_length=20, blank=True, null=True)
    code = models.CharField("Код подтверждения", max_length=10, blank=True, null=True, default=None)

    ROLES = (
        ('CTZ', 'Гражданин'),
        ('CO', 'Представитель ЦО'),
        ('COR', 'Координатор')
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


class PartnerOrganization(models.Model):
    name = models.CharField("Название организации", max_length=250, blank=False, null=False)
    organization_inn = models.CharField("ИНН Организации", max_length=20, blank=False, null=False)
    ORG_TYPES = (
        ('ECSPO', 'ЦО СПО'),
        ('ECVO', 'ЦО ВО'),
        ('ECP', 'ЦО частные'),
        ('SCHL', 'СОУ'),
        ('GOV', 'Гос. орган'),
        ('OTH', 'Другие')
    )
    organization_type = models.CharField(max_length=5, choices=ORG_TYPES, verbose_name='Роль', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Органзация партнёр"
        verbose_name_plural = "Органзации партнёры"


class Project(models.Model):
    project_name = models.CharField("Название проекта", max_length=250, blank=False, null=False)

    def __str__(self):
        return self.project_name

    class Meta:
        verbose_name = "Проекты"
        verbose_name_plural = "Проект"


class PartnerContact(models.Model):
    user = models.ForeignKey(User, related_name="пользователь", on_delete=DO_NOTHING, blank=True, null=True)

    first_name = models.CharField("Имя", max_length=30, blank=False, null=False)
    middle_name = models.CharField("Отчество", max_length=30, blank=True, null=True)
    last_name = models.CharField("Фамилия", max_length=30, blank=False, null=False)

    organization = models.ForeignKey(PartnerOrganization, related_name="Организация", on_delete=CASCADE, blank=False, null=False)
    job_title = models.CharField("Должность", max_length=100, blank=False, null=False)
    projects = models.ManyToManyField(Project, related_name="partners", verbose_name="Проекты", blank=True)

    commentary = models.TextField("Комментарий", blank=True, null=True)

    def __str__(self):
        return self.last_name

    class Meta:
        verbose_name = "Контакты партнёра"
        verbose_name_plural = "Контакты партнёров"


class PartnerContactEmail(models.Model):
    contact = models.ForeignKey(PartnerContact, verbose_name="Контакт", related_name="emails", on_delete=CASCADE)
    email = models.EmailField(_("email address"), max_length=254, unique=False)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Контактная почта"
        verbose_name_plural = "Контактные почты"


class PartnerContactPhone(models.Model):
    contact = models.ForeignKey(PartnerContact, verbose_name="Контакт", related_name="phones", on_delete=CASCADE)
    phone = models.CharField("Контактный телефон", max_length=20, blank=True, null=True)

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name = "Контактный телефон"
        verbose_name_plural = "Контактные телефоны"


class DistributionEmail(models.Model):
    email = models.EmailField(_("email address"), max_length=254, unique=True)
    
    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Рассылочный email"
        verbose_name_plural = "Почтовые ящики для рассылки"

class MailAttachFile(models.Model):
    name = models.CharField("Название файла", max_length=100, blank=False, null=False)
    attached_file = models.FileField("Прикреплённый файл", upload_to='media/email_attached/')
    upload_date_time = models.DateTimeField("Дата и время загрузки", default=datetime.now(), blank=False, null=False)

    def __str__(self):
        if self.name == None:
            return self.attached_file
        return self.name

