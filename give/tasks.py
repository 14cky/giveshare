from background_task import background
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import Message
from django.db.models import Q

def count_and_send_email_notification(user_id, sender_id):
    user = User.objects.get(id=user_id)
    sender = User.objects.get(id=sender_id)
    
    # Calculate the time window (last 5 minutes)
    time_threshold = timezone.now() - timedelta(minutes=5)
    
    # Count the messages from sender to the user within the last 5 minutes
    message_count = Message.objects.filter(
        chat__participants=user,
        sender=sender,
        timestamp__gte=time_threshold
    ).count()

    if message_count > 0:
        # Prepare the email content
        subject = 'New Messages Notification'
        message = f"You have received {message_count} new message(s) from {sender.username} in the last 5 minutes."
        recipient_list = [user.email]
        send_mail(subject, message, 'no-reply@yourapp.com', recipient_list)
