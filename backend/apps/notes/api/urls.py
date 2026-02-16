from django.urls import path

from .views import NoteViews

urlpatterns = [
    path("notes/", NoteViews.as_view())
    ]