from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title"]
    raw_id_fields = ["author", "tags", "likes"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["title"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "author"]
    raw_id_fields = ["post", "author"]
