# استيراد المكتبات اللازمة
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from functools import wraps
from .models import (
    Property, PropertyRequest, PropertyImage, PropertyLike,
    PropertyComment, UserFollow, Chat, Message, CommentLike,
    Governorate, District
)
from .forms import PropertyForm, PropertyRequestForm
from .services import notify_udate
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import PropertySerializer
from django_filters.rest_framework import DjangoFilterBackend

# دالة مساعدة للتحقق من تسجيل الدخول مع رسالة
def login_required_with_message(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'يرجى تسجيل الدخول أولاً.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# عرض قائمة العقارات
class PropertyListView(ListView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 9  # عدد العقارات في كل صفحة

    def get_queryset(self):
        # الحصول على العقارات المتاحة مرتبة حسب تاريخ الإنشاء
        queryset = Property.objects.filter(is_available=True).order_by('-created_at')
        
        # فلترة حسب نوع العقار
        property_type = self.request.GET.get('property_type')
        if property_type:
            queryset = queryset.filter(property_type=property_type)
            
        # فلترة حسب نوع العرض
        listing_type = self.request.GET.get('listing_type')
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
        
        # تحميل الصور والمعلومات المرتبطة
        queryset = queryset.prefetch_related(
            'images',
            'comments',
            'comments__user',
            'comments__user__profile'
        ).select_related('governorate', 'district')
            
        return queryset

    def get_context_data(self, **kwargs):
        # إضافة معلومات إضافية للقالب
        context = super().get_context_data(**kwargs)
        context['governorates'] = Governorate.objects.all()  # قائمة المحافظات
        context['users'] = User.objects.filter(is_active=True)  # المستخدمين النشطين
        context['deals_count'] = Property.objects.filter(is_available=False).count()  # عدد الصفقات المنتهية
        return context

# الصفحة الرئيسية
def home(request):
    pass
    # properties = Property.objects.all().order_by('-created_at')
    # return render(request, 'properties/home.html', {'properties': properties})

# عرض تفاصيل عقار معين
def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)  # الحصول على العقار
    comments = property.comments.all().order_by('-created_at')  # التعليقات مرتبة
    return render(request, 'properties/property_detail.html', {
        'property': property,
        'comments': comments,
    })

# إضافة عقار جديد
@login_required_with_message
def create_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            # حفظ العقار مع ربطه بالمستخدم الحالي
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            
            # معالجة رفع الصور
            if request.FILES.get('images'):
                image = request.FILES['images']
                PropertyImage.objects.create(
                    property=property,
                    image=image,
                    is_primary=True
                )
            
            messages.success(request, 'تم إضافة العقار بنجاح!')
            return redirect('properties:property_detail', pk=property.pk)
    else:
        form = PropertyForm()
    
    return render(request, 'properties/property_form.html', {
        'form': form,
        'title': 'إضافة عقار جديد'
    })

# تعديل عقار
@login_required_with_message
def edit_property(request, pk):
    # التحقق من وجود العقار وملكية المستخدم له
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property)
        images = request.FILES.getlist('images')  # الحصول على الصور المرفقة
        
        if form.is_valid():
            property = form.save()
            
            # إضافة الصور الجديدة
            for image in images:
                PropertyImage.objects.create(
                    property=property,
                    image=image,
                    is_primary=not PropertyImage.objects.filter(property=property).exists()
                )
            
            messages.success(request, 'تم تحديث العقار بنجاح.')
            return redirect('properties:property_detail', pk=property.pk)
    else:
        form = PropertyForm(instance=property)
    
    return render(request, 'properties/property_form.html', {
        'form': form,
        'property': property
    })

# حذف عقار
@login_required_with_message
def delete_property(request, pk):
    # التحقق من وجود العقار وملكية المستخدم له
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        property.delete()
        messages.success(request, 'تم حذف العقار بنجاح.')
    return redirect('properties:property_list')

# إنشاء طلب عقار
@login_required_with_message
def create_request(request):
    if request.method == 'POST':
        form = PropertyRequestForm(request.POST)
        if form.is_valid():
            # حفظ الطلب مع ربطه بالمستخدم الحالي
            property_request = form.save(commit=False)
            property_request.requester = request.user
            property_request.save()
            messages.success(request, 'تم إنشاء الطلب بنجاح.')
            return redirect('request_detail', pk=property_request.pk)
    else:
        form = PropertyRequestForm()
    
    return render(request, 'properties/request_form.html', {'form': form})

# تعديل طلب عقار
@login_required_with_message
def edit_request(request, pk):
    # التحقق من وجود الطلب وملكية المستخدم له
    property_request = get_object_or_404(PropertyRequest, pk=pk, requester=request.user)
    
    if request.method == 'POST':
        form = PropertyRequestForm(request.POST, instance=property_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الطلب بنجاح.')
            return redirect('request_detail', pk=property_request.pk)
    else:
        form = PropertyRequestForm(instance=property_request)
    
    return render(request, 'properties/request_form.html', {
        'form': form,
        'property_request': property_request
    })

# حذف طلب عقار
@login_required_with_message
def delete_request(request, pk):
    # التحقق من وجود الطلب وملكية المستخدم له
    property_request = get_object_or_404(PropertyRequest, pk=pk, requester=request.user)
    
    if request.method == 'POST':
        property_request.delete()
        messages.success(request, 'تم حذف الطلب بنجاح.')
        return redirect('home')
    
    return render(request, 'properties/request_confirm_delete.html', {
        'property_request': property_request
    })

# عرض تفاصيل طلب عقار
def request_detail(request, pk):
    property_request = get_object_or_404(PropertyRequest, pk=pk)
    return render(request, 'properties/request_detail.html', {
        'property_request': property_request
    })

# عرض عقارات المستخدم
@login_required_with_message
def my_properties(request):
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'properties/my_properties.html', {'properties': properties})

# عرض طلبات المستخدم
@login_required_with_message
def my_requests(request):
    requests = PropertyRequest.objects.filter(requester=request.user).order_by('-created_at')
    return render(request, 'properties/my_requests.html', {'requests': requests})

# البحث عن العقارات
def search_properties(request):
    query = request.GET.get('q', '')  # مصطلح البحث
    property_type = request.GET.get('property_type', '')  # نوع العقار
    listing_type = request.GET.get('listing_type', '')  # نوع العرض
    governorate = request.GET.get('governorate', '')  # المحافظة
    district = request.GET.get('district', '')  # المديرية
    min_price = request.GET.get('min_price', '')  # الحد الأدنى للسعر
    max_price = request.GET.get('max_price', '')  # الحد الأقصى للسعر
    min_area = request.GET.get('min_area', '')  # الحد الأدنى للمساحة
    max_area = request.GET.get('max_area', '')  # الحد الأقصى للمساحة
    
    # البدء بجميع العقارات المتاحة
    properties = Property.objects.filter(is_available=True)
    
    # تطبيق معايير البحث
    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(address__icontains=query)
        )
    
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    if listing_type:
        properties = properties.filter(listing_type=listing_type)
    
    if min_price:
        properties = properties.filter(price__gte=min_price)
    
    if max_price:
        properties = properties.filter(price__lte=max_price)
    
    if min_area:
        properties = properties.filter(area__gte=min_area)
    
    if max_area:
        properties = properties.filter(area__lte=max_area)
    
    if bedrooms:
        properties = properties.filter(bedrooms=bedrooms)
    
    if bathrooms:
        properties = properties.filter(bathrooms=bathrooms)
    
    if location:
        properties = properties.filter(location__icontains=location)
    
    return render(request, 'properties/search_results.html', {
        'properties': properties,
        'query': query
    })

@login_required_with_message
def add_comment(request, pk):
    if request.method == 'POST':
        try:
            property = get_object_or_404(Property, pk=pk)
            content = request.POST.get('content')
            
            if not content:
                return JsonResponse({'status': 'error', 'message': 'المحتوى مطلوب'}, status=400)
            
            comment = PropertyComment.objects.create(
                user=request.user,
                property=property,
                content=content
            )
            
            # إنشاء إشعار للمالك
            if request.user != property.owner:
                try:
                    from notifications.models import Notification
                    from django.contrib.contenttypes.models import ContentType
                    from channels.layers import get_channel_layer
                    from asgiref.sync import async_to_sync
                    import json
                    
                    notification = Notification.objects.create(
                        recipient=property.owner,
                        sender=request.user,
                        notification_type='comment',
                        content_type=ContentType.objects.get_for_model(PropertyComment),
                        object_id=comment.id,
                        text=f"علق {request.user.get_full_name() or request.user.username} على عقارك: {property.title}"
                    )
                    
                    # إرسال الإشعار عبر WebSocket
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'notifications_{property.owner.id}',
                        {
                            'type': 'send_notification',
                            'notification': {
                                'id': notification.id,
                                'text': notification.text,
                                'type': notification.notification_type,
                                'sender': {
                                    'username': request.user.username,
                                    'name': request.user.get_full_name() or request.user.username,
                                    'profile_picture_url': request.user.profile.profile_picture.url if hasattr(request.user, 'profile') and request.user.profile.profile_picture else None
                                },
                                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
                            }
                        }
                    )
                except Exception as e:
                    print(f"Error creating notification: {str(e)}")
            
            from django.http import JsonResponse
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'comment': {
                        'id': comment.id,
                        'user': request.user.username,
                        'content': comment.content,
                        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'profile_picture_url': request.user.profile.profile_picture.url if hasattr(request.user, 'profile') and request.user.profile.profile_picture else None
                    }
                })
            
            return redirect('properties:property_detail', pk=pk)
            
        except Exception as e:
            print(f"Error in add_comment: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'طريقة غير مسموح بها'}, status=405)

@login_required_with_message
def like_property(request, pk):
    # notify_udate(pk);
    if request.method == 'POST':
        try:
            from django.http import JsonResponse
            property = get_object_or_404(Property, pk=pk)
            user = request.user
            is_liked = property.liked_by.filter(id=user.id).exists()

            if is_liked:
                property.liked_by.remove(user)
                liked = False
            else:
                property.liked_by.add(user)
                liked = True
                
                # إنشاء إشعار للمالك عند الإعجاب
                if user != property.owner:
                    try:
                        from notifications.models import Notification
                        from django.contrib.contenttypes.models import ContentType
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        
                        notification = Notification.objects.create(
                            recipient=property.owner,
                            sender=user,
                            notification_type='like',
                            content_type=ContentType.objects.get_for_model(Property),
                            object_id=property.id,
                            text=f"أعجب {user.get_full_name() or user.username} بعقارك: {property.title}"
                        )
                        
                        # إرسال الإشعار عبر WebSocket
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            f'notifications_{property.owner.id}',
                            {
                                'type': 'send_notification',
                                'notification': {
                                    'id': notification.id,
                                    'text': notification.text,
                                    'type': notification.notification_type,
                                    'sender': {
                                        'username': user.username,
                                        'name': user.get_full_name() or user.username,
                                        'profile_picture_url': user.profile.profile_picture.url if hasattr(user, 'profile') and user.profile.profile_picture else None
                                    },
                                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
                                }
                            }
                        )
                    except Exception as e:
                        print(f"Error creating notification: {str(e)}")

            return JsonResponse({
                'status': 'success',
                'liked': liked,
                'likes_count': property.liked_by.count()
            })
        except Exception as e:
            print(f"Error in like_property: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'طريقة غير مسموح بها'}, status=405)

@login_required_with_message
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow == request.user:
        return JsonResponse({'status': 'error', 'message': 'لا يمكنك متابعة نفسك'}, status=400)
    
    follow, created = UserFollow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    if not created:
        follow.delete()
        return JsonResponse({
            'status': 'unfollowed',
            'count': user_to_follow.followers.count()
        })
    return JsonResponse({
        'status': 'followed',
        'count': user_to_follow.followers.count()
    })

@login_required_with_message
def chat_list(request):
    chats = Chat.objects.filter(participants=request.user)
    return render(request, 'properties/chat_list.html', {'chats': chats})

@login_required_with_message
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            message = Message.objects.create(
                chat=chat,
                sender=request.user,
                content=content
            )
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.get_full_name() or message.sender.username,
                    'created_at': message.created_at.strftime('%Y/%m/%d %I:%M %p')
                }
            })
    messages = chat.messages.all()
    return render(request, 'properties/chat_detail.html', {
        'chat': chat,
        'messages': messages
    })

@login_required_with_message
def start_chat(request, username):
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        return JsonResponse({'status': 'error', 'message': 'لا يمكنك بدء محادثة مع نفسك'}, status=400)
    
    # البحث عن محادثة موجودة أو إنشاء واحدة جديدة
    chat = Chat.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(request.user, other_user)
    
    return redirect('properties:chat_detail', chat_id=chat.id)

@login_required_with_message
def like_comment(request, comment_id):
    if request.method == 'POST':
        try:
            comment = get_object_or_404(PropertyComment, id=comment_id)
            user = request.user
            
            if CommentLike.objects.filter(comment=comment, user=user).exists():
                CommentLike.objects.filter(comment=comment, user=user).delete()
                liked = False
            else:
                CommentLike.objects.create(comment=comment, user=user)
                liked = True
                
                # إنشاء إشعار لصاحب التعليق
                if user != comment.user:
                    try:
                        from notifications.models import Notification
                        from django.contrib.contenttypes.models import ContentType
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        
                        notification = Notification.objects.create(
                            recipient=comment.user,
                            sender=user,
                            notification_type='comment_like',
                            content_type=ContentType.objects.get_for_model(PropertyComment),
                            object_id=comment.id,
                            text=f"أعجب {user.get_full_name() or user.username} بتعليقك على العقار: {comment.property.title}"
                        )
                        
                        # إرسال الإشعار عبر WebSocket
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            f'notifications_{comment.user.id}',
                            {
                                'type': 'send_notification',
                                'notification': {
                                    'id': notification.id,
                                    'text': notification.text,
                                    'type': notification.notification_type,
                                    'sender': {
                                        'username': user.username,
                                        'name': user.get_full_name() or user.username,
                                        'profile_picture_url': user.profile.profile_picture.url if hasattr(user, 'profile') and user.profile.profile_picture else None
                                    },
                                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
                                }
                            }
                        )
                    except Exception as e:
                       print(f"Error creating notification: {str(e)}")
            a=CommentLike.objects.filter(comment=comment).count()
            print(a)
            return JsonResponse({
                'status': 'success',
                'liked': liked,
                'likes_count': CommentLike.objects.filter(comment=comment).count()
            })
        except Exception as e:
            print(f"Error in like_comment: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'طريقة غير مسموح بها'}, status=405)

@login_required_with_message
def reply_to_comment(request, comment_id):
    if request.method == 'POST':
        try:
            parent_comment = get_object_or_404(PropertyComment, id=comment_id)
            content = request.POST.get('content')
            
            if not content:
                return JsonResponse({'status': 'error', 'message': 'Content is required'}, status=400)
                
            reply = PropertyComment.objects.create(
                user=request.user,
                property=parent_comment.property,
                content=content,
                parent=parent_comment
            )
            
            # إنشاء إشعار للمستخدم صاحب التعليق الأصلي
            if request.user != parent_comment.user:
                from notifications.models import Notification
                notification = Notification.objects.create(
                    recipient=parent_comment.user,
                    sender=request.user,
                    notification_type='comment_reply',
                    content_object=reply,
                    text=f'رد {request.user.get_full_name() or request.user.username} على تعليقك'
                )
                
                # إرسال الإشعار عبر WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{parent_comment.user.id}',
                    {
                        'type': 'send_notification',
                        'notification': {
                            'id': notification.id,
                            'text': notification.text,
                            'type': notification.notification_type,
                            'sender': {
                                'name': request.user.get_full_name() or request.user.username,
                                'avatar': request.user.profile.avatar_url if hasattr(request.user, 'profile') else None,
                            },
                            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    }
                )

            return JsonResponse({
                'status': 'success',
                'reply': {
                    'id': reply.id,
                    'content': reply.content,
                    'user': {
                        'username': reply.user.username,
                        'name': reply.user.get_full_name() or reply.user.username,
                        'profile_picture_url': reply.user.profile.avatar_url if hasattr(reply.user, 'profile') else None,
                    },
                    'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@require_http_methods(['GET'])
def get_districts(request, governorate_id):
    districts = District.objects.filter(governorate_id=governorate_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.filter(is_available=True).order_by('-created_at')
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'listing_type', 'governorate', 'district']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
