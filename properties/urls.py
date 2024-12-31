from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='property_list'),
    path('property/create/', views.create_property, name='create_property'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('property/<int:pk>/edit/', views.edit_property, name='edit_property'),
    path('property/<int:pk>/delete/', views.delete_property, name='delete_property'),
    path('property/<int:pk>/like/', views.like_property, name='like_property'),
    path('property/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/reply/', views.reply_to_comment, name='reply_to_comment'),
    path('request/create/', views.create_request, name='create_request'),
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
    path('request/<int:pk>/edit/', views.edit_request, name='edit_request'),
    path('request/<int:pk>/delete/', views.delete_request, name='delete_request'),
    path('user/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('my-properties/', views.my_properties, name='my_properties'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('search/', views.search_properties, name='search_properties'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chat/start/<str:username>/', views.start_chat, name='start_chat'),
    path('api/districts/<int:governorate_id>/', views.get_districts, name='get_districts'),
]
