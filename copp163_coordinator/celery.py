import os
import time
from datetime import date

from celery import Celery
from celery.schedules import crontab
from django.apps import apps

from future_ticket.tasks import find_participants_dublicates,\
                                update_completed_quota
# Set the default Django settings module for the 'celery' program.
# "sample_app" is name of the root app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'copp163_coordinator.settings')

app = Celery( 'celery_app',
               broker='redis://localhost:6379/0',
               backend='redis://localhost:6379/0'
            )
app.conf.timezone = 'Europe/Samara'            
# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

@app.on_after_configure.connect()
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute="*/1"),
        update_events_cycles_statuses,
        name='update_events_cycles_statuses_everyday'
    )

@app.task()
def update_events_cycles_statuses():
    from future_ticket.models import EventsCycle

    today = date.today()
    #Регистрация
    cycles_reg = EventsCycle.objects.filter(
        end_reg_date__gte=today,
    )
    cycles_reg.update(status='REG')
    #Проверка и коррекция
    cycles_check = EventsCycle.objects.filter(
        end_reg_date__lt=today,
        start_period_date__gt=today
    )
    cycles_check.update(status='CHCK')
    #В процессе
    cycles_in_progress = EventsCycle.objects.filter(
        start_period_date__lte=today,
        end_period_date__gte=today
    )
    cycles_in_progress.update(status='HSTNG')
    #Завершено
    cycles_end = EventsCycle.objects.filter(
        end_period_date__lt=today
    )
    cycles_end.update(status='END')
    #Проверяем дубликатов
    for cycle in EventsCycle.objects.all():
        find_participants_dublicates.delay(cycle.id)
    update_completed_quota()
