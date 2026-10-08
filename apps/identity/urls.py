from django.urls import path

from .views import CredentialListView, IdentityDocumentUploadView


urlpatterns = [
    path(
        "credentials/",
        CredentialListView.as_view(),
        name="credential-list",
    ),
    path(
        "documents/",
        IdentityDocumentUploadView.as_view(),
        name="identity-document-upload",
    ),
]