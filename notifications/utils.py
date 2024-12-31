# استيراد المكتبات اللازمة
from django.contrib.contenttypes.models import ContentType  # نموذج نوع المحتوى
from .models import Notification  # نموذج الإشعارات

def create_notification(sender, recipient, notification_type, content_object, text):
    """
    إنشاء إشعار جديد مع تجنب التكرار
    
    المعاملات:
        sender: المستخدم الذي قام بالإجراء (مثل: من قام بالإعجاب أو التعليق)
        recipient: المستخدم الذي سيتلقى الإشعار (مثل: صاحب المنشور)
        notification_type: نوع الإشعار (message, property, follow, like, comment)
        content_object: الكائن المرتبط بالإشعار (مثل العقار أو التعليق)
        text: نص الإشعار الذي سيظهر للمستخدم
        
    ملاحظات:
        - لا يتم إنشاء إشعار إذا كان المرسل والمستلم نفس المستخدم
        - يتم التحقق من عدم وجود إشعار مماثل غير مقروء قبل الإنشاء
    """
    # تجنب إنشاء إشعارات للمستخدم نفسه
    if sender != recipient:
        # الحصول على نوع المحتوى للكائن المرتبط
        content_type = ContentType.objects.get_for_model(content_object)
        
        # البحث عن إشعار مماثل غير مقروء
        existing_notification = Notification.objects.filter(
            recipient=recipient,    # نفس المستلم
            sender=sender,          # نفس المرسل
            notification_type=notification_type,  # نفس النوع
            content_type=content_type,           # نفس نوع المحتوى
            object_id=content_object.id,         # نفس الكائن
            is_read=False                        # غير مقروء
        ).first()
        
        # إنشاء إشعار جديد فقط إذا لم يكن هناك إشعار مماثل
        if not existing_notification:
            Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                content_type=content_type,
                object_id=content_object.id,
                text=text
            )
