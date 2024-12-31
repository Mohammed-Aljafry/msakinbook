from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Max, F, Count
from .models import Conversation, Message
from django.db.models import Q, Max, Count, F, Value
from django.db.models.functions import Coalesce

@login_required
def conversations_list1(request):
    print('start')
    conversations = (
        Conversation.objects.filter(participants=request.user)
        .annotate(
            last_message_time=Max('messages__created_at'),
            other_user=F('participants__id'),
            unread_count=Count(
                'messages',
                filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
            )
        )
        # .exclude(other_user=request.user.id)
        .order_by('-last_message_time')
    )


    formatted_conversations = []
    print(conversations)
    for conv in conversations:
        print('faiz')
        other_user = conv.participants.exclude(id=request.user.id).first()
        last_message = conv.messages.order_by('-created_at').first()
        
        if other_user and last_message:
            formatted_conversations.append({
                'conversation': conv,
                'other_user': other_user,
                'last_message': last_message,
                'unread_count': conv.unread_count
            })
    # print(conversations)


    print(formatted_conversations)

    return render(request, 'chat/conversations_list.html', {
        'conversations': formatted_conversations
    })

def conversations_list(request):
    # طباعة نقطة بدء الدالة
    print("Start fetching conversations for user:", request.user.username)

    # استعلام لجلب المحادثات المرتبطة بالمستخدم
    conversations = (
        Conversation.objects.filter(participants=request.user)
        .annotate(
            last_message_time=Max('messages__created_at'),
            unread_count=Count(
                'messages',
                filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
            )
        )
        .order_by('-last_message_time')
    )

    # طباعة الاستعلام الناتج
    print("Conversations Query:", conversations.query)

    # قائمة لتنسيق المحادثات
    formatted_conversations = []

    for conv in conversations:
        print(f"Processing conversation ID: {conv.id}")

        # جلب المستخدم الآخر في المحادثة
        other_user = conv.participants.exclude(id=request.user.id).first()
        last_message = conv.messages.order_by('-created_at').first()

        print(f"Other user: {other_user}, Last message: {last_message}")

        # التحقق من وجود مستخدم آخر وآخر رسالة
        if other_user and last_message:
            formatted_conversations.append({
                'conversation': conv,
                'other_user': other_user,
                'last_message': last_message,
                'unread_count': conv.unread_count
            })

    # طباعة النتائج بعد التنسيق
    print("Formatted Conversations:", formatted_conversations)

    # تمرير النتائج إلى القالب
    return render(request, 'chat/conversations_list.html', {
        'conversations': formatted_conversations
    })

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    messages = conversation.messages.all()
    
    # Mark all messages as read
    messages.filter(receiver=request.user, is_read=False).update(is_read=True)
    
    other_participant = conversation.participants.exclude(id=request.user.id).first()
    
    return render(request, 'chat/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages,
        'other_participant': other_participant
    })

@login_required
def start_conversation(request, username):
    other_user = get_object_or_404(User, username=username)
    
    if other_user == request.user:
        return redirect('conversations_list')
    
    # Check if conversation exists
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    
    return redirect('conversation_detail', conversation_id=conversation.id)

@login_required
def chat_room(request, username):
    other_user = get_object_or_404(User, username=username)
    
    if other_user == request.user:
        return redirect('conversations_list')
    
    # Get or create conversation
    conversation = (
        Conversation.objects.filter(participants=request.user)
        .filter(participants=other_user)
        .first()
    )
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    
    # Mark messages as read
    Message.objects.filter(
        conversation=conversation,
        sender=other_user,
        is_read=False
    ).update(is_read=True)
    
    messages = conversation.messages.order_by('created_at')
    
    return render(request, 'chat/chat_room.html', {
        'conversation': conversation,
        'other_user': other_user,
        'messages': messages
    })

@login_required
def mark_messages_as_read(request, conversation_id):
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        # تحديث حالة القراءة للرسائل المستلمة فقط
        unread_messages = Message.objects.filter(
            conversation=conversation,
            receiver=request.user,
            is_read=False
        )
        unread_messages.update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def chat_room(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Get or create conversation
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    
    # Get messages
    messages = conversation.messages.all()
    
    # Mark messages as read
    messages.filter(receiver=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'chat/chat_room.html', {
        'other_user': other_user,
        'conversation': conversation,
        'messages': messages,
    })

@login_required
def get_conversations(request):
    # Get all conversations for the current user
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        last_message_time=Coalesce(Max('messages__created_at'), Value(None)),
        unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False, messages__receiver=request.user)
        )
    ).prefetch_related('participants', 'messages').order_by('-last_message_time')
    
    conversations_data = []
    for conv in conversations:
        # Get the other participant
        other_user = conv.participants.exclude(id=request.user.id).first()
        
        # Get last message
        last_message = conv.messages.order_by('-created_at').first()
        
        conversations_data.append({
            'id': conv.id,
            'participants': [{
                'id': p.id,
                'name': p.get_full_name() or p.username,
                'avatar_url': p.profile.avatar_url if hasattr(p, 'profile') else None
            } for p in conv.participants.all()],
            'last_message': last_message.content if last_message else None,
            'last_message_time': last_message.created_at.isoformat() if last_message else None,
            'unread_count': conv.unread_count
        })
    
    return JsonResponse({'conversations': conversations_data})
