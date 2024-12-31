# استيراد المكتبات اللازمة
from channels.layers import get_channel_layer  # للتعامل مع طبقات القنوات
from asgiref.sync import async_to_sync  # لتحويل الدوال غير المتزامنة إلى متزامنة

# دالة لإرسال إشعار بتحديث العقار
def notify_udate(post_id):
    """
    إرسال إشعار للمستخدمين عند تحديث عقار معين
    
    المعاملات:
        post_id: معرف العقار المحدث
    """
    print('post :', post_id)  # طباعة معرف العقار للتتبع
    
    # الحصول على طبقة القنوات
    channel_layer = get_channel_layer()
    
    # إرسال الحدث إلى مجموعة العقارات
    async_to_sync(channel_layer.group_send)(
        # f"post_{post_id}",  # يمكن استخدام مجموعة خاصة لكل عقار
        "properties",  # مجموعة العقارات العامة
        {
            "type": "update_event",  # نوع الحدث
            "data": "faiz"  # البيانات المرسلة (يمكن تعديلها حسب الحاجة)
        }
    )