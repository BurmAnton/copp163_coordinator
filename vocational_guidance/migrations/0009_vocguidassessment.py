# Generated by Django 3.2.8 on 2021-10-24 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('citizens', '0004_alter_citizen_middle_name'),
        ('vocational_guidance', '0008_alter_timeslot_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='VocGuidAssessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance', models.BooleanField(default=False, verbose_name='Посещаемость')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voc_guid_assessment', to='citizens.citizen', verbose_name='Участник')),
                ('slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessments', to='vocational_guidance.timeslot', verbose_name='Слот')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessments', to='vocational_guidance.vocguidtest', verbose_name='Проба')),
            ],
        ),
    ]