# استيراد المكتبات اللازمة
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Property
from .serializers import PropertySerializer

# قائمة العقارات - عرض وإضافة
@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticatedOrReadOnly])
def property_list(request):
    if request.method == 'GET':
        # عرض جميع العقارات
        properties = Property.objects.all()
        serializer = PropertySerializer(properties, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # التحقق من تسجيل دخول المستخدم
        if not request.user.is_authenticated:
            return Response(
                {'error': 'يجب تسجيل الدخول لإضافة عقار'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # إضافة عقار جديد
        serializer = PropertySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# تفاصيل العقار - عرض وتعديل وحذف
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def property_detail(request, pk):
    # الحصول على العقار
    property = get_object_or_404(Property, pk=pk)

    if request.method == 'GET':
        # عرض تفاصيل العقار
        serializer = PropertySerializer(property, context={'request': request})
        return Response(serializer.data)
    
    # التحقق من أن المستخدم هو مالك العقار
    if property.owner != request.user:
        return Response(
            {'error': 'ليس لديك الصلاحية لتعديل هذا العقار'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'PUT':
        # تحديث بيانات العقار
        serializer = PropertySerializer(property, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # حذف العقار
        property.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# البحث عن العقارات
@api_view(['GET'])
def property_search(request):
    # البدء بجميع العقارات
    queryset = Property.objects.all()
    
    # تصفية حسب السعر
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)

    # تصفية حسب نوع العقار ونوع العرض
    property_type = request.query_params.get('property_type')
    listing_type = request.query_params.get('listing_type')
    if property_type:
        queryset = queryset.filter(property_type=property_type)
    if listing_type:
        queryset = queryset.filter(listing_type=listing_type)

    # تصفية حسب الموقع
    governorate = request.query_params.get('governorate')
    district = request.query_params.get('district')
    if governorate:
        queryset = queryset.filter(governorate=governorate)
    if district:
        queryset = queryset.filter(district=district)

    # تحويل النتائج إلى JSON
    serializer = PropertySerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)

# عرض عقارات المستخدم الحالي
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def my_properties(request):
    """عرض عقارات المستخدم الحالي"""
    # الحصول على عقارات المستخدم
    properties = Property.objects.filter(owner=request.user)
    serializer = PropertySerializer(properties, many=True, context={'request': request})
    return Response(serializer.data)
