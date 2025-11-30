from django.db import models
from django.conf import settings
from django.utils import timezone


class Points(models.Model):
    """One row per user storing accumulated points."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}: {self.score} points"

    def add(self, amount: int):
        self.score = (self.score or 0) + (amount or 0)
        self.save(update_fields=["score"])


class Task(models.Model):
    """A task assigned/created by a user with a point value."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    points = models.IntegerField(default=0)
    # optional photo proof for weekly challenges
    image = models.ImageField(upload_to='task_proofs/', blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    def mark_completed(self):
        if not self.completed:
            self.completed = True
            self.save(update_fields=["completed", "updated_at"])
            pts, _ = Points.objects.get_or_create(user=self.user)
            pts.add(self.points)

    def mark_incomplete(self):
        if self.completed:
            self.completed = False
            self.save(update_fields=["completed", "updated_at"])
            pts, _ = Points.objects.get_or_create(user=self.user)
            pts.add(-self.points)

    def delete(self, *args, **kwargs):
        # remove stored image file (if any) when deleting the Task
        try:
            if self.image:
                self.image.delete(save=False)
        except Exception:
            pass
        return super().delete(*args, **kwargs)