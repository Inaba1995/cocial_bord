from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'text')
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'author__username')
