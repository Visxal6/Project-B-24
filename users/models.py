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
        ('student', 'Student'),
        ('cio', 'CIO'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    is_completed = models.BooleanField(default=False)

    interests = models.ManyToManyField(
        Interest, blank=True, related_name="profiles")

    def __str__(self):
        return f"{self.user.username} profile"


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    bio = models.TextField(blank=True, null=True)
    sustainability_interests = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
