# استيراد المكتبات اللازمة
from django import forms
from .models import Property, PropertyRequest, PropertyImage, District
from django.utils.translation import gettext_lazy as _

# نموذج إضافة وتعديل العقار
class PropertyForm(forms.ModelForm):
    # حقل الصور مع خيارات التحميل
    images = forms.ImageField(
        required=False,
        label='صور العقار',
        help_text='اختر صورة للعقار. يمكنك إضافة المزيد من الصور لاحقاً.',
        error_messages={
            'invalid_image': 'الملف المختار ليس صورة صالحة.',
        }
    )
    
    # دالة التهيئة - تحديد المديريات بناءً على المحافظة
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تهيئة حقل المديريات فارغاً
        self.fields['district'].queryset = District.objects.none()
        
        # تحديث المديريات عند اختيار محافظة
        if 'governorate' in self.data:
            try:
                governorate_id = int(self.data.get('governorate'))
                self.fields['district'].queryset = District.objects.filter(governorate_id=governorate_id)
            except (ValueError, TypeError):
                pass
        # عرض المديريات الحالية عند تعديل عقار موجود
        elif self.instance.pk and self.instance.governorate:
            self.fields['district'].queryset = self.instance.governorate.districts.all()
    
    class Meta:
        model = Property
        # تحديد الحقول المطلوبة في النموذج
        fields = [
            'title', 'description', 'property_type', 'listing_type', 
            'price', 'currency', 'area','area_measurment',
            'governorate', 'district', 'neighborhood', 'map_location',
            'bedrooms', 'living_rooms', 'bathrooms', 'kitchens', 'majlis',
            'floor_number', 'number_of_floors',
            'location', 'address'
        ]
        # تعريب أسماء الحقول
        labels = {
            'title': "العنوان",
            'description': "الوصف",
            'property_type': "نوع العقار",
            'listing_type': "نوع العرض",
            'price': "السعر",
            'currency': "العملة",
            'area': "المساحة",
            'area_measurment':"وحدة القياس",
            'governorate': "المحافظة",
            'district': "المديرية",
            'neighborhood': "الحي",
            'map_location': "موقع الخريطة",
            'bedrooms': "عدد غرف النوم",
            'living_rooms': "عدد  الصالات",
            'bathrooms': "عدد دورات المياه",
            'kitchens': "عدد المطابخ",
            'majlis': "عدد المجالس",
            'floor_number': "رقم الطابق",
            'number_of_floors': "عدد الطوابق",
            'location': "الموقع",
            'address': "العنوان التفصيلي",
        }
        # تخصيص شكل عرض بعض الحقول
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),  # مربع نص متعدد الأسطر للوصف
            'address': forms.Textarea(attrs={'rows': 2}),  # مربع نص متعدد الأسطر للعنوان
            'map_location': forms.TextInput(attrs={'class': 'map-location-input'}),  # حقل نصي لموقع الخريطة
            'neighborhood': forms.TextInput(attrs={'placeholder': _('Enter neighborhood or street name')}),  # حقل نصي للحي
        }

    # التحقق من صحة البيانات
    def clean(self):
        cleaned_data = super().clean()
        property_type = cleaned_data.get('property_type')
        floor_number = cleaned_data.get('floor_number')
        number_of_floors = cleaned_data.get('number_of_floors')

        # التحقق من إدخال رقم الطابق للشقق
        if property_type == 'apartment' and not floor_number:
            self.add_error('floor_number', _('Floor number is required for apartments'))
        
        # التحقق من إدخال عدد الطوابق للمنازل
        if property_type == 'house' and not number_of_floors:
            self.add_error('number_of_floors', _('Number of floors is required for houses'))

        return cleaned_data

# نموذج طلب عقار
class PropertyRequestForm(forms.ModelForm):
    class Meta:
        model = PropertyRequest
        # تحديد الحقول المطلوبة في نموذج الطلب
        fields = ['property_type', 'listing_type', 'preferred_location', 
                 'max_price', 'min_area', 'bedrooms', 'description']
        # تخصيص شكل عرض الوصف
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),  # مربع نص متعدد الأسطر للوصف
        }
