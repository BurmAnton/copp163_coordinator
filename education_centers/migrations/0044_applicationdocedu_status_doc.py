# Generated by Django 4.2.6 on 2024-11-05 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0043_remove_applicationdocedu_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationdocedu',
            name='status_doc',
            field=models.CharField(blank=True, choices=[('NEW', 'Новое'), ('GEN', 'Сгенерировано'), ('UPL', 'Загружено')], default='NEW', max_length=20, null=True, verbose_name='Статус документа'),
        ),
    ]
