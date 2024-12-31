import os
from channels.routing import get_default_application
# from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator
# from chat.consumers import ChatConsumer
# from django.urls import re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'msakin.settings')


application = get_default_application()


