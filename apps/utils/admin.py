import json

from django.contrib import admin
# from django.contrib.postgres.fields import JSONField  # or from django.db.models import JSONField in Django 3.1+
from django.utils.html import format_html

class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]




class ReadOnlyAdminJ(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        # Make all model fields read-only
        fields = [field.name for field in self.model._meta.fields]

        # If there's a JSONField, replace it with the pretty display method
        if "config" in fields:
            fields.remove("config")
            fields.append("pretty_config")  # replace raw with pretty version

        return fields

    def pretty_config(self, obj):
        if not obj.config:
            return "-"
        try:
            pretty = json.dumps(obj.config, indent=2, ensure_ascii=False)
        except Exception:
            return str(obj.config)
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', pretty)

    pretty_config.short_description = "Config (Pretty JSON)"

    # Make the entire model read-only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
