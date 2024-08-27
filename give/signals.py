from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from django.utils.text import slugify
from .utils import get_timezone_from_ip, get_geolocation_from_ip
from .apps import user_signed_up

@receiver(user_signed_up)
def create_or_update_user_profile(sender, request, user, **kwargs):
    username = user.username if user.username else user.email.split('@')[0]
    username = slugify(username)  # Ensure the username is slugified
    if Profile.objects.filter(username=username).exists():
        username = f"{username}-{user.id}"  # Append user ID to make it unique

    # Use X-Forwarded-For header if available
    user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if user_ip:
        user_ip = user_ip.split(',')[0]  # Get the first IP in the list
    else:
        user_ip = request.META.get('REMOTE_ADDR')

    print(f"User IP in signal: {user_ip}")  # Debugging line

    # Determine timezone from IP
    user_timezone = get_timezone_from_ip(user_ip) if user_ip else 'UTC'
    print(f"Timezone from IP in signal: {user_timezone}")  # Debugging line

    # Get geolocation data
    geolocation_data = get_geolocation_from_ip(user_ip)
    city = geolocation_data.get('city', None)
    state = geolocation_data.get('region', None)
    country = geolocation_data.get('country', None)

    Profile.objects.create(
        user=user,
        username=username,
        timezone=user_timezone,
        city=city,
        state=state,
        country=country,
    )
