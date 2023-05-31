from django.urls import path

from . import views

urlpatterns = [
    path(
        'professions/import/', 
        views.import_ticket_professions, 
        name='import_ticket_professions'
    ),
    path(
        'programs/import/', 
        views.import_ticket_programs, 
        name='import_ticket_programs'
    ),
]