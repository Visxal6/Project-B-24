from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


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
    is_moderator = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspension_reason = models.TextField(blank=True, null=True)
    suspended_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='suspended_users')

    @property
    def is_leader(self):
        return self.role == "cio"

    def suspend(self, moderator, reason):
        """Suspend this user"""
        self.is_suspended = True
        self.suspended_at = timezone.now()
        self.suspension_reason = reason
        self.suspended_by = moderator
        self.save()

    def reinstate(self):
        """Reinstate this user"""
        self.is_suspended = False
        self.suspended_at = None
        self.suspension_reason = None
        self.suspended_by = None
        self.save()

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
