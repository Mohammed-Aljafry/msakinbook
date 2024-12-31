# استيراد المكتبات اللازمة
import json  # للتعامل مع بيانات JSON
from channels.generic.websocket import AsyncWebsocketConsumer  # المستهلك الأساسي للـ WebSocket
from channels.db import database_sync_to_async  # لتحويل عمليات قاعدة البيانات المتزامنة إلى غير متزامنة
from django.contrib.auth.models import User  # نموذج المستخدم
from .models import Message, Conversation, UserStatus  # نماذج التطبيق
from django.utils import timezone  # للتعامل مع التوقيت
import base64  # للتعامل مع الصور المشفرة
from django.core.files.base import ContentFile  # للتعامل مع الملفات

class ChatConsumer(AsyncWebsocketConsumer):
    """
    مستهلك المحادثة - يتعامل مع اتصالات WebSocket للدردشة المباشرة
    """
    
    async def connect(self):
        """
        معالجة اتصال WebSocket جديد
        - قبول الاتصال
        - تحديث حالة المستخدم إلى متصل
        - إضافة المستخدم إلى مجموعة القناة
        """
        await self.accept()
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.update_user_status(True)
            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )

    async def disconnect(self, close_code):
        """
        معالجة قطع اتصال WebSocket
        - تحديث حالة المستخدم إلى غير متصل
        - إزالة المستخدم من مجموعة القناة
        """
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.update_user_status(False)
            await self.channel_layer.group_discard(
                f"user_{self.user.id}",
                self.channel_name
            )

    async def receive(self, text_data):
        """
        معالجة البيانات الواردة عبر WebSocket
        
        المعاملات:
            text_data: البيانات الواردة بتنسيق JSON
        """
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')

        if message_type == 'typing_status':
            await self.handle_typing_status(data)
        elif message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'delete_message':
            await self.handle_delete_message(data)
        elif message_type == 'mark_read':
            await self.handle_mark_read(data)

    async def handle_typing_status(self, data):
        """
        معالجة حالة الكتابة
        
        المعاملات:
            data: بيانات حالة الكتابة
        """
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', False)
        
        await self.update_typing_status(conversation_id, is_typing)
        
        # إخطار المستخدم الآخر
        conversation = await self.get_conversation(conversation_id)
        other_user = await self.get_other_user(conversation)
        
        await self.channel_layer.group_send(
            f"user_{other_user.id}",
            {
                "type": "typing_notification",
                "user_id": self.user.id,
                "is_typing": is_typing,
                "conversation_id": conversation_id
            }
        )

    async def handle_chat_message(self, data):
        """
        معالجة رسالة دردشة جديدة
        
        المعاملات:
            data: بيانات الرسالة
        """
        message = await self.save_message(data)
        conversation = message.conversation
        other_user = await self.get_other_user(conversation)

        # إرسال الرسالة للمستخدم الآخر
        await self.channel_layer.group_send(
            f"user_{other_user.id}",
            {
                'type': 'chat_message',
                'message': await self.message_to_json(message)
            }
        )

        # إرسال الرسالة للمرسل
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': await self.message_to_json(message)
        }))

        # إرسال تحديث للمحادثات
        await self.send_chat_update(self.user.id)
        await self.send_chat_update(other_user.id)

    async def handle_delete_message(self, data):
        """
        معالجة حذف رسالة
        
        المعاملات:
            data: بيانات الرسالة المراد حذفها
        """
        message_id = data.get('message_id')
        if message_id:
            message = await self.get_message(message_id)
            if message and message.sender == self.user:
                await self.delete_message(message_id)
                
                # إرسال إشعار الحذف لجميع المشاركين
                conversation = message.conversation
                for participant in await self.get_conversation_participants(conversation):
                    await self.channel_layer.group_send(
                        f"user_{participant.id}",
                        {
                            "type": "message_deleted",
                            "message": {
                                "message_id": str(message_id)
                            }
                        }
                    )

    async def handle_mark_read(self, data):
        """
        معالجة تحديث حالة قراءة الرسائل
        
        المعاملات:
            data: بيانات المحادثة المراد تحديثها
        """
        conversation_id = data.get('conversation_id')
        if conversation_id:
            await self.mark_messages_as_read(conversation_id)
            conversation = await self.get_conversation(conversation_id)
            other_user = await self.get_other_user(conversation)
            
            await self.channel_layer.group_send(
                f"user_{other_user.id}",
                {
                    "type": "messages_read",
                    "conversation_id": conversation_id,
                    "reader_id": self.user.id
                }
            )

    # دوال معالجة الأحداث

    async def chat_message(self, event):
        """إرسال رسالة دردشة"""
        await self.send(text_data=json.dumps(event))

    async def typing_notification(self, event):
        """إرسال إشعار الكتابة"""
        await self.send(text_data=json.dumps(event))

    async def message_deleted(self, event):
        """إرسال إشعار حذف الرسالة"""
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message': event['message']
        }))

    async def messages_read(self, event):
        """إرسال إشعار قراءة الرسائل"""
        await self.send(text_data=json.dumps(event))

    async def send_chat_update(self, user_id):
        """
        إرسال تحديث للمحادثات
        
        المعاملات:
            user_id: معرف المستخدم المراد إرسال التحديث له
        """
        await self.channel_layer.group_send(
            f"user_{user_id}",
            {
                'type': 'chat_update',
                'message': {
                    'type': 'chat_update'
                }
            }
        )

    async def chat_update(self, event):
        """إرسال تحديث المحادثات للعميل"""
        await self.send(text_data=json.dumps(event['message']))

    # دوال قاعدة البيانات

    @database_sync_to_async
    def update_user_status(self, is_online):
        """
        تحديث حالة اتصال المستخدم
        
        المعاملات:
            is_online: حالة الاتصال (متصل/غير متصل)
        """
        UserStatus.objects.update_or_create(
            user=self.user,
            defaults={'is_online': is_online, 'last_seen': timezone.now()}
        )

    @database_sync_to_async
    def update_typing_status(self, conversation_id, is_typing):
        """
        تحديث حالة كتابة المستخدم
        
        المعاملات:
            conversation_id: معرف المحادثة
            is_typing: حالة الكتابة
        """
        status, _ = UserStatus.objects.get_or_create(user=self.user)
        status.is_typing = is_typing
        status.typing_in_conversation_id = conversation_id if is_typing else None
        status.save()

    @database_sync_to_async
    def get_or_create_conversation(self, recipient_id):
        """
        جلب أو إنشاء محادثة جديدة
        
        المعاملات:
            recipient_id: معرف المستلم
            
        يرجع:
            محادثة موجودة أو جديدة
        """
        recipient = User.objects.get(id=recipient_id)
        conversation = Conversation.objects.filter(
            participants=self.user
        ).filter(
            participants=recipient
        ).first()
        
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(self.user, recipient)
            
        return conversation

    @database_sync_to_async
    def create_message(self, conversation, content='', image_data=None):
        """
        إنشاء رسالة جديدة
        
        المعاملات:
            conversation: المحادثة
            content: محتوى الرسالة
            image_data: بيانات الصورة (اختياري)
            
        يرجع:
            الرسالة المنشأة
        """
        message = Message(
            conversation=conversation,
            sender=self.user,
            receiver=conversation.participants.exclude(id=self.user.id).first(),
            content=content
        )
        
        if image_data:
            # تحويل الصورة من base64
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_content = ContentFile(base64.b64decode(imgstr), name=f'msg_{conversation.id}_{timezone.now().timestamp()}.{ext}')
            message.image = image_content
            
        message.save()
        return message

    @database_sync_to_async
    def delete_message(self, message_id):
        """
        حذف رسالة
        
        المعاملات:
            message_id: معرف الرسالة
            
        يرجع:
            True إذا تم الحذف بنجاح، False إذا لم يتم العثور على الرسالة
        """
        try:
            message = Message.objects.get(id=message_id, sender=self.user)
            message.is_deleted = True
            message.save()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_messages_as_read(self, conversation_id):
        """
        تحديث حالة قراءة الرسائل
        
        المعاملات:
            conversation_id: معرف المحادثة
        """
        Message.objects.filter(
            conversation_id=conversation_id,
            receiver=self.user,
            is_read=False
        ).update(is_read=True)

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        """
        جلب محادثة
        
        المعاملات:
            conversation_id: معرف المحادثة
            
        يرجع:
            المحادثة المطلوبة
        """
        return Conversation.objects.get(id=conversation_id)

    @database_sync_to_async
    def get_message(self, message_id):
        """
        جلب رسالة
        
        المعاملات:
            message_id: معرف الرسالة
            
        يرجع:
            الرسالة المطلوبة أو None إذا لم يتم العثور عليها
        """
        try:
            return Message.objects.select_related('conversation', 'sender').get(id=message_id)
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def get_other_user(self, conversation):
        """
        جلب المستخدم الآخر في المحادثة
        
        المعاملات:
            conversation: المحادثة
            
        يرجع:
            المستخدم الآخر
        """
        return conversation.participants.exclude(id=self.user.id).first()

    @database_sync_to_async
    def save_message(self, data):
        """
        حفظ رسالة جديدة
        
        المعاملات:
            data: بيانات الرسالة
            
        يرجع:
            الرسالة المحفوظة
        """
        recipient_id = data.get('recipient_id')
        if not recipient_id:
            raise ValueError('recipient_id is required')
            
        conversation = self.get_or_create_conversation_sync(recipient_id)
        content = data.get('message', '')
        image_data = data.get('image')
        
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            receiver=User.objects.get(id=recipient_id),
            content=content
        )
        
        if image_data:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_content = ContentFile(base64.b64decode(imgstr), name=f'msg_{conversation.id}_{timezone.now().timestamp()}.{ext}')
            message.image = image_content
            message.save()
            
        return message

    def get_or_create_conversation_sync(self, recipient_id):
        """
        جلب أو إنشاء محادثة (نسخة متزامنة)
        
        المعاملات:
            recipient_id: معرف المستلم
            
        يرجع:
            المحادثة
        """
        recipient = User.objects.get(id=recipient_id)
        conversation = Conversation.objects.filter(
            participants=self.user
        ).filter(
            participants=recipient
        ).first()
        
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(self.user, recipient)
            
        return conversation

    @database_sync_to_async
    def message_to_json(self, message):
        """
        تحويل الرسالة إلى تنسيق JSON
        
        المعاملات:
            message: الرسالة
            
        يرجع:
            بيانات الرسالة بتنسيق JSON
        """
        return {
            'id': message.id,
            'sender_id': message.sender.id,
            'content': message.content,
            'image': message.image.url if message.image else None,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read
        }

    @database_sync_to_async
    def get_conversation_participants(self, conversation):
        """
        جلب المشاركين في محادثة
        
        المعاملات:
            conversation: المحادثة
            
        يرجع:
            قائمة المشاركين
        """
        return list(conversation.participants.all())
