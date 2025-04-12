from django.contrib import admin
from django.db import models
from .models import UserProfile, CardPackage, Card, Guardianship, HealthSchedule, Profile
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.forms import TextInput, Textarea

admin.site.site_header = '智慧养老管理系统'  # 设置header
admin.site.site_title = '智慧养老管理系统'   # 设置title
admin.site.index_title = '智慧养老管理系统'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户资料管理"""
    list_display = ['user', 'nickname', 'phone', 'health_id', 'avatar_preview']
    search_fields = ['user__username', 'nickname', 'phone', 'health_id']
    list_filter = ['user__is_active']
    readonly_fields = ['avatar_preview']
    fields = ['user', 'nickname', 'avatar_file', 'avatar', 'avatar_preview', 'health_id', 'phone',
              'blood_pressure', 'blood_sugar', 'blood_oxygen', 'temperature', 'weight']

    def avatar_preview(self, obj):
        """显示头像预览"""
        if obj.avatar_file:
            return mark_safe(f'<img src="{obj.avatar_file.url}" style="width: 50px; height: 50px; border-radius: 50%;" />')
        return "无头像"
    avatar_preview.short_description = '头像预览'
    avatar_preview.allow_tags = True

    def get_group(self, obj):
        return obj.group

    get_group.short_description = "用户组"
    list_filter = ("user__groups",)
    search_fields = ("nickname", "phone")
    ordering = ("nickname",)

    # 配置图片上传字段
    formfield_overrides = {
        models.ImageField: {'widget': admin.widgets.AdminFileWidget},
    }

@admin.register(CardPackage)
class CardPackageAdmin(admin.ModelAdmin):
    """用户卡包管理"""
    list_display = ('display_name', 'created_at', 'updated_at')
    search_fields = ('user_profile__user__username',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

    def display_name(self, obj):
        return f"{obj.user_profile.user.username}的卡包"
    display_name.short_description = '卡包名称'

@admin.register(Guardianship)
class GuardianshipAdmin(admin.ModelAdmin):
    """监护关系管理"""
    list_display = ('guardian', 'ward', 'relationship')
    list_filter = ('relationship',)
    search_fields = ('guardian__phone', 'ward__phone', 'relationship')
    raw_id_fields = ('guardian', 'ward')
    ordering = ('-id',)
    actions = ['delete_selected']
    RELATIONSHIP_CHOICES = [
        ('子女', '子女'),
        ('配偶', '配偶'),
        ('亲戚', '亲戚'),
        ('朋友', '朋友'),
        ('其他', '其他'),
    ]

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'relationship':
            kwargs['choices'] = self.RELATIONSHIP_CHOICES
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # 验证监护人手机号
        if not obj.guardian.phone:
            raise ValueError('监护人手机号不能为空')
        # 验证被监护人手机号
        if not obj.ward.phone:
            raise ValueError('被监护人手机号不能为空')
        super().save_model(request, obj, form, change)

@admin.register(HealthSchedule)
class HealthScheduleAdmin(admin.ModelAdmin):
    """健康日程管理"""
    list_display = ('user_profile', 'title', 'reminder_time', 'created_at')
    list_filter = ('reminder_time',)
    search_fields = ('title', 'content', 'user_profile__user__username')
    date_hierarchy = 'reminder_time'
    ordering = ('-reminder_time',)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    """卡片信息管理"""
    list_display = ('name', 'card_type', 'number', 'card_package', 'created_at')
    list_filter = ('card_type', 'created_at')
    search_fields = ('name', 'number', 'remark')
    date_hierarchy = 'created_at'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """个人档案管理"""
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'content', 'user__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    filter_horizontal = ()
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    
    # 富文本编辑器配置
    from ckeditor.widgets import CKEditorWidget
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()}
    }
