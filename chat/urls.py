from django.urls import path

from chat.views import home, signup, login_view, logout_view, chat, update_status, match_users, connect

urlpatterns = [
    path('', home, name="home"),
    path('chat/<str:room_name>', chat, name="chat"),
    path('signup/', signup, name="signup"),
    path('update-status/', update_status, name="status"),
    path('match-user/', match_users, name="status"),
    path('connect/', connect, name="connect"),
    path('accounts/login/', login_view, name="login"),
    path('accounts/logout/', logout_view, name="logout"),
]
