from django.contrib import admin
from .models import Post, PostImage


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('caption', 'author__username')


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'uploaded_at')
    list_filter = ('uploaded_at', 'post__author')
    search_fields = ('post__title', 'post__author__username')
