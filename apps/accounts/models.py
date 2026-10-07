from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bank = models.ForeignKey(
        "banks.Bank",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="operators",
    )

    email = models.EmailField(unique=True)

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    is_identity_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username