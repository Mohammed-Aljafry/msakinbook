# استيراد المكتبات اللازمة
from django.urls import path
from django.contrib.auth import views as auth_views  # مشاهدات المصادقة المدمجة في Django
from . import views  # مشاهدات التطبيق المخصصة

# اسم التطبيق للاستخدام في التوجيه العكسي للروابط
app_name = 'accounts'

# قائمة المسارات URL
urlpatterns = [
    # مسارات التسجيل وتسجيل الدخول/الخروج
    path('register/', views.register, name='register'),  # تسجيل مستخدم جديد
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        extra_context={'title': 'تسجيل الدخول'},
        next_page='home:home'
    ), name='login'),  # صفحة تسجيل الدخول
    
    path('logout/', auth_views.LogoutView.as_view(
        template_name='accounts/logged_out.html',
        # next_page='home:home'
    ), name='logout'),  # تسجيل الخروج
    
    # مسارات الملف الشخصي
    path('profile/', views.profile, name='profile'),  # عرض الملف الشخصي للمستخدم الحالي
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # تعديل الملف الشخصي
    path('profile/setup/', views.setup_profile, name='setup_profile'),  # إعداد الملف الشخصي لأول مرة
    path('profile/<str:username>/', views.user_profile, name='user_profile'),  # عرض ملف شخصي لمستخدم معين
    
    # مسارات المتابعة
    path('follow/<str:username>/', views.follow_user, name='follow_user'),  # متابعة مستخدم
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),  # إلغاء متابعة مستخدم
    path('followers/', views.followers_list, name='followers_list'),  # قائمة المتابعين
    path('following/', views.following_list, name='following_list'),  # قائمة المتابَعين
    
    # مسارات إعادة تعيين كلمة المرور
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             extra_context={'title': 'إعادة تعيين كلمة المرور'}
         ),
         name='password_reset'),  # طلب إعادة تعيين كلمة المرور
         
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html',
             extra_context={'title': 'تم إرسال رابط إعادة التعيين'}
         ),
         name='password_reset_done'),  # تأكيد إرسال بريد إعادة التعيين
         
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             extra_context={'title': 'تعيين كلمة المرور الجديدة'}
         ),
         name='password_reset_confirm'),  # تأكيد إعادة تعيين كلمة المرور
         
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html',
             extra_context={'title': 'تم تغيير كلمة المرور'}
         ),
         name='password_reset_complete'),  # اكتمال إعادة تعيين كلمة المرور
]
