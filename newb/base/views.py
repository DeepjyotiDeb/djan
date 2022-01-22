from django.shortcuts import render
# Create your views here.
from .models import Room

# rooms = [
#     {'id':1, 'name':'learn django'},
#     {'id':2, 'name':'its hard'},
#     {'id':3, 'name':'has a lot of things'},
#     {'id':4, 'name':'will do it'},
# ]

def home(request):
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, 'base/room.html', context)