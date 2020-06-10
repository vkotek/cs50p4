from django.contrib import admin

# Register your models here.


from subscribers.models import Subscriber

admin.site.register(Subscriber)