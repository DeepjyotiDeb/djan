from django.db import models

# Create your models here.

class Room(models.Model): #id created by default
    # host = 
    # topic = 
    name = models.CharField(max_length = 200)
    description = models.TextField(null = True, blank = True) #cannot be blank when set to false
    # participants = 
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.name

class Message(models.Model):
    User = 
