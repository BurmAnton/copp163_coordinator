# Generated by Django 3.2.8 on 2023-03-30 07:28

import datetime
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('middle_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Отчество')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Номер телефона')),
                ('code', models.CharField(blank=True, default=None, max_length=10, null=True, verbose_name='Код подтверждения')),
                ('role', models.CharField(blank=True, choices=[('CTZ', 'Гражданин'), ('CO', 'Представитель ЦО'), ('COR', 'Координатор')], max_length=3, null=True, verbose_name='Роль')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
        ),
        migrations.CreateModel(
            name='DistributionEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
            ],
            options={
                'verbose_name': 'Рассылочный email',
                'verbose_name_plural': 'Почтовые ящики для рассылки',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.group')),
            ],
            options={
                'verbose_name': 'Группа',
                'verbose_name_plural': 'Группы',
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='MailAttachFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название файла')),
                ('attached_file', models.FileField(upload_to='media/email_attached/', verbose_name='Прикреплённый файл')),
                ('upload_date_time', models.DateTimeField(default=datetime.datetime(2023, 3, 30, 11, 28, 7, 371166), verbose_name='Дата и время загрузки')),
            ],
        ),
        migrations.CreateModel(
            name='PartnerContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30, verbose_name='Имя')),
                ('middle_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Отчество')),
                ('last_name', models.CharField(max_length=30, verbose_name='Фамилия')),
                ('job_title', models.CharField(max_length=100, verbose_name='Должность')),
                ('commentary', models.TextField(blank=True, null=True, verbose_name='Комментарий')),
            ],
            options={
                'verbose_name': 'Контакты партнёра',
                'verbose_name_plural': 'Контакты партнёров',
            },
        ),
        migrations.CreateModel(
            name='PartnerOrganization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Название организации')),
                ('organization_inn', models.CharField(max_length=20, verbose_name='ИНН Организации')),
                ('organization_type', models.CharField(blank=True, choices=[('ECSPO', 'ЦО СПО'), ('ECVO', 'ЦО ВО'), ('ECP', 'ЦО частные'), ('SCHL', 'СОУ'), ('GOV', 'Гос. орган'), ('OTH', 'Другие')], max_length=5, null=True, verbose_name='Роль')),
            ],
            options={
                'verbose_name': 'Органзация партнёр',
                'verbose_name_plural': 'Органзации партнёры',
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('permission_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.permission')),
            ],
            bases=('auth.permission',),
            managers=[
                ('objects', django.contrib.auth.models.PermissionManager()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=250, verbose_name='Название проекта')),
            ],
            options={
                'verbose_name': 'Проекты',
                'verbose_name_plural': 'Проект',
            },
        ),
        migrations.CreateModel(
            name='PartnerContactPhone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Контактный телефон')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phones', to='users.partnercontact', verbose_name='Контакт')),
            ],
            options={
                'verbose_name': 'Контактный телефон',
                'verbose_name_plural': 'Контактные телефоны',
            },
        ),
        migrations.CreateModel(
            name='PartnerContactEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emails', to='users.partnercontact', verbose_name='Контакт')),
            ],
            options={
                'verbose_name': 'Контактная почта',
                'verbose_name_plural': 'Контактные почты',
            },
        ),
        migrations.AddField(
            model_name='partnercontact',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Организация', to='users.partnerorganization'),
        ),
        migrations.AddField(
            model_name='partnercontact',
            name='projects',
            field=models.ManyToManyField(blank=True, related_name='partners', to='users.Project', verbose_name='Проекты'),
        ),
        migrations.AddField(
            model_name='partnercontact',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='пользователь', to=settings.AUTH_USER_MODEL),
        ),
    ]
