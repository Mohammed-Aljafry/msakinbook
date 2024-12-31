# استيراد المكتبات اللازمة
from django.urls import re_path
from . import consumers

# تعريف مسارات WebSocket للعقارات
websocket_urlpatterns = [
    # مسار WebSocket للعقارات - يستخدم للتحديثات المباشرة
    re_path(r'ws/properties/', consumers.PropertyConsumer.as_asgi()),
]
