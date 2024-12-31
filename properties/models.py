# استيراد المكتبات اللازمة
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# نموذج المحافظات
class Governorate(models.Model):
    # اسم المحافظة
    name = models.CharField(max_length=100, verbose_name=_('Governorate Name'))
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Governorate')
        verbose_name_plural = _('Governorates')

# نموذج المديريات
class District(models.Model):
    # العلاقة مع المحافظة (كل مديرية تتبع محافظة)
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name='districts')
    # اسم المديرية
    name = models.CharField(max_length=100, verbose_name=_('District Name'))
    
    def __str__(self):
        return f"{self.name} - {self.governorate.name}"
    
    class Meta:
        verbose_name = _('District')
        verbose_name_plural = _('Districts')

# نموذج العقارات
class Property(models.Model):
    # خيارات نوع العقار
    PROPERTY_TYPE_CHOICES = [
        ('apartment', _('شقة')),
        ('house', _('منزل')),
        ('villa', _('فلة')),
        ('land', _('أرض')),
        ('commercial', _('دكان')),
    ]

    # خيارات نوع العرض
    LISTING_TYPE_CHOICES = [
        ('sale', _('للبيع')),
        ('rent', _('للإجار')),
    ]

    # خيارات العملة
    CURRENCY_CHOICES = [
        ('YER', _('ريال يمني ')),
        ('USD', _('دولار')),
        ('SAR', _(' ريال سعودي')),
    ]

    # خيارات وحدة قياس المساحة
    area_meas = [
        ('meter', _('متر مربع')),
        ('labinh', _('لبنه')),
        ('q', _('قصبة')),
    ]

    # معلومات العقار الأساسية
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')  # مالك العقار
    title = models.CharField(max_length=200)  # عنوان العقار
    description = models.TextField()  # وصف العقار
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)  # نوع العقار
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES)  # نوع العرض
    price = models.DecimalField(max_digits=12, decimal_places=2)  # السعر
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='YER')  # العملة
    
    # معلومات الغرف
    halls_count = models.PositiveIntegerField(verbose_name=_('Number of Halls'), default=0)  # عدد الصالات
    councils_count = models.PositiveIntegerField(verbose_name=_('Number of Councils'), default=0)  # عدد المجالس
    rooms_count = models.PositiveIntegerField(verbose_name=_('Number of Rooms'), default=0)  # عدد الغرف
    
    # معلومات المساحة
    area = models.DecimalField(max_digits=10, decimal_places=2)  # المساحة
    area_measurment = models.CharField(max_length=20, choices=area_meas)  # وحدة قياس المساحة
    
    # معلومات الموقع
    governorate = models.ForeignKey(Governorate, on_delete=models.SET_NULL, null=True, related_name='properties')  # المحافظة
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='properties')  # المديرية
    neighborhood = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Neighborhood/Street'))  # الحي/الشارع
    map_location = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('Map Location'))  # موقع الخريطة
    
    # تفاصيل الغرف
    bedrooms = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Number of Bedrooms'))  # عدد غرف النوم
    living_rooms = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Number of Living Rooms'))  # عدد غرف المعيشة
    bathrooms = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Number of Bathrooms'))  # عدد الحمامات
    kitchens = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Number of Kitchens'))  # عدد المطابخ
    majlis = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Number of Majlis'))  # عدد المجالس
    
    # تفاصيل الطوابق
    floor_number = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Floor Number'))  # رقم الطابق (للشقق)
    number_of_floors = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Number of Floors'))  # عدد الطوابق (للمنازل)
    
    # معلومات إضافية
    location = models.CharField(max_length=200)  # الموقع العام
    address = models.TextField()  # العنوان التفصيلي
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ الإنشاء
    updated_at = models.DateTimeField(auto_now=True)  # تاريخ التحديث
    is_available = models.BooleanField(default=True)  # متاح للبيع/الإيجار
    views_count = models.PositiveIntegerField(default=0)  # عدد المشاهدات
    liked_by = models.ManyToManyField(User, related_name='liked_properties', blank=True)  # المستخدمين الذين أعجبوا بالعقار

    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# نموذج صور العقار
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')  # العقار المرتبط
    image = models.ImageField(upload_to='property_images/')  # الصورة
    is_primary = models.BooleanField(default=False)  # هل هي الصورة الرئيسية
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ الإضافة

    class Meta:
        ordering = ['-is_primary', '-created_at']

# نموذج طلبات العقارات
class PropertyRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_requests')  # المستخدم الطالب
    property_type = models.CharField(max_length=20, choices=Property.PROPERTY_TYPE_CHOICES)  # نوع العقار المطلوب
    listing_type = models.CharField(max_length=10, choices=Property.LISTING_TYPE_CHOICES)  # نوع الطلب
    preferred_location = models.CharField(max_length=200)  # الموقع المفضل
    max_price = models.DecimalField(max_digits=12, decimal_places=2)  # أقصى سعر
    min_area = models.DecimalField(max_digits=10, decimal_places=2)  # أقل مساحة
    bedrooms = models.PositiveIntegerField(null=True, blank=True)  # عدد غرف النوم المطلوبة
    description = models.TextField()  # وصف الطلب
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ الطلب
    is_active = models.BooleanField(default=True)  # هل الطلب نشط

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s request for {self.get_property_type_display()}"

# نموذج الإعجاب بالعقارات
class PropertyLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_likes')  # المستخدم المعجب
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='likes')  # العقار
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ الإعجاب

    class Meta:
        unique_together = ('user', 'property')

# نموذج التعليقات على العقارات
class PropertyComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_comments')  # المستخدم المعلق
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='comments')  # العقار
    content = models.TextField()  # محتوى التعليق
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ التعليق
    updated_at = models.DateTimeField(auto_now=True)  # تاريخ التحديث
    liked_by = models.ManyToManyField(User, related_name='liked_comments', through='CommentLike')  # المستخدمين المعجبين
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')  # التعليق الأصلي (للردود)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s comment on {self.property.title}"

# نموذج الإعجاب بالتعليقات
class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')  # المستخدم المعجب
    comment = models.ForeignKey(PropertyComment, on_delete=models.CASCADE, related_name='likes')  # التعليق
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ الإعجاب

    class Meta:
        unique_together = ('user', 'comment')

# نموذج متابعة المستخدمين
class UserFollow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')  # المتابِع
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')  # المتابَع
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ المتابعة

    class Meta:
        unique_together = ('follower', 'following')

# نموذج المحادثات
class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')  # المشاركون في المحادثة
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ إنشاء المحادثة
    updated_at = models.DateTimeField(auto_now=True)  # تاريخ آخر تحديث

    class Meta:
        ordering = ['-updated_at']

# نموذج الرسائل
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')  # المحادثة
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_messages')  # المرسل
    content = models.TextField()  # محتوى الرسالة
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ الإرسال
    is_read = models.BooleanField(default=False)  # هل تم القراءة

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} in {self.chat.id}"
