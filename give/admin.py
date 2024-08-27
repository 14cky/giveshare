from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import NotificationForm

# Register Ad model
@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'created_at']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'username', 'avatar']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'default')
    list_filter = ('default', 'user')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'username', 'post_titles', 'created_at', 'country', 'city']

    def post_titles(self, obj):
        posts = Post.objects.filter(user=obj.user)
        return ", ".join([post.title for post in posts])
    post_titles.short_description = 'Post Titles'

class NotificationAdmin(admin.ModelAdmin):
    form = NotificationForm
    list_display = ('user', 'message', 'timestamp', 'is_read')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read', 'timestamp')

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('send_to_all'):
            users = User.objects.all()
            notifications = [
                Notification(user=user, message=obj.message, is_read=obj.is_read)
                for user in users
            ]
            Notification.objects.bulk_create(notifications)
        else:
            super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['send_to_all'].widget.attrs.update({'style': 'display:block; margin-top:20px;'})
        return form

admin.site.register(Notification, NotificationAdmin)
admin.site.register(MessageFile)
