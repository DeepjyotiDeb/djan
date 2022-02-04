from email.message import Message
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
# from django.contrib.auth.models import User #creating a user model using django library
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message, User
from .forms import RoomForm, MessageForm, UserForm, MyUserCreationForm
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
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email) #comparing usernames from db with the username from request
        except:
            pass

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user) #creating a session
            return redirect('home')
        else:
            messages.error(request, 'User or password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) #to not auto save and go to next line
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

    topics = Topic.objects.all()[0:3]
    room_count = rooms.count() #works faster than len
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q)) #.order_by('-created')
    # room_messages = Message.objects.all()
    context = {'rooms': rooms, 'topics': topics, 
                'room_count': room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created') #from Message in models, small here #many-to-one=> _set.all()
    participants = room.participants.all()#many-many= .all()
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

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms =  user.room_set.all()
    room_messages =  user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_messages':room_messages,
                'topics':topics} #rooms is used beacuse feed_comp and others use rooms
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        # form = RoomForm(request.POST) #saving to db
        # if form.is_valid():
        #     room = form.save(commit=False) #to not automatically save
        #     room.host = request.user
        #     room.save()
        return redirect('home')

    context = {'form': form , 'topics':topics} 
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form=RoomForm(instance=room)
    topics = Topic.objects.all()
    # pdb.set_trace()
    form = RoomForm(instance = room)#prefilling the room form
    
    if request.user != room.host:
        return HttpResponse('Not your instance!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name=request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        
    context = {'form': form, 'topics':topics, 'room':room}
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
    # pdb.set_trace()
    if request.user != message.user:
        return HttpResponse('Not your instance!')

    if request.method == 'POST':
        form = MessageForm(request.POST, instance = message) #directing to the form in room_form.html
        if form.is_valid():
            form.save()
            return redirect('room', pk=message.room_id)
            # return render(f'base/room/{message.room_id}.html')
            # return HttpResponseRedirect(previous_page) #find more

    context = {'form': form} #KEEP NAMES SAME!!!!!
    return render(request, 'base/edit-message-form.html', context)

@login_required(login_url='login')
def updateUser(request):
    user =request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form':form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' #returning all at empty

    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics})    

def activity(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages':room_messages})