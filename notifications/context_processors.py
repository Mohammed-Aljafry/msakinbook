# استيراد نموذج الإشعارات
from .models import Notification

def notifications_processor(request):
    """
    معالج سياق لإضافة معلومات الإشعارات إلى جميع قوالب Django
    
    المعاملات:
        request: كائن الطلب الحالي
        
    يرجع:
        قاموس يحتوي على:
        - unread_notifications_count: عدد الإشعارات غير المقروءة
        - recent_notifications: قائمة بأحدث 5 إشعارات
        
    ملاحظات:
        - يتم استدعاء هذا المعالج تلقائياً مع كل طلب
        - متوفر في جميع القوالب عبر المتغيرات:
          {{ unread_notifications_count }} و {{ recent_notifications }}
    """
    # التحقق من تسجيل دخول المستخدم
    if request.user.is_authenticated:
        # حساب عدد الإشعارات غير المقروءة
        unread_notifications_count = Notification.objects.filter(
            recipient=request.user,  # الإشعارات الموجهة للمستخدم الحالي
            is_read=False           # غير المقروءة فقط
        ).count()
        
        # جلب أحدث 5 إشعارات
        recent_notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5]  # ترتيب تنازلي حسب تاريخ الإنشاء
        
        # إرجاع المتغيرات للقوالب
        return {
            'unread_notifications_count': unread_notifications_count,
            'recent_notifications': recent_notifications
        }
        
    # إرجاع قيم افتراضية للمستخدمين غير المسجلين
    return {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }
