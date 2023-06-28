from django.urls import path

from . import views

urlpatterns = [
    path(
        'professions/import/', 
        views.import_ticket_professions, 
        name='import_ticket_professions'
    ),
    path(
        'professions/import/merge', 
        views.merge_ticket_professions, 
        name='merge_ticket_professions'
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
    path(
        'schools/application', 
        views.schools_application, 
        name='schools_application'
    ),
    path(
        'schools/applications', 
        views.schools_applications, 
        name='schools_applications'
    )
]