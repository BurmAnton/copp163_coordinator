import os
import time

from celery import Celery

# Set the default Django settings module for the 'celery' program.
# "sample_app" is name of the root app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'copp163_coordinator.settings')

app = Celery( 'celery_app',
               broker='redis://localhost:6379/0',
               backend='redis://localhost:6379/0'
            )
app.conf.timezone = 'Europe/Samara'            
# Load task modules from all registered Django apps.
app.autodiscover_tasks()

