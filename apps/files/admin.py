from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE

from .models import (
    Category,
    Comment,
    EncodeProfile,
    Encoding,
    Language,
    Media,
    Page,
    Subtitle,
    Tag,
    TinyMCEMedia,
    TranscriptionRequest,
    VideoTrimRequest,
)


class CommentAdmin(admin.ModelAdmin):
    search_fields = ["text"]
    list_display = ["text", "add_date", "user", "media"]
    ordering = ("-add_date",)
    readonly_fields = ("user", "media", "parent")


class MediaAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = [
        "title",
        "user",
        "add_date",
        "media_type",
        "duration",
        "state",
        "is_reviewed",
        "encoding_status",
        "featured",
        "get_comments_count",
    ]
    list_filter = ["state", "is_reviewed", "encoding_status", "featured", "category"]
    ordering = ("-add_date",)
    readonly_fields = ("user", "tags", "category", "channel")

    def get_comments_count(self, obj):
        return obj.comments.count()

    @admin.action(description="Generate missing encoding(s)", permissions=["change"])
    def generate_missing_encodings(modeladmin, request, queryset):
        for m in queryset:
            m.encode(force=False)

    actions = [generate_missing_encodings]
    get_comments_count.short_description = "Comments count"


class TagAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = ["title", "user", "media_count"]
    readonly_fields = ("user", "media_count")


class EncodeProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "extension", "resolution", "codec", "description", "active")
    list_filter = ["extension", "resolution", "codec", "active"]
    search_fields = ["name", "extension", "resolution", "codec", "description"]
    list_per_page = 100
    fields = ("name", "extension", "resolution", "codec", "description", "active")


class LanguageAdmin(admin.ModelAdmin):
    pass


class SubtitleAdmin(admin.ModelAdmin):
    list_display = ["id", "language", "media"]
    list_filter = ["language"]
    search_fields = ["media__title"]
    readonly_fields = ("media", "user")


class VideoTrimRequestAdmin(admin.ModelAdmin):
    list_display = ["media", "status", "add_date", "video_action", "media_trim_style", "timestamps"]
    list_filter = ["status", "video_action", "media_trim_style", "add_date"]
    search_fields = ["media__title"]
    readonly_fields = ("add_date",)
    ordering = ("-add_date",)


class EncodingAdmin(admin.ModelAdmin):
    list_display = ["get_title", "chunk", "profile", "progress", "status", "has_file"]
    list_filter = ["chunk", "profile", "status"]

    def get_title(self, obj):
        return str(obj)

    get_title.short_description = "Encoding"

    def has_file(self, obj):
        return obj.media_encoding_url is not None

    has_file.short_description = "Has file"


class TranscriptionRequestAdmin(admin.ModelAdmin):
    list_display = ["media", "add_date", "status", "translate_to_english"]
    list_filter = ["status", "translate_to_english", "add_date"]
    search_fields = ["media__title"]
    readonly_fields = ("add_date", "logs")
    ordering = ("-add_date",)


class PageAdminForm(forms.ModelForm):
    description = forms.CharField(widget=TinyMCE())

    def clean_description(self):
        content = self.cleaned_data['description']
        # Add sandbox attribute to all iframes
        content = content.replace('<iframe ', '<iframe sandbox="allow-scripts allow-same-origin allow-presentation" ')
        return content

    class Meta:
        model = Page
        fields = "__all__"


class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm


admin.site.register(EncodeProfile, EncodeProfileAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Encoding, EncodingAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Subtitle, SubtitleAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(VideoTrimRequest, VideoTrimRequestAdmin)
admin.site.register(TranscriptionRequest, TranscriptionRequestAdmin)

Media._meta.app_config.verbose_name = "Media"
