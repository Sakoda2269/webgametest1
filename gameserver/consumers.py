import json
import random
from collections import defaultdict
import math
 
from channels.generic.websocket import AsyncWebsocketConsumer
 
 
class ChatConsumer(AsyncWebsocketConsumer):
    joined = defaultdict(list)
    async def connect(self):
        print("connect")
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
 
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
 
        await self.accept()
 
    async def disconnect(self, close_code):
        # Leave room group
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
            id = data["id"]
            send_data["joined"] = self.joined
            self.joined[id] = [pos["pos_x"], 1, pos["pos_z"], 0, 90, 0]
            await self.channel_layer.group_send( #メッセージを送信(chat_message()を使用?)
                self.room_group_name, {"type": "chat_message", "method": "join", "id" : id, "data" : send_data}
            )
            print(data["name"] + " joined!")

        if data["method"] == "updata":
            pos_x = data["possd_x"]
            pos_y = data["pos_y"]
            pos_z = data["pos_z"]
            rotate_y = math.degrees(float(data["rotate_y"]))
            id = data["id"]
            self.joined[id] = [pos_x, pos_y, pos_z, 0, rotate_y, 0]
            send_data = self.joined[id]
            await self.channel_layer.group_send( #メッセージを送信(chat_message()を使用?)
                self.room_group_name, {"type": "chat_message", "method": "updata", "id" : id, "data" : send_data}
            )
 
        # Send message to room group

 
    # Receive message from room group
    async def chat_message(self, event):
        message = event["method"]
        data = event["data"]
        id = event["id"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"method": message, "data":data, "id":id}))