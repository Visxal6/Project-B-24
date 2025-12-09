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



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'role',
                    'is_moderator', 'is_suspended')
    list_filter = ('role', 'is_moderator', 'is_suspended', 'is_completed')
    search_fields = ('user__username', 'display_name', 'user__email')
    readonly_fields = ('suspended_at', 'suspended_by')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'display_name', 'role', 'bio')
        }),
        ('Settings', {
            'fields': ('is_moderator', 'is_completed')
        }),
        ('Suspension', {
            'fields': ('is_suspended', 'suspension_reason', 'suspended_at', 'suspended_by'),
            'classes': ('collapse',)
        }),
    )

    def suspend_user_action(modeladmin, request, queryset):
        queryset.update(is_suspended=True)
    suspend_user_action.short_description = "Suspend selected users"

    def reinstate_user_action(modeladmin, request, queryset):
        queryset.update(is_suspended=False, suspension_reason=None,
                        suspended_at=None, suspended_by=None)
    reinstate_user_action.short_description = "Reinstate selected users"

    def promote_to_moderator(modeladmin, request, queryset):
        queryset.update(is_moderator=True)
    promote_to_moderator.short_description = "Promote to moderator"

    def demote_from_moderator(modeladmin, request, queryset):
        queryset.update(is_moderator=False)
    demote_from_moderator.short_description = "Remove moderator status"

    actions = [suspend_user_action, reinstate_user_action,
               promote_to_moderator, demote_from_moderator]


admin.site.register(Interest)
admin.site.register(ProfilePicture, ProfilePictureAdmin)
