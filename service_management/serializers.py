from rest_framework import serializers
from .models import Service
from user_profile.models import UserProfile
from user_profile.serializers import UserProfileSerializer
from django.utils import timezone

class ServiceSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        required=True
    )
    caregiver = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Service
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['client'] = UserProfileSerializer(instance.client).data
        if instance.caregiver:
            representation['caregiver'] = UserProfileSerializer(instance.caregiver).data
        return representation

    def validate(self, data):
        # 验证服务时间不能早于当前时间
        if data.get('service_time') and data['service_time'] < timezone.now():
            raise serializers.ValidationError("服务时间不能早于当前时间")
        
        # 验证护工角色
        caregiver = data.get('caregiver')
        if caregiver and not caregiver.user.groups.filter(name='护工').exists():
            raise serializers.ValidationError("护工必须是护工用户组")
            
        return data
