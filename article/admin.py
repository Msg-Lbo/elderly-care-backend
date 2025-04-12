from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Article


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "article_count", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)

    def article_count(self, obj):
        return obj.article_count()

    article_count.short_description = "文章数量"


class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "category", "cover_preview", "views", "likes_count", "created_at")
    search_fields = ("title", "content")
    list_filter = ("category", "created_at")
    readonly_fields = ("views", "likes_count", "cover_preview")
    filter_horizontal = ()
    list_per_page = 20

    fieldsets = (
        ("基本信息", {"fields": ("title", "description", "category", "cover", "content")}),
        ("统计信息", {"fields": ("views", "likes_count")}),
    )

    def cover_preview(self, obj):
        if obj.cover:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.cover.url)
        return "-"
    cover_preview.short_description = "封面预览"


admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
