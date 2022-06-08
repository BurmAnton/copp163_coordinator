from django.urls import include, path
from acdmx_bot_api import views

from rest_framework import routers

from acdmx_bot_api.views import DiscordSeverViewSet, EducationTrackViewSet, GuildMemberViewSet

router = routers.DefaultRouter()
router.register(r'tracks', EducationTrackViewSet)
router.register(r'guidls', GuildMemberViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('servers/', views.servers_list),
    path('servers/<int:pk>', views.server_details),
    path('tracks/', views.tracks_list),
    path('tracks/<int:pk>', views.track_details)
]