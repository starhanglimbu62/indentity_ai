from django.urls import path

from .views import (
    CreateVerificationRequestView,
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