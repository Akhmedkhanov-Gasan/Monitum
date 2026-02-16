
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", obtain_auth_token),
    path("api/", include("apps.monitors.api.urls")),
    path("api2/", include("apps.notes.api.urls")),
]
