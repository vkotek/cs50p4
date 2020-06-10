from django.db import models

from restaurants.models import Restaurant

# Create your models here.
class Subscriber(models.Model):

    email = models.EmailField()
    preferences = models.ManyToManyField(Restaurant)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    modified = models.DateTimeField(auto_now=True, blank=True)
    token = models.CharField(max_length=24, blank=True)

    def __str__(self):
        return f'{self.email}'