import random

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
    return render(request, 'home.html')


@login_required
def chat(request, room_name):
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


# @login_required
# def match_users(request):
#     user = request.user
#     online_users = User.objects.filter(is_online=True).exclude(pk=user.pk)
#     matched_users = online_users.filter(interests__in=user.interests.all())
#
#     if matched_users.exists():
#         matched_user = random.choice(matched_users)
#     else:
#         matched_user = random.choice(online_users)
#
#     # Create a chat room name based on user IDs
#     room_name = f"{user.pk}-{matched_user.pk}"
#     print(room_name)
#
#     # Redirect the users to the chat room
#     self.send(text_data=json.dumps({'redirect': f'/chat/{room_name}'}))


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

