from django.urls import path
from acdmx_bot_api import views


urlpatterns = [
    path('servers/', views.servers_list),
    path('servers/<int:server_id>', views.server_details),
    path('tracks/', views.tracks_list),
    path('tracks/<int:server_id>/<str:name>', views.track_details),
    path('roles/', views.roles_list),
    path('roles/<int:user_id>', views.role_details),
    path('members/', views.members_list),
    path('members/<int:user_id>', views.member_details),
    path('tasks/', views.task_list),
    path('criteria/', views.criteria_list),
    path('assignments/', views.assignments_list),
    path('assessments/', views.assessment_list),
]
