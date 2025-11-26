from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm

from .models import User


class UserAdmin(BaseUserAdmin):
    # Use Django’s built-in change password form
    change_password_form = AdminPasswordChangeForm

    # Fields shown in the list view
    list_display = [
        "username",
        "name",
        "email",
        "is_superuser",
        "is_editor",
        "is_manager",
    ]

    search_fields = ["email", "username", "name"]
    ordering = ("-date_added",)

    # Remove fields you don’t want
    exclude = [
        # "first_name",
        # "last_name",
        "title",
        "location",
        "media_count",
    ]


admin.site.register(User, UserAdmin)
