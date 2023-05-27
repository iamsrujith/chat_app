import random

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect

from chat.forms import SignupForm
from chat.models import User

user = get_user_model()


@login_required
def home(request):
    if request.user is not None:
        current_user = User.objects.get(pk=request.user.pk)
        if current_user.in_chat:
            current_user.in_chat = False
        current_user.save()
    return render(request, 'home.html')


@login_required
def chat(request, room_name):
    if request.user is not None:
        current_user = User.objects.get(pk=request.user.pk)
        if not current_user.in_chat:
            current_user.in_chat = True
        current_user.save()
    return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                user.is_online = True
                user.save()
                return redirect('home')
    else:
        if request.user.is_authenticated:
            return redirect('home')
        form = AuthenticationForm()
        form.fields['username'].label = 'Email'

    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    user = User.objects.filter(pk=request.user.pk).first()
    user.is_online = False
    user.save()
    logout(request)
    return redirect('login')


@login_required
def match_users(request):
    user = request.user
    online_users = User.objects.filter(is_online=True).exclude(pk=user.pk)
    matched_users = []
    for i in online_users:
        for interest in i.interests:
            if interest in user.interests:
                matched_users.append(i)
                break

    if matched_users:
        matched_user = random.choice(matched_users)
    else:
        matched_user = random.choice(online_users)

    # Create a chat room name based on user IDs
    room_name = f"{user.pk}-{matched_user.pk}"
    # print(room_name)

    # Get the channel layer
    channel_layer = get_channel_layer()

    # Send the redirect message to the matched user's channel group
    async_to_sync(channel_layer.group_send)(
        f"chat_{room_name}",
        {
            'type': 'chat_message',
            'text': f'/chat/{room_name}'
        }
    )

    return HttpResponse(f'/chat/{room_name}')


def update_status(request):
    user = request.GET.get("user")
    status = request.GET.get("status")
    if user is not None:
        user = User.objects.get(pk=user)
        if status == "on":
            user.is_online = True
            updated_status = "Online"
        else:
            user.is_online = False
            updated_status = "Offline"
        user.save()

    # Return the updated content as HTTP response
    return HttpResponse(updated_status)
