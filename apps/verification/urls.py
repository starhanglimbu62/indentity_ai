from django.urls import path

from .views import (
    CreateVerificationRequestView,
    RequestChallengeView,
    ConsentView,
    VerifyRequestView,
)


urlpatterns = [

    path(
        "request/",
        CreateVerificationRequestView.as_view(),
        name="create-verification-request",
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
        "<uuid:pk>/verify/",
        VerifyRequestView.as_view(),
        name="verify-request",
    ),
]