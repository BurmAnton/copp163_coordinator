from django.urls import path
from acdmx_bot_api import views


urlpatterns = [
    path('servers/', views.servers_list),
    path('servers/<int:server_id>', views.server_details),
    path('tracks/', views.tracks_list),
    path('tracks/<int:track_id>', views.track_details),
    path('roles/', views.roles_list),
    path('roles/<int:role_id>', views.role_details),
    path('members/', views.members_list),
    path('members/<int:user_id>', views.member_details),
    path('tasks/', views.task_list),
    path('tasks/<int:task_id>', views.task_details),
    path('criteria/', views.criteria_list),
    path('assignments/', views.assignments_list),
    path('assignments/<int:assignment_id>', views.assignment_details),
    path('assessments/', views.assessment_list),
]
