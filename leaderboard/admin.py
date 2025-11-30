from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Task, Points


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	def image_preview(self, obj):
		if getattr(obj, 'image', None):
			return mark_safe(f"<img src='{obj.image.url}' style='max-width:120px; max-height:90px;' />")
		return ""

	image_preview.short_description = "Proof"

	list_display = ("title", "user", "points", "completed", "image_preview", "created_at")
	list_filter = ("completed", "user")
	search_fields = ("title", "content", "user__username")


@admin.register(Points)
class PointsAdmin(admin.ModelAdmin):
	list_display = ("user", "score")
	search_fields = ("user__username",)
