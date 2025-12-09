from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Task, Points, Event


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


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ("title", "created_by", "start_at", "location", "image_preview_admin")
	list_filter = ("start_at", "created_by")
	search_fields = ("title", "location", "created_by__username")

	def image_preview_admin(self, obj):
		if obj.image:
			return mark_safe(f"<img src='{obj.image.url}' style='max-width:160px; max-height:90px;' />")
		return ""

	image_preview_admin.short_description = "Image"
