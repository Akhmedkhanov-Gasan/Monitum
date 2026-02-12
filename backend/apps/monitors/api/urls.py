from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, MonitorViewSet
from .test_views import PingView, PingPrivateView, EchoView, HelloView

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"monitors", MonitorViewSet, basename="monitor")

urlpatterns = [
    path('hello/', HelloView.as_view()),
    path("echo/", EchoView.as_view()),
    path("ping/", PingView.as_view()),
    path("ping/private/", PingPrivateView.as_view()),
    path("", include(router.urls)),
]
