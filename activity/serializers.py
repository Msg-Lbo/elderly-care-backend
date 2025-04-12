from rest_framework import serializers
from .models import Activity, ActivityRegistration

class ActivityListSerializer(serializers.ModelSerializer):
    registration_count = serializers.SerializerMethodField()
    cover = serializers.CharField(source='cover.url')
    
    class Meta:
        model = Activity
        fields = ['id', 'title', 'cover', 'start_time', 'end_time', 'registration_count']
    
    def get_registration_count(self, obj):
        return obj.registrations.count()

class ActivityDetailSerializer(serializers.ModelSerializer):
    registration_count = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    cover = serializers.CharField(source='cover.url')
    
    class Meta:
        model = Activity
        fields = ['id', 'title', 'cover', 'start_time', 'end_time', 'content', 
                 'registration_count', 'is_registered', 'created_at', 'updated_at']
    
    def get_registration_count(self, obj):
        return obj.registrations.count()
    
    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ActivityRegistration.objects.filter(
                activity=obj, 
                user=request.user
            ).exists()
        return False

class ActivityRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityRegistration
        fields = ['id', 'activity', 'user', 'registered_at']
        read_only_fields = ['user', 'registered_at'] 