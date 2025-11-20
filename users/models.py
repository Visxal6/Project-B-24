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
