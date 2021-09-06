from django.urls import path

from . import views

urlpatterns = [
    path('ed_centers/applications/fed_empl_program', views.ed_centers_empl, name='ed_centers_empl'),
    path('applications/groups_suggestions/fed_empl_program', views.groups_suggestions, name='groups_suggestions_empl'),
    path('', views.dashboard, name='dashboard'),
    path('dashboard/filter/', views.group_filter, name='group_filter')
]
