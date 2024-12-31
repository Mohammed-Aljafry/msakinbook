# استيراد المكتبات اللازمة
from django.db import models  # نماذج قاعدة البيانات
from django.contrib.auth.models import User  # نموذج المستخدم
from django.contrib.contenttypes.fields import GenericForeignKey  # حقل العلاقة العامة
from django.contrib.contenttypes.models import ContentType  # نموذج نوع المحتوى

class Notification(models.Model):
    """
    نموذج الإشعارات
    يستخدم لتخزين وإدارة جميع أنواع الإشعارات في النظام
    يدعم الإشعارات المرتبطة بأي نوع من المحتوى (رسائل، عقارات، متابعة، إعجاب، تعليقات)
    """
    
    # أنواع الإشعارات المدعومة في النظام
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),          # إشعار رسالة جديدة
        ('property', 'Property Update'),     # إشعار تحديث عقار
        ('follow', 'New Follower'),          # إشعار متابع جديد
        ('like', 'New Like'),                # إشعار إعجاب جديد
        ('comment', 'New Comment'),          # إشعار تعليق جديد
        ('comment_like', 'Comment Like'),     # إشعار إعجاب بتعليق
        ('comment_reply', 'Comment Reply'),   # إشعار رد على تعليق
    ]

    # العلاقات والحقول الأساسية
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )  # المستلم
    
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_notifications'
    )  # المرسل
    
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES
    )  # نوع الإشعار
    
    # حقول العلاقة العامة للربط مع أي نوع من المحتوى
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # نوع المحتوى
    object_id = models.PositiveIntegerField()  # معرف المحتوى
    content_object = GenericForeignKey('content_type', 'object_id')  # المحتوى المرتبط
    
    # حقول إضافية
    text = models.CharField(max_length=255)  # نص الإشعار
    is_read = models.BooleanField(default=False)  # حالة القراءة
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ الإنشاء

    class Meta:
        """
        خيارات النموذج:
        - ترتيب الإشعارات من الأحدث إلى الأقدم
        """
        ordering = ['-created_at']

    def __str__(self):
        """تمثيل نصي للإشعار يوضح المستلم والمرسل"""
        return f"Notification to {self.recipient} from {self.sender}"
