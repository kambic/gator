# models.py
from django.db import models
from django.urls import reverse
from django.utils.html import format_html


class FileNode(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    is_folder = models.BooleanField(default=False, verbose_name="Is Folder")
    file_size = models.PositiveBigIntegerField(null=True, blank=True, help_text="In bytes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_folder', 'name']
        verbose_name = "File / Folder"
        verbose_name_plural = "File System Tree"

    def __str__(self):
        return self.get_full_path()

    def get_full_path(self):
        path = []
        node = self
        while node:
            path.append(node.name)
            node = node.parent
        return "/".join(reversed(path)) or "/"

    # Icon for admin list
    def icon(self):
        if self.is_folder:
            return format_html('<i class="fa-solid fa-folder text-yellow-500 text-lg"></i>')
        ext = self.name.lower().split(".")[-1]
        icons = {
            "pdf": "fa-file-pdf text-red-500",
            "png": "fa-image text-green-500",
            "jpg": "fa-image text-green-500",
            "jpeg": "fa-image text-green-500",
            "psd": "fa-file-lines text-purple-500",
            "zip": "fa-file-zipper text-gray-500",
            "docx": "fa-file-word text-blue-600",
            "xlsx": "fa-file-excel text-green-600",
        }
        icon_class = icons.get(ext, "fa-file text-gray-400")
        return format_html(f'<i class="fa-solid {icon_class} text-lg"></i>')

    icon.short_description = ""
    icon.admin_order_field = "name"
