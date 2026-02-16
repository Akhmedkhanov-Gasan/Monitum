from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.notes.models import Note
from apps.notes.api.serializers import NoteSerializer


class NoteViews(APIView):

    def get(self, request):
        qs = Note.objects.all().order_by("-created_at")
        ser = NoteSerializer(qs, many=True)
        return Response(ser.data)

    def post(self, request):
        ser = NoteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)

