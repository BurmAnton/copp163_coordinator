# Generated by Django 3.2.5 on 2021-09-14 10:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('citizens', '0010_auto_20210914_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='inn',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='ИНН'),
        ),
        migrations.AlterField(
            model_name='school',
            name='school_coordinators',
            field=models.ManyToManyField(blank=True, related_name='coordinated_schools', to=settings.AUTH_USER_MODEL, verbose_name='Педагоги-навигаторы'),
        ),
    ]