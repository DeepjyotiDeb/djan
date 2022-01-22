from email.message import Message
from django.contrib import admin

# Register your models here.
from .models import Room, Topic, Message

admin.site.register(Room) #tables registered here ?
admin.site.register(Topic)
admin.site.register(Message)