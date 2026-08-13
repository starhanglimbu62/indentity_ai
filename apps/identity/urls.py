from django.urls import path

from .views import IdentityDocumentUploadView


urlpatterns = [
    path(
        "documents/",
        IdentityDocumentUploadView.as_view(),
        name="identity-document-upload",
    ),
]