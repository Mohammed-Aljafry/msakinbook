# استيراد المكتبات اللازمة
from django.contrib import admin
from .models import (
    Property, PropertyImage, PropertyRequest, PropertyLike,
    PropertyComment, CommentLike, UserFollow, Chat, Message,
    Governorate, District
)

# تسجيل نموذج المحافظات في لوحة التحكم
@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    list_display = ('name',)  # عرض اسم المحافظة في القائمة
    search_fields = ('name',)  # إمكانية البحث باسم المحافظة

# تسجيل نموذج المديريات في لوحة التحكم
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'governorate')  # عرض اسم المديرية والمحافظة التابعة لها
    list_filter = ('governorate',)  # تصفية حسب المحافظة
    search_fields = ('name', 'governorate__name')  # البحث باسم المديرية أو المحافظة

# تسجيل نموذج العقارات في لوحة التحكم
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    # حقول العرض في القائمة الرئيسية
    list_display = (
        'title', 'property_type', 'listing_type',
        'price', 'currency', 'governorate',
        'district', 'is_available'
    )
    
    # خيارات التصفية
    list_filter = (
        'property_type',  # نوع العقار
        'listing_type',   # نوع العرض
        'is_available',   # متاح/غير متاح
        'governorate',    # المحافظة
        'district'        # المديرية
    )
    
    # حقول البحث
    search_fields = (
        'title',         # العنوان
        'description',   # الوصف
        'location'       # الموقع
    )
    
    # حقول الاختيار السريع للمالك
    raw_id_fields = ('owner',)

# تسجيل النماذج الأخرى في لوحة التحكم
admin.site.register(PropertyImage)    # صور العقارات
admin.site.register(PropertyRequest)  # طلبات العقارات
admin.site.register(PropertyLike)     # الإعجاب بالعقارات
admin.site.register(PropertyComment)  # التعليقات على العقارات
admin.site.register(CommentLike)      # الإعجاب بالتعليقات
admin.site.register(UserFollow)       # متابعة المستخدمين
admin.site.register(Chat)            # المحادثات
admin.site.register(Message)         # الرسائل
