from django.contrib import admin

from .models import Bank


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "bank_code", "is_active", "created_at")
    search_fields = ("name", "bank_code")
    readonly_fields = ("api_key_hash", "created_at")

    def has_add_permission(self, request):
        return False
