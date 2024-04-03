from datetime import datetime, timedelta
import django_filters
from django.contrib.auth import authenticate
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import  PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import CustomUser, Friend, FriendRequest
from .serializers import (FriendRequestSerializer, FriendSerializer,
                          UserLoginSerializer, UserSignupSerializer)
import logging
from django.http import HttpResponse


# Get an instance of a logger
logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')

    return HttpResponse('Logged some messages')

class UserSignupView(APIView):
    # API view for user registration/signup
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # save data in over database after vaildate signup
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    # API view for user login/authentication
    serializer_class = UserLoginSerializer

    # post api for user login
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            email = serializer.validated_data.get("email")  # get email data
            password = serializer.validated_data.get("password")  # get password

            # Authenticate user
            user = authenticate(email=email, password=password)
            if user is not None:
                # User authenticated, generate or retrieve token
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {"message": "User login successful", "token": token.key},
                    status=status.HTTP_200_OK,
                )
            else:
                # Authentication failed
                return Response(
                    {"error": "Invalid email or password"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class FriendRequestViewSet(viewsets.ViewSet):
    # ViewSet for managing friend requests
    permission_classes = [
        IsAuthenticated
    ]  # Ensure user is authenticated to access this endpoint

    def create(self, request):
        # Create a new friend request
        time_threshold = datetime.now() - timedelta(minutes=1)
        recent_requests_count = FriendRequest.objects.filter(
            from_user=request.user, created_at__gte=time_threshold
        ).count()
        # if user send multiple firend request in one minutes. show error
        if recent_requests_count >= 3:
            return Response(
                {
                    "error": "You cannot send more than 3 friend requests within a minute."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = FriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Extract the email of the user to whom the friend request is being sent
            to_email = serializer.validated_data.get("to_user")
            try:
                # Retrieve the user with the provided email
                to_user = CustomUser.objects.get(email=to_email)
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": f"User with email {to_email} does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Ensure that the user is not sending a friend request to themselves
            if to_user == request.user:
                return Response(
                    {"error": "You cannot send a friend request to yourself."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if there is already an existing friend request from the requesting user to the target user
            existing_request = FriendRequest.objects.filter(
                from_user=request.user, to_user=to_user
            ).exists()
            if existing_request:
                return Response(
                    {"error": "You have already sent a friend request to this user."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create the friend request
            FriendRequest.objects.create(from_user=request.user, to_user=to_user)
            return Response(
                {"message": "Friend request sent successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def accept(self, request, pk):
        # Accept a friend request
        try:
            friend_request = self.get_friend_request(pk)  # get friend_request object id
        except FriendRequest.DoesNotExist:
            return Response(
                {"error": "Friend request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # user is not authorized
            if friend_request.to_user != request.user:
                raise PermissionDenied("You are not authorized to perform this action.")
            elif friend_request.accepted:
                return Response(
                    {"error": "This friend request has already been accepted."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                friend_request.accept()  # Accept friends request
                friend_request.delete() # Delete friends request
        except AttributeError:
            return Response(
                {
                    "error": "The friend request object does not have 'to_user' attribute. Please ensure your friend request ID."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"detail": "Friend request Accepted successfully."})

    def reject(self, request, pk):
        # Reject a friend request
        try:
            friend_request = self.get_friend_request(pk)  # get friend_request object id
        except FriendRequest.DoesNotExist:
            return Response(
                {"error": "Friend request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # user is not authorized
            if friend_request.to_user != request.user:
                raise PermissionDenied("You are not authorized to perform this action.")
            elif friend_request.accepted:
                return Response(
                    {"error": "This friend request has already been accepted."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                friend_request.reject()  # reject friends request
        except AttributeError:
            return Response(
                {
                    "error": "The friend request object does not have 'to_user' attribute. Please ensure your friend request ID."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        # send successful message
        return Response({"detail": "Friend request rejected successfully."})

    def get_friend_request(self, pk):
        # Helper function to get a friend request by its ID
        try:
            return FriendRequest.objects.get(pk=pk)
        except FriendRequest.DoesNotExist:
            return Response(
                {"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def list_pending_requests(self, request):
        # List pending friend requests for the current user
        friend_requests = FriendRequest.objects.filter(
            to_user=request.user, accepted=False
        )
        friend_requests_with_emails = (
            []
        )  # this list store a  from_user email after filter a data according to request user
        for request in friend_requests:
            from_user_email = request.from_user.email
            friend_requests_with_emails.append({"from_user_email": from_user_email})
        return Response(friend_requests_with_emails, status=status.HTTP_200_OK)



class CustomPagination(PageNumberPagination):
    # Custom pagination class
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = CustomUser
        fields = ['email', 'username']  # Define the fields you want to filter on
class UserSearchViewSet(viewsets.ViewSet):
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]  # Specify the filter backend
    filterset_class = UserFilter  # Specify the filter class

    def list(self, request):
        search_keyword = request.query_params.get('q')
        if search_keyword:
            users = CustomUser.objects.all()

            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(users, request)
            if page is not None:
                serializer = UserSignupSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = UserSignupSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Search keyword 'q' is required."}, status=400)

class FriendViewSet(viewsets.ModelViewSet):
    # ViewSet for managing friend relationships
    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter friends based on the current user
        user = self.request.user
        queryset = Friend.objects.filter(user=user)
        return queryset

