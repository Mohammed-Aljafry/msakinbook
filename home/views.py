from django.shortcuts import render
from django.contrib.auth.models import User
from properties.models import Property, Governorate
from django.db.models import Q 

def home(request):
    # Get featured properties (newest 9 properties with images)
    featured_properties = Property.objects.filter(
        is_available=True,
        images__isnull=False
    ).prefetch_related(
        'images',
        'district',
        'district__governorate'
    ).distinct().order_by('-created_at')[:9]
    
    # Initialize query
    properties = Property.objects.filter(is_available=True)
    
    # Get search parameters
    query = request.GET.get('q')
    property_type = request.GET.get('property_type')
    listing_type = request.GET.get('listing_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Apply filters
    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )
    
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    if listing_type:
        properties = properties.filter(listing_type=listing_type)
    
    if min_price:
        properties = properties.filter(price__gte=min_price)
    
    if max_price:
        properties = properties.filter(price__lte=max_price)
    
    # Order results
    properties = properties.order_by('-created_at')[:12]
    
    # Get statistics
    properties_count = Property.objects.filter(is_available=True).count()
    governorates_count = Governorate.objects.count()
    users_count = User.objects.filter(is_active=True).count()
    deals_count = Property.objects.filter(is_available=False).count()
    
    context = {
        'featured_properties': featured_properties,
        'properties': properties,
        'query': query,
        'title': 'الصفحة الرئيسية',
        'properties_count': properties_count,
        'governorates_count': governorates_count,
        'users_count': users_count,
        'deals_count': deals_count
    }
    return render(request, 'home/index.html', context)
