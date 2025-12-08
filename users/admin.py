from django.contrib import admin
from django.utils.html import format_html

from .models import Profile, Interest, ProfilePicture


class ProfilePictureAdmin(admin.ModelAdmin):
    list_display = ['user', 'image_preview', 'uploaded_at']
    readonly_fields = ['image_preview', 'uploaded_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 50%;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


admin.site.register(Profile)
admin.site.register(Interest)
admin.site.register(ProfilePicture, ProfilePictureAdmin)
