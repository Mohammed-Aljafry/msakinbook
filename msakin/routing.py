# استيراد المكتبات اللازمة للتعامل مع WebSocket
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator

# استيراد مسارات WebSocket من التطبيقات المختلفة
from chat.routing import websocket_urlpatterns as chat_ws_urls  # مسارات المحادثات
from notifications.routing import websocket_urlpatterns as notifiations_ws_urls  # مسارات الإشعارات
from properties.routing import websocket_urlpatterns as properties_ws_urls  # مسارات العقارات

# إعداد تطبيق ASGI
django_asgi_app = get_asgi_application()

# تكوين مسارات البروتوكولات
application = ProtocolTypeRouter({
    # مسارات HTTP العادية
    "http": get_asgi_application(),
    
    # مسارات WebSocket
    "websocket": AllowedHostsOriginValidator(  # التحقق من صحة المضيف
        AuthMiddlewareStack(  # التحقق من المصادقة
            URLRouter(  # توجيه المسارات
                chat_ws_urls+  # مسارات المحادثات المباشرة
                notifiations_ws_urls+  # مسارات الإشعارات الفورية
                properties_ws_urls  # مسارات تحديثات العقارات
            )
        )
    ),
})