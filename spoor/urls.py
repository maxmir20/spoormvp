from . import views
from django.urls import path

urlpatterns = [
    path("<int:userID>/", views.get_current_track, name="current_track"),
    path("<int:userID>/authorize", views.authorize_spotify_user, name="authorize"),
    path("callback", views.request_access_token, name="access_token"),
]