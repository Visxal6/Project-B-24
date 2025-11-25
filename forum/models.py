from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


def forum_image_upload_to(instance, filename):
    # store uploads under forum/<user_id>/<filename> optionally with date
    return f'forum/{instance.author.id}/{filename}'

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Post(models.Model):
    TAG_CHOICES = [
        ('general', 'General'),
        ('food', 'Food'),
        ('leaderboard', 'Leaderboard'),
        ('cio_leaders', 'CIO Leaders'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    image = models.ImageField(upload_to=forum_image_upload_to, blank=False, null=False)
    title = models.CharField(max_length=200, default="Title")
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=50, choices=TAG_CHOICES, default='general')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Post by {self.author} at {self.created_at:%Y-%m-%d %H:%M}'

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.author} - {self.content[:20]}'
    
    @property
    def level(self):
        if not self.parent:
            return 0
        else:
            return 1 + self.parent.level


@receiver(pre_delete, sender=Post)
def delete_post_image_from_s3(sender, instance, **kwargs):
    """Delete the associated image from S3 when a Post is deleted."""
    if instance.image:
        try:
            # Delete the image file from storage
            logger.info(f"Deleting image from S3: {instance.image.name}")
            instance.image.delete(save=False)
            logger.info(f"Successfully deleted image: {instance.image.name}")
        except Exception as e:
            logger.error(f"Error deleting image from S3: {str(e)}", exc_info=True)