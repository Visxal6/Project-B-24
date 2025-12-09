from django.contrib import admin
from .models import Post, Comment, PostImage


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'created_at',
                    'is_flagged_inappropriate')
    list_filter = ('created_at', 'author', 'is_flagged_inappropriate')
    search_fields = ('caption', 'title', 'author__username')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Post Information', {
            'fields': ('author', 'title', 'caption', 'image', 'tag', 'created_at')
        }),
        ('Moderation', {
            'fields': ('is_flagged_inappropriate', 'moderation_note')
        }),
    )

    def make_flagged(modeladmin, request, queryset):
        queryset.update(is_flagged_inappropriate=True)
    make_flagged.short_description = "Mark selected posts as inappropriate"

    def unflag(modeladmin, request, queryset):
        queryset.update(is_flagged_inappropriate=False)
    unflag.short_description = "Clear inappropriate flag"

    actions = [make_flagged, unflag]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'created_at',
                    'is_flagged_inappropriate')
    list_filter = ('created_at', 'author', 'is_flagged_inappropriate', 'post')
    search_fields = ('content', 'author__username')
    readonly_fields = ('created_at', 'post')
    fieldsets = (
        ('Comment Information', {
            'fields': ('post', 'author', 'content', 'parent', 'created_at', 'is_deleted')
        }),
        ('Moderation', {
            'fields': ('is_flagged_inappropriate', 'moderation_note')
        }),
    )

    def make_flagged(modeladmin, request, queryset):
        queryset.update(is_flagged_inappropriate=True)
    make_flagged.short_description = "Mark selected comments as inappropriate"

    def unflag(modeladmin, request, queryset):
        queryset.update(is_flagged_inappropriate=False)
    unflag.short_description = "Clear inappropriate flag"

    actions = [make_flagged, unflag]


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'uploaded_at')
    list_filter = ('uploaded_at', 'post__author')
    search_fields = ('post__title', 'post__author__username')
