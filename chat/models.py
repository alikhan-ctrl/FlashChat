from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    CHAT_TYPES = (
        ("saved", "Избранное"),
        ("private", "Личный чат"),
    )

    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User)
    chat_type = models.CharField(max_length=20, choices=CHAT_TYPES, default="private")
    is_pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        upload_to="chat_images/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.text


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return self.user.username