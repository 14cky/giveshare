from django.urls import path, include
from . views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('signup', signup, name="signup"),
    path('deal/', deal_view, name='deal'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='give/password_reset.html',
        email_template_name='registration/password_reset_email.txt',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='give/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='give/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='give/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('dashboard/', dashboard, name='dashboard'),
    path('create_post/', create_post, name='create_post'),
    path('post/<int:post_id>/', view_post, name='view_post'),
    path('logout/', logout_user, name='logout'),
    path('portfolio/', portfolio, name='portfolio'),
    path('portfolio/<int:user_id>/', portfolio, name='portfolio'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('post/<int:post_id>/edit/', edit_post, name='edit_post'),
    path('search/', search, name='search'),
    path('portfolio2/<int:user_id>/', portfolio2, name='portfolio2'),
    path('start_private_chat/<int:user_id>/', start_private_chat, name='start_private_chat'),
    path('upload_file/', upload_file, name='upload_file'),
    path('delete_file/', delete_file, name='delete_file'),
    path('about/', about_us, name='about_us'),
    path('contact_us/', contact_us, name='contact_us'),
    path('notifications/', notifications, name='notifications'),
    path('delete_notification/<int:notification_id>/', delete_notification, name='delete_notification'),
    path('chat/', chat_page, name='chat_page'),
    path('chat/<int:chat_id>/', load_chat, name='load_chat'),
    path('chat/<int:chat_id>/send_message/', send_message, name='send_message'),
    path('chat/<int:chat_id>/new_messages/', new_messages, name='new_messages'),
    path('save_location/', save_location, name='save_location'),
    path('chat/<int:chat_id>/delete/', delete_chat, name='delete_chat'),
]



