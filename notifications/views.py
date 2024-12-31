# استيراد المكتبات اللازمة
from django.shortcuts import render, redirect, get_object_or_404  # دوال مساعدة للعرض والتوجيه
from django.contrib.auth.decorators import login_required  # مزخرف للتحقق من تسجيل الدخول
from django.http import JsonResponse  # استجابة JSON
from django.views.decorators.http import require_GET  # مزخرف لتقييد الطلبات إلى GET
from .models import Notification  # نموذج الإشعارات

# Create your views here.

@login_required
def notifications_list(request):
    """
    عرض قائمة الإشعارات للمستخدم الحالي
    - ترتيب الإشعارات من الأحدث إلى الأقدم
    """
    notifications = request.user.notifications.all().order_by('-created_at')
    # for i in notifications:
        # print(i.sender.user_name)
    # print('imgaes')
    # print(notifications[5].sender.profile.profile_picture)
    return render(request, 'notifications/notifications_list.html', {'notifications': notifications})

@login_required
def mark_as_read(request, notification_id):
    """
    تحديث حالة إشعار معين إلى مقروء
    
    المعاملات:
        notification_id: معرف الإشعار المراد تحديثه
        
    يدعم الطلبات العادية وطلبات AJAX
    """
    # التحقق من وجود الإشعار وملكية المستخدم له
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # التعامل مع طلبات AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications')

@login_required
def mark_all_as_read(request):
    """
    تحديث حالة جميع الإشعارات غير المقروءة للمستخدم إلى مقروءة
    
    يدعم الطلبات العادية وطلبات AJAX
    """
    # تحديث جميع الإشعارات غير المقروءة
    request.user.notifications.filter(is_read=False).update(is_read=True)
    
    # التعامل مع طلبات AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications')

@require_GET
def get_notification_count(request):
    """
    جلب عدد الإشعارات غير المقروءة للمستخدم الحالي
    
    - إذا كان المستخدم غير مسجل الدخول، يتم إرجاع 0
    - يستخدم في تحديث عداد الإشعارات في الواجهة
    """
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0})
    
    # حساب عدد الإشعارات غير المقروءة
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'count': count})
