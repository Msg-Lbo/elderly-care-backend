from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage
from django.db import models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Guardianship, UserProfile, CardPackage, Card, Profile, HealthSchedule
from .serializers import GuardianshipSerializer, UserProfileSerializer, UserSerializer, CardPackageSerializer, CardSerializer, ProfileSerializer, HealthScheduleSerializer
from .permissions import IsSuperAdmin, HasGroupPermission
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView, TokenObtainPairView as BaseTokenObtainPairView
from django.http import HttpResponse
from django.conf import settings

class ProfileView(APIView):
    """
    个人档案视图
    处理个人档案的创建、查询、更新和删除
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        获取当前用户的个人档案列表
        """
        print(request)
        
        try:
            profiles = Profile.objects.filter(user_id=request.user.id)
            serializer = ProfileSerializer(profiles, many=True)
            return Response({
                'code': 200,
                'message': '获取个人档案列表成功',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取个人档案列表失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        创建个人档案
        """
        try:
            serializer = ProfileSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'code': 201,
                    'message': '创建个人档案成功',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'code': 400,
                'message': '创建个人档案失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'创建个人档案失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileDetailView(APIView):
    """
    个人档案详情视图
    处理个人档案的更新和删除
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        """获取并验证个人档案对象"""
        try:
            profile = Profile.objects.get(pk=pk)
            # 验证当前用户是否有权限访问
            if profile.user_id != self.request.user.id:
                raise PermissionDenied('无权访问此个人档案')
            return profile
        except Profile.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        获取个人档案详情
        """
        try:
            profile = self.get_object(pk)
            serializer = ProfileSerializer(profile)
            return Response({
                'code': 200,
                'message': '获取个人档案详情成功',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取个人档案详情失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """
        更新个人档案
        """
        try:
            profile = self.get_object(pk)
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'code': 200,
                    'message': '更新个人档案成功',
                    'data': serializer.data
                })
            return Response({
                'code': 400,
                'message': '更新个人档案失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'更新个人档案失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """
        删除个人档案
        """
        try:
            profile = self.get_object(pk)
            profile.delete()
            return Response({
                'code': 204,
                'message': '删除个人档案成功'
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'删除个人档案失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserCardPackageView(APIView):
    """
    获取指定用户的卡包信息
    管理员可以查看所有用户，普通用户只能查看自己
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        获取指定用户的卡包信息
        """
        try:
            # 管理员可以查看所有用户
            if request.user.is_superuser:
                profile = UserProfile.objects.get(user__id=user_id)
            # 普通用户只能查看自己
            else:
                if request.user.id != user_id:
                    return Response({
                        'code': 403,
                        'message': '无权查看其他用户的卡包信息'
                    }, status=status.HTTP_403_FORBIDDEN)
                profile = UserProfile.objects.get(user=request.user)
                
            card_package = profile.card_package
            serializer = CardPackageSerializer(card_package)
            return Response({
                'code': 200,
                'message': '获取卡包信息成功',
                'data': serializer.data
            })
        except UserProfile.DoesNotExist:
            return Response({
                'code': 404,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
    """
    用户个人信息视图
    获取当前登录用户的个人信息
    """
    permission_classes = [IsAuthenticated]
    required_groups = ['admin']

    def get(self, request):
        """
        获取用户个人信息
        """
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response({
                'code': 200,
                'message': '获取用户信息成功',
                'data': serializer.data
            })
        except UserProfile.DoesNotExist:
            return Response({
                'code': 404,
                'message': '用户信息不存在'
            }, status=status.HTTP_404_NOT_FOUND)

class RegisterView(APIView):
    """
    用户注册视图
    处理新用户注册请求
    """
    authentication_classes = []  # 移除认证要求
    permission_classes = []     # 移除权限要求

    def post(self, request):
        """
        用户注册接口
        参数：
            - username: 用户名
            - password: 密码
            - email: 邮箱
            - phone: 手机号
        """
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    'code': 200,
                    'message': '注册成功',
                    'data': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                })
            
            # 整合错误信息
            error_messages = []
            for field, errors in serializer.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            
            return Response({
                'code': 400,
                'message': '; '.join(error_messages)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'注册失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    """
    用户登录视图
    处理用户登录请求并返回JWT token
    """
    authentication_classes = []  # 移除认证要求
    permission_classes = []     # 移除权限要求

    def post(self, request):
        """
        用户登录接口
        参数：
            - username: 用户名
            - password: 密码
        """
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'code': 200,
                    'message': '登录成功',
                    'data': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email
                        }
                    }
                })
            return Response({
                'code': 400,
                'message': '用户名或密码错误'
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'登录失败: {str(e)}'
            })

class CardPackageView(APIView):
    """
    用户卡包视图
    获取当前登录用户的卡包信息
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        """
        获取用户卡包信息
        """
        try:
            profile = UserProfile.objects.get(user=request.user)
            card_package = profile.card_package
            serializer = CardPackageSerializer(card_package)
            return Response({
                'code': 200,
                'message': '获取卡包信息成功',
                'data': serializer.data
            })
        except UserProfile.DoesNotExist:
            return Response({
                'code': 404,
                'message': '用户信息不存在'
            }, status=status.HTTP_404_NOT_FOUND)

class CardListView(APIView):
    """
    用户卡片列表视图
    获取当前登录用户的所有卡片信息
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        获取用户卡片列表
        """
        try:
            profile = UserProfile.objects.get(user=request.user)
            cards = profile.card_package.cards.all()
            serializer = CardSerializer(cards, many=True)
            return Response({
                'code': 200,
                'message': '获取卡片列表成功',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取卡片列表失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        创建新卡片
        """
        try:
            profile = UserProfile.objects.get(user=request.user)
            request.data['card_package'] = profile.card_package.id
            serializer = CardSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'code': 201,
                    'message': '创建卡片成功',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'code': 400,
                'message': '创建卡片失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'创建卡片失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GuardianshipView(APIView):
    """监护关系视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, user_id=None, ward_id=None):
        """
        获取监护关系列表或详情
        支持通过手机号搜索用户
        """
        try:
            # 获取查询参数
            phone = request.query_params.get('phone', None)
            
            if phone:
                # 通过手机号搜索用户
                profiles = UserProfile.objects.filter(phone__icontains=phone)
                serializer = UserProfileSerializer(profiles, many=True)
                return Response({
                    'code': 200,
                    'message': '搜索用户成功',
                    'data': serializer.data
                })
            
            if pk:
                # 获取指定监护关系详情
                guardianship = Guardianship.objects.get(id=pk)
                serializer = GuardianshipSerializer(guardianship)
                return Response({
                    'code': 200,
                    'message': '获取监护关系详情成功',
                    'data': serializer.data
                })
            
            if user_id:
                # 获取指定用户的监护关系
                guardianships = Guardianship.objects.filter(guardian__user__id=user_id)
                serializer = GuardianshipSerializer(guardianships, many=True)
                return Response({
                    'code': 200,
                    'message': '获取用户监护关系成功',
                    'data': serializer.data
                })
            
            if ward_id:
                # 获取指定被监护人的监护关系
                guardianships = Guardianship.objects.filter(ward__user__id=ward_id)
                serializer = GuardianshipSerializer(guardianships, many=True)
                return Response({
                    'code': 200,
                    'message': '获取被监护人关系成功',
                    'data': serializer.data
                })
            
            # 获取所有监护关系
            guardianships = Guardianship.objects.all()
            serializer = GuardianshipSerializer(guardianships, many=True)
            return Response({
                'code': 200,
                'message': '获取监护关系列表成功',
                'data': serializer.data
            })
            
        except Guardianship.DoesNotExist:
            return Response({
                'code': 404,
                'message': '监护关系不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取监护关系失败：{str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """创建监护关系"""
        try:
            serializer = GuardianshipSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'code': 201,
                    'message': '创建监护关系成功',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'code': 400,
                'message': '创建监护关系失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'创建监护关系失败：{str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk=None):
        """删除监护关系"""
        try:
            if not pk:
                return Response({
                    'code': 400,
                    'message': '请提供监护关系ID',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            guardianship = Guardianship.objects.get(id=pk)
            guardianship.delete()
            return Response({
                'code': 200,
                'message': '删除监护关系成功',
                'data': None
            })
        except Guardianship.DoesNotExist:
            return Response({
                'code': 404,
                'message': '监护关系不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'删除监护关系失败：{str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CardDetailView(APIView):
    """
    卡片详情视图
    处理卡片的修改和删除
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, card_id):
        """
        修改卡片信息
        """
        try:
            card = Card.objects.get(id=card_id)
            # 检查卡片是否属于当前用户
            if card.card_package.user_profile.user != request.user:
                return Response({
                    'code': 403,
                    'message': '无权修改此卡片'
                }, status=status.HTTP_403_FORBIDDEN)
            serializer = CardSerializer(card, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'code': 200,
                    'message': '修改卡片成功',
                    'data': serializer.data
                })
            return Response({
                'code': 400,
                'message': '修改卡片失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'修改卡片失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, card_id):
        """
        删除卡片
        """
        try:
            card = Card.objects.get(id=card_id)
            # 检查卡片是否属于当前用户
            if card.card_package.user_profile.user != request.user:
                return Response({
                    'code': 403,
                    'message': '无权删除此卡片'
                }, status=status.HTTP_403_FORBIDDEN)
            card.delete()
            return Response({
                'code': 204,
                'message': '删除卡片成功'
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'删除卡片失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser,)

    def post(self, request):
        try:
            user_profile = request.user.profile
            print("前端来的", request.data['avatar'])
            # 更新昵称
            if 'nickname' in request.data:
                user_profile.nickname = request.data['nickname']
            # 更新头像
            if 'avatar' in request.data:
                # 删除旧头像
                if user_profile.avatar:
                    try:
                        default_storage.delete(user_profile.avatar.path)
                    except:
                        pass
                # 直接设置新头像路径，不进行文件保存
                user_profile.avatar = request.data['avatar']
            user_profile.save()
            serializer = UserProfileSerializer(user_profile)
            print("后端返回的", serializer.data['avatar'])
            return Response({
                "code": 200,
                "message": "用户资料更新成功",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"更新用户资料失败：{str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            if 'file' not in request.FILES:
                return Response({
                    "code": 400,
                    "message": "请提供文件",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.FILES['file']
            file_type = request.data.get('type', 'other')  # 文件类型，默认为other
            
            # 生成唯一的文件名
            file_ext = os.path.splitext(file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            
            # 统一使用 avatar 作为头像目录名
            if file_type == 'avatar':
                file_path = f"upload/avatar/{unique_filename}"
            else:
                file_path = f"upload/{file_type}/{unique_filename}"
            
            # 保存文件
            saved_path = default_storage.save(file_path, ContentFile(file.read()))
            
            # 如果是头像文件，更新用户资料
            if file_type == 'avatar':
                try:
                    profile = request.user.profile
                    profile.avatar_file = saved_path
                    profile.save()
                except Exception as e:
                    return Response({
                        "code": 500,
                        "message": f"更新用户头像失败：{str(e)}",
                        "data": None
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                "code": 200,
                "message": "文件上传成功",
                "data": {
                    "url": f"/{saved_path}",
                    "path": saved_path,
                    "name": file.name,
                    "size": file.size,
                    "type": file_type
                }
            })
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"文件上传失败：{str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CardPackageViewSet(viewsets.ModelViewSet):
    """卡包视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = CardPackageSerializer

    def get_queryset(self):
        """获取当前用户的卡包"""
        return CardPackage.objects.filter(user_profile=self.request.user.profile)

    def get_object(self):
        """获取当前用户的卡包"""
        return self.request.user.profile.card_package

    # 获取用户卡包
    @action(detail=False, methods=['get'])
    def get_card_list(self, request):
        """获取用户卡包列表"""
        card_package = self.get_object()
        serializer = self.get_serializer(card_package)
        return Response({
            'code': 200,
            'message': '获取卡包列表成功',
            'data': serializer.data
        })
        
    
    @action(detail=False, methods=['get'], url_path='get_card/(?P<card_id>[^/.]+)')
    def get_card(self, request, card_id):
        """获取指定卡片信息"""
        try:
            card_package = request.user.profile.card_package
            card = Card.objects.get(id=card_id, card_package=card_package)
            serializer = CardSerializer(card)
            return Response({
                'code': 200,
                'message': '获取卡片信息成功',
                'data': serializer.data
            })
        except Card.DoesNotExist:
            return Response({
                'code': 404,
                'message': '卡片不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取卡片信息失败：{str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def add_card(self, request):
        """添加卡片到卡包"""
        try:
            card_package = request.user.profile.card_package
            serializer = CardSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(card_package=card_package)
                return Response({
                    "code": 200,
                    "message": "卡片添加成功",
                    "data": serializer.data
                })
            return Response({
                "code": 400,
                "message": "卡片添加失败",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"卡片添加失败：{str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def update_card(self, request, card_id):
        """修改卡片信息"""
        try:
            card_package = request.user.profile.card_package
            card = Card.objects.get(id=card_id, card_package=card_package)
            serializer = CardSerializer(card, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "code": 200,
                    "message": "卡片修改成功",
                    "data": serializer.data
                })
            return Response({
                "code": 400,
                "message": "卡片修改失败",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Card.DoesNotExist:
            return Response({
                "code": 404,
                "message": "卡片不存在",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"卡片修改失败：{str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def remove_card(self, request, card_id):
        """从卡包中移除卡片"""
        try:
            card_package = request.user.profile.card_package
            card = Card.objects.get(id=card_id, card_package=card_package)
            card.delete()
            return Response({
                "code": 200,
                "message": "卡片移除成功",
                "data": None
            })
        except Card.DoesNotExist:
            return Response({
                "code": 404,
                "message": "卡片不存在",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"卡片移除失败：{str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthScheduleViewSet(viewsets.ModelViewSet):
    """健康日程视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = HealthScheduleSerializer

    def get_queryset(self):
        """获取当前用户的健康日程"""
        return HealthSchedule.objects.filter(user_profile=self.request.user.profile)

    def list(self, request, *args, **kwargs):
        """获取当前用户的日程列表"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取日程列表成功',
            'data': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        """获取指定日程详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取日程详情成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """添加日程"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_profile=request.user.profile)
            return Response({
                'code': 201,
                'message': '日程添加成功',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '日程添加失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """修改日程"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'message': '日程修改成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '日程修改失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class TokenRefreshView(BaseTokenRefreshView):
    """
    刷新Token视图
    处理刷新Token请求
    """
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                return Response({
                    'code': 200,
                    'message': '刷新Token成功',
                    'data': {
                        'access': response.data['access']
                    }
                })
            return Response({
                'code': 400,
                'message': '刷新Token失败'
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'刷新Token失败: {str(e)}'
            })

class TokenObtainPairView(BaseTokenObtainPairView):
    """
    获取Token视图
    处理用户登录并返回JWT token
    """
    authentication_classes = []  # 移除认证要求
    permission_classes = []     # 移除权限要求

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                return Response({
                    'code': 200,
                    'message': '登录成功',
                    'data': {
                        'access': response.data['access'],
                        'refresh': response.data['refresh']
                    }
                })
            return Response({
                'code': 400,
                'message': '用户名或密码错误'
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'登录失败: {str(e)}'
            })
