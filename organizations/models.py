from django.db import models
from django.db.models.deletion import CASCADE

class Company(models.Model):
    company_name = models.CharField("Место работы", max_length=50)
    region = models.CharField("Регион", max_length=50)
    city = models.CharField("Город", max_length=50)
    prof_area = models.CharField("Проф. область", max_length=50)
    
    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return  f"{self.company_name}"

class ContactPersone(models.Model):
    company = models.OneToOneField(Company, verbose_name="Контактное лицо", on_delete=CASCADE)

    first_name = models.CharField("Имя", max_length=30)
    last_name = models.CharField("Фамилия", max_length=50)
    middle_name = models.CharField("Отчество", max_length=30, blank=True, null=True)

    email = models.EmailField("Email", max_length=320, blank=True, null=True)
    phone_number = models.CharField("Номер телефона", max_length=16, blank=True, null=True)

    class Meta:
        verbose_name = "Контактное лицо"
        verbose_name_plural = "Контактные лица"

    def __str__(self):
        return  f"{self.first_name} {self.first_name} ({self.company})"

class Vacancy(models.Model):
    company = models.ForeignKey(Company, verbose_name="Компания", on_delete=CASCADE, related_name='vacancies')
    job_title = models.CharField("Имя", max_length=50, default='')
    salary = models.IntegerField('Зарплата', blank=True, null=True)

    class Meta:
        verbose_name = "Вакасия"
        verbose_name_plural = "Вакансии"

    def __str__(self):
        return  f"{self.job_title (self.company)}"

