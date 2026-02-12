from http.client import responses

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import EchoSerializer


class PingView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "ping": "pong",
                "message": "pong",
                "method": request.method,
            },
        )

class PingPrivateView(APIView):

    def get(self, request):
        return Response(
            {
                "ping": "FUCKYOUPONG",
                "method": request.method,
                "user": request.user.username
            },
        )
class EchoView(APIView):

    def post(self, request):
        serializer = EchoSerializer(data={"data": request.data})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "user": request.user.username,
            "data": serializer.validated_data["data"],
        })

class HelloView(APIView):

    def get(self, request):
        if not request.query_params.get('name'):
            return Response({
                "message": "Hello stranger"
            })
        return Response({
            "message": f"Hello {request.query_params.get('name')}"
        })
