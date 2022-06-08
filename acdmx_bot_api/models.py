from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE

# Create your models here.

class DiscordSever(models.Model):
    server_id = models.CharField("Сервер ID", max_length=200)
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
   

class GuildMember(models.Model):
    user_id = models.CharField("ID пользователя", max_length=200)
    email = models.EmailField('email', unique=False)

    last_name = models.CharField("Фамилия", max_length=50, blank=False, null=False)
    first_name = models.CharField("Имя", max_length=50, blank=False, null=False)
    middle_name = models.CharField("Отчество", max_length=50, blank=True, null=True)
    
    ROLES = (
        ('ST', 'Студент'),
        ('TCH', 'Преподователь')
    )
    role = models.CharField(max_length=3, choices=ROLES, verbose_name='Роль', blank=False, null=False)
    education_track = models.ForeignKey(EducationTrack, verbose_name="Трек", on_delete=CASCADE, related_name='members')

    class Meta:
        verbose_name = "Участник сервера"
        verbose_name_plural = "Участники сервера"

    def __str__(self):
        return f'{self.first_name} {self.last_name}'