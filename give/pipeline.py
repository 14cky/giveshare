import logging
from give.utils import get_timezone_from_ip, get_geolocation_from_ip
from give.models import Profile  # Ensure Profile model is imported
from social_core.exceptions import AuthAlreadyAssociated
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

User = get_user_model()

def link_to_existing_user(backend, user, response, *args, **kwargs):
    email = response.get('email')
    if email:
        try:
            existing_user = User.objects.get(email=email)
            if existing_user != user:
                social = backend.strategy.storage.user.get_social_auth(
                    backend.name,
                    response.get('id')
                )
                if social:
                    if social.user != user:
                        raise AuthAlreadyAssociated(backend, social.user)
                else:
                    backend.strategy.storage.user.create_social_auth(
                        existing_user, response.get('id'), backend.name
                    )
                    return {'social': social, 'is_new': False, 'user': existing_user}
        except User.MultipleObjectsReturned:
            existing_users = User.objects.filter(email=email).order_by('-date_joined')
            existing_user = existing_users.first()
            if existing_user != user:
                social = backend.strategy.storage.user.get_social_auth(
                    backend.name,
                    response.get('id')
                )
                if social:
                    if social.user != user:
                        raise AuthAlreadyAssociated(backend, social.user)
                else:
                    backend.strategy.storage.user.create_social_auth(
                        existing_user, response.get('id'), backend.name
                    )
                    return {'social': social, 'is_new': False, 'user': existing_user}
        except User.DoesNotExist:
            pass
    return {'is_new': True}

def get_username(strategy, details, user=None, *args, **kwargs):
    if user:
        return {'username': user.username}

    username = details.get('username') or details.get('email').split('@')[0]
    user_model = strategy.storage.user.user_model()

    # Ensure unique username
    original_username = username
    count = 1
    while user_model.objects.filter(username=username).exists():
        username = f"{original_username}{count}"
        count += 1

    return {'username': username}

def update_user_profile(backend, user, response, *args, **kwargs):
    try:
        with transaction.atomic():
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                # Initialize profile fields if needed
                profile.username = user.username
            else:
                # Ensure unique username for the profile
                original_username = profile.username
                count = 1
                while Profile.objects.filter(username=profile.username).exists():
                    profile.username = f"{original_username}{count}"
                    count += 1
            profile.save()
    except IntegrityError:
        # Retry creating a unique username
        original_username = user.username
        count = 1
        while Profile.objects.filter(username=original_username).exists():
            original_username = f"{user.username}{count}"
            count += 1
        profile, created = Profile.objects.get_or_create(user=user, defaults={'username': original_username})
        profile.username = original_username
        profile.save()
    return {'profile': profile}
