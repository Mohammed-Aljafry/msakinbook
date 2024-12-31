# استيراد المكتبات اللازمة
from django.db import models  # نماذج قاعدة البيانات
from django.contrib.auth.models import User  # نموذج المستخدم

# Create your models here.

class Conversation(models.Model):
    """
    نموذج المحادثة
    يمثل محادثة بين مستخدمين أو أكثر
    """
    # المشاركون في المحادثة (علاقة متعددة لمتعددة مع المستخدمين)
    participants = models.ManyToManyField(
        User, 
        related_name='conversations'
    )
    
    # توقيت إنشاء وتحديث المحادثة
    created_at = models.DateTimeField(auto_now_add=True)  # يتم تعيينه تلقائياً عند الإنشاء
    updated_at = models.DateTimeField(auto_now=True)      # يتم تحديثه تلقائياً عند كل تعديل

    class Meta:
        """ترتيب المحادثات من الأحدث إلى الأقدم"""
        ordering = ['-updated_at']

    def __str__(self):
        """تمثيل نصي للمحادثة يوضح المشاركين"""
        return f"Conversation {self.id} between {', '.join(user.username for user in self.participants.all())}"

    def get_unread_count(self, user):
        """
        حساب عدد الرسائل غير المقروءة في المحادثة لمستخدم معين
        
        المعاملات:
            user: المستخدم المراد حساب الرسائل غير المقروءة له
            
        يرجع:
            عدد الرسائل غير المقروءة التي لم يرسلها المستخدم
        """
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def get_other_participant(self, user):
        """
        الحصول على المستخدم الآخر في المحادثة
        
        المعاملات:
            user: المستخدم الحالي
            
        يرجع:
            المستخدم الآخر في المحادثة
        """
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    """
    نموذج الرسالة
    يمثل رسالة في محادثة بين مستخدمين
    """
    # العلاقات الأساسية
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )  # المحادثة التي تنتمي إليها الرسالة
    
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )  # مرسل الرسالة
    
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        null=True
    )  # مستلم الرسالة
    
    # محتوى الرسالة
    content = models.TextField(blank=True)  # نص الرسالة
    image = models.ImageField(
        upload_to='chat_images/', 
        null=True, 
        blank=True
    )  # صورة الرسالة (اختياري)
    
    # حالة الرسالة
    is_read = models.BooleanField(default=False)     # هل تم قراءة الرسالة
    is_deleted = models.BooleanField(default=False)  # هل تم حذف الرسالة
    
    # التوقيت
    created_at = models.DateTimeField(auto_now_add=True)  # وقت إنشاء الرسالة
    updated_at = models.DateTimeField(auto_now=True)      # وقت آخر تحديث للرسالة

    class Meta:
        """ترتيب الرسائل من الأقدم إلى الأحدث"""
        ordering = ['created_at']

    def __str__(self):
        """تمثيل نصي للرسالة يوضح المرسل والمستلم"""
        return f"Message from {self.sender.username} to {self.receiver.username if self.receiver else 'Unknown'}"

    def save(self, *args, **kwargs):
        """
        حفظ الرسالة مع:
        1. تعيين المستلم تلقائياً إذا لم يتم تحديده
        2. تحديث وقت آخر تحديث للمحادثة
        """
        # تعيين المستلم إذا لم يتم تحديده
        if not self.receiver:
            self.receiver = self.conversation.get_other_participant(self.sender)
            
        # تحديث وقت آخر تحديث للمحادثة
        self.conversation.updated_at = self.created_at
        self.conversation.save()
        
        super().save(*args, **kwargs)

class UserStatus(models.Model):
    """
    نموذج حالة المستخدم
    يتتبع حالة المستخدم في نظام المحادثات (متصل، آخر ظهور، يكتب حالياً)
    """
    # العلاقة مع المستخدم (علاقة واحد لواحد)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # حالة الاتصال
    is_online = models.BooleanField(default=False)  # هل المستخدم متصل حالياً
    last_seen = models.DateTimeField(auto_now=True)  # آخر ظهور للمستخدم
    
    # حالة الكتابة
    is_typing = models.BooleanField(default=False)  # هل المستخدم يكتب حالياً
    typing_in_conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )  # المحادثة التي يكتب فيها المستخدم

    def __str__(self):
        """تمثيل نصي لحالة المستخدم"""
        return f"{self.user.username}'s status"
