from ast import Delete
from tabnanny import verbose
from unicodedata import name
from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class DiscordSever(models.Model):
    server_id = models.CharField("Сервер ID", max_length=200, primary_key=True)
    name = models.CharField("Название сервера", max_length=200)
    
    class Meta:
        verbose_name = "Сервер"
        verbose_name_plural = "Сервера"

    def __str__(self):
        return self.name


class EducationTrack(models.Model):
    server = models.ForeignKey(DiscordSever, verbose_name="Дискорд сервер", on_delete=CASCADE, related_name='tracks')
    name = models.CharField("Название трека", max_length=200)

    class Meta:
        verbose_name = "Трек"
        verbose_name_plural = "Треки"
        
    def __str__(self):
        return self.name


class GuildRole(models.Model):
    role_id = models.CharField("ID роли", max_length=200, unique=True)
    name = models.CharField("Название роли", max_length=50, blank=False, null=False)
    server = models.ForeignKey(DiscordSever, verbose_name="Сервер", related_name="roles", null=False, on_delete=CASCADE)
    track = models.OneToOneField(EducationTrack, verbose_name="Трек", related_name="track_role", on_delete=DO_NOTHING, null=True)
    
    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"
        
    def __str__(self):
        return self.name
    
   
class GuildMember(models.Model):
    user_id = models.CharField("ID пользователя", max_length=200, unique=True)
    email = models.EmailField('email')
    
    last_name = models.CharField("Фамилия", max_length=50, blank=False, null=False)
    first_name = models.CharField("Имя", max_length=50, blank=False, null=False)
    middle_name = models.CharField("Отчество", max_length=50, blank=True, null=True)
    
    STATUSES = (
        ('ST', 'Студент'),
        ('TCH', 'Преподователь')
    )
    status = models.CharField(max_length=3, choices=STATUSES, verbose_name='Статус', default='ST', blank=False, null=False)
    server = models.ForeignKey(DiscordSever, verbose_name="Сервер", related_name="members", null=False, on_delete=CASCADE)
    server_role = models.ForeignKey(GuildRole, verbose_name="Роль на сервере", related_name="members", on_delete=CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Участник сервера"
        verbose_name_plural = "Участники сервера"

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Criterion(models.Model):
    name = models.CharField("Название роли", max_length=200, blank=False, null=False, unique=True)

    class Meta:
        verbose_name = "Критерий оценки"
        verbose_name_plural = "Критерии оценки"
        
    def __str__(self):
        return self.name


class Task(models.Model):
    track = models.ForeignKey(EducationTrack, verbose_name="Трек", related_name="tasks", on_delete=CASCADE)
    number = models.IntegerField("Номер задания", validators=[MinValueValidator(1)])
    description = models.TextField("Описание")
    days_required = models.IntegerField("Дней на выполнение задания", validators=[MinValueValidator(1)])
    criteria = models.ManyToManyField(Criterion, verbose_name="Критерии оценки", related_name="tasks", blank=True)
    
    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"
        
    def __str__(self):
        return f"Задание №{self.number} ({self.track})"


class Assignment(models.Model):
    task = models.ForeignKey(Task, verbose_name="Задание", related_name="assigments", on_delete=CASCADE)
    executor = models.ForeignKey(GuildMember, verbose_name="Исполнитель", related_name="assigments", on_delete=CASCADE)
    start_date = models.DateTimeField("Дата и время начала", null=True, blank=True)
    deadline = models.DateTimeField("Дедлайн", null=True, blank=True)
    delivery_day = models.DateTimeField("Дата и время сдачи", null=True, blank=True)
    is_done = models.BooleanField("Задание сдано", default=False)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
    
    def __str__(self):
        return f"Задание №{self.task.number} ({self.executor})"


class Assessment(models.Model):
    assignment = models.ForeignKey(Assignment, verbose_name="Задача", related_name="assessment", on_delete=models.CASCADE)
    criterion = models.ForeignKey(Criterion, verbose_name="Критерий", related_name="assessment", on_delete=models.CASCADE)
    is_met = models.BooleanField("Критерий выполнен", default=False)

    class Meta:
        verbose_name = "Ассессмент"
        verbose_name_plural = "Ассессмент"

    def __str__(self):
        return f"{self.assignment.executor}: {self.criterion} (#{self.assignment.task.number})"
