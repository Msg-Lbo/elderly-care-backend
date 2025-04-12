from rest_framework import serializers
from .models import Article, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "article_count", "created_at"]
        read_only_fields = ["article_count"]


class ArticleListSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Article
        fields = ["id", "title", "description", "category", "cover", "views", "likes_count", "created_at"]
        read_only_fields = ["views", "likes_count"]


class ArticleDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "category",
            "category_id",
            "cover",
            "views",
            "likes_count",
            "created_at",
        ]
        read_only_fields = ["views", "likes_count", "category"]
