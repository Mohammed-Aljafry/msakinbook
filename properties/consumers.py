# استيراد المكتبات اللازمة
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Property, PropertyComment, PropertyLike, CommentLike

# مستهلك WebSocket عام
class My(AsyncWebsocketConsumer):
    async def connect(self):
        # الانضمام إلى مجموعة العقارات
        await self.channel_layer.group_add(
            "properties",
            self.channel_name
        )
        await self.accept()
    
    async def update_event(self, event):
        # إرسال تحديث للعميل
        await self.send(json.dumps(
            {"data": event["data"]}
        ))

# مستهلك WebSocket للعقارات
class PropertyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # الانضمام إلى مجموعة العقارات عند الاتصال
        await self.channel_layer.group_add(
            "properties",
            self.channel_name
        )
        await self.accept()
        print('connected')

    async def disconnect(self, close_code):
        # إزالة المستخدم من المجموعة عند قطع الاتصال
        await self.channel_layer.group_discard(
            "properties",
            self.channel_name
        )

    async def receive(self, text_data):
        # استقبال البيانات من العميل
        print('start recive in server')
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'like_property':
            # معالجة الإعجاب بالعقار
            print('like')
            property_id = data.get('property_id')
            user_id = data.get('user_id')
            user_idd = 1
            user_iddd = self.scope['user'].id if self.scope['user'].is_authenticated else None
            print(f'user1 {user_id} user2 {user_iddd}')
            
            # تبديل حالة الإعجاب وإرسال التحديث للمجموعة
            response = await self.toggle_property_like(property_id, user_iddd)
            await self.channel_layer.group_send(
                "properties",
                {
                    "type": "property_like_update",
                    "data": response
                }
            )
        
        elif action == 'add_comment':
            # إضافة تعليق جديد
            property_id = data.get('property_id')
            user_id = data.get('user_id')
            content = data.get('content')
            
            # إنشاء التعليق وإرسال التحديث للمجموعة
            response = await self.add_comment(property_id, user_id, content)
            await self.channel_layer.group_send(
                "properties",
                {
                    "type": "comment_update",
                    "data": response
                }
            )
        
        elif action == 'like_comment':
            # معالجة الإعجاب بالتعليق
            comment_id = data.get('comment_id')
            user_id = data.get('user_id')
            
            # تبديل حالة الإعجاب وإرسال التحديث للمجموعة
            response = await self.toggle_comment_like(comment_id, user_id)
            await self.channel_layer.group_send(
                "properties",
                {
                    "type": "comment_like_update",
                    "data": response
                }
            )

    async def property_like_update(self, event):
        # إرسال تحديث الإعجاب بالعقار للعميل
        await self.send(text_data=json.dumps(event['data']))

    async def comment_update(self, event):
        # إرسال تحديث التعليق للعميل
        await self.send(text_data=json.dumps(event['data']))

    async def comment_like_update(self, event):
        # إرسال تحديث الإعجاب بالتعليق للعميل
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def toggle_property_like(self, property_id, user_id):
        try:
            # الحصول على العقار والمستخدم
            property = Property.objects.get(id=property_id)
            user = User.objects.get(id=user_id)
            print('in tray')
            
            # تبديل حالة الإعجاب
            if PropertyLike.objects.filter(property=property, user=user).exists():
                PropertyLike.objects.filter(property=property, user=user).delete()
                liked = False
            else:
                PropertyLike.objects.create(property=property, user=user)
                liked = True
            
            # حساب عدد الإعجابات الجديد
            likes_count = PropertyLike.objects.filter(property=property).count()
            
            return {
                'status': 'success',
                'action': 'property_like',
                'property_id': property_id,
                'liked': liked,
                'likes_count': likes_count
            }
        except (Property.DoesNotExist, User.DoesNotExist):
            return {'status': 'error', 'message': 'Property or user not found'}

    @database_sync_to_async
    def add_comment(self, property_id, user_id, content):
        try:
            # الحصول على العقار والمستخدم
            property = Property.objects.get(id=property_id)
            user = User.objects.get(id=user_id)
            
            # إنشاء التعليق الجديد
            comment = PropertyComment.objects.create(
                property=property,
                user=user,
                content=content
            )
            
            # إرجاع بيانات التعليق
            return {
                'status': 'success',
                'action': 'comment_added',
                'property_id': property_id,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'user': user.username,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'profile_picture_url': user.profile.avatar_url if hasattr(user, 'profile') else None
                }
            }
        except (Property.DoesNotExist, User.DoesNotExist):
            return {'status': 'error', 'message': 'Property or user not found'}

    @database_sync_to_async
    def toggle_comment_like(self, comment_id, user_id):
        try:
            # الحصول على التعليق والمستخدم
            comment = PropertyComment.objects.get(id=comment_id)
            user = User.objects.get(id=user_id)
            
            # تبديل حالة الإعجاب
            if CommentLike.objects.filter(comment=comment, user=user).exists():
                CommentLike.objects.filter(comment=comment, user=user).delete()
                liked = False
            else:
                CommentLike.objects.create(comment=comment, user=user)
                liked = True
            
            # حساب عدد الإعجابات الجديد
            likes_count = CommentLike.objects.filter(comment=comment).count()
            
            return {
                'status': 'success',
                'action': 'comment_like',
                'comment_id': comment_id,
                'liked': liked,
                'likes_count': likes_count
            }
        except (PropertyComment.DoesNotExist, User.DoesNotExist):
            return {'status': 'error', 'message': 'Comment or user not found'}
