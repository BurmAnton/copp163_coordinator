# Generated by Django 3.2.8 on 2023-09-19 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('future_ticket', '0003_ticketprogram_created_at_ticketprogram_updated_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventsCycle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('end_reg_date', models.DateTimeField(verbose_name='Дата окончания регистрации')),
                ('start_period_date', models.DateTimeField(verbose_name='Старт проведения мероприятий')),
                ('end_period_date', models.DateTimeField(verbose_name='Конец проведения мероприятий')),
            ],
            options={
                'verbose_name': 'Цикл проб',
                'verbose_name_plural': 'Циклы проб',
            },
        ),
        migrations.CreateModel(
            name='StudentBVB',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bvb_id', models.IntegerField(db_index=True, verbose_name='ID БВБ')),
                ('is_double', models.BooleanField(default=False, verbose_name='Дубликат?')),
                ('first_name', models.CharField(max_length=50, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=50, verbose_name='Фамилия')),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Отчество')),
                ('grade', models.CharField(max_length=50, verbose_name='Класс')),
                ('school', models.CharField(max_length=100, verbose_name='Школа')),
            ],
            options={
                'verbose_name': 'Студент',
                'verbose_name_plural': 'Студенты',
            },
        ),
        migrations.CreateModel(
            name='TicketEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_date', models.DateTimeField(verbose_name='Дата проведения')),
                ('participants_limit', models.IntegerField(default=15, verbose_name='Колво участников')),
                ('cycle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='future_ticket.eventscycle', verbose_name='Цикл')),
                ('ed_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='future_ticket.educationcenterticketprojectyear', verbose_name='Центр обучения')),
                ('participants', models.ManyToManyField(blank=True, related_name='events', to='future_ticket.StudentBVB', verbose_name='Участники')),
                ('quota', models.ManyToManyField(blank=True, related_name='events', to='future_ticket.TicketQuota', verbose_name='Квота')),
            ],
            options={
                'verbose_name': 'Профпроба',
                'verbose_name_plural': 'Профпробы',
            },
        ),
    ]
