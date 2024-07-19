from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib.auth import authenticate, login,logout
from .forms import *
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from validate_email import validate_email
import re 
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.gis.measure import D
from geopy.distance import geodesic
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.views.generic import View
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.views import PasswordContextMixin
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.utils.encoding import force_bytes
from django_countries import countries
from geopy.distance import geodesic   
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PrivateChat, Message, Profile, DeletedChat
from .forms import MessageForm
from django.utils.dateparse import parse_datetime
from django.db.models import Q
import mimetypes
from geopy.geocoders import Nominatim
from django.contrib.sites.shortcuts import get_current_site

User = get_user_model()

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'give/home.html')
def deal_view(request):
    return render(request, 'give/deal.html')

def is_valid_email(email):
    """Simple regex check for email format."""
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email)

def send_verification_email(user, request):
    current_site = get_current_site(request)
    mail_subject = 'Activate your Give&Share account'
    message = render_to_string('registration/verification_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'That email is already registered in our website.')
            else:
                user = form.save(commit=False)
                user.is_active = False  # Deactivate account until email confirmation
                user.save()
                profile = Profile.objects.create(user=user, username=username)
                form.send_verification_email(user)
                messages.success(request, 'Account created! Please check your email to verify your account. It can take 3-5 minutes.')
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'give/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        backend = 'django.contrib.auth.backends.ModelBackend'  # Change this if you are using a different backend
        login(request, user, backend=backend)
        messages.success(request, 'Your account has been confirmed.')
        return redirect('dashboard')
    else:
        messages.warning(request, 'The confirmation link was invalid, possibly because it has already been used.')
        return redirect('signup')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session.set_expiry(30*24*60*60)
                return redirect('dashboard')
            else:
                messages.error(request, 'Email or password is incorrect')
    else:
        form = LoginForm()
    return render(request, 'give/login.html', {'form': form})


@login_required(login_url='login')
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'username': request.user.email})

    # Ensure profile has latitude, longitude, and country
    if profile.latitude and profile.longitude and not profile.country:
        geolocator = Nominatim(user_agent="give")
        location = geolocator.reverse((profile.latitude, profile.longitude), language='en')
        if location:
            address = location.raw.get('address', {})
            profile.country = address.get('country')
            profile.save()

    user_location = (profile.latitude, profile.longitude)
    user_country = profile.country

    # Fetch all posts
    all_posts = Post.objects.all().order_by('-created_at')
    post_list = []

    for post in all_posts:
        post_list.append({
            'post': post,
        })

    # Filter posts by user's country
#    same_country_posts = [post_info['post'] for post_info in post_list if post_info['post'].country and post_info['post'].country.strip().lower() == user_country]

#    if len(same_country_posts)>0:
#        posts = same_country_posts
#    else:
        # If no posts from the same country, take recent posts from other countries
    posts = [post_info['post'] for post_info in post_list]
  # Get top 10 recent posts

    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    notifications_count = notifications.filter(is_read=False).count()

    for notification in notifications:
        notification.is_read = True
        notification.save()

    context = {
        'posts': posts,
        'notifications': notifications,
        'notifications_count': notifications_count,
    }

    return render(request, 'give/dashboard.html', context)

@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        category_id = request.POST.get('category')
        new_category_name = request.POST.get('category_new')
        images = request.FILES.getlist('images')
        uploaded_file_ids = request.POST.get('uploaded_file_ids', '')
        deleted_file_ids = request.POST.get('deleted_file_ids', '')

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Convert empty strings to None
        latitude = float(latitude) if latitude else None
        longitude = float(longitude) if longitude else None

        category = None
        if category_id and category_id != 'none':
            category = get_object_or_404(Category, id=category_id)
        elif new_category_name:
            category, _ = Category.objects.get_or_create(
                user=request.user,
                name=new_category_name
            )

        country = None
        city = None
        state = None
        if latitude and longitude:
            geolocator = Nominatim(user_agent="your_app_name")
            location = geolocator.reverse((latitude, longitude), language='en')
            if location:
                address = location.raw.get('address', {})
                country = address.get('country')
                state = address.get('state')
                city = address.get('city') or address.get('town') or address.get('village')

        post = Post.objects.create(
            user=request.user,
            title=title,
            description=description,
            category=category,
            latitude=latitude,
            longitude=longitude,
            country=country,
            state=state,
            city=city
        )

        # Add files uploaded immediately
        for image in images:
            photo = Photo.objects.create(image=image, description="")
            post.photos.add(photo)

        # Add files uploaded gradually
        if uploaded_file_ids:
            for file_id in uploaded_file_ids.split(','):
                if file_id and file_id not in deleted_file_ids.split(','):
                    try:
                        photo = Photo.objects.get(id=file_id)
                        post.photos.add(photo)
                    except Photo.DoesNotExist:
                        pass

        messages.success(request, 'Post created successfully')
        return redirect('dashboard')

    categories = Category.objects.filter(Q(user=request.user) | Q(default=True))
    return render(request, 'give/create_post.html', {'categories': categories})

@login_required(login_url='login')
def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        try:
            photo = Photo.objects.create(image=file, description="")
            return JsonResponse({'success': True, 'file_id': photo.id, 'file_url': photo.image.url})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required(login_url='login')
def delete_file(request):
    if request.method == 'POST':
        file_id = request.GET.get('file_id')
        try:
            photo = Photo.objects.get(id=file_id)
            photo.delete()
            return JsonResponse({'success': True})
        except Photo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'File does not exist'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required(login_url='login')
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile, created = Profile.objects.get_or_create(user=post.user)
    return render(request, 'give/view_post.html', {'post': post, 'profile': profile})


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def portfolio(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('portfolio')
    else:
        form = ProfileForm(instance=profile)

    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    post_list = [{
        'post': post,
        'first_photo': post.photos.first(),  # Get the first photo
    } for post in posts]

    return render(request, 'give/portfolio.html', {
        'form': form,
        'profile': profile,
        'post_list': post_list,
    })


@login_required(login_url='login')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:
        post.delete()
        messages.success(request, 'Post deleted successfully')
    else:
        messages.error(request, 'You do not have permission to delete this post')
    return redirect('portfolio')

@login_required(login_url='login')
def edit_post(request, post_id):
    post_instance = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post_instance)
        if form.is_valid():
            # Handle image deletion
            delete_images = request.POST.getlist('delete_images')
            if delete_images:
                Photo.objects.filter(id__in=delete_images).delete()
            
            # Save the post form
            form.save()

            # Handle new images
            images = request.FILES.getlist('images')
            for image in images:
                photo = Photo.objects.create(image=image)
                post_instance.photos.add(photo)
                
            messages.success(request, 'Post updated successfully!')
            return redirect('portfolio')
    else:
        form = PostForm(instance=post_instance)

    categories = Category.objects.filter(Q(user=request.user) | Q(default=True))
    context = {
        'form': form,
        'post': post_instance,
        'categories': categories
    }
    return render(request, 'give/edit_post.html', context)


@login_required(login_url='login')
def search(request):
    query = request.GET.get('query', '')
    filter_by = request.GET.get('filter_by', 'title')
    country = request.GET.get('country', '')
    state = request.GET.get('state','')

    posts = Post.objects.all()
    users = User.objects.all()

#    if query or country or state:
#        if filter_by == 'user':
#            users = User.objects.filter(username__icontains=query)
#        else:
#            filters = Q()
            
#            if filter_by == 'title':
#                filters &= Q(title__icontains=query)
#            elif filter_by == 'category':
#                filters &= Q(category__name__icontains=query)
            
#            if country:
#                filters &= Q(country__icontains=country)
#                if country.lower()=='united states' and state:
#                    filters &= Q(state_icontains=state)
            
#            posts = Post.objects.filter(filters).distinct()
            
#            post_list = []
#            for post in posts:
#                if post.latitude and post.longitude:
#                    post_distance = geodesic((request.user.profile.latitude, request.user.profile.longitude), (post.latitude, post.longitude)).km
#                else:
#                    post_distance = float('inf')  # Assign a very high distance for posts with no location

#                post_list.append({
#                    'post': post,
#                    'distance': post_distance
#                })
#
#            post_list.sort(key=lambda x: (x['distance'], -x['post'].created_at.timestamp()))
#            posts = [post_info['post'] for post_info in post_list]
 
    if query:
         if filter_by == 'title':
             posts = posts.filter(title__icontains=query)
         elif filter_by == 'category':
             posts = posts.filter(category__name__icontains=query)
         elif filter_by == 'user':
             users = users.filter(username__icontains=query)

    if country:
         posts = posts.filter(country=country)
         if country == 'United States' and state:
             posts = posts.filter(state=state)
   
    # List of countries for the dropdown
    countries = [
        "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda",
        "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",
        "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia",
        "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso",
        "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic",
        "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba",
        "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic",
        "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia",
        "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany",
        "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti",
        "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel",
        "Italy", "Ivory Coast", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
        "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia",
        "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia",
        "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico",
        "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique",
        "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger",
        "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau",
        "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland",
        "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia",
        "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe",
        "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia",
        "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan",
        "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan",
        "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia",
        "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates",
        "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City",
        "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
    ]

    states = [
        "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming",
    ]

    return render(request, 'give/search.html', {
        'posts': posts,
        'users': users,
        'query': query,
        'filter_by': filter_by,
        'state': state,
        'states': states,
        'country': country,
        'countries': countries,
    })



@login_required
def start_private_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    chats = PrivateChat.objects.filter(participants=request.user).filter(participants=other_user)

    if chats.exists():
        chat = chats.first()
        DeletedChat.objects.filter(user=request.user, chat=chat).delete()
    else:
        chat = PrivateChat.objects.create()
        chat.participants.add(request.user)
        chat.participants.add(other_user)
    
    return redirect('load_chat', chat_id=chat.id)



@login_required
def private_chat(request, chat_id):
    chat = get_object_or_404(PrivateChat, id=chat_id)
    other_user = chat.participants.exclude(id=request.user.id).first()
    messages = chat.messages.all()  # Use the related_name 'messages'

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.save()
            DeletedChat.objects.filter(user=request.user, chat=chat).delete()
            
            # Create a notification for the recipient
            Notification.objects.create(
            user=other_user,
            message=f"{request.user.username} texted you",
        )

            return redirect('chat_page', chat_id=chat.id)
    else:
        form = MessageForm()

    context = {
        'chat': chat,
        'profile': other_user.profile,
        'messages': messages,
        'form': form
    }
    return render(request, 'give/chat.html', context)


@csrf_exempt
@login_required
def save_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        state = data.get('state')

        # Use an external API to get location details
        url = f'https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={latitude}&longitude={longitude}&localityLanguage=en'
        response = requests.get(url)
        location_data = response.json()

        # Save location data to the database
        user = request.user
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.country = location_data.get('countryName')
        user_profile.city = location_data.get('city')
        user_profile.state = location_data.get('principalSubdivision')
        user_profile.latitude = latitude
        user_profile.longitude = longitude
        user_profile.state = state
        user_profile.save()

        return JsonResponse(location_data,{'latitude': latitude, 'longitude': longitude, 'state': state})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required(login_url='login')
def portfolio2(request, user_id):
    profile = Profile.objects.get(user_id=user_id)
    posts = Post.objects.filter(user=profile.user).order_by('-created_at')

    post_list = [{
        'post': post,
        'first_photo': post.photos.first(),  # Get the first photo
    } for post in posts]

    return render(request, 'give/portfolio2.html', {
        'profile': profile,
        'post_list': post_list,
        'post_count': posts.count(),
    })

def about_us(request):
    return render(request, 'give/about_us.html')

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Get the username
        username = request.user.username

        # Construct the email message
        subject = f"Contact Us Message from {name}"
        full_message = f"Username: {username}\nName: {name}\nEmail: {email}\n\nMessage:\n{message}"

        # Send an email
        send_mail(
            subject=subject,
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['giveshare18@gmail.com'],
            fail_silently=False,
        )

        messages.success(request, "Your message was submitted successfully, we will read it as soon as possible.")
        return redirect('contact_us')

    return render(request, 'give/contact_us.html')

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')
    for notification in notifications:
        notification.is_read = True
        notification.save()
    return render(request, 'give/notifications.html', {'notifications': notifications})

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect('dashboard')

@login_required
def chat_page(request):
    deleted_chats = DeletedChat.objects.filter(user=request.user).values_list('chat_id', flat=True)
    chats = PrivateChat.objects.filter(participants=request.user).exclude(id__in=deleted_chats)
    query = request.GET.get('q')
    if query:
        chats = chats.filter(participants__username__icontains(query)).distinct()

    context = {
        'chats': chats,
    }
    return render(request, 'give/newchatpage.html', context)

@login_required
def load_chat(request, chat_id):
    chat = get_object_or_404(PrivateChat, id=chat_id)
    other_user = chat.participants.exclude(id=request.user.id).first()
    messages = chat.messages.all()
    profile = other_user.profile

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        message_list = [{
            'text': message.text,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sender': message.sender.username,
            'file': [{
                'url': file.file.url,
                'is_image': mimetypes.guess_type(file.file.url)[0].startswith('image') if file.file else False
            } for file in message.files.all()] if message.files.all() else None,
        } for message in messages]
        data = {
            'profile': {
                'avatar_url': profile.avatar_url,
                'username': profile.username,
                'last_seen': profile.last_seen.strftime('%Y-%m-%d %H:%M:%S'),
            },
            'messages': message_list,
            'current_user': request.user.username,
        }
        return JsonResponse(data)
    return redirect('chat_page')

@login_required
def send_message(request, chat_id):
    chat = get_object_or_404(PrivateChat, id=chat_id)
    form = MessageForm(request.POST, request.FILES)
    if form.is_valid():
        text = form.cleaned_data['text']
        files = request.FILES.getlist('file')
        sender = request.user

        if files:
            msg = Message.objects.create(
                chat=chat,
                sender=sender,
                text=text,
                status='sent'
            )
            for file in files:
                upload_file = MessageFile.objects.create(
                    message = msg,
                    file=file,
                )
        else:
            Message.objects.create(
                chat=chat,
                sender=sender,
                text=text,
                status='sent'
            )
        recipient = chat.participants.exclude(id=request.user.id).first()
        Notification.objects.create(user=recipient, message=f"{request.user.username} sent you a message.")

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})

@login_required
def new_messages(request, chat_id):
    chat = Message.objects.filter(chat__id = chat_id)
    since = request.GET.get('since')
    if since:
        since = parse_datetime(since)
        new_messages = chat.filter(timestamp__gt=since)
    else:
        new_messages = chat.all()

    message_list = []
    for message in new_messages:
        img_file = []
        files = message.files.all()
        for file in files:
            img_file.append({
                'url': file.file.url,
                'is_image': mimetypes.guess_type(file.file.url)[0].startswith('image') if file.file else False
            })
        sms_body = {
            'text': message.text,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sender': message.sender.username,
            'file': img_file,
        }

        message_list.append(sms_body)

    data = {
        'messages': message_list,
        'current_user': request.user.username,
    }
    return JsonResponse(data)

@login_required
def delete_chat(request, chat_id):
    chat = get_object_or_404(PrivateChat, id=chat_id)
    DeletedChat.objects.get_or_create(user=request.user, chat=chat)
    return JsonResponse({'status': 'success'})

