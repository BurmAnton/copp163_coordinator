from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
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
    path('documents/fed-empl/', views.documents_fed, name='documents_fed'),
    path('programs/import/', views.import_programs, name='import_programs')
]
