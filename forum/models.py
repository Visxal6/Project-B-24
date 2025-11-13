from django.db import models
from django.conf import settings


def forum_image_upload_to(instance, filename):
    # store uploads under forum/<user_id>/<filename> optionally with date
    return f'forum/{instance.author.id}/{filename}'


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    image = models.ImageField(upload_to=forum_image_upload_to)
    title = models.CharField(max_length=200, default="Title")
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Post by {self.author} at {self.created_at:%Y-%m-%d %H:%M}'
