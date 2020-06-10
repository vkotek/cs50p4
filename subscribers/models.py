from django.db import models

from restaurants.models import Restaurant

# Create your models here.
class Subscriber(models.Model):

    email = models.EmailField()
    preferences = models.ManyToManyField(Restaurant)
    subscribed = models.DateTimeField()
    token = models.CharField(max_length=24)
