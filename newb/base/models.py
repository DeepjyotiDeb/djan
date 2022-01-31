from django.db import models
from django.contrib.auth.models import User #creating a user model using django library
# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model): #id created by default
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null = True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null = True) #Room can have only one topic
    name = models.CharField(max_length = 200)
    description = models.TextField(null = True, blank = True) #cannot be blank when set to false
    participants = models.ManyToManyField(User, related_name='participants', blank=True) #User already used in host, so related_name is used
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)

    class Meta: #order by which data is displayed
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) #SET_NULL to preserve room on parent deletion
    body = models.TextField() #put empty to force entry data
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)

    class Meta: #order by which data is displayed
        ordering = ['-updated', '-created']
        
    def __str__(self):
        return self.body[0:50]
