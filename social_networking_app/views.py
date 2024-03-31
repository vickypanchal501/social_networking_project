from rest_framework import viewsets, status, permissions , pagination 
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import FriendRequest, Friend , CustomUser
from .serializers import  FriendRequestSerializer, FriendSerializer , UserSignupSerializer, UserLoginSerializer
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.db.models import Q
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated




class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated] 




class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserSearchViewSet(viewsets.ViewSet):
    pagination_class = CustomPagination

    def list(self, request):
        search_keyword = request.query_params.get('q')
        if search_keyword:
            users_by_email = CustomUser.objects.filter(email__iexact=search_keyword)
            users_by_name = CustomUser.objects.filter(username__icontains=search_keyword)
            users = users_by_email | users_by_name  # Merge querysets

            page = self.paginate_queryset(users)
            if page is not None:
                serializer = UserSignupSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = UserSignupSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Search keyword 'q' is required."}, status=400)
        

class FriendRequestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Ensures user is authenticated to access this endpoint
    print(permission_classes,IsAuthenticated )
    def create(self, request):
        print(self.permission_classes) 
        # Check if the user has sent more than 3 friend requests within the last minute
        time_threshold = datetime.now() - timedelta(minutes=1)
        print("Time threshold:", time_threshold)
        recent_requests_count = FriendRequest.objects.filter(from_user=request.user, created_at__gte=time_threshold).count()
        print("Recent requests count:", recent_requests_count)
        if recent_requests_count >= 3:
            return Response({"error": "You cannot send more than 3 friend requests within a minute."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        serializer = FriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Extract the email of the user to whom the friend request is being sent
            to_email = serializer.validated_data.get('to_user')
            try:
                # Retrieve the user with the provided email
                to_user = CustomUser.objects.get(email=to_email)
            except CustomUser.DoesNotExist:
                return Response({"error": f"User with email {to_email} does not exist."}, status=status.HTTP_404_NOT_FOUND)

            # Ensure that the user is not sending a friend request to themselves
            if to_user == request.user:
                return Response({"error": "You cannot send a friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)

            # Create the friend request
            FriendRequest.objects.create(from_user=request.user, to_user=to_user)
            return Response({"message": "Friend request sent successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def accept(self, request, pk):
        friend_request = self.get_friend_request(pk)
        friend_request.accept()
        return Response({"detail": "Friend request accepted successfully."})

    def reject(self, request, pk):
        friend_request = self.get_friend_request(pk)
        friend_request.reject()
        return Response({"detail": "Friend request rejected successfully."})

    def get_friend_request(self, pk):
        try:
            return FriendRequest.objects.get(pk=pk)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)       
    
    def list_friends(self, request):
        friends = Friend.objects.filter(Q(user=request.user) | Q(friend=request.user))
        friend_user_ids = list(set([friend.user.id if friend.user != request.user else friend.friend.id for friend in friends]))
        friends_list = CustomUser.objects.filter(id__in=friend_user_ids)
        serializer = UserSignupSerializer(friends_list, many=True)
        return Response(serializer.data)

    def list_pending_requests(self, request):
        pending_requests = FriendRequest.objects.filter( accepted=False)
        serializer = FriendRequestSerializer(pending_requests, many=True)
        pending_requests_data = serializer.data
        print(pending_requests_data)
        # for request_data in pending_requests_data:
        #     from_user_email = request_data['from_user']
        #     request_data['from_user_email'] = from_user_email
        
        return Response(pending_requests_data, status=status.HTTP_200_OK)
        # # Include sender's email in each pending request
        # for request_data in pending_requests_data:
        #     from_user_email = FriendRequest.objects.get(id=request_data['id']).from_user.email
        #     request_data['from_user_email'] = from_user_email

        # return Response(pending_requests_data)
     

from rest_framework.permissions import AllowAny


class UserSignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
from rest_framework.authtoken.views import ObtainAuthToken

class UserLoginView(ObtainAuthToken):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)  # Create or retrieve token
            return Response({"message": "User login successful", 'token': token.key}, status=status.HTTP_200_OK)  # Return token key
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # def post(self, request):
    #     serializer = UserLoginSerializer(data=request.data)
    #     if serializer.is_valid():
    #         email = serializer.validated_data['email']
    #         password = serializer.validated_data['password']
    #         user = authenticate(request, email=email, password=password)
    #         if user:
    #             token, _ = Token.objects.get_or_create(user=user)
    #             return Response({"message": "User login successful", "token": token.key}, status=status.HTTP_200_OK)
    #         else:
    #             return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class FriendRequestViewSet(viewsets.ModelViewSet):
#     queryset = FriendRequest.objects.all()
#     serializer_class = FriendRequestSerializer
#     permission_classes = [permissions.IsAuthenticated]  # Add this line to enforce authentication

#     def perform_create(self, serializer):
#         serializer.save(from_user=self.request.user)
    

# class UserViewSet(viewsets.ViewSet):
#     def list(self, request):
#         queryset = CustomUser.objects.all()
#         serializer = UserSignupSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = CustomUser.objects.all()
#         user = get_object_or_404(queryset, pk=pk)
#         serializer = UserSignupSerializer(user)
#         return Response(serializer.data)
