import uuid

from django.db import models


class Bank(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=255
    )

    bank_code = models.CharField(
        max_length=50,
        unique=True
    )

    api_key_hash = models.CharField(
        max_length=64,
        unique=True,
    )

    webhook_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.name