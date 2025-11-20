from django.contrib import admin
from .models import Task, Points


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = ("title", "user", "points", "completed", "created_at")
	list_filter = ("completed", "user")
	search_fields = ("title", "content", "user__username")


@admin.register(Points)
class PointsAdmin(admin.ModelAdmin):
	list_display = ("user", "score")
	search_fields = ("user__username",)
