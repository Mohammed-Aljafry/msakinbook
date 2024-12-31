# استيراد المكتبات اللازمة
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    """
    محول لإنشاء مستخدم جديد مع التحقق من صحة البيانات
    يتطلب:
    - اسم المستخدم
    - كلمة المرور (مع التأكيد)
    - رقم الهاتف
    - البريد الإلكتروني (اختياري)
    - الاسم الأول والأخير (اختياري)
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])  # كلمة المرور
    password2 = serializers.CharField(write_only=True, required=True)  # تأكيد كلمة المرور
    phone = serializers.CharField(write_only=True, required=True)  # رقم الهاتف

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'phone')

    def validate(self, attrs):
        """
        التحقق من صحة البيانات:
        - تطابق كلمتي المرور
        - عدم تكرار اسم المستخدم
        - عدم تكرار البريد الإلكتروني
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "كلمات المرور غير متطابقة"})
        
        # التحقق من وجود اسم المستخدم
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "اسم المستخدم موجود مسبقاً"})
        
        # التحقق من وجود البريد الإلكتروني
        if 'email' in attrs and User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "البريد الإلكتروني مستخدم مسبقاً"})
            
        return attrs

    def create(self, validated_data):
        """
        إنشاء مستخدم جديد بعد التحقق من صحة البيانات
        - إزالة تأكيد كلمة المرور
        - إنشاء المستخدم
        - تحديث رقم الهاتف في الملف الشخصي
        """
        validated_data.pop('password2')
        phone = validated_data.pop('phone')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        
        # تحديث رقم الهاتف في الملف الشخصي الذي تم إنشاؤه تلقائياً
        user.profile.phone_number = phone
        user.profile.save()
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """
    محول الملف الشخصي للمستخدم
    يستخدم لعرض وتحديث بيانات الملف الشخصي
    """
    # حقول المستخدم الأساسية
    id = serializers.IntegerField(source='user.id', read_only=True)  # معرف المستخدم
    name = serializers.SerializerMethodField()  # الاسم الكامل
    email = serializers.EmailField(source='user.email')  # البريد الإلكتروني
    phone = serializers.CharField(source='phone_number')  # رقم الهاتف
    
    # حقول الملف الشخصي
    avatar = serializers.ImageField(source='profile_picture', required=False)  # الصورة الشخصية
    bio = serializers.CharField(required=False, allow_blank=True)  # نبذة شخصية
    address = serializers.CharField(required=False, allow_blank=True)  # العنوان
    city = serializers.CharField(required=False, allow_blank=True)  # المدينة
    country = serializers.CharField(required=False, allow_blank=True)  # البلد
    
    # حقول الحالة
    is_verified = serializers.BooleanField(read_only=True)  # حالة التحقق
    is_agent = serializers.BooleanField(read_only=True)  # حالة الوكيل
    
    # الطوابع الزمنية
    created_at = serializers.DateTimeField(source='user.date_joined', read_only=True)  # تاريخ الإنشاء
    updated_at = serializers.DateTimeField(read_only=True)  # تاريخ التحديث

    class Meta:
        model = Profile
        fields = (
            'id', 'name', 'email', 'phone', 'avatar', 'bio',
            'address', 'city', 'country', 'is_verified', 'is_agent',
            'created_at', 'updated_at'
        )

    def get_name(self, obj):
        """إرجاع الاسم الكامل للمستخدم، أو اسم المستخدم إذا لم يكن الاسم موجوداً"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def update(self, instance, validated_data):
        """
        تحديث بيانات الملف الشخصي
        - تحديث البريد الإلكتروني إذا تم تغييره
        - تحديث باقي بيانات الملف الشخصي
        """
        user_data = validated_data.pop('user', {})
        user = instance.user

        # تحديث بيانات المستخدم
        if 'email' in user_data:
            user.email = user_data['email']
        
        # تحديث الملف الشخصي
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        user.save()
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    """محول تسجيل الدخول باستخدام البريد الإلكتروني وكلمة المرور"""
    email = serializers.EmailField()  # البريد الإلكتروني
    password = serializers.CharField()  # كلمة المرور

class GoogleLoginSerializer(serializers.Serializer):
    """محول تسجيل الدخول باستخدام حساب Google"""
    access_token = serializers.CharField()  # رمز الوصول من Google

class AppleLoginSerializer(serializers.Serializer):
    """محول تسجيل الدخول باستخدام حساب Apple"""
    identity_token = serializers.CharField()  # رمز الهوية من Apple
    authorization_code = serializers.CharField()  # رمز التفويض من Apple
