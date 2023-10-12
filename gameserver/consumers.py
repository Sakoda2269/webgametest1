import json
import random
from collections import defaultdict
import math
from . import models
from channels.generic.websocket import AsyncWebsocketConsumer
import uuid
 
class ChatConsumer(AsyncWebsocketConsumer):
    joined = defaultdict(list)
    player_id = defaultdict(str)
    async def connect(self):
        print("connect")
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        self.user_id = uuid.uuid4()
 
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
 
        await self.accept()
 
    async def disconnect(self, close_code):
        # Leave room group
        leave_id = self.player_id[self.user_id]
        print(leave_id, "left game")
        self.joined.pop(leave_id, None)
        self.player_id.pop(self.user_id, None)
        await self.channel_layer.group_send( #メッセージを送信(chat_message()を使用?)
            self.room_group_name, {"type": "chat_message", "method": "leave", "id" : leave_id, "data":{}}
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
 
    # Receive message from WebSocket
    #websocketからメッセージを受け取ったら呼ばれる
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data["method"] == "join":
            send_data = {}
            pos = {
                "pos_x": random.randrange(-40, 40, 1),
                "pos_z" : random.randrange(-40, 40, 1)
            }
            players = list(self.joined.keys())
            send_data["pos"] = pos
            send_data["players"] = players
            join_id = data["id"]
            self.player_id[self.user_id] = join_id
            send_data["joined"] = self.joined
            self.joined[join_id] = [pos["pos_x"], 1, pos["pos_z"], 0, 90, 0]
            await self.channel_layer.group_send( #メッセージを送信(chat_message()を使用?)
                self.room_group_name, {"type": "chat_message", "method": "join", "id" : join_id, "data" : send_data}
            )
            print(data["name"] + " joined!")

        if data["method"] == "updata":
            pos_x = data["pos_x"]
            pos_y = data["pos_y"]
            pos_z = data["pos_z"]
            rotate_y = data["rotate_y"]
            updata_id = data["id"]
            self.joined[updata_id] = [pos_x, pos_y, pos_z, 0, rotate_y, 0]
            send_data = self.joined[updata_id]
            await self.channel_layer.group_send( #メッセージを送信(chat_message()を使用?)
                self.room_group_name, {"type": "chat_message", "method": "updata", "id" : updata_id, "data" : send_data}
            )
        
        if data["method"] == "shot":
            pos_x = data["pos_x"]
            pos_y = data["pos_y"]
            pos_z = data["pos_z"]
            rotate_y = data["rotate_y"]
            shot_id = data["id"]
            send_data = {
                "pos_x":pos_x,
                "pos_y":pos_y,
                "pos_z":pos_z,
                "rotate_y":rotate_y
            }
            await self.channel_layer.group_send( #メッセージを送信(chat_message()を使用?)
                self.room_group_name, {"type": "chat_message", "method": "shot", "id" : shot_id, "data" : send_data}
            )

            
 
        # Send message to room group

 
    # Receive message from room group
    async def chat_message(self, event):
        message = event["method"]
        data = event["data"]
        id = event["id"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"method": message, "data":data, "id":id}))