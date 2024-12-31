"""
إعدادات مشروع مساكن
"""

# استيراد المكتبات اللازمة
from pathlib import Path
import os

# تحديد المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# مفتاح الأمان - يجب تغييره في الإنتاج
SECRET_KEY = 'django-insecure-your-secret-key'

# وضع التطوير - يجب إيقافه في الإنتاج
DEBUG = True

# المضيفين المسموح لهم
ALLOWED_HOSTS = ['*']

# التطبيقات المثبتة
INSTALLED_APPS = [
    # تطبيقات النظام الأساسية
    'daphne',  # خادم ASGI
    'django.contrib.admin',  # لوحة التحكم
    'django.contrib.auth',  # نظام المصادقة
    'django.contrib.contenttypes',  # أنواع المحتوى
    'django.contrib.sessions',  # الجلسات
    'django.contrib.messages',  # الرسائل
    'django.contrib.staticfiles',  # الملفات الثابتة
    'django.contrib.sites',  # المواقع
    
    # تطبيقات المصادقة
    'allauth',  # نظام المصادقة المتقدم
    'allauth.account',  # حسابات المستخدمين
    'allauth.socialaccount',  # المصادقة الاجتماعية
    
    # تطبيقات واجهة المستخدم
    'crispy_forms',  # تنسيق النماذج
    'crispy_bootstrap5',  # نمط بوتستراب 5
    
    # تطبيقات المشروع
    'chat',  # نظام المحادثات
    'home',  # الصفحة الرئيسية
    'properties',  # نظام العقارات
    'accounts',  # نظام الحسابات
    'notifications',  # نظام الإشعارات
    
    # تطبيقات API والويب سوكيت
    'channels',  # دعم WebSocket
    'rest_framework',  # إطار عمل REST
    'rest_framework.authtoken',  # مصادقة التوكن
    'corsheaders',  # دعم CORS
    'django_filters',  # تصفية البيانات
]

# الوسطاء (Middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # الأمان
    'django.contrib.sessions.middleware.SessionMiddleware',  # الجلسات
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.middleware.common.CommonMiddleware',  # عام
    'django.middleware.csrf.CsrfViewMiddleware',  # حماية CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # المصادقة
    'allauth.account.middleware.AccountMiddleware',  # حسابات المستخدمين
    'django.contrib.messages.middleware.MessageMiddleware',  # الرسائل
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # حماية الإطارات
]

# إعدادات URL الرئيسي
ROOT_URLCONF = 'msakin.urls'

# إعدادات القوالب
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # مجلد القوالب
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications.context_processors.notifications_processor',  # معالج الإشعارات
            ],
        },
    },
]

# إعدادات WSGI و ASGI
WSGI_APPLICATION = 'msakin.wsgi.application'
ASGI_APPLICATION = 'msakin.routing.application'

# إعدادات Channel layers للويب سوكيت
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# إعدادات قاعدة البيانات
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # نوع قاعدة البيانات
        'NAME': 'Msakin-book_db',  # اسم قاعدة البيانات
        'USER': 'postgres',  # اسم المستخدم
        'PASSWORD': 'mohammed2000',  # كلمة المرور
        'HOST': '127.0.0.1',  # المضيف
        'PORT': '5432',  # المنفذ
    }
}

# التحقق من كلمات المرور
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # التحقق من التشابه
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # الحد الأدنى للطول
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # كلمات المرور الشائعة
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # التحقق من الأرقام
    },
]

# إعدادات اللغة والتوقيت
LANGUAGE_CODE = 'ar'  # اللغة الافتراضية
TIME_ZONE = 'Asia/Riyadh'  # المنطقة الزمنية
USE_I18N = True  # دعم الترجمة
USE_L10N = True  # تنسيق التاريخ والوقت
USE_TZ = True  # دعم المناطق الزمنية

# مسارات ملفات الترجمة
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# اللغات المدعومة
LANGUAGES = [
    ('ar', 'Arabic'),
    ('en', 'English'),
]

# الترميز الافتراضي
DEFAULT_CHARSET = 'utf-8'

# إعدادات REST Framework
REST_FRAMEWORK = {
    # إعدادات المصادقة
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # مصادقة التوكن
    ],
    # إعدادات العرض
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    # إعدادات التحليل
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ],
    # إعدادات الصلاحيات
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    # إعدادات الترميز
    'DEFAULT_CHARSET': 'utf-8',
    # إعدادات JSON
    'UNICODE_JSON': True,
    'COMPACT_JSON': False,
}

# إعدادات CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://10.0.2.2:8000",
    "http://localhost:8000",
]

CORS_ALLOW_ALL_ORIGINS = True  # للتطوير فقط
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# إعدادات Character encoding
FILE_CHARSET = 'utf-8'

# إعدادات الملفات الثابتة
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# إعدادات الملفات الوسيطة
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# إعدادات Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# إعدادات المفتاح الأساسي الافتراضي
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# إعدادات تسجيل الدخول
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'home:home'
# LOGOUT_REDIRECT_URL = 'home:home'

# إعدادات Django AllAuth
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# إعدادات AllAuth
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
