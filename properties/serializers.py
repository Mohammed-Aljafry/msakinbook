# -*- coding: utf-8 -*-
# استيراد المكتبات اللازمة
from rest_framework import serializers
from .models import Property, PropertyImage

# مسلسل صور العقار
class PropertyImageSerializer(serializers.ModelSerializer):
    # تعريف حقل الصورة كدالة محسوبة
    image = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = ['id', 'image']

    def get_image(self, obj):
        """
        دالة للحصول على الرابط الكامل للصورة
        Args:
            obj: كائن الصورة
        Returns:
            str: الرابط الكامل للصورة أو None إذا لم تكن موجودة
        """
        if obj.image:
            request = self.context.get('request')
            if request:
                # بناء رابط كامل للصورة باستخدام نطاق الطلب
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

# مسلسل العقارات
class PropertySerializer(serializers.ModelSerializer):
    # تضمين صور العقار
    images = PropertyImageSerializer(many=True, read_only=True)
    # إضافة حقول محسوبة لمعلومات المالك
    owner_name = serializers.SerializerMethodField()
    owner_phone = serializers.SerializerMethodField()

    class Meta:
        model = Property
        # تحديد الحقول التي سيتم تضمينها في التسلسل
        fields = [
            'id',              # معرف العقار
            'title',           # عنوان العقار
            'description',     # وصف العقار
            'property_type',   # نوع العقار
            'listing_type',    # نوع العرض
            'price',          # السعر
            'currency',       # العملة
            'area',          # المساحة
            'bedrooms',      # عدد غرف النوم
            'bathrooms',     # عدد الحمامات
            'governorate',   # المحافظة
            'district',      # المديرية
            'living_rooms',  # عدد غرف المعيشة
            'majlis',        # عدد المجالس
            'kitchens',      # عدد المطابخ
            'images',        # صور العقار
            'owner_name',    # اسم المالك
            'owner_phone'    # رقم هاتف المالك
        ]

    def get_owner_name(self, obj):
        """
        دالة للحصول على اسم مالك العقار
        Args:
            obj: كائن العقار
        Returns:
            str: الاسم الكامل للمالك أو اسم المستخدم إذا لم يكن الاسم الكامل متوفراً
        """
        return obj.owner.get_full_name() or obj.owner.username

    def get_owner_phone(self, obj):
        """
        دالة للحصول على رقم هاتف مالك العقار
        Args:
            obj: كائن العقار
        Returns:
            str: رقم الهاتف أو None إذا لم يكن متوفراً
        """
        return obj.owner.profile.phone_number if hasattr(obj.owner, 'profile') else None
