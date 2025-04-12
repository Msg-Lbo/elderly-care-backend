from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Service
from .serializers import ServiceSerializer
from django.core.exceptions import ValidationError
from django.utils import timezone

class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Service.objects.all()
        status_param = self.request.query_params.get('status', None)
        
        if status_param:
            # 验证状态参数是否有效
            valid_statuses = [status[0] for status in Service.STATUS_CHOICES]
            if status_param not in valid_statuses:
                raise ValidationError(f"无效的状态值。有效值为: {', '.join(valid_statuses)}")
            queryset = queryset.filter(status=status_param)
        
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "code": 200,
                "message": "获取服务列表成功",
                "data": serializer.data
            })
        except ValidationError as e:
            return Response({
                "code": 400,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"获取服务列表失败：{str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ServiceCreateView(generics.CreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "code": 201,
                "message": "服务创建成功",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                "code": 400,
                "message": f"数据验证失败：{str(e)}",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"服务器内部错误：{str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ServiceUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            instance = Service.objects.get(id=id)
            serializer = ServiceSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "code": 200,
                "message": "服务更新成功",
                "data": serializer.data
            })
        except Service.DoesNotExist:
            return Response({
                "code": 404,
                "message": "未找到该服务",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({
                "code": 400,
                "message": f"数据验证失败：{str(e)}",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"服务器内部错误：{str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ServiceDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            instance = Service.objects.get(id=id)
            instance.delete()
            return Response({
                "code": 200,
                "message": "服务删除成功",
                "data": None
            })
        except Service.DoesNotExist:
            return Response({
                "code": 404,
                "message": "未找到该服务",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"服务器内部错误：{str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                "code": 200,
                "message": "获取服务详情成功",
                "data": serializer.data
            })
        except Service.DoesNotExist:
            return Response({
                "code": 404,
                "message": "未找到该服务",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"获取服务详情失败：{str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

