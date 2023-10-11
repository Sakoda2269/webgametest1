 
from django.shortcuts import render
 
 
def index(request):
    return render(request, "gameserver/index.html")
 
 
def room(request, room_name):
    return render(request, "gameserver/room.html", {"room_name": room_name})