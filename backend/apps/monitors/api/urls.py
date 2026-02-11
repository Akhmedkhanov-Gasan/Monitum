from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, MonitorViewSet
from .ping import PingView, PingPrivateView

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"monitors", MonitorViewSet, basename="monitor")

urlpatterns = [
    path("ping/", PingView.as_view()),
    path("ping/private/", PingPrivateView.as_view()),
    path("", include(router.urls)),
]
