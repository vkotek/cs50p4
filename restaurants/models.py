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
    css_selector = models.CharField(max_length=128)
