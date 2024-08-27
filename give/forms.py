from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from email_validator import validate_email, EmailNotValidError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    agree_to_terms = forms.BooleanField(required=True, label='I agree with the terms and conditions')
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def clean_agree_to_terms(self):
        agree = self.cleaned_data.get('agree_to_terms')
        if not agree:
            raise forms.ValidationError('You must agree to the terms and conditions to register.')
        return agree

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered. Please choose another one.")
        
        # Send a test email to the provided address
        try:
            send_mail(
                'Email Verification - Give&Share',
                'This is a test email to verify your email address. If you received this email, your address is valid.',
                'no-reply@giveshare.com',
                [email],
            )
        except BadHeaderError:
            raise ValidationError("Invalid header found.")
        except Exception as e:
            raise ValidationError("Failed to send email. Please ensure the email address is valid.")
        
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
        
class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'avatar', 'email_notifications_enabled']

    def clean_username(self):
        username = self.cleaned_data['username']
        if Profile.objects.filter(username=username).exclude(user=self.instance.user).exists():
            raise forms.ValidationError("This username is already in use. Please choose another one.")
        return username

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'category', 'city', 'state', 'country', 'latitude', 'longitude']
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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PostForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(Q(user=user) | Q(default=True))

class SearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=True)

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'file']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Type a message...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        file = cleaned_data.get('file')

        if not text and not file:
            raise forms.ValidationError('You must provide a message or a file.')
        
        return cleaned_data

class NotificationForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Recipient", required=False)
    send_to_all = forms.BooleanField(required=False, label="Send to All Users")

    class Meta:
        model = Notification
        fields = ['user', 'message', 'is_read', 'send_to_all']




