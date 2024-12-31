# استيراد المكتبات اللازمة
from django.urls import path  # دالة المسار
from . import views  # مشاهدات التطبيق

# قائمة المسارات URL
urlpatterns = [
    # الصفحة الرئيسية للإشعارات - عرض قائمة الإشعارات
    path('', views.notifications_list, name='notifications'),
    
    # تحديث حالة إشعار معين إلى مقروء
    path('mark-as-read/<int:notification_id>/', 
         views.mark_as_read, 
         name='mark_notification_as_read'),
    
    # تحديث حالة جميع الإشعارات إلى مقروءة
    path('mark-all-as-read/', 
         views.mark_all_as_read, 
         name='mark_all_notifications_as_read'),
    
    # جلب عدد الإشعارات غير المقروءة (يستخدم في AJAX)
    path('count/', 
         views.get_notification_count, 
         name='notification_count'),
]
