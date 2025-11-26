from django import forms
from .models import Video


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['original_package', 'title']

    def clean_original_package(self):
        file = self.cleaned_data['original_package']
        if not file.name.lower().endswith(('.tar', '.tar.gz', '.tgz')):
            raise forms.ValidationError("Only .tar, .tar.gz or .tgz packages allowed")
        if file.size > 200 * 1024 * 1024:  # 200 MB
            raise forms.ValidationError("File too large (max 200 MB)")
        return file
