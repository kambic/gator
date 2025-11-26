from xml.dom import minidom

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html

from .models import Video, Package
from .tasks import validate_adi


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'user', 'created_at')
    readonly_fields = ('processing_log', 'metadata')
    list_filter = ('status', 'created_at')


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('vendor/highlightjs/default.min.css',)}
        js = (
            'vendor/highlightjs/highlight.min.js',
            'admin/js/init-hljs.js',
        )

    list_display = ('id', 'created_at', 'created_at', 'name', 'original')
    list_filter = ('created_at', 'created_at', 'original')
    search_fields = ('name',)
    fields = 'name', 'original', 'manifest', 'adi_xml', 'xml_preview'
    readonly_fields = ('xml_preview',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [path('<int:object_id>/my-view/', self.admin_site.admin_view(self.my_view), name='validate_adi')]

        return custom_urls + urls

    def my_view(self, request, object_id):
        try:
            obj = self.get_object(request, object_id)
        except self.model.DoesNotExist:
            from django.http import Http404

            raise Http404("Object not found")

        if request.method == "GET":
            context = dict(
                self.admin_site.each_context(request),
                # Optional: Pass the object to the context if you render a template
                current_object=obj,
            )

            validate_adi(obj.manifest.file)

            # return self.render_to_response(context)
            return HttpResponse(f"Admin object name: {obj.name} with ID: {obj.pk}")

        else:
            # Handle POST requests, e.g., processing a form related to 'obj'
            pass

    @admin.display(description='XML Preview')
    def xml_preview(self, obj):
        if not obj.adi_xml:
            return "(no XML file uploaded)"

        return format_html(
            """
                <!-- Core -->
                <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css">
                
                <!-- Essential for proper XML -->
                <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
                
                <!-- OR manually load the exact languages you need (faster): -->
                <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markup-templating.min.js"></script> <!-- required dependency -->
                <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-xml-doc.min.js"></script>   <!-- this is the real XML one -->
                <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-html.min.js"></script>      <!-- alias of markup -->
                <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-svg.min.js"></script>

            <pre style="font-size: 13px;">
                <code class="language-xml">{}</code>
            </pre>
            """,
            obj.adi_xml,
        )
