from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ChatRoom, Message
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth import logout
from .models import ChatRoom, Message, Profile
from .models import Profile


@login_required
def chats_page(request):
    saved_chat, created = ChatRoom.objects.get_or_create(
        name=f"Избранное {request.user.username}",
        chat_type="saved",
    )

    saved_chat.users.set([request.user])

    rooms = ChatRoom.objects.filter(users=request.user).order_by("-is_pinned", "name")

    for room in rooms:
        room.last_message = Message.objects.filter(room=room).order_by("-created_at").first()

    return render(request, "chat/chats.html", {
        "rooms": rooms
    })

@login_required
def create_chat(request):
    users = User.objects.exclude(id=request.user.id)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        friend = User.objects.get(id=user_id)

        room = ChatRoom.objects.create(
            name=f"{request.user.username} и {friend.username}",
            chat_type="private"
        )
        room.users.add(request.user, friend)

        return redirect("room", room_id=room.id)

    return render(request, "chat/create_chat.html", {
        "users": users
    })


@login_required
def room_page(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, users=request.user)

    if request.method == "POST":
        text = ""
        image = request.FILES.get("image")

        if text or image:
            Message.objects.create(
                room=room,
                user=request.user,
                text=text,
                image=image
            )

        return redirect("room", room_id=room.id)

    messages = Message.objects.filter(room=room).order_by("created_at")

    return render(request, "chat/room.html", {
        "room": room,
        "messages": messages
    })


@login_required
def delete_message(request, message_id):
    if request.method == "POST":
        message = get_object_or_404(Message, id=message_id)

        if message.user == request.user:
            message.delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"})

def register_page(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("chats")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {
        "form": form
    })

@login_required
def profile_page(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.display_name = request.POST.get("display_name", "").strip()

        if request.FILES.get("avatar"):
            profile.avatar = request.FILES.get("avatar")

        profile.save()
        return redirect("profile")

    return render(request, "chat/profile.html", {
        "profile": profile
    })


@login_required
def logout_page(request):
    logout(request)
    return redirect("/accounts/login/")

@login_required
def delete_chat(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, users=request.user)

    if request.method == "POST":
        room.delete()
        return redirect("chats")

    return redirect("chats")


@login_required
def rename_chat(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, users=request.user)

    if request.method == "POST":
        new_name = request.POST.get("name", "").strip()

        if new_name:
            room.name = new_name
            room.save()

    return redirect("room", room_id=room.id)

@login_required
def pin_chat(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, users=request.user)

    if request.method == "POST":
        room.is_pinned = not room.is_pinned
        room.save()

    return redirect("chats")

def home_page(request):
    if request.user.is_authenticated:
        return redirect("chats")
    return render(request, "chat/index.html")