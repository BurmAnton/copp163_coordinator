from django.urls import path

from . import views

urlpatterns = [
    path(
        'events/<int:ed_center_id>/', 
        views.center_events, 
        name='ticket_center_events'
    ),
    path(
        'events/<>/applications', 
        views.schools_applications, 
        name='schools_applications'
    ),
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
        'schools/adress/import/', 
        views.import_schools_address, 
        name='import_schools_address'
    ),
    path(
        'export/professions/', 
        views.export_professions, 
        name='export_professions'
    ),
    path(
        'export/programs/', 
        views.export_ticket_programs, 
        name='export_ticket_programs'
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
    ),
]