from importlib import import_module

from django.core.exceptions import ImproperlyConfigured


class PageTitleMixin(object):
    def get_page_title(self, context):
        return getattr(self, "page_title", "Default Page Title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_page_title(context)

        return context


def import_class(path):
    path_bits = path.split(".")

    if len(path_bits) < 2:
        message = f"'{path}' is not a complete Python path."
        raise ImproperlyConfigured(message)

    class_name = path_bits.pop()
    module_path = ".".join(path_bits)
    module_itself = import_module(module_path)

    if not hasattr(module_itself, class_name):
        message = f"The Python module '{module_path}' has no '{class_name}' class."
        raise ImportError(message)

    return getattr(module_itself, class_name)
