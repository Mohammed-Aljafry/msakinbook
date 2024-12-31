from django.urls import path
from . import api_views

urlpatterns = [
    path('register/', api_views.register_user, name='api-register'),
    path('login/', api_views.login_user, name='api-login'),
    path('profile/', api_views.get_user_profile, name='api-profile'),
    path('profile/update/', api_views.update_user_profile, name='api-profile-update'),
]
