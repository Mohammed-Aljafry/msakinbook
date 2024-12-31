# استيراد المكتبات اللازمة
from django.urls import re_path  # دالة لتعريف مسارات URL باستخدام التعبيرات النمطية
from . import consumers  # مستهلكات WebSocket

# تعريف مسارات WebSocket
websocket_urlpatterns = [
    # مسار WebSocket للإشعارات
    # يتم توجيه الاتصالات على المسار 'ws/notifications/' إلى NotificationConsumer
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
