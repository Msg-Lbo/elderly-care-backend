from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField


class UserProfile(models.Model):
    """
    用户资料模型
    存储用户的个人信息和健康数据
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="用户"
    )
    nickname = models.CharField(max_length=50, verbose_name="昵称", default="待填写")
    avatar_file = models.ImageField(
        upload_to="avatars/", verbose_name="头像文件", blank=True, null=True
    )
    avatar = models.CharField(
        max_length=255, verbose_name="头像路径", blank=True, null=True
    )
    health_id = models.CharField(
        max_length=20, verbose_name="健康ID卡号", default="待填写"
    )
    phone = models.CharField(max_length=20, verbose_name="手机号")
    blood_pressure = models.CharField(
        max_length=20, verbose_name="血压", default="待填写"
    )
    blood_sugar = models.CharField(max_length=20, verbose_name="血糖", default="待填写")
    blood_oxygen = models.CharField(
        max_length=20, verbose_name="血氧", default="待填写"
    )
    temperature = models.CharField(max_length=20, verbose_name="体温", default="待填写")
    weight = models.CharField(max_length=20, verbose_name="体重", default="待填写")

    @property
    def group(self):
        """
        获取用户所属的用户组
        返回：
            Group: 用户所属的第一个用户组
        """
        return self.user.groups.first()

    def __str__(self):
        """
        返回用户的字符串表示
        返回：
            str: 用户的昵称
        """
        return self.nickname

    class Meta:
        """
        用户资料的元数据配置
        """

        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class CardPackage(models.Model):
    """
    用户卡包模型
    存储用户的所有卡片信息
    """

    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="card_package",
        verbose_name="用户资料",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        """
        返回卡包的字符串表示
        返回：
            str: 格式为"用户名 + 的卡包"
        """
        return f"{self.user_profile.user.username}的卡包"

    class Meta:
        """
        卡包的元数据配置
        """

        verbose_name = "卡包"
        verbose_name_plural = "卡包"


class Card(models.Model):
    """
    卡片模型
    存储用户的各类卡片信息
    """

    CARD_TYPES = (
        ("ID", "身份证"),
        ("BANK", "银行卡"),
        ("MEMBER", "会员卡"),
        ("OTHER", "其他"),
    )
    """
    卡片类型选项：
    - ID: 身份证
    - BANK: 银行卡
    - MEMBER: 会员卡
    - OTHER: 其他类型卡片
    """

    card_package = models.ForeignKey(
        CardPackage,
        on_delete=models.CASCADE,
        related_name="cards",
        verbose_name="所属卡包",
    )
    name = models.CharField(max_length=50, verbose_name="卡名")
    card_type = models.CharField(
        max_length=20, choices=CARD_TYPES, verbose_name="卡类型"
    )
    number = models.CharField(max_length=50, verbose_name="卡号")
    remark = models.TextField(blank=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        """
        返回卡片的字符串表示
        返回：
            str: 格式为"卡名 (卡片类型)"
        """
        return f"{self.name} ({self.get_card_type_display()})"

    class Meta:
        """
        卡片的元数据配置
        """

        verbose_name = "卡片"
        verbose_name_plural = "卡片"


class Guardianship(models.Model):
    """
    监护关系模型
    存储用户之间的监护关系信息
    """

    guardian = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="guardianships_as_guardian",
        verbose_name="监护人",
    )
    ward = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="guardianships_as_ward",
        verbose_name="被监护人",
    )
    relationship = models.CharField(max_length=20, verbose_name="监护关系称呼")

    def __str__(self):
        """
        返回监护关系的字符串表示
        返回：
            str: 格式为"监护人 是 被监护人 的 关系称呼"
        """
        return f"{self.guardian.user.username} 是 {self.ward.user.username} 的 {self.relationship}"

    class Meta:
        """
        监护关系的元数据配置
        """

        verbose_name = "监护关系"
        verbose_name_plural = "监护关系"
        unique_together = ("guardian", "ward")  # 确保每个监护人-被监护人关系唯一


class HealthSchedule(models.Model):
    """健康日程模型"""
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='health_schedules',
        verbose_name="用户资料"
    )
    title = models.CharField(max_length=100, verbose_name="日程标题")
    reminder_time = models.DateTimeField(verbose_name="提醒时间")
    content = models.TextField(verbose_name="提醒内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.title} - {self.reminder_time}"

    class Meta:
        verbose_name = "健康日程"
        verbose_name_plural = "健康日程"
        ordering = ['-reminder_time']


@receiver(post_save, sender=UserProfile)
def create_card_package(sender, instance, created, **kwargs):
    """
    用户资料创建后自动创建关联的卡包
    参数：
        sender: 发送信号的模型类
        instance: 保存的用户资料实例
        created: 是否是新建实例
        **kwargs: 其他参数
    """
    if created:  # 仅在新建用户资料时创建卡包
        CardPackage.objects.create(user_profile=instance)


class Profile(models.Model):
    """
    个人档案模型
    存储用户的个人档案信息，包含标题、富文本内容和创建时间
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="profiles", verbose_name="用户", null=True, blank=True
    )
    title = models.CharField(max_length=100, verbose_name="标题")
    content = RichTextField("内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        """
        返回个人档案的字符串表示
        返回：
            str: 格式为"标题 (创建时间)"
        """
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"

    class Meta:
        """
        个人档案的元数据配置
        """

        verbose_name = "个人档案"
        verbose_name_plural = "个人档案"
        ordering = ["-created_at"]  # 默认按创建时间降序排列
