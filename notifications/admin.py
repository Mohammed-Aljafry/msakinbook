# استيراد المكتبات اللازمة
from django.contrib import admin  # وحدة الإدارة في Django
from .models import Notification  # نموذج الإشعارات

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    تكوين عرض نموذج الإشعارات في لوحة الإدارة
    """
    # الحقول التي تظهر في قائمة الإشعارات
    list_display = ['recipient', 'sender', 'notification_type', 'is_read', 'created_at']
    
    # الحقول التي يمكن البحث من خلالها
    search_fields = ['recipient__username', 'sender__username', 'text']
    
    # الحقول التي يمكن التصفية من خلالها
    list_filter = ['notification_type', 'is_read', 'created_at']
    
    # ترتيب الإشعارات من الأحدث إلى الأقدم
    ordering = ['-created_at']
    
    # عدد الإشعارات في كل صفحة
    list_per_page = 20
    
    # الحقول التي يمكن تعديلها مباشرة من قائمة الإشعارات
    list_editable = ['is_read']
