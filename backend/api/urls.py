
from django.urls import path
from .views import create_text, create_user, clear_chat

urlpatterns = [
    path('create-user/', create_user, name='create_user'),
    path('create-text/', create_text, name='create_text'),
    path('clear-chat/', clear_chat, name='clear_chat'),
]
