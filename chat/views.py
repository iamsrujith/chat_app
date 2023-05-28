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
        if current_user.is_ready:
            current_user.is_ready = False
        current_user.save()
    return render(request, 'home.html')


@login_required
def connect(request):
    if request.user is not None:
        current_user = User.objects.get(pk=request.user.pk)
        if not current_user.is_ready:
            current_user.is_ready = True
        if current_user.in_chat:
            current_user.in_chat = False
        current_user.save()
    return render(request, 'connect.html')


@login_required
def chat(request, room_name):
    if request.user is not None:
        current_user = User.objects.get(pk=request.user.pk)
        if not current_user.in_chat:
            current_user.in_chat = True
        if current_user.is_ready:
            current_user.is_ready = False
        current_user.save()
    return render(request, 'chat.html')


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
    user.in_chat = False
    user.is_ready = False
    user.save()
    logout(request)
    return redirect('login')


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

    return HttpResponse(updated_status)
