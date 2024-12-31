# استيراد المكتبات اللازمة
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os

# نموذج الملف الشخصي للمستخدم
class Profile(models.Model):
    # العلاقة مع نموذج المستخدم الأساسي
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # معلومات الملف الشخصي
    bio = models.TextField(max_length=500, blank=True)  # نبذة شخصية
    phone_number = models.CharField(max_length=20, blank=True)  # رقم الهاتف
    profile_picture = models.ImageField(upload_to='profile_pics', default='default/default_avatar.png')  # الصورة الشخصية
    
    # معلومات العنوان
    address = models.CharField(max_length=255, blank=True)  # العنوان
    city = models.CharField(max_length=100, blank=True)    # المدينة
    country = models.CharField(max_length=100, blank=True)  # البلد
    
    # الحالة والأدوار
    is_verified = models.BooleanField(default=False)  # حالة التحقق
    is_agent = models.BooleanField(default=False)     # هل هو وكيل عقاري
    
    # العلاقات الاجتماعية
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)  # المتابَعون
    
    # الطوابع الزمنية
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ الإنشاء
    updated_at = models.DateTimeField(auto_now=True)      # تاريخ التحديث

    def __str__(self):
        """تمثيل نصي للملف الشخصي"""
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        """
        حفظ الملف الشخصي مع معالجة الصورة الشخصية
        - تحويل الصورة إلى RGB إذا كانت RGBA
        - جعل الصورة مربعة
        - تغيير حجم الصورة إذا كانت كبيرة جداً
        """
        super().save(*args, **kwargs)

        if self.profile_picture and not self.profile_picture.name.endswith('default_avatar.png'):
            img = Image.open(self.profile_picture.path)
            
            # تحويل RGBA إلى RGB إذا لزم الأمر
            if img.mode == 'RGBA':
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg

            # جعل الصورة مربعة
            size = min(img.size)
            left = (img.width - size) // 2
            top = (img.height - size) // 2
            right = left + size
            bottom = top + size
            img = img.crop((left, top, right, bottom))

            # تغيير الحجم
            if size > 300:
                img = img.resize((300, 300), Image.Resampling.LANCZOS)

            # حفظ الصورة
            img.save(self.profile_picture.path, quality=90, optimize=True)

    @property
    def avatar_url(self):
        """إرجاع رابط الصورة الشخصية، مع استخدام الصورة الافتراضية إذا لم تكن موجودة"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/accounts/default/default_avatar.png'

    @property
    def name(self):
        """إرجاع الاسم الكامل للمستخدم، أو اسم المستخدم إذا لم يكن الاسم موجوداً"""
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        return full_name or self.user.username

    @property
    def first_name(self):
        """إرجاع الاسم الأول للمستخدم"""
        return self.user.first_name

    @property
    def last_name(self):
        """إرجاع الاسم الأخير للمستخدم"""
        return self.user.last_name

    @property
    def email(self):
        """إرجاع البريد الإلكتروني للمستخدم"""
        return self.user.email

# إشارات لإنشاء وحفظ الملف الشخصي تلقائياً
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """إنشاء ملف شخصي جديد عند إنشاء مستخدم جديد"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """حفظ الملف الشخصي عند تحديث المستخدم"""
    instance.profile.save()

# نموذج الحسابات الاجتماعية
class SocialAccount(models.Model):
    # خيارات مزودي الخدمة
    PROVIDER_CHOICES = (
        ('google', 'Google'),
        ('apple', 'Apple'),
    )

    # العلاقات والحقول
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')  # المستخدم
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)  # مزود الخدمة
    provider_id = models.CharField(max_length=100)  # معرف المستخدم لدى مزود الخدمة
    
    # الطوابع الزمنية
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ الإنشاء
    updated_at = models.DateTimeField(auto_now=True)      # تاريخ التحديث

    class Meta:
        unique_together = ('provider', 'provider_id')

    def __str__(self):
        """تمثيل نصي للحساب الاجتماعي"""
        return f'{self.user.username} - {self.provider}'
