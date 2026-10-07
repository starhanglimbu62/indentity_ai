from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Bank access", {"fields": ("bank",)}),
    )
    list_display = DjangoUserAdmin.list_display + ("bank",)
