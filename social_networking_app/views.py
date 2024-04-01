from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import FriendRequest, Friend, CustomUser
from .serializers import (
    FriendRequestSerializer,
    FriendSerializer,
    UserSignupSerializer,
    UserLoginSerializer,
)
from datetime import datetime, timedelta
from django.db.models import Q
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework.pagination import PageNumberPagination


class FriendViewSet(viewsets.ModelViewSet):
    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Friend.objects.filter(user=user)

        return queryset


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserSearchViewSet(viewsets.ViewSet):
    pagination_class = CustomPagination

    def list(self, request):
        search_keyword = request.query_params.get("q")
        if search_keyword:
            users_by_email = CustomUser.objects.filter(email__icontains=search_keyword)
            users_by_name = CustomUser.objects.filter(
                username__icontains=search_keyword
            )
            users = users_by_email | users_by_name  # Merge querysets

            # Use the pagination class to paginate the queryset
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(users, request)
            if page is not None:
                serializer = UserSignupSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = UserSignupSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Search keyword 'q' is required."}, status=400)


class FriendRequestViewSet(viewsets.ViewSet):
    permission_classes = [
        IsAuthenticated
    ]  # Ensures user is authenticated to access this endpoint

    def create(self, request):
        # Check if the user has sent more than 3 friend requests within the last minute
        time_threshold = datetime.now() - timedelta(minutes=1)
        recent_requests_count = FriendRequest.objects.filter(
            from_user=request.user, created_at__gte=time_threshold
        ).count()
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
        friend_request = self.get_friend_request(pk)
        if friend_request.to_user != request.user:
            return Response(
                {"error": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if friend_request.accepted:
            return Response(
                {"error": "This friend request has already been accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        friend_request.accept()
        return Response({"detail": "Friend request accepted successfully."})

    def reject(self, request, pk):
        friend_request = self.get_friend_request(pk)
        if friend_request.to_user != request.user:
            return Response(
                {"error": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # # Check if the friend request is already accepted or rejected
        if friend_request.accepted:
            try:
                friend = Friend.objects.get(
                    user=request.user, friend=friend_request.from_user
                )
                friend.delete()
            except ObjectDoesNotExist:
                # Handle the case where no Friend object is found
                return Response(
                    {"error": "No friend object found for the given query parameters."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except MultipleObjectsReturned:
                # Handle the case where multiple Friend objects are returned
                return Response(
                    {
                        "error": "Multiple friend objects found for the given query parameters."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {"error": "This friend request Reject Successfull "},
                status=status.HTTP_400_BAD_REQUEST,
            )

        friend_request.reject()

        return Response({"detail": "Friend request rejected successfully."})

    def get_friend_request(self, pk):
        try:
            return FriendRequest.objects.get(pk=pk)
        except FriendRequest.DoesNotExist:
            return Response(
                {"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def list_friends(self, request):
        friends = Friend.objects.filter(Q(user=request.user) | Q(friend=request.user))
        friend_user_ids = list(
            set(
                [
                    friend.user.id if friend.user != request.user else friend.friend.id
                    for friend in friends
                ]
            )
        )
        friends_list = CustomUser.objects.filter(id__in=friend_user_ids)
        serializer = UserSignupSerializer(friends_list, many=True)
        return Response(serializer.data)

    def list_pending_requests(self, request):
        # Filter friend requests where the current user is the to_user
        friend_requests = FriendRequest.objects.filter(
            to_user=request.user, accepted=False
        )
        friend_requests_with_emails = []
        for request in friend_requests:
            from_user_email = request.from_user.email
            friend_requests_with_emails.append({"from_user_email": from_user_email})
            print(request.from_user.email)
        return Response(friend_requests_with_emails, status=status.HTTP_200_OK)


from rest_framework.permissions import AllowAny


class UserSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

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
