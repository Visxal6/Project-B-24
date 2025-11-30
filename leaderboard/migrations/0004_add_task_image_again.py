"""Add image field back to Task so weekly proofs can be stored.

This migration re-adds the ImageField after it was removed in 0003_remove_task_image.py
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("leaderboard", "0003_remove_task_image"),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='image',
            field=models.ImageField(upload_to='task_proofs/', null=True, blank=True),
        ),
    ]
