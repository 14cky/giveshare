import os
import django

# Set the environment variable for Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from give.models import Profile
from django.utils.text import slugify

User = get_user_model()

# Ensure all users have profiles
for user in User.objects.all():
    if not hasattr(user, 'profile'):
        base_username = user.username if user.username else user.email.split('@')[0]
        username = slugify(base_username)
        
        # Ensure the username is unique
        original_username = username
        counter = 1
        while Profile.objects.filter(username=username).exists():
            username = f"{original_username}-{counter}"
            counter += 1

        profile = Profile(user=user, username=username)
        profile.save()
        print(f"Profile created for user: {user.username}")
