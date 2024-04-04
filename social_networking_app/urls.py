from django.urls import include, path

from social_networking_app.views import (
    FriendRequestStatus,
    FriendRequestViewSet,
    FriendViewSet,
    UserSearchViewSet,

)

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("friend-list/", FriendViewSet.as_view(), name="friend-list"),
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
        FriendRequestStatus.as_view({"post": "accept"}),
        name="friend-requests-accept",
    ),
    path(
        "friend-requests/<int:pk>/reject/",
        FriendRequestStatus.as_view({"post": "reject"}),
        name="friend-requests-reject",
    ),
    path(
        "friend-requests/list-pending-requests/",
        FriendRequestStatus.as_view({"get": "list_pending_requests"}),
        name="list-pending-requests",
    ),
]
