from django.core.files.storage import FileSystemStorage

fenix_storage = FileSystemStorage(
    location="/export/isilj/fenix2",
    base_url="/fenix2/",  # must be served by nginx/apache
)
