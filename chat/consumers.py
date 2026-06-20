import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        allowed = await self.user_in_room()

        if not allowed:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("type") == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_event",
                    "username": self.user.username,
                    "display_name": await self.get_display_name(),
                }
            )
            return

        if data.get("type") == "delete":
            message_id = data["message_id"]
            deleted = await self.delete_message(message_id)

            if deleted:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "delete_message_event",
                        "message_id": message_id
                    }
                )
            return

        message = data["message"].strip()

        if message == "":
            return

        message_id = await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": self.user.username,
                "display_name": await self.get_display_name(),
                "avatar_url": await self.get_avatar_url(),
                "message_id": message_id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "username": event["username"],
            "display_name": event["display_name"],
            "avatar_url": event["avatar_url"],
            "message_id": event["message_id"]
        }))

    async def typing_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "username": event["username"],
            "display_name": event["display_name"]
        }))

    async def delete_message_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "delete",
            "message_id": event["message_id"]
        }))

    @database_sync_to_async
    def user_in_room(self):
        return ChatRoom.objects.filter(
            id=self.room_id,
            users=self.user
        ).exists()

    @database_sync_to_async
    def save_message(self, message):
        room = ChatRoom.objects.get(id=self.room_id)

        msg = Message.objects.create(
            room=room,
            user=self.user,
            text=message
        )

        return msg.id

    @database_sync_to_async
    def delete_message(self, message_id):
        msg = Message.objects.filter(
            id=message_id,
            room_id=self.room_id,
            user=self.user
        ).first()

        if msg:
            msg.delete()
            return True

        return False

    @database_sync_to_async
    def get_display_name(self):
        profile = self.user.profile
        return profile.display_name or self.user.username

    @database_sync_to_async
    def get_avatar_url(self):
        try:
            if self.user.profile.avatar:
                return self.user.profile.avatar.url
        except:
            return ""

        return ""