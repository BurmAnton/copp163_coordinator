from django.urls import path

from . import views

urlpatterns = [
    path('ed_centers/applications/fed_empl_program', views.ed_centers_empl, name='ed_centers_empl'),
]
