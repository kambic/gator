from django import forms
from django.db import models

__all__ = ("EmbedVideoField", "EmbedVideoFormField")


class EmbedVideoField(models.URLField):
    """
    Model field for embedded video. Descendant of
    :py:class:`django.db.models.URLField`.
    """

    def formfield(self, **kwargs):
        defaults = {"form_class": EmbedVideoFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class EmbedVideoFormField(forms.URLField):
    """
    Form field for embeded video. Descendant of
    :py:class:`django.forms.URLField`
    """

    def validate(self, url):
        # if empty url is not allowed throws an exception
        super().validate(url)

        if not url:
            return

        try:
            backend = (url)
            backend.get_code()
        except:
            raise forms.ValidationError("TODO")
        return url
