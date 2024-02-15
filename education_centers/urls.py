from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('export/programs/', views.export_programs, name='export_programs'),
    path('export/ed_centers/', views.export_ed_centers, name='export_ed_centers'),
    path('export/workshops/', views.export_workshops, name='export_workshops'),
    path(
        '<int:ed_center>/groups',
        views.ed_center_groups, 
        name='ed_center_groups'
    ),
    path(
        '<int:ed_center_id>/application',
        views.ed_center_application,
        name='ed_center_application'
    ),
    path('applications', views.applications, name='applications'),
    path('documents/fed-empl/', views.documents_fed, name='documents_fed'),
    path('programs/import/', views.import_programs, name='import_programs'),
    path('centers/merge/', views.merge_centers, name='merge_centers'),
    path('abilimpics/',  views.abilimpics, name='abilimpics')
]
