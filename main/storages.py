from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)


class StaticStorage(S3Boto3Storage):
    """S3 storage for static files."""
    location = getattr(settings, 'AWS_LOCATION', 'static')
    default_acl = None
    custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)


class MediaStorage(S3Boto3Storage):
    """S3 storage for user uploaded media files."""
    location = getattr(settings, 'AWS_MEDIA_LOCATION', 'media')
    file_overwrite = False
    default_acl = 'public-read'
    custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Log S3 configuration on initialization
        logger.debug(f"MediaStorage initialized - AWS_STORAGE_BUCKET_NAME: {os.environ.get('AWS_STORAGE_BUCKET_NAME', 'NOT SET')}")
        logger.debug(f"MediaStorage location: {self.location}")
        logger.debug(f"AWS_S3_REGION_NAME: {os.environ.get('AWS_S3_REGION_NAME', 'NOT SET')}")
        logger.debug(f"AWS credentials available: Access Key={bool(os.environ.get('AWS_ACCESS_KEY_ID'))}, Secret Key={bool(os.environ.get('AWS_SECRET_ACCESS_KEY'))}")
        logger.debug(f"Custom domain: {self.custom_domain}")
    
    def url(self, name):
        """Override url method to log generated URLs and ensure public access."""
        logger.debug(f"Generating URL for file: {name}")
        url = super().url(name)
        logger.info(f"Generated URL for {name}: {url}")
        return url
    
    def save(self, name, content, max_length=None):
        """Override save to add logging."""
        logger.info(f"Starting S3 upload: file name={name}")
        try:
            saved_name = super().save(name, content, max_length=max_length)
            logger.info(f"Successfully uploaded to S3: {saved_name}")
            # Log the generated URL after save
            url = self.url(saved_name)
            logger.info(f"File accessible at: {url}")
            return saved_name
        except Exception as e:
            logger.error(f"Failed to upload to S3: {name} - Error: {str(e)}", exc_info=True)
            raise
