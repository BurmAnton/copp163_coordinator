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
    path(
        'export/professions/', 
        views.export_professions, 
        name='export_professions'
    ),
    path('quotas/dashboard/', views.quotas, name='quotas'),
    path('quotas/equalize/', views.equalize_quotas, name='equalize_quotas'),
]