# Generated by Django 4.2.6 on 2024-02-14 08:27

from django.db import migrations, models
import django.db.models.deletion
import federal_empl_program.models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0029_remove_networkagreement_ed_center_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='networkagreement',
            name='ed_center_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='net_agreements', to='federal_empl_program.educationcenterprojectyear', verbose_name='Центра обучения (год проекта)'),
        ),
        migrations.AlterField(
            model_name='networkagreement',
            name='agreement_file',
            field=models.FileField(blank=True, null=True, upload_to=federal_empl_program.models.NetworkAgreement.agreement_path, verbose_name='Договор'),
        ),
    ]
