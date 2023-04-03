from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path(
        '<int:ed_center>/groups',
        views.ed_center_groups, 
        name='ed_center_groups'
    ),
]
