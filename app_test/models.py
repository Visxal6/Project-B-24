from django.db import models

# Create your models here.

# TestImage table


class TestImage(models.Model):
    # image field
    image = models.ImageField(upload_to="test_uploads/")
    # upload_at field
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Test image {self.id}"
