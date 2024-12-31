# استيراد المكتبات اللازمة
from django.urls import path
from . import api_views

# تعريف مسارات API
urlpatterns = [
    # قائمة العقارات
    path('', api_views.property_list, name='api-property-list'),
    
    # تفاصيل عقار محدد
    path('<int:pk>/', api_views.property_detail, name='api-property-detail'),
    
    # البحث في العقارات
    path('search/', api_views.property_search, name='api-property-search'),
    
    # عقارات المستخدم الحالي
    path('my-properties/', api_views.my_properties, name='api-my-properties'),
]
