from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    agree_to_terms = forms.BooleanField(required=True, label='I agree with the terms and conditions')
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_agree_to_terms(self):
        agree = self.cleaned_data.get('agree_to_terms')
        if not agree:
            raise forms.ValidationError('You must agree to the terms and conditions to register.')
        return agree

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.is_active = False  # Deactivate account until email confirmation
        if commit:
            user.save()
            profile = Profile.objects.create(user=user, username=user.username)
            self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        subject = 'Email Verification'
        message = render_to_string('registration/verification_email.html', {
            'user': user,
            'domain': settings.DOMAIN_NAME,
            'uid': uid,
            'token': token,
        })
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

        
class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'avatar']

    def clean_username(self):
        username = self.cleaned_data['username']
        if Profile.objects.filter(username=username).exclude(user=self.instance.user).exists():
            raise ValidationError("This username is already in use. Please choose another one.")
        return username
    

# forms.py
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'image', 'category', 'city', 'state', 'country', 'latitude', 'longitude']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }



class SearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=True)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'file']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Type a message...'}),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text or not text.strip():
            raise forms.ValidationError('Message cannot be empty.')
        return text


class NotificationForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Recipient", required=False)
    send_to_all = forms.BooleanField(required=False, label="Send to All Users")

    class Meta:
        model = Notification
        fields = ['user', 'message', 'is_read', 'send_to_all']




