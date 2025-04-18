from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Activity, ActivityRegistration
from .serializers import ActivityListSerializer, ActivityDetailSerializer, ActivityRegistrationSerializer
from .utils import APIResponse, APIError

class ActivityViewSet(viewsets.ModelViewSet):
    """活动视图集，处理所有活动相关的API请求"""
    queryset = Activity.objects.all()  # 查询所有活动数据
    
    def get_serializer_class(self):
        """根据不同的操作类型返回不同的序列化器类"""
        if self.action == 'list':
            return ActivityListSerializer  # 列表视图使用列表序列化器
        return ActivityDetailSerializer  # 其他视图使用详情序列化器
    
    def list(self, request, *args, **kwargs):
        """获取活动列表"""
        try:
            queryset = self.filter_queryset(self.get_queryset())  # 获取并过滤查询集
            serializer = self.get_serializer(queryset, many=True, context={'request': request})  # 序列化多个活动对象，并传入请求上下文
            return APIResponse(data=serializer.data)  # 返回活动列表数据
        except Exception as e:
            return APIResponse(code=500, message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # 处理服务器内部错误
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个活动的详细信息"""
        try:
            instance = self.get_object()  # 获取指定的活动对象
            serializer = self.get_serializer(instance, context={'request': request})  # 序列化活动对象，并传入请求上下文
            data = serializer.data
            return APIResponse(data=data)  # 返回活动详情数据
        except Exception as e:
            return APIResponse(code=500, message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # 处理服务器内部错误
    
    def create(self, request, *args, **kwargs):
        """创建新活动"""
        try:
            serializer = self.get_serializer(data=request.data)  # 使用请求数据创建序列化器
            serializer.is_valid(raise_exception=True)  # 验证数据有效性
            self.perform_create(serializer)  # 执行创建操作
            return APIResponse(data=serializer.data, status=status.HTTP_201_CREATED)  # 返回创建成功的数据
        except Exception as e:
            return APIResponse(code=400, message=str(e), status=status.HTTP_400_BAD_REQUEST)  # 处理请求错误
    
    def update(self, request, *args, **kwargs):
        """更新活动信息"""
        try:
            partial = kwargs.pop('partial', False)  # 确定是全部更新还是部分更新
            instance = self.get_object()  # 获取要更新的活动对象
            serializer = self.get_serializer(instance, data=request.data, partial=partial)  # 使用请求数据创建序列化器
            serializer.is_valid(raise_exception=True)  # 验证数据有效性
            self.perform_update(serializer)  # 执行更新操作
            return APIResponse(data=serializer.data)  # 返回更新后的数据
        except Exception as e:
            return APIResponse(code=400, message=str(e), status=status.HTTP_400_BAD_REQUEST)  # 处理请求错误
    
    def destroy(self, request, *args, **kwargs):
        """删除活动"""
        try:
            instance = self.get_object()  # 获取要删除的活动对象
            self.perform_destroy(instance)  # 执行删除操作
            return APIResponse(message='删除成功')  # 返回删除成功的消息
        except Exception as e:
            return APIResponse(code=400, message=str(e), status=status.HTTP_400_BAD_REQUEST)  # 处理请求错误
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        """用户报名参加活动"""
        try:
            activity = self.get_object()  # 获取要报名的活动对象
            
            # 检查用户是否已经报名该活动
            if ActivityRegistration.objects.filter(activity=activity, user=request.user).exists():
                raise APIError(code=400, message='您已经报名过该活动')
            
            # 创建新的报名记录
            registration = ActivityRegistration.objects.create(
                activity=activity,
                user=request.user
            )
            
            serializer = ActivityRegistrationSerializer(registration)  # 序列化报名记录
            return APIResponse(data=serializer.data, status=status.HTTP_201_CREATED)  # 返回报名成功的数据
        except APIError as e:
            return APIResponse(code=e.code, message=e.message, status=status.HTTP_400_BAD_REQUEST)  # 处理业务逻辑错误
        except Exception as e:
            return APIResponse(code=500, message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # 处理服务器内部错误
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel_registration(self, request, pk=None):
        """用户取消活动报名"""
        try:
            activity = self.get_object()  # 获取要取消报名的活动对象
            
            # 检查用户是否已经报名该活动
            registration = ActivityRegistration.objects.filter(activity=activity, user=request.user).first()
            if not registration:
                raise APIError(code=400, message='您尚未报名该活动，无法取消')
            
            # 删除报名记录
            registration.delete()
            
            return APIResponse(message='取消报名成功', status=status.HTTP_200_OK)  # 返回取消成功的消息
        except APIError as e:
            return APIResponse(code=e.code, message=e.message, status=status.HTTP_400_BAD_REQUEST)  # 处理业务逻辑错误
        except Exception as e:
            return APIResponse(code=500, message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # 处理服务器内部错误 