from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .views import *
from django.urls import path

schema_view = get_schema_view(
   openapi.Info(
      title="Spoor API",
      default_version='v1',
      description="Documentation of available API",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("<int:userID>/", profile.get_current_track, name="current_track"),
    path("<int:userID>/session", profile.update_session, name="update_session"),
    path("<int:userID>/authorize", profile.authorize_spotify_user, name="authorize"),
    path("<int:userID>/playlist", playlist.add_playlist, name="add_playlist"),
    path("<int:userID>/track", track.add_track, name="add_track"),
    path("callback", profile.request_access_token, name="access_token"),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]