# استيراد الوحدة الأساسية لتكوين التطبيقات في Django
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """
    تكوين تطبيق الإشعارات
    
    يحدد:
    - نوع الحقل التلقائي المستخدم في النماذج
    - اسم التطبيق المستخدم في الإعدادات
    """
    # تحديد نوع الحقل التلقائي للمفاتيح الأساسية
    default_auto_field = "django.db.models.BigAutoField"
    
    # اسم التطبيق كما يظهر في INSTALLED_APPS
    name = "notifications"
