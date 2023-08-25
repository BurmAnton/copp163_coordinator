# Generated by Django 3.2.8 on 2023-04-10 08:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0016_auto_20230406_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractorsdocument',
            name='parent_doc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_docs', to='education_centers.contractorsdocument', verbose_name='Родительский документ'),
        ),
    ]
