from django.urls import include, path
from rest_framework.routers import DefaultRouter

from social_networking_app.views import (FriendRequestViewSet, FriendViewSet,
                                         UserLoginView, UserSearchViewSet,
                                         UserSignupView)

router = DefaultRouter()
router.register(r"friends", FriendViewSet, basename="friends")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", UserLoginView.as_view(), name="login"),
    path("signup/", UserSignupView.as_view(), name="signup"),
    path(
        "user-search/", UserSearchViewSet.as_view({"get": "list"}), name="user-search"
    ),
    path(
        "friend-requests/",
        FriendRequestViewSet.as_view({"post": "create"}),
        name="friend-requests",
    ),
    path(
        "friend-requests/<int:pk>/accept/",
        FriendRequestViewSet.as_view({"post": "accept"}),
        name="friend-requests-accept",
    ),
    path(
        "friend-requests/<int:pk>/reject/",
        FriendRequestViewSet.as_view({"post": "reject"}),
        name="friend-requests-reject",
    ),
    path(
        "friend-requests/list-friends/",
        FriendRequestViewSet.as_view({"get": "list_friends"}),
        name="list-friends",
    ),
    path(
        "friend-requests/list-pending-requests/",
        FriendRequestViewSet.as_view({"get": "list_pending_requests"}),
        name="list-pending-requests",
    ),
]
