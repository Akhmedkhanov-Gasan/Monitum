from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.notes.models import Note
from apps.notes.api.serializers import NoteSerializer


class NoteViews(APIView):

    def get(self, request):
        qs = Note.objects.all().order_by("-created_at")
        title = request.query_params.get("title")
        if title:
            qs = qs.filter(title__icontains=title)

        ser = NoteSerializer(qs, many=True)
        return Response(ser.data)

    def post(self, request):
        ser = NoteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)


class NoteDetailView(APIView):

    def get(self, request, pk):
        ser = NoteSerializer(get_object_or_404(Note, pk=pk))
        return Response(ser.data)

    def delete(self, request, pk):
        obj = get_object_or_404(Note, pk=pk)
        obj.delete()
        return Response(status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        obj = get_object_or_404(Note, pk=pk)
        ser = NoteSerializer(obj, data=request.data, partial=True)
        ser.is_valid()
        ser.save()
        return Response(ser.data)
