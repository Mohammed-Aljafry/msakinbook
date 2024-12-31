# استيراد المكتبات اللازمة
from django.urls import path  # دالة المسار
from . import views  # مشاهدات التطبيق

# تعريف اسم التطبيق للمساعدة في تحديد المسارات
app_name = 'chat'

# قائمة مسارات URL للتطبيق
urlpatterns = [
    # الصفحة الرئيسية - قائمة المحادثات
    path('', 
         views.conversations_list, 
         name='conversation_list'),
    
    # غرفة المحادثة مع مستخدم معين
    path('<int:user_id>/', 
         views.chat_room, 
         name='chat_room'),
    
    # واجهة برمجة التطبيقات API
    
    # جلب قائمة المحادثات
    path('api/conversations/', 
         views.get_conversations, 
         name='get_conversations'),
    
    # تحديث حالة الرسائل إلى مقروءة
    path('api/messages/mark-read/<int:conversation_id>/', 
         views.mark_messages_as_read, 
         name='mark_messages_as_read'),
]
