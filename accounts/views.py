# استيراد المكتبات اللازمة
from django.shortcuts import render, redirect, get_object_or_404  # دوال مساعدة للعرض والتوجيه
from django.contrib.auth.decorators import login_required  # مزخرف للتحقق من تسجيل الدخول
from django.contrib.auth.models import User  # نموذج المستخدم
from django.contrib import messages  # نظام الرسائل
from django.contrib.auth import login  # دالة تسجيل الدخول
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ProfilePictureForm  # نماذج الحسابات
from .models import Profile  # نموذج الملف الشخصي
from properties.models import Property  # نموذج العقارات

def register(request):
    """
    عرض نموذج التسجيل ومعالجة البيانات المرسلة
    - إذا كان الطلب POST: التحقق من صحة البيانات وإنشاء المستخدم
    - إذا كان الطلب GET: عرض نموذج فارغ
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'تم إنشاء حسابك بنجاح!')
            login(request, user)
            return redirect('accounts:setup_profile')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {
        'form': form,
        'title': 'إنشاء حساب جديد'
    })

@login_required
def profile(request):
    """
    عرض الملف الشخصي للمستخدم الحالي
    يتضمن:
    - العقارات المملوكة
    - العقارات المفضلة
    - إحصائيات المتابعة
    """
    properties = Property.objects.filter(owner=request.user)
    liked_properties = request.user.liked_properties.all().order_by('-created_at')[:3]
    
    context = {
        'properties': properties,
        'liked_properties': liked_properties,
        'properties_count': properties.count(),
        'followers_count': request.user.profile.followers.count(),
        'following_count': request.user.profile.following.count()
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """
    تعديل الملف الشخصي للمستخدم
    - تحديث بيانات المستخدم الأساسية
    - تحديث بيانات الملف الشخصي
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'تم تحديث ملفك الشخصي بنجاح!')
            return redirect('accounts:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'title': 'تعديل الملف الشخصي'
    }
    return render(request, 'accounts/edit_profile.html', context)

def user_profile(request, username):
    """
    عرض الملف الشخصي لمستخدم معين
    - عرض العقارات المتاحة
    - التحقق من حالة المتابعة
    """
    profile_user = get_object_or_404(User, username=username)
    properties = Property.objects.filter(owner=profile_user, is_available=True).order_by('-created_at')
    
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = profile_user.profile in request.user.profile.following.all()
    
    context = {
        'profile_user': profile_user,
        'properties': properties,
        'is_following': is_following
    }
    
    return render(request, 'accounts/user_profile.html', context)

@login_required
def follow_user(request, username):
    """
    متابعة مستخدم معين
    - إضافة المستخدم إلى قائمة المتابَعين
    - إضافة المستخدم الحالي إلى قائمة المتابِعين للمستخدم المتابَع
    """
    user_to_follow = get_object_or_404(User, username=username)
    if request.user != user_to_follow:
        request.user.profile.following.add(user_to_follow.profile)
        user_to_follow.profile.followers.add(request.user.profile)
        
        display_name = user_to_follow.get_full_name() or username
        messages.success(request, f'تم متابعة {display_name} بنجاح!')
    
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('accounts:user_profile', username=username)

@login_required
def unfollow_user(request, username):
    """
    إلغاء متابعة مستخدم معين
    - إزالة المستخدم من قائمة المتابَعين
    - إزالة المستخدم الحالي من قائمة المتابِعين للمستخدم المتابَع
    """
    user_to_unfollow = get_object_or_404(User, username=username)
    if request.user != user_to_unfollow:
        request.user.profile.following.remove(user_to_unfollow.profile)
        user_to_unfollow.profile.followers.remove(request.user.profile)
        
        display_name = user_to_unfollow.get_full_name() or username
        messages.success(request, f'تم إلغاء متابعة {display_name} بنجاح!')
    
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('accounts:user_profile', username=username)

@login_required
def followers_list(request):
    """عرض قائمة المتابِعين للمستخدم الحالي"""
    followers = request.user.profile.followers.all()
    return render(request, 'accounts/followers_list.html', {'followers': followers})

@login_required
def following_list(request):
    """عرض قائمة المستخدمين الذين يتابعهم المستخدم الحالي"""
    following = request.user.profile.following.all()
    return render(request, 'accounts/following_list.html', {'following': following})

def setup_profile(request):
    """
    إعداد الملف الشخصي للمستخدم الجديد
    - إضافة صورة شخصية (اختياري)
    - يمكن تخطي هذه الخطوة
    """
    if request.method == 'POST':
        if 'skip' in request.POST:
            messages.info(request, 'يمكنك إضافة صورة شخصية لاحقاً من صفحة الملف الشخصي')
            return redirect('home:home')
        
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث صورتك الشخصية بنجاح!')
            return redirect('home:home')
    else:
        form = ProfilePictureForm(instance=request.user.profile)
    
    return render(request, 'accounts/setup_profile.html', {'form': form})
