from .views import *
from django.urls import path

urlpatterns = [
    path("<int:userID>/", profile.get_current_track, name="current_track"),
    path("<int:userID>/authorize", profile.authorize_spotify_user, name="authorize"),
    path("<int:userID>/playlist", playlist.add_playlist, name="add_playlist"),
    path("<int:userID>/track", track.add_track, name="add_track"),
    path("callback", profile.request_access_token, name="access_token"),
]