from django.urls import path

from .views import NoteViews, NoteDetailView

urlpatterns = [
    path("notes/", NoteViews.as_view()),
    path("notes/<int:pk>/", NoteDetailView.as_view()),
    ]