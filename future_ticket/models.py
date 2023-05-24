from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.utils.translation import gettext_lazy as _

from education_centers.models import Competence, EducationProgram, \
                                     EducationCenter,Group, Employee

# Create your models here.
class TicketProjectYear(models.Model):
    year = models.IntegerField(_('year'), null=False, blank=False)
    programs = models.ManyToManyField(
        EducationProgram,
        verbose_name="Программы",
        related_name="ticket_project_years",
        blank=True
    )

    def __str__(self):
        return  str(self.year)

    class Meta:
        verbose_name = "Год проекта (БВБ)"
        verbose_name_plural = "Годы проекта (БВБ)"


class EducationCenterTicketProjectYear(models.Model):
    ed_center = models.ForeignKey(
        EducationCenter, 
        verbose_name="Центр обучения",
        related_name="ticket_project_years",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    project_year = models.ForeignKey(
        TicketProjectYear, 
        verbose_name="Год проекта (БВБ)",
        related_name="ed_centers",
        null=False, 
        blank=False,
        on_delete=models.CASCADE
    )
    STAGES = [
        ('FLLNG', "заполнение заявки"),
        ('VRFD', "заявка проверена"),
        ('FRMD', "документы сформированы"),
        ('PRVD', "заявка принята"),
    ]
    appl_docs_link = models.TextField('Ссылка на комп. документов', default="")
    stage = models.CharField("Работа с заявкой", max_length=5, 
                             default='FLLNG', choices=STAGES)
    quota = models.IntegerField('Квота', null=False, blank=False, default=0)

    def __str__(self):
        return  f'{self.ed_center} ({self.year} г.)'

    class Meta:
        verbose_name = "Данные колледжа на год (БВБ)"
        verbose_name_plural = "Данные колледжей на годы (БВБ)"