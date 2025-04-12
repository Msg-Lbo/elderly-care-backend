from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Activity, ActivityRegistration
from .serializers import ActivityListSerializer, ActivityDetailSerializer, ActivityRegistrationSerializer
from .utils import APIResponse, APIError

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ActivityListSerializer
        return ActivityDetailSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return APIResponse(data=serializer.data)
        except Exception as e:
            return APIResponse(code=500, message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return APIResponse(data=serializer.data)
        except Exception as e:
            return APIResponse(code=500, message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return APIResponse(data=serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return APIResponse(code=400, message=str(e), status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return APIResponse(data=serializer.data)
        except Exception as e:
            return APIResponse(code=400, message=str(e), status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return APIResponse(message='删除成功')
        except Exception as e:
            return APIResponse(code=400, message=str(e), status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        try:
            activity = self.get_object()
            
            # 检查是否已经报名
            if ActivityRegistration.objects.filter(activity=activity, user=request.user).exists():
                raise APIError(code=400, message='您已经报名过该活动')
            
            # 创建报名记录
            registration = ActivityRegistration.objects.create(
                activity=activity,
                user=request.user
            )
            
            serializer = ActivityRegistrationSerializer(registration)
            return APIResponse(data=serializer.data, status=status.HTTP_201_CREATED)
        except APIError as e:
            return APIResponse(code=e.code, message=e.message, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return APIResponse(code=500, message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR) 