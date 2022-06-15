from django.urls import path
from acdmx_bot_api import views


urlpatterns = [
    path('servers/', views.servers_list),
    path('servers/<int:server_id>', views.server_details),
    path('tracks/', views.tracks_list),
    path('roles/', views.roles_list),
    path('roles/<int:user_id>', views.role_details),
    path('members/', views.members_list),
    path('members/<int:user_id>', views.member_details),
    path('tasks/', views.task_list)
]
