from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("cio", "CIO"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=150, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    bio = models.TextField(blank=True, null=True)

    interests = models.ManyToManyField(
        Interest, blank=True, related_name="profiles"
    )

    is_completed = models.BooleanField(default=False)

    @property
    def is_leader(self):
        return self.role == "cio"

    def __str__(self):
        if self.display_name:
            return f"{self.display_name} ({self.user.username})"
        return f"{self.user.username} profile"


class ProfilePicture(models.Model):
    user = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="profile_picture"
    )
    image = models.ImageField(upload_to="profile_pictures/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ProfilePicture for {self.user.username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("message", "Message"),
        ("event", "Event"),
        ("mention", "Mention"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notif_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    text = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.text[:40]}"
    
def create_notification(user, notif_type, text, url=""):
    from .models import Notification
    Notification.objects.create(
        user=user,
        notif_type=notif_type,
        text=text,
        url=url,
    )