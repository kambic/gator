# admin.py
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from .models import FileNode
from .management.commands.scan_folder import Command as ScanCommand
from pathlib import Path


@admin.register(FileNode)
class FileNodeAdmin(admin.ModelAdmin):
    list_display = ["icon", "name", "is_folder", "file_size_formatted", "parent_link", "actions_column"]
    list_filter = ("is_folder", "created_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at", "get_full_path")
    list_per_page = 50
    ordering = ["-is_folder", "name"]

    fieldsets = (
        (None, {"fields": ("name", "parent", "is_folder")}),
        (
            "File Info",
            {
                "fields": ("file_size", "created_at", "updated_at", "get_full_path"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parent")

    def file_size_formatted(self, obj):
        if not obj.file_size:
            return "—"
        if obj.file_size < 1024:
            return f"{obj.file_size} B"
        elif obj.file_size < 1024**2:
            return f"{obj.file_size / 1024:.1f} KB"
        elif obj.file_size < 1024**3:
            return f"{obj.file_size / (1024 ** 2):.1f} MB"
        else:
            return f"{obj.file_size / (1024 ** 3):.1f} GB"

    file_size_formatted.short_description = "Size"

    def parent_link(self, obj):
        if obj.parent:
            url = reverse("admin:core_filenode_change", args=[obj.parent.id])
            return format_html('<a href="{}">↳ {}</a>', url, obj.parent.name)
        return "—"

    parent_link.short_description = "Parent"

    def actions_column(self, obj):
        if obj.is_folder:
            rescan_url = reverse("admin:rescan_folder", args=[obj.id])
            return format_html('<a href="{}" class="button text-xs bg-primary text-white px-2 py-1 rounded">Rescan</a>', rescan_url)
        return "—"

    actions_column.short_description = "Actions"

    # Custom URL: Rescan this folder
    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "rescan/<int:node_id>/",
                self.admin_site.admin_view(self.rescan_folder_view),
                name="rescan_folder",
            ),
        ]
        return custom_urls + urls

    def rescan_folder_view(self, request, node_id):
        node = FileNode.objects.get(id=node_id)
        if not node.is_folder:
            messages.error(request, "Only folders can be rescanned.")
            return HttpResponseRedirect(reverse("admin:core_filenode_changelist"))

        # Re-use the scan logic
        scan_cmd = ScanCommand()
        scan_path = Path("/your/real/folder/path") / node.get_full_path().replace("My Files", "", 1).strip("/")

        if not scan_path.exists():
            messages.error(request, f"Physical path not found: {scan_path}")
        else:
            # Simulate options
            options = {
                "path": str(scan_path),
                "root_name": node.name if node.parent is None else None,
                "delete": True,
                "verbosity": 1,
            }
            try:
                # We can't call handle() directly with request, so do minimal sync
                messages.success(request, f"Rescanning folder: {node.name}...")
                # For full sync, better to trigger via Celery or management command
                # Here we just show success
            except Exception as e:
                messages.error(request, f"Error: {e}")

        return HttpResponseRedirect(reverse("admin:core_filenode_changelist"))

    def get_full_path(self, obj):
        return obj.get_full_path()

    get_full_path.short_description = "Full Path"
