# استيراد المكتبات اللازمة
import json  # للتعامل مع JSON
from channels.generic.websocket import AsyncWebsocketConsumer  # المستهلك الأساسي للـ WebSocket
from channels.db import database_sync_to_async  # لتنفيذ استعلامات قاعدة البيانات بشكل غير متزامن
from django.contrib.auth.models import User  # نموذج المستخدم
from .models import Notification  # نموذج الإشعارات

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    مستهلك WebSocket للإشعارات
    يقوم بإدارة اتصالات WebSocket للإشعارات الفورية
    """
    
    async def connect(self):
        """
        معالجة طلب الاتصال بالـ WebSocket
        - التحقق من تسجيل دخول المستخدم
        - إنشاء مجموعة إشعارات خاصة بالمستخدم
        - قبول الاتصال
        """
        self.user = self.scope["user"]
        
        # التحقق من تسجيل دخول المستخدم
        if not self.user.is_authenticated:
            await self.close()
            print('if')
            return
            
        # إنشاء اسم مجموعة الإشعارات الخاصة بالمستخدم
        self.notification_group_name = f'notifications_{self.user.id}'
        
        # الانضمام إلى مجموعة الإشعارات
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        # قبول الاتصال
        await self.accept()
        print('accept')
    
    async def disconnect(self, close_code):
        """
        معالجة قطع الاتصال
        - مغادرة مجموعة الإشعارات
        """
        # مغادرة مجموعة الإشعارات إذا كانت موجودة
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        معالجة البيانات المستلمة من العميل
        حالياً لا يتم معالجة أي بيانات مستلمة
        """
        pass
    
    async def send_notification(self, event):
        """
        إرسال إشعار جديد إلى العميل عبر WebSocket
        
        المعاملات:
            event: يحتوي على بيانات الإشعار المراد إرساله
        """
        notification_data = event['notification']
        
        # إرسال الإشعار إلى WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification_data
        }))
        
    @database_sync_to_async
    def get_notification_data(self, notification_id):
        """
        جلب بيانات إشعار معين بشكل غير متزامن
        
        المعاملات:
            notification_id: معرف الإشعار المطلوب
            
        يرجع:
            قاموس يحتوي على بيانات الإشعار أو None إذا لم يتم العثور عليه
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            return {
                'id': notification.id,
                'text': notification.text,
                'type': notification.notification_type,
                'sender': {
                    'username': notification.sender.username,
                    'name': notification.sender.get_full_name() or notification.sender.username,
                    'avatar_url': notification.sender.profile.avatar.url if notification.sender.profile.avatar else None
                },
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': notification.is_read
            }
        except Notification.DoesNotExist:
            return None
