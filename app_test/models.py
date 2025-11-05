from django.db import models

# Create your models here.


class TestImage(models.Model):
    image = models.ImageField(upload_to="test_uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Test image {self.id}"
