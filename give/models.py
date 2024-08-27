from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, Group, Permission
import pytz

class Ad(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='ads/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Categories"
    

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    last_seen = models.DateTimeField(default=timezone.now)
    is_typing = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)  # Add this line
    city = models.CharField(max_length=100, null=True, blank=True)   # Add this line
    timezone = models.CharField(max_length=100, choices=[(tz, tz) for tz in pytz.all_timezones], default='UTC')
    email_notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        else:
            return '/static/default/avatar.png'
    


class PrivateChat(models.Model):
    participants = models.ManyToManyField(User)

class Message(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]

    chat = models.ForeignKey(PrivateChat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages_sent', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='messages/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    
    def __str__(self):
        return str(self.id)
    def files(self):
        file = MessageFile.objects.filter(message=self)
        return file


class MessageFile(models.Model):
    message = models.ForeignKey(Message, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='messages/', blank=True, null=True)

class DeletedChat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat = models.ForeignKey(PrivateChat, on_delete=models.CASCADE)


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Specify related_name to avoid conflicts
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)

class Photo(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='photos/')
    description = models.TextField()

    def __str__(self):
        return self.description

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    photos = models.ManyToManyField(Photo, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    username = models.CharField(max_length=100) 
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)  # Add this line
    country = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)  # Add this line
    longitude = models.FloatField(null=True, blank=True) 
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.title

    @property
    def image_url(self):
        first_photo = self.photos.first()
        if first_photo:
            return first_photo.image.url
        elif self.image:
            return self.image.url
        else:
            return '/staticfiles/default/defaulp.png'

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    sender_name = models.CharField(max_length=100, default="Give&Share")
    message_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Notification for {self.user.username}"
