from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from ckeditor.fields import RichTextField


class Category(models.Model):
    """
    文章分类模型
    """

    name = models.CharField("分类名称", max_length=100)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return self.name

    def article_count(self):
        """获取分类下的文章数量"""
        return self.article_set.count()

    article_count.short_description = "文章数量"

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类"
        ordering = ["-created_at"]


class Article(models.Model):
    """
    文章模型
    """

    title = models.CharField("标题", max_length=200)
    content = RichTextField("内容")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="分类"
    )
    cover = models.ImageField("封面图", upload_to="article/covers/", blank=True, null=True)
    description = models.CharField("摘要", max_length=200, blank=True)
    views = models.PositiveIntegerField("阅读量", default=0)
    likes_count = models.PositiveIntegerField("点赞数", default=0)
    liked_users = models.ManyToManyField(
        'auth.User', 
        verbose_name="点赞用户",
        blank=True,
        related_name="liked_articles"
    )
    created_at = models.DateTimeField("创建时间", default=timezone.now)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return self.title

    def increase_views(self):
        """增加阅读量"""
        self.views += 1
        self.save(update_fields=["views"])

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ["-created_at"]
