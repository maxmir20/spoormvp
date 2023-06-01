from . import views
from django.urls import path

urlpatterns = [
    path("<int:userID>/", views.get_current_track, name="current_track"),
]