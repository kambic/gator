import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    AtemeJobEvent,
    VidraJob,
    ExpiredEdgeware,
    SFTPGoEvent,
    Provider,
    Edgeware,
    Stream
)
from ..utils.admin import ReadOnlyAdmin


@admin.register(Provider)
class ProviderAdmin(ImportExportModelAdmin):

    class ProviderResource(resources.ModelResource):
        class Meta:
            model = Provider

    class EdgesInline(admin.TabularInline):
        model = Edgeware
        extra = 0
        show_change_link = True
        can_delete = False

        def has_add_permission(self, request, obj=None):
            return False

        def has_change_permission(self, request, obj=None):
            return False

        def has_delete_permission(self, request, obj=None):
            return False

    resource_classes = [ProviderResource]
    inlines = [EdgesInline]
    list_display = ("user__name", 'active', "num_expired")
    readonly_fields = (
        # "user",
        "logo_preview",
        "vidra_task",
        "queue",
        "view_ftp_auth",
    )
    list_filter = (
        "active",
    )
    fieldsets = (
        (
            "Basic Info",
            {
                "fields": ("user", "catalog_name", "logo_preview"),
            },
        ),

        (
            "Ingest",
            {
                "fields":
                    (
                        "vidra_task",
                        "queue",
                        "view_ftp_auth",
                        ("use_staging_db", "enable_drm"),
                        ("default_active_tv", "default_active_web", "default_active_mobile", "default_active_lte",)
                    ),
                "description": "Ingest data for Vidra",
            }
        )

    )

    def get_queryset(self, request):
        return Provider.objects.with_expired_count()

    @admin.display(ordering="num_expired")
    def num_expired(self, obj):
        return obj.num_expired

    @admin.display(empty_value="???")
    def view_ftp_auth(self, obj):
        return obj.provider_fs

    def logo_preview(self, obj):
        path = f"images/logo/{obj.user.username}.png"

        return format_html(
            '<img src="{}" alt="/" width="60" style="border:1px solid #ccc;"/>',
            static(path),
        )

    logo_preview.short_description = "Logo Preview"

from django.templatetags.static import static # Don't forget this import if it's not there

class StreamInline(admin.StackedInline):
    model = Stream
    extra = 0
    # Note: 'media' is not a real field, it is used by Django Admin
    readonly_fields = 'type', 'uri', 'video_player'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def video_player(self, obj):
        if obj.uri:
            video_id = f"video_{obj.pk}"
            video_url = f"http://ew-backend-01.tv.telekom.si{obj.uri}"

            # The HTML is now much simpler.
            # It just provides the necessary container, video tag, and data attributes.
            html_code = """
                <div class="js-video-player" data-stream-url="{url}"
                     style="position: relative; display: inline-block;">
                    <video id="{video_id}" controls preload="metadata"
                           style="width: 480px; height: 270px; border:1px solid #ccc; background:#000;"></video>
                </div>
            """

            return format_html(
                html_code,
                video_id=video_id,
                url=video_url
            )
        return "No video uploaded."

    video_player.short_description = "Video Player"

    # --- NEW: Media Inner Class ---
    class Media:
        js = (
            # 1. Vendor Libraries (dashjs and hls should be loaded first)
            'vendor/dashjs/dash.all.min.js',  # Replaced static() with string path
            'vendor/hls/hls.min.js',  # Replaced static() with string path

            # 2. Your custom initialization script
            'js/video_player_init.js',
        )


class HarvestFilter(admin.SimpleListFilter):
    title = "Has offer_id"
    parameter_name = "offer_id_exists"

    def lookups(self, request, model_admin):
        return (
            ("yes", "With offer_id"),
            ("no", "Without offer_id"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(offer_id__isnull=False)
        if self.value() == "no":
            return queryset.filter(offer_id__isnull=True)
        return queryset


class EdgewareResource(resources.ModelResource):
    class Meta:
        model = Edgeware


@admin.register(Edgeware, ExpiredEdgeware)
class EdgewareAdmin(ImportExportModelAdmin):
    class EdgewareResource(resources.ModelResource):
        class Meta:
            model = Edgeware

    resource_classes = [EdgewareResource]
    inlines = (StreamInline,)
    readonly_fields = (
        'title',
        'short_name',
        'ingested',
        'status',
        'ftp_dir',
        'celery_id',
        'ew_id',
        'encoder',
        'host',
        'created',
        'modified',
        'playable',
        'content_duration',
        'expired',
        'offer_id',
        'msg',
        'mtcms_stag',
        'mtcms_prod',
        'provider',
    )
    list_display = (
        "short_name",
        "created",
        'expired',
        'provider',
        'offer_id',
        'mtcms_stag',
        'mtcms_prod',
        'playable',
        "ew_id",
        "status",
    )
    list_filter = (HarvestFilter, "provider", "mtcms_stag", "mtcms_prod", "ew_dump_loaded", "status", "ingested",)
    search_fields = ("title", "celery_id", "ew_id", "ftp_dir", "stream__uri")
    fieldsets = [
        ('Loaded', {
            'fields': [
                'title',
                'provider',
                'status',
                'ftp_dir',
                'created',
                'modified',
                'expired',
                'ingested',
                'content_duration'
            ],
        }),
        ('Metadata', {
            'fields': ['celery_id',
                       'ew_id',
                       'offer_id',
                       'encoder', 'host', 'msg',
                       ('mtcms_stag', 'mtcms_prod', 'playable',)],
        })
    ]


# @admin.register(Packet)
class PacketAdmin(admin.ModelAdmin):
    readonly_fields = 'provider', 'title', 'collect_file_stats', 'file', 'size'
    fieldsets = [
        ('packets', {
            'fields': [
                'title',
                'provider',
                'file',
                'size'
            ],
        }),
        ('metadata', {
            'fields': [
                'collect_file_stats'
            ]
        })
    ]
    list_display = (
        "title",
        "provider",
        'size',
        "delivery_time",
        "status",
        "file",
    )
    list_filter = (
        "status",
        "provider",
    )
    actions = ["vidra_ping"]

    @admin.action(description="vidra ping selected")
    def vidra_ping(self, request, queryset):
        for item in queryset:
            # logger.info("Pinging selected %s for vidra" % item.file)
            provider = item.provider
            task = provider.get_provider_task

            item.move_to_vidra_ftp_folder()

            result = task.delay(item.task_payload)


class AtemeEventInline(admin.StackedInline):
    model = AtemeJobEvent
    extra = 0
    can_delete = False
    show_change_link = True

    @admin.display(empty_value="???", description="prettified")
    def prettified(self, instance):
        """Function to display pretty version of our data"""

        das = json.dumps(instance.msg, indent=4, sort_keys=True)
        return mark_safe(f"<pre>{das}</pre>")


@admin.register(VidraJob)
class VidraJobAdmin(ReadOnlyAdmin):
    list_display = ("uuid", "name", "state")

    # inlines = [AtemeEventInline]
    # formfield_overrides = {
    #     JSONField: {"widget": JSONEditorWidget},
    # }
    list_filter = ("state", "name")


@admin.register(SFTPGoEvent)
class SFTPGoEventAdmin(admin.ModelAdmin):
    list_display = [
        "colored_event",
        "username",
        "ip",
        "protocol",
        "short_path",
        "formatted_size",
        "status_icon",
        "date",
        "elapsed_ms",
    ]
    list_filter = (
        "event",
        "protocol",
        "status",
        "date",  # Built-in date hierarchy + range filter
        "username",
        "ip",
    )
    search_fields = (
        "username",
        "ip",
        "path",
        "virtual_path",
        "object_name",
        "error",
    )
    readonly_fields = [f.name for f in SFTPGoEvent._meta.fields]  # Everything readonly
    exclude = ["id"]  # Hide primary key

    # Performance: only load needed fields in list view
    list_select_related = False
    list_per_page = 50

    # Date hierarchy for quick navigation
    date_hierarchy = "date"

    # Custom columns
    def colored_event(self, obj):
        colors = {
            "upload": "success",
            "download": "info",
            "delete": "danger",
            "rename": "warning",
            "mkdir": "primary",
        }
        color = colors.get(obj.event.lower(), "secondary")
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.event.upper()
        )

    colored_event.short_description = "Event"

    def short_path(self, obj):
        return obj.virtual_path or obj.path.split("/")[-1] or "-"

    short_path.short_description = "File/Path"

    def formatted_size(self, obj):
        if not obj.file_size:
            return "-"
        size = obj.file_size
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    formatted_size.short_description = "Size"

    def status_icon(self, obj):
        if obj.status == 1:
            return format_html('<span style="color:green;">✓</span> Success')
        return format_html('<span style="color:red;">✗</span> Error')

    status_icon.short_description = "Status"

    def elapsed_ms(self, obj):
        return f"{obj.elapsed} ms" if obj.elapsed else "-"

    elapsed_ms.short_description = "Duration"

    # Make JSON pretty in detail view
    def object_data_pretty(self, instance):
        if not instance.object_data:
            return "-"
        pretty = json.dumps(instance.object_data, indent=2, ensure_ascii=False)
        return format_html("<pre>{}</pre>", pretty)

    object_data_pretty.short_description = "Object Data"

    # Override fields display in detail view
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj:
            # Replace raw object_data with pretty version
            fields = list(fields)
            if "object_data" in fields:
                fields[fields.index("object_data")] = "object_data_pretty"
        return fields

    # Optimize queryset
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.only(
            "event", "username", "ip", "protocol",
            "path", "virtual_path", "file_size",
            "status", "date", "elapsed", "object_data"
        )

    # Optional: actions
    actions = None  # Disable delete/select-all for audit logs (recommended)

    # Disable add/delete permissions
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
