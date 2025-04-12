from django.db import models
from user_profile.models import UserProfile
from django.core.exceptions import ValidationError
from django.utils import timezone

class Service(models.Model):
    SERVICE_TYPES = (
        ('FOOD', '喂药'),
        ('MEDICINE', '看护'),
        ('DIET', '做饭'),
        ('CLEANING', '打扫'),
        ('TRANSPORT', '代取'),
        ('DELIVERYGET', '代送'),
        ('DELIVERYBUY', '代购'),
        ('OTHERS', '其他'),
    )

    STATUS_CHOICES = (
        ('PENDING', '待处理'),
        ('IN_PROGRESS', '进行中'),
        ('COMPLETED', '已完成'),
        ('CANCELLED', '已取消'),
    )

    client = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='services_received',
        verbose_name='被服务人'
    )
    caregiver = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services_provided',
        verbose_name='护工'
    )
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPES,
        verbose_name='服务类型'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='状态'
    )
    service_time = models.DateTimeField(verbose_name='服务时间')
    address = models.TextField(verbose_name='详细地址')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '服务'
        verbose_name_plural = '服务管理'
        ordering = ['-created_at']

    def clean(self):
        # 验证护工用户组
        if self.caregiver and not self.caregiver.user.groups.filter(name='护工').exists():
            raise ValidationError('护工用户组不正确')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.client}"
