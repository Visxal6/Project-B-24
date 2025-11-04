from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    """S3 storage for static files."""
    location = getattr(settings, 'AWS_LOCATION', 'static')
    default_acl = None


class MediaStorage(S3Boto3Storage):
    """S3 storage for user uploaded media files."""
    location = getattr(settings, 'AWS_MEDIA_LOCATION', 'media')
    file_overwrite = False
    default_acl = None
