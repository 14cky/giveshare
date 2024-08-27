import os
import django

# Set the environment variable for Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from give.models import Profile, Post, Photo, PrivateChat, Message, DeletedChat, Notification, Category

User = get_user_model()

# Check for orphaned profiles
orphan_profiles = Profile.objects.exclude(user_id__in=User.objects.values_list('id', flat=True))
print(f"Found {orphan_profiles.count()} orphan profiles")
orphan_profiles.delete()

# Check for orphaned posts
orphan_posts = Post.objects.exclude(user_id__in=User.objects.values_list('id', flat=True))
print(f"Found {orphan_posts.count()} orphan posts")
orphan_posts.delete()

# Check for orphaned photos
orphan_photos = Photo.objects.exclude(category__user_id__in=User.objects.values_list('id', flat=True))
print(f"Found {orphan_photos.count()} orphan photos")
orphan_photos.delete()

# Check for orphaned private chats
orphan_private_chats = PrivateChat.objects.exclude(participants__id__in=User.objects.values_list('id', flat=True))
print(f"Found {orphan_private_chats.count()} orphan private chats")
orphan_private_chats.delete()

# Check for orphaned messages
orphan_messages = Message.objects.exclude(sender_id__in=User.objects.values_list('id', flat=True))
print(f"Found {orphan_messages.count()} orphan messages")
orphan_messages.delete()

# Check for orphaned deleted chats
orphan_deleted_chats = DeletedChat.objects.exclude(user_id__in=User.objects.values_list('id', flat=True))
print(f"Found {orphan_deleted_chats.count()} orphan deleted chats")
orphan_deleted_chats.delete()

# Check for orphaned notifications
orphan_notifications = Notification.objects.exclude(user_id__in=User.objects.values_list('id', flat=True))
print(f"Found {orphan_notifications.count()} orphan notifications")
orphan_notifications.delete()

# Check for orphaned categories
orphan_categories = Category.objects.exclude(user_id__in=User.objects.values_list('id', flat=True))
print(f"Found {orphan_categories.count()} orphan categories")
orphan_categories.delete()

# Ensure all users have profiles
for user in User.objects.all():
    if not hasattr(user, 'profile'):
        base_username = user.username if user.username else user.email.split('@')[0]
        username = base_username.replace(' ', '').lower()
        
        # Ensure the username is unique
        original_username = username
        counter = 1
        while Profile.objects.filter(username=username).exists():
            username = f"{original_username}-{counter}"
            counter += 1

        profile = Profile(user=user, username=username)
        profile.save()
        print(f"Profile created for user: {user.username}")
