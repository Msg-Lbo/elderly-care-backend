from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class IsSuperAdmin(BasePermission):
    """
    超级管理员权限
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        raise PermissionDenied({
            'code': 'permission_denied',
            'message': '您没有权限执行此操作'
        })

class HasGroupPermission(BasePermission):
    """
    用户组权限验证
    根据用户所属的用户组进行权限验证
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # 获取视图所需的权限组
        required_groups = getattr(view, 'required_groups', None)
        if not required_groups:
            return True

        # 获取用户所属的用户组
        user_groups = request.user.groups.values_list('name', flat=True)
        
        # 检查用户是否属于任一所需用户组
        if any(group in user_groups for group in required_groups):
            return True
            
        raise PermissionDenied({
            'code': 'permission_denied',
            'message': '您没有权限执行此操作'
        })
