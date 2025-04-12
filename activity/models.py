from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Activity(models.Model):
    title = models.CharField(max_length=200, verbose_name='活动标题')
    cover = models.ImageField(upload_to='activity_covers/', verbose_name='活动封面')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    content = models.TextField(verbose_name='活动详情')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '活动'
        verbose_name_plural = '活动'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class ActivityRegistration(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='registrations', verbose_name='活动')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_registrations', verbose_name='用户')
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='报名时间')
    
    class Meta:
        verbose_name = '活动报名'
        verbose_name_plural = '活动报名'
        unique_together = ('activity', 'user')  # 确保用户不能重复报名同一活动
    
    def __str__(self):
        return f"{self.user.username} - {self.activity.title}" 