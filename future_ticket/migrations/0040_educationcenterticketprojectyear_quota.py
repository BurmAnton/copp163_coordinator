# Generated by Django 4.2.6 on 2024-08-10 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('future_ticket', '0039_educationcenterticketprojectyear_exp_other_events_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationcenterticketprojectyear',
            name='quota',
            field=models.IntegerField(default=0, verbose_name='Квота ЦО'),
        ),
    ]
