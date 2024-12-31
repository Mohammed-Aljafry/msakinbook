# استيراد المكتبات اللازمة
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from properties.views import PropertyViewSet
from rest_framework.authtoken.views import obtain_auth_token

# إعداد راوتر REST Framework (معطل حالياً)
# router = DefaultRouter()
# router.register(r'api/properties', PropertyViewSet)

# تعريف مسارات URL الرئيسية
urlpatterns = [
    # مسار لوحة التحكم
    path('admin/', admin.site.urls),
    
    # مسار للحصول على توكن المصادقة
    path('api/token/', obtain_auth_token, name='api_token'),

    # مسار الصفحة الرئيسية
    path('', include('home.urls')),

    # مسارات العقارات
    path('properties/', include('properties.urls')),  # واجهة المستخدم
    path('api/properties/', include('properties.api_urls')),  # واجهة API

    # مسارات الحسابات
    path('accounts/', include('accounts.urls')),  # واجهة المستخدم
    path('api/accounts/', include('accounts.api_urls')),  # واجهة API

    # مسارات المحادثات والإشعارات
    path('chat/', include('chat.urls')),  # نظام المحادثات
    path('notifications/', include('notifications.urls')),  # نظام الإشعارات
    
    # مسار راوتر REST Framework (معطل حالياً)
    # path('', include(router.urls)),
    
# إضافة مسارات الوسائط للتطوير
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
