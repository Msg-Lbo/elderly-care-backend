from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Article, Category
from .serializers import (
    CategorySerializer,
    ArticleListSerializer,
    ArticleDetailSerializer,
)


class CategoryListView(APIView):
    """文章分类视图"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取所有文章分类"""
        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(
                {"code": 200, "message": "获取分类列表成功", "data": serializer.data}
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": "服务器内部错误", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ArticleListView(APIView):
    """文章列表视图"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取文章列表"""
        try:
            category_name = request.query_params.get("category")
            is_hot = request.query_params.get("is_hot")
            search_title = request.query_params.get("search")
            articles = Article.objects.all()

            # 取阅读量前5的文章
            if is_hot:
                articles = articles.order_by("-views")[:5]

            if category_name:
                articles = articles.filter(category__name=category_name)
                if not articles.exists():
                    return Response(
                        {"code": 404, "message": "该分类下没有文章", "data": None},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            if search_title:
                articles = articles.filter(title__icontains=search_title)
                if not articles.exists():
                    return Response(
                        {"code": 404, "message": "没有找到相关文章", "data": None},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            serializer = ArticleListSerializer(articles, many=True)
            return Response(
                {"code": 200, "message": "获取文章列表成功", "data": serializer.data}
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": "服务器内部错误", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        """创建新文章"""
        try:
            serializer = ArticleDetailSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"code": 201, "message": "文章创建成功", "data": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"code": 400, "message": "文章创建失败", "data": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": "服务器内部错误", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ArticleDetailView(APIView):
    """文章详情视图"""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """获取文章详情"""
        try:
            article = Article.objects.get(pk=pk)
            article.increase_views()  # 增加阅读量
            serializer = ArticleDetailSerializer(article)
            return Response(
                {"code": 200, "message": "获取文章详情成功", "data": serializer.data}
            )
        except Article.DoesNotExist:
            return Response(
                {"code": 404, "message": "文章不存在", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": "服务器内部错误", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        """更新文章"""
        try:
            article = Article.objects.get(pk=pk)
            serializer = ArticleDetailSerializer(
                article, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"code": 200, "message": "文章更新成功", "data": serializer.data}
                )
            return Response(
                {"code": 400, "message": "文章更新失败", "data": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Article.DoesNotExist:
            return Response(
                {"code": 404, "message": "文章不存在", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": "服务器内部错误", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        """删除文章"""
        try:
            article = Article.objects.get(pk=pk)
            article.delete()
            return Response(
                {"code": 204, "message": "文章删除成功", "data": None},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Article.DoesNotExist:
            return Response(
                {"code": 404, "message": "文章不存在", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": "服务器内部错误", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ArticleLikeView(APIView):
    """文章点赞视图"""
    
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """点赞文章"""
        try:
            article = Article.objects.get(pk=pk)
            user = request.user
            
            if article.liked_users.filter(id=user.id).exists():
                return Response(
                    {"code": 400, "message": "您已经点赞过该文章", "data": None},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            article.liked_users.add(user)
            article.likes_count += 1
            article.save()
            
            return Response(
                {"code": 200, "message": "点赞成功", "data": {"likes_count": article.likes_count}},
                status=status.HTTP_200_OK,
            )
            
        except Article.DoesNotExist:
            return Response(
                {"code": 404, "message": "文章不存在", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": "服务器内部错误", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
