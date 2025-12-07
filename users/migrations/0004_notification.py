from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    # IMPORTANT: change '0003_profile' if your previous users migration
    # has a different filename (e.g. '0002_profile' etc.)
    dependencies = [
        ('users', '0003_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('notif_type', models.CharField(max_length=50)),
                ('text', models.CharField(max_length=255)),
                ('is_read', models.BooleanField(default=False)),
                ('url', models.CharField(max_length=255, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'user',
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        related_name='notifications',
                    ),
                ),
            ],
        ),
    ]
