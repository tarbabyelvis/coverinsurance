from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from claims.models import Claim
from drf_yasg.utils import swagger_auto_schema
from .serializers import ClaimSerializer

class ClaimCreateAPIView(APIView):
    @swagger_auto_schema(
        methods=['post'],
        request_body=ClaimSerializer,
        responses={201: ClaimSerializer}
    )
    def post(self, request, format=None):
        serializer = ClaimSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        methods=['get'],
        responses={200: ClaimSerializer(many=True)}
    )
    def get(self, request, format=None):
        claims = Claim.objects.all()
        serializer = ClaimSerializer(claims, many=True)
        return Response(serializer.data)
