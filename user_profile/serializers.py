from rest_framework import serializers
from .models import Guardianship, Profile, UserProfile, CardPackage, Card, HealthSchedule
from django.contrib.auth.models import User

"""
序列化器模块用于处理用户、用户资料、监护关系和卡片包的序列化与反序列化。

UserSerializer: 处理用户的序列化，包括创建用户时的密码处理。
CardSerializer: 处理卡片的序列化，支持与卡片包的关联。
CardPackageSerializer: 处理卡片包的序列化，包含与用户资料的关联信息。
GuardianshipSerializer: 处理监护关系的序列化，验证监护人和被监护人的手机号及关系称呼。
UserProfileSerializer: 处理用户资料的序列化，包含用户和卡片包的信息。
HealthScheduleSerializer: 处理健康日程的序列化，包含日程标题、内容和提醒时间。
"""

class HealthScheduleSerializer(serializers.ModelSerializer):
    """
    健康日程序列化器
    处理健康日程的创建、更新和查询
    """
    class Meta:
        model = HealthSchedule
        fields = ['id', 'title', 'reminder_time', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_reminder_time(self, value):
        """
        验证提醒时间是否在未来
        """
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("提醒时间必须是将来的时间")
        return value

    def create(self, validated_data):
        """
        创建健康日程
        """
        user_profile = self.context['request'].user.profile
        validated_data['user_profile'] = user_profile
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        更新健康日程
        """
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.reminder_time = validated_data.get('reminder_time', instance.reminder_time)
        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "phone"]
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {"required": True},
        }

    def validate_phone(self, value):
        """
        验证手机号是否已存在
        """
        if UserProfile.objects.filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已被注册")
        return value

    def validate_email(self, value):
        """
        验证邮箱是否已存在
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value

    def create(self, validated_data):
        """
        创建用户和用户资料
        """
        phone = validated_data.pop('phone')
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        # 更新用户资料
        profile = user.profile
        profile.phone = phone
        profile.nickname = validated_data["username"]
        profile.save()
        return user


class CardSerializer(serializers.ModelSerializer):
    """卡片序列化器"""
    class Meta:
        model = Card
        fields = ['id', 'name', 'card_type', 'number', 'remark', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CardPackageSerializer(serializers.ModelSerializer):
    """卡包序列化器"""
    cards = CardSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user_profile.user.username', read_only=True)
    nickname = serializers.CharField(source='user_profile.nickname', read_only=True)

    class Meta:
        model = CardPackage
        fields = ['id', 'username', 'nickname', 'cards', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class GuardianshipSerializer(serializers.ModelSerializer):
    guardian = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())
    ward = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())
    guardian_name = serializers.CharField(
        source="guardian.user.username", read_only=True
    )
    ward_name = serializers.CharField(source="ward.user.username", read_only=True)

    class Meta:
        model = Guardianship
        fields = [
            "id",
            "guardian",
            "ward",
            "relationship",
            "guardian_name",
            "ward_name",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        # 验证关系称呼是否为空
        if not data.get("relationship"):
            raise serializers.ValidationError({"relationship": "关系称呼不能为空"})

        return data


class SimpleUserProfileSerializer(serializers.ModelSerializer):
    """简化的用户资料序列化器"""
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'nickname', 'avatar', 'phone']


class GuardianshipListSerializer(serializers.ModelSerializer):
    """用于显示监护人列表的序列化器"""
    guardian = SimpleUserProfileSerializer(read_only=True)

    class Meta:
        model = Guardianship
        fields = ['id', 'guardian', 'relationship']


class WardListSerializer(serializers.ModelSerializer):
    """用于显示被监护人列表的序列化器"""
    ward_id = serializers.IntegerField(source='ward.id')
    ward_name = serializers.CharField(source='ward.user.username')
    ward_nickname = serializers.CharField(source='ward.nickname')
    ward_phone = serializers.CharField(source='ward.phone')

    class Meta:
        model = Guardianship
        fields = ['id', 'ward_id', 'ward_name', 'ward_nickname', 'ward_phone', 'relationship']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    card_package = CardPackageSerializer(read_only=True)
    avatar = serializers.SerializerMethodField()
    guardians = GuardianshipListSerializer(source='guardianships_as_ward', many=True, read_only=True)
    wards = WardListSerializer(source='guardianships_as_guardian', many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'nickname', 'avatar', 'health_id', 'phone', 
                 'blood_pressure', 'blood_sugar', 'blood_oxygen', 
                 'temperature', 'weight', 'card_package', 'guardians', 'wards']
        read_only_fields = ['id', 'user', 'card_package', 'guardians', 'wards']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar_file:
            # 统一使用 /upload/avatar/ 作为头像路径前缀
            avatar_url = obj.avatar_file.url
            if avatar_url.startswith('/upload/avatars/'):
                avatar_url = avatar_url.replace('/upload/avatars/', '/upload/avatar/')
            return request.build_absolute_uri(avatar_url) if request else avatar_url
        return obj.avatar


class ProfileSerializer(serializers.ModelSerializer):
    """
    个人档案序列化器
    处理个人档案的创建、更新和查询
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        创建个人档案
        """
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        更新个人档案
        """
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
