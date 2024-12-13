from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, \
    extend_schema_view
from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event
from .permissions import IsOwnerOrReadOnly
from .serializers import EventSerializer, UserSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='invited',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter events by invitation status, "true" or "false"',
                required=False
            ),
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter events by date (YYYY-MM-DD)',
                required=False
            ),
            OpenApiParameter(
                name='title',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter events by title',
                required=False
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number',
                required=False
            )

        ],
        description='Retrieve a list of events with optional filtering',
    ),
    create=extend_schema(
        request=EventSerializer,
        description='Create a new event with optional invitees',
        responses={201: EventSerializer}
    ),
    retrieve=extend_schema(
        description='Retrieve details of a specific event',
    ),
    update=extend_schema(
        request=EventSerializer,
        description='Update an existing event',
        responses={200: EventSerializer}
    ),
    partial_update=extend_schema(
        request=EventSerializer,
        description='Partially update an event',
        responses={200: EventSerializer}
    ),
    destroy=extend_schema(
        description='Delete an event'
    )
)
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [TokenAuthentication]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        invited = self.request.query_params.get('invited')
        if invited == 'true':
            queryset = queryset.filter(attendees=user)
        elif invited == 'false':
            queryset = queryset.exclude(attendees=user)

        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(date__date=date)

        title = self.request.query_params.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset


    def perform_create(self, serializer):
        event = serializer.save(organizer=self.request.user)

        invitee_emails = self.request.data.get('invitees', [])
        if invitee_emails:
            for email in invitee_emails:
                try:
                    user = User.objects.get(email=email)
                    event.attendees.add(user)
                except ObjectDoesNotExist:
                    pass

    @extend_schema(
        request=None,
        responses={200: OpenApiTypes.OBJECT},
        description='Register user for the event',
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, pk=None):
        event = self.get_object()
        event.attendees.add(request.user)
        return Response({"status": "registered"})

class UserRegistrationAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "example": "johndoe"},
                    "email": {"type": "string", "example": "johndoe@example.com"},
                    "password": {"type": "string", "example": "userpassword"},
                },
                "required": ["username", "email", "password"],
            }
        },
        examples=[
            OpenApiExample(
                "Registration Example",
                value={"username": "johndoe", "email": "johndoe@example.com",
                       "password": "userpassword"},
                request_only=True,
            )
        ],
        description="Register a new user"
    )
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if not username or not email or not password:
            return Response({"error": "All fields are required"}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        Token.objects.create(user=user)
        return Response(UserSerializer(user).data)

class CustomAuthToken(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "example": "johndoe"},
                    "password": {"type": "string", "example": "userpassword"},
                },
                "required": ["username", "password"],
            }
        },
        description="Obtain an authentication token"
    )
    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email
        })
