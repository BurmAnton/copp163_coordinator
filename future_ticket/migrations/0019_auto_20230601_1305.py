# Generated by Django 3.2.8 on 2023-06-01 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('future_ticket', '0018_ticketprofession_is_centers'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketprogram',
            name='program_link',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Ссылка на программу'),
        ),
        migrations.AlterField(
            model_name='educationcenterticketprojectyear',
            name='stage',
            field=models.CharField(choices=[('FLLNG', 'заполнение'), ('FLLD', 'на проверке'), ('RWRK', 'отправленна на доработку'), ('VRFD', 'проверена'), ('FRMD', 'сформирована'), ('DWNLD', 'подгружена'), ('PRVD', 'принята')], default='FLLNG', max_length=5, verbose_name='Работа с заявкой'),
        ),
    ]
