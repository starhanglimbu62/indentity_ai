from django.urls import path

from .views import (
    CreateVerificationRequestView,
    RequestChallengeView,
    ConsentView,
    GenerateProofView,
    VerifyRequestView,
    ListVerificationRequestsView,
    GetVerificationRequestView,
    ListNotificationsView,
    MarkNotificationAsReadView,
    SearchUsersView,
    GetBankRequestsView,
    GetBankRequestDetailView,
)


urlpatterns = [

    path(
        "request/",
        CreateVerificationRequestView.as_view(),
        name="create-verification-request",
    ),

    path(
        "requests/",
        ListVerificationRequestsView.as_view(),
        name="list-verification-requests",
    ),

    path(
        "requests/<uuid:pk>/",
        GetVerificationRequestView.as_view(),
        name="get-verification-request",
    ),

    path(
        "<uuid:pk>/challenge/",
        RequestChallengeView.as_view(),
        name="request-challenge",
    ),

    path(
        "<uuid:pk>/consent/",
        ConsentView.as_view(),
        name="verification-consent",
    ),

    path(
        "<uuid:pk>/prove/",
        GenerateProofView.as_view(),
        name="generate-verification-proof",
    ),

    path(
        "<uuid:pk>/verify/",
        VerifyRequestView.as_view(),
        name="verify-request",
    ),

    path(
        "notifications/",
        ListNotificationsView.as_view(),
        name="list-notifications",
    ),

    path(
        "notifications/<uuid:pk>/read/",
        MarkNotificationAsReadView.as_view(),
        name="mark-notification-read",
    ),

    path(
        "search-users/",
        SearchUsersView.as_view(),
        name="search-users",
    ),

    path(
        "bank-requests/",
        GetBankRequestsView.as_view(),
        name="list-bank-requests",
    ),

    path(
        "bank-requests/<uuid:pk>/",
        GetBankRequestDetailView.as_view(),
        name="get-bank-request",
    ),
]