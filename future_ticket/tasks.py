from datetime import date
import time
from copp163_coordinator.celery import app
from celery.schedules import crontab



@app.on_after_configure.connect()
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=0, hours=0),
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
