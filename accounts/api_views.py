# استيراد المكتبات اللازمة
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from .serializers import UserSerializer, UserProfileSerializer

@api_view(['POST'])
@csrf_exempt
def register_user(request):
    """
    تسجيل مستخدم جديد
    
    Args:
        request: طلب HTTP يحتوي على بيانات المستخدم
        
    Returns:
        Response: رد يحتوي على رمز المصادقة ومعرف المستخدم واسم المستخدم
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        # حفظ المستخدم الجديد
        user = serializer.save()
        # إنشاء أو الحصول على رمز المصادقة
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@csrf_exempt
def login_user(request):
    """
    تسجيل دخول المستخدم
    
    Args:
        request: طلب HTTP يحتوي على اسم المستخدم وكلمة المرور
        
    Returns:
        Response: رد يحتوي على رمز المصادقة ومعرف المستخدم واسم المستخدم
    """
    username = request.data.get('username')
    password = request.data.get('password')

    # التحقق من وجود اسم المستخدم وكلمة المرور
    if username is None or password is None:
        return Response({'error': 'الرجاء إدخال اسم المستخدم وكلمة المرور'},
                      status=status.HTTP_400_BAD_REQUEST)

    # التحقق من صحة بيانات الدخول
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'بيانات الدخول غير صحيحة'},
                      status=status.HTTP_404_NOT_FOUND)

    # إنشاء أو الحصول على رمز المصادقة
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user_id': user.pk,
        'username': user.username
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    عرض الملف الشخصي للمستخدم
    
    Args:
        request: طلب HTTP مصادق عليه
        
    Returns:
        Response: رد يحتوي على بيانات الملف الشخصي
    """
    serializer = UserProfileSerializer(request.user.profile)
    return Response(serializer.data)

@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    تحديث الملف الشخصي للمستخدم
    
    Args:
        request: طلب HTTP يحتوي على البيانات المحدثة
        
    Returns:
        Response: رد يحتوي على بيانات الملف الشخصي المحدثة
    """
    serializer = UserProfileSerializer(request.user.profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
