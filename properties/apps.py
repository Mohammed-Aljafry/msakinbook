# استيراد المكتبات اللازمة
from django.apps import AppConfig


# تكوين تطبيق العقارات
class PropertiesConfig(AppConfig):
    # تعريف نوع الحقل التلقائي الافتراضي
    default_auto_field = "django.db.models.BigAutoField"
    
    # اسم التطبيق
    name = "properties"
