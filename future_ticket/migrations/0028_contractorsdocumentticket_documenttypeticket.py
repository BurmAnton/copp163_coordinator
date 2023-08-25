# Generated by Django 3.2.8 on 2023-08-22 07:19

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import future_ticket.models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0049_auto_20230616_1519'),
        ('future_ticket', '0027_alter_ticketprogram_age_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTypeTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Тип документа')),
                ('stage', models.CharField(choices=[('GRMNT', 'Договорные'), ('CLS', 'Закрывающие'), ('PRV', 'Подтверждающие')], max_length=6, verbose_name='Этап')),
                ('template', models.FileField(upload_to=future_ticket.models.DocumentTypeTicket.template_directory_path, verbose_name='Документ')),
                ('project_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='docs_templates', to='future_ticket.ticketprojectyear', verbose_name='Год проекта (БВБ)')),
            ],
            options={
                'verbose_name': 'Шаблон документов (БВБ)',
                'verbose_name_plural': 'Шаблоны документов (БВБ)',
            },
        ),
        migrations.CreateModel(
            name='ContractorsDocumentTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Дата создания')),
                ('register_number', models.IntegerField(verbose_name='Номер в реестре')),
                ('doc_stage', models.CharField(choices=[('CRTD', 'Создан'), ('CHCKD', 'Проверен'), ('SGND', 'Подписан'), ('SGNDAP', 'Подписан и проверен')], default='CRTD', max_length=6, verbose_name='Стадия')),
                ('doc_file', models.FileField(upload_to=future_ticket.models.ContractorsDocumentTicket.doc_directory_path, verbose_name='Документ')),
                ('contractor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ticket_docs', to='education_centers.educationcenter', verbose_name='подрядчик')),
                ('doc_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='future_ticket.documenttypeticket', verbose_name='Тип документа')),
                ('parent_doc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_docs', to='future_ticket.contractorsdocumentticket', verbose_name='Родительский документ')),
            ],
            options={
                'verbose_name': 'Документ с подрядчиком (БВБ)',
                'verbose_name_plural': 'Документы с подрядчиками (БВБ)',
            },
        ),
    ]
