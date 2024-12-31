from django.db.models import Count, Q, Max, F, ExpressionWrapper, BooleanField
from .models import Conversation, Message

def chat_context(request):
    if not request.user.is_authenticated:
        return {
            'unread_messages_count': 0,
            'recent_chats': []
        }

    # Get all conversations for the user with latest message and unread count
    conversations = (
        Conversation.objects.filter(participants=request.user)
        .annotate(
            last_message_time=Max('messages__created_at'),
            other_user=F('participants__id'),
            unread_count=Count(
                'messages',
                filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
            ),
            has_unread=ExpressionWrapper(
                Q(unread_count__gt=0),
                output_field=BooleanField()
            )
        )
        .exclude(other_user=request.user.id)
        .prefetch_related('participants', 'messages')
        .order_by('-last_message_time')[:5]
    )

    # Format the conversations for the template
    recent_chats = []
    for conv in conversations:
        other_user = conv.participants.exclude(id=request.user.id).first()
        last_message = conv.messages.order_by('-created_at').first()
        
        if other_user and last_message:
            recent_chats.append({
                'other_user': other_user,
                'last_message': last_message,
                'has_unread': conv.has_unread,
            })

    # Get total unread messages count
    conversations = Conversation.objects.filter(participants=request.user)
    unread_messages_count = sum(conversation.get_unread_count(request.user) for conversation in conversations)

    return {
        'unread_messages_count': unread_messages_count,
        'recent_chats': recent_chats
    }
