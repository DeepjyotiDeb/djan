from email.message import Message
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User #creating a user model using django library
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, MessageForm
import pdb

# Create your views here.
# rooms = [
#     {'id':1, 'name':'learn django'},
#     {'id':2, 'name':'its hard'},
#     {'id':3, 'name':'has a lot of things'},
#     {'id':4, 'name':'will do it'},
# ]

# def loginPage(request): #basic template to create a page
#     context = {}
#     return render(request, 'base/login_register.html', context)

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method=='POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username) #comparing usernames from db with the username from request
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user) #creating a session
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) #to get user object? to make sure data can be clean data?
            user.username = user.username.lower()
            user.save()
            login(request, user) #log the user
            return redirect('home')
        else:
            messages.error(request, 'an error occured during registration')
            
    return render(request, 'base/login_register.html', {'form':form} )

def logoutUser(request):
    logout(request)  #deletes session token
    return redirect('home')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' #returning all at empty
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains=q) |
        Q(description__icontains = q)
        )

    topics = Topic.objects.all()
    room_count = rooms.count() #works faster than len

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created') #from Message in models, small here #many-to-one=> set_all
    participants = room.participants.all()#many-many= all()
    if request.method == 'POST':
        message = Message.objects.create( #creating the message here
            user=request.user,
            room=room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)#adding participant(user) to the many-to-many field
        return redirect('room', pk=room.id) 
    
    context = {'room': room, 'room_messages': room_messages,
                'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST) #saving to db
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form} 
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    # pdb.set_trace()
    form = RoomForm(instance = room)#prefilling the room form
    
    if request.user != room.host:
        return HttpResponse('Not your instance!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance = room)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Not your instance')

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

    
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    # pdb.set_trace()
    if request.user != message.user:
        return HttpResponse('Not your instance')

    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def editMessage(request, pk):
    # previous_page = request.META.get('HTTP_REFERER')
    message = Message.objects.get(id=pk)
    form = MessageForm(instance = message) #prefilling the message form

    if request.user != message.user:
        return HttpResponse('Not your instance!')

    if request.method == 'POST':
        form = MessageForm(request.POST, instance = message)
        if form.is_valid():
            form.save()
            return redirect('room', pk=message.room_id)
            # return HttpResponseRedirect(previous_page) #find more

    context = {'form': form} #KEEP NAMES SAME!!!!!
    return render(request, 'base/room_form.html', context)

