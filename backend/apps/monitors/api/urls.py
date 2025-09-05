from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, MonitorViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"monitors", MonitorViewSet, basename="monitor")

urlpatterns = [
    path("", include(router.urls)),
]
