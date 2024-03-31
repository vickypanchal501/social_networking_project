from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from social_networking_app.views import  FriendRequestViewSet, UserSearchViewSet, UserLoginView, UserSignupView

# router = DefaultRouter()

# router = DefaultRouter()
# router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')

urlpatterns = [
    # path('', include(router.urls)),
    path('login/', UserLoginView.as_view(), name='login'),
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('user-search/', UserSearchViewSet.as_view({'get': 'list'}), name='user-search'),
    path('friend-requests/', FriendRequestViewSet.as_view({'post': 'create'}), name='friend-requests'),
    path('friend-requests/<int:pk>/accept/', FriendRequestViewSet.as_view({'post': 'accept'}), name='friend-requests-accept'),
    # path('friend-requests/list/', FriendRequestViewSet.as_view({'get': 'get_friend_request'}), name='get_friend_request'),
    path('friend-requests/<int:pk>/reject/', FriendRequestViewSet.as_view({'post': 'reject'}), name='friend-requests-reject'),
    path('friend-requests/list-friends/', FriendRequestViewSet.as_view({'get': 'list_friends'}), name='list-friends'),
    path('friend-requests/list-pending-requests/', FriendRequestViewSet.as_view({'get': 'list_pending_requests'}), name='list-pending-requests'),

]


   # path('list-friends/', FriendRequestViewSet.as_view({'get': 'list_friends'}), name='list-friends'),
    # path('list-pending-requests/', FriendRequestViewSet.as_view({'get': 'list_pending_requests'}), name='list-pending-requests'),
# router.register(r'users', UserViewSet, basename='users')
# router.register(r'friend-requests', FriendRequestViewSet, basename='friend-requests')
# router.register(r'friends', FriendViewSet, basename='friends')
# router.register(r'user-search', UserSearchViewSet, basename='user-search')