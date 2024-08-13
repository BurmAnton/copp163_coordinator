# Generated by Django 4.2.6 on 2024-08-10 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('future_ticket', '0038_remove_partnerevent_city_partnerevent_cities'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationcenterticketprojectyear',
            name='exp_other_events',
            field=models.IntegerField(default=0, verbose_name='Колво прочих мероприятий профориентационного характера'),
        ),
        migrations.AddField(
            model_name='educationcenterticketprojectyear',
            name='exp_predprof',
            field=models.IntegerField(default=0, verbose_name='Колво предпрофильных курсов/мастер-классов'),
        ),
        migrations.AddField(
            model_name='educationcenterticketprojectyear',
            name='exp_skillsguide',
            field=models.IntegerField(default=0, verbose_name='Колво проб в рамках «Мой выбор»'),
        ),
        migrations.AddField(
            model_name='educationcenterticketprojectyear',
            name='exp_ticket_events',
            field=models.IntegerField(default=0, verbose_name='Колво мероприятий в рамках «Билет в будущее»'),
        ),
        migrations.AddField(
            model_name='educationcenterticketprojectyear',
            name='is_disability_friendly',
            field=models.BooleanField(default=False, verbose_name=' Может обеспечить участия ОВЗ?'),
        ),
        migrations.AddField(
            model_name='educationcenterticketprojectyear',
            name='step_7_check',
            field=models.BooleanField(default=False, verbose_name='Шаг 7. Проверка'),
        ),
        migrations.AddField(
            model_name='educationcenterticketprojectyear',
            name='step_7_commentary',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Шаг 7. Комментарий'),
        ),
    ]