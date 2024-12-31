# استيراد المكتبات اللازمة
from django.conf import settings
from django.db.models.signals import post_save  # إشارة ما بعد الحفظ
from django.dispatch import receiver  # مستقبل الإشارات
from rest_framework.authtoken.models import Token  # نموذج رمز المصادقة

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    دالة لإنشاء رمز مصادقة للمستخدم الجديد
    
    المعاملات:
        sender: نموذج المستخدم المرسل للإشارة
        instance: كائن المستخدم الذي تم حفظه
        created: مؤشر يدل على ما إذا كان هذا إنشاء جديد
        kwargs: معاملات إضافية
    """
    # إنشاء رمز مصادقة فقط للمستخدمين الجدد
    if created:
        Token.objects.create(user=instance)