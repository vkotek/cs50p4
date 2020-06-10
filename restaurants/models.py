from django.db import models

# Create your models here.
class Restaurant(models.Model):

    languages = [
        ('cs', 'Czech'),
        ('en', 'English'),
    ]

    name = models.CharField(max_length=32)
    language = models.CharField(
        max_length=2, 
        choices=languages
    )
    url = models.URLField()
    location_url = models.URLField(blank=True)
    css_selector = models.CharField(max_length=128, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    modified = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f'{self.name}'

class Menu(models.Model):

    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True, blank=True)
    content = models.CharField(max_length=2048)