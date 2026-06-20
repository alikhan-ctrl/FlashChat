from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("register/", views.register_page, name="register"),
    path("chats/", views.chats_page, name="chats"),
    path("chats/create/", views.create_chat, name="create_chat"),
    path("chats/<int:room_id>/", views.room_page, name="room"),
    path("messages/<int:message_id>/delete/", views.delete_message, name="delete_message"),
    path("profile/", views.profile_page, name="profile"),
    path("logout/", views.logout_page, name="logout"),
    path("chats/<int:room_id>/delete/", views.delete_chat, name="delete_chat"),
    path("chats/<int:room_id>/rename/", views.rename_chat, name="rename_chat"),
    path("chats/<int:room_id>/pin/", views.pin_chat, name="pin_chat"),
]